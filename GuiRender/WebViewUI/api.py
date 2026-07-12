from __future__ import annotations

import logging
import os
from typing import Any

import webview

from GuiRender.AppCore.models import AppConfig, DeviceNode, MemoryTabState, RegisterItem
from GuiRender.AppCore.services import (
    ConfigFileService,
    DeviceTreeService,
    FakeLink,
    LinkService,
    MemoryService,
    RegisterService,
    StartupService,
    clone_items,
    format_hex,
    parse_number,
)


class JGKitApi:
    def __init__(self):
        self.window: webview.Window | None = None
        self._startup_service = StartupService()
        self._device_tree_service = DeviceTreeService()
        self._link_service = LinkService()
        self._register_service = RegisterService(self._link_service)
        self._config_file_service = ConfigFileService()
        self._memory_service = MemoryService(self._link_service)

        self.configs: list[AppConfig] = []
        self.current_config: AppConfig | None = None
        self.core_value: str | None = None
        self.device_nodes: list[DeviceNode] = []
        self.modify_items: list[RegisterItem] = []
        self.memory_tabs: list[MemoryTabState] = []
        self.memory_index = 0
        self.connected = False
        self.launched = False
        self.debug_mode = os.environ.get("JGKIT_LINK_DEBUG", "").lower() in {"1", "true", "yes", "on"}
        self.logs: list[str] = []

    def bootstrap(self) -> dict[str, Any]:
        try:
            self.configs = self._startup_service.load_configs()
            if self.configs and self.current_config is None:
                self.current_config = self.configs[0]
            return self._ok(self._state())
        except Exception as exc:
            logging.exception("Startup failed")
            return self._fail(f"Failed to load startup config: {exc}")

    def launch(self, chip_name: str, tif: str) -> dict[str, Any]:
        try:
            config = self._find_config(chip_name).with_tif(tif)
            if self.connected:
                self.disconnect()
            self.current_config = config
            self._startup_service.activate_config(config)
            self.core_value = config.core_options[0] if config.core_options else None
            self.device_nodes = self._device_tree_service.load_device_tree(config)
            self.modify_items = []
            self.memory_tabs = []
            self.memory_index = 0
            self.connected = False
            self.launched = True
            self._log(f"Loaded {config.name} / {config.selected_tif}")
            return self._ok(self._state())
        except Exception as exc:
            logging.exception("Launch failed")
            return self._fail(f"Launch failed: {exc}")

    def back_to_startup(self) -> dict[str, Any]:
        if self.connected:
            self.disconnect()
        self.launched = False
        return self._ok(self._state())

    def connect(self, core: str | None = None) -> dict[str, Any]:
        try:
            if core:
                self.core_value = core
            self._log("Connecting in debug mode..." if self.debug_mode else "Connecting...")
            if self.debug_mode:
                self._link_service.disconnect()
                self._link_service.handler = FakeLink()
                self.connected = True
            else:
                self.connected = self._link_service.connect(self.core_value)
            self._log("Connected" if self.connected else "Connect failed")
            return self._ok(self._state())
        except Exception as exc:
            logging.exception("Connect failed")
            self.connected = False
            return self._fail(f"Connect failed: {exc}", state=True)

    def disconnect(self) -> dict[str, Any]:
        try:
            self._link_service.disconnect()
            self.connected = False
            self._log("Disconnected")
            return self._ok(self._state())
        except Exception as exc:
            logging.exception("Disconnect failed")
            return self._fail(f"Disconnect failed: {exc}", state=True)

    def set_core(self, core: str) -> dict[str, Any]:
        if not self.connected:
            self.core_value = core
            self._log(f"Core switched to {core}")
        return self._ok(self._state())

    def set_debug_mode(self, enabled: bool) -> dict[str, Any]:
        self.debug_mode = bool(enabled)
        if self.connected:
            self._link_service.disconnect()
            self.connected = False
            self._log("Disconnected")
        self._log("Debug mode enabled" if self.debug_mode else "Debug mode disabled")
        return self._ok(self._state())

    def add_modify_item(self, source_path: list[int]) -> dict[str, Any]:
        try:
            if not self.connected:
                return self._fail("Connect before adding items to Modify Tree.", state=True)
            item = self._get_source_item(source_path)
            cloned = clone_items([item])[0]
            self._refresh_item_tree(cloned)
            self.modify_items.append(cloned)
            self._log(f"Added {cloned.name}")
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Add failed: {exc}", state=True)

    def remove_modify_item(self, path: list[int]) -> dict[str, Any]:
        try:
            parent, index = self._get_modify_parent(path)
            parent.pop(index)
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Remove failed: {exc}", state=True)

    def set_write_value(self, path: list[int], value: str) -> dict[str, Any]:
        try:
            item = self._get_modify_item(path)
            item.write_value = value if value else "NA"
            return self._ok({"updated": True})
        except Exception as exc:
            return self._fail(f"Update failed: {exc}")

    def read_item(self, path: list[int]) -> dict[str, Any]:
        try:
            item = self._get_modify_item(path)
            self._refresh_item_tree(item)
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Read failed: {exc}", state=True)

    def write_item(self, path: list[int], value: str | None = None) -> dict[str, Any]:
        try:
            item = self._get_modify_item(path)
            if value is not None:
                item.write_value = value if value else "NA"
            self._write_item(item)
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Write failed: {exc}", state=True)

    def refresh_modify(self) -> dict[str, Any]:
        try:
            for item in self._iter_modify_items():
                if item.level != 0:
                    item.read_value = format_hex(self._register_service.read32_plus(item.address_expr))
            self._log("Modify tree refreshed")
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Refresh failed: {exc}", state=True)

    def upload_modify(self) -> dict[str, Any]:
        try:
            for item in self._iter_modify_items():
                if item.level != 0 and item.write_value not in {"", "NA"}:
                    self._register_service.write32_plus(item.address_expr, item.write_value)
                    item.read_value = format_hex(self._register_service.read32_plus(item.address_expr))
            self._log("Upload complete")
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Upload failed: {exc}", state=True)

    def refresh_all(self) -> dict[str, Any]:
        try:
            if self.connected:
                for item in self._iter_modify_items():
                    if item.level != 0:
                        item.read_value = format_hex(self._register_service.read32_plus(item.address_expr))
                for tab in self.memory_tabs:
                    self._memory_service.refresh_tab(tab)
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Auto refresh stopped: {exc}", state=True)

    def open_regcfg(self) -> dict[str, Any]:
        path = self._pick_open_file(("Register configuration (*.regcfg)",))
        if not path:
            return self._ok(self._state())
        try:
            self.modify_items = self._config_file_service.read_regcfg(path)
            if self.connected:
                for item in self._iter_modify_items():
                    if item.level != 0 and item.write_value not in {"", "NA"}:
                        self._register_service.write32_plus(item.address_expr, item.write_value)
                self.refresh_modify()
            self._log(f"Opened {path}")
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Open failed: {exc}", state=True)

    def save_regcfg(self) -> dict[str, Any]:
        path = self._pick_save_file("jgkit.regcfg", ("Register configuration (*.regcfg)",))
        if not path:
            return self._ok(self._state())
        try:
            self._config_file_service.write_regcfg(path, self.modify_items)
            self._log(f"Saved {path}")
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Save failed: {exc}", state=True)

    def save_glicfg(self) -> dict[str, Any]:
        path = self._pick_save_file("jgkit.glicfg", ("Glimpse configuration (*.glicfg)",))
        if not path:
            return self._ok(self._state())
        try:
            self._config_file_service.write_glicfg(path, self.modify_items, self._register_service)
            self._log(f"Saved {path}")
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Glimpse failed: {exc}", state=True)

    def add_memory(self, address: str) -> dict[str, Any]:
        try:
            tab = self._memory_service.create_tab(parse_number(address))
            self.memory_tabs.append(tab)
            self.memory_index = len(self.memory_tabs) - 1
            self._log(f"Added memory tab {tab.name}")
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Add memory failed: {exc}", state=True)

    def select_memory(self, index: int) -> dict[str, Any]:
        if self.memory_tabs:
            self.memory_index = max(0, min(int(index), len(self.memory_tabs) - 1))
        return self._ok(self._state())

    def remove_memory(self, index: int) -> dict[str, Any]:
        try:
            if self.memory_tabs:
                self.memory_tabs.pop(int(index))
                self.memory_index = max(0, min(self.memory_index, len(self.memory_tabs) - 1))
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Remove memory failed: {exc}", state=True)

    def rename_memory(self, index: int, name: str) -> dict[str, Any]:
        try:
            if self.memory_tabs and name.strip():
                self.memory_tabs[int(index)].name = name.strip()
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Rename failed: {exc}", state=True)

    def refresh_memory(self, index: int | None = None) -> dict[str, Any]:
        try:
            tab = self._get_memory_tab(index)
            self._memory_service.refresh_tab(tab)
            self._log(f"Memory refreshed {tab.name}")
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Memory refresh failed: {exc}", state=True)

    def shift_memory(self, index: int, direction: int) -> dict[str, Any]:
        try:
            tab = self._get_memory_tab(index)
            byte_delta = (tab.tail_address - tab.head_address) * int(direction)
            self._memory_service.shift_tab(tab, byte_delta)
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Memory block move failed: {exc}", state=True)

    def write_memory_word(self, index: int, value_index: int, value: str) -> dict[str, Any]:
        try:
            tab = self._get_memory_tab(index)
            address = tab.head_address + int(value_index) * 4
            self._memory_service.write_word(address, value)
            self._memory_service.refresh_tab(tab)
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Memory write failed: {exc}", state=True)

    def import_memory(self, index: int, address: str | None = None) -> dict[str, Any]:
        try:
            tab = self._get_memory_tab(index)
            path = self._pick_open_file(("Memory files (*.raw;*.bin)", "All files (*.*)"))
            if not path:
                return self._ok(self._state())
            target = parse_number(address) if address else tab.head_address
            self._memory_service.import_raw_or_bin(target, path)
            self._memory_service.refresh_tab(tab)
            self._log(f"Imported {path}")
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Import failed: {exc}", state=True)

    def export_memory(self, index: int, start: str, length: str) -> dict[str, Any]:
        try:
            tab = self._get_memory_tab(index)
            path = self._pick_save_file(f"{tab.name.replace('0x', '')}.raw", ("Raw memory (*.raw)",))
            if not path:
                return self._ok(self._state())
            self._memory_service.export_raw(parse_number(start), parse_number(length), path)
            self._log(f"Exported {path}")
            return self._ok(self._state())
        except Exception as exc:
            return self._fail(f"Export failed: {exc}", state=True)

    def commander(self, command: str) -> dict[str, Any]:
        text = command.strip()
        if text:
            self._log(f"JGKit: {text}")
        return self._ok(self._state())

    def _state(self) -> dict[str, Any]:
        config = self.current_config
        return {
            "launched": self.launched,
            "connected": self.connected,
            "debugMode": self.debug_mode,
            "configs": [self._config_to_dict(item) for item in self.configs],
            "currentConfig": self._config_to_dict(config) if config else None,
            "coreOptions": config.core_options if config else [],
            "coreValue": self.core_value,
            "deviceNodes": [self._device_to_dict(item) for item in self.device_nodes],
            "modifyItems": [self._register_to_dict(item) for item in self.modify_items],
            "memoryTabs": [self._memory_to_dict(item) for item in self.memory_tabs],
            "memoryIndex": self.memory_index,
            "logs": self.logs[-120:],
        }

    def _find_config(self, chip_name: str) -> AppConfig:
        config = next((item for item in self.configs if item.name == chip_name), None)
        if config is None:
            raise ValueError(f"Unknown chip: {chip_name}")
        return config

    def _get_source_item(self, path: list[int]) -> RegisterItem:
        if not path:
            raise ValueError("Empty source path")
        device = self.device_nodes[int(path[0])]
        if len(path) == 1:
            return device.as_register_item()
        register = device.children[int(path[1])]
        if len(path) == 2:
            return register
        return register.children[int(path[2])]

    def _get_modify_item(self, path: list[int]) -> RegisterItem:
        parent, index = self._get_modify_parent(path)
        return parent[index]

    def _get_modify_parent(self, path: list[int]) -> tuple[list[RegisterItem], int]:
        if not path:
            raise ValueError("Empty modify path")
        parent = self.modify_items
        for index in path[:-1]:
            parent = parent[int(index)].children
        return parent, int(path[-1])

    def _get_memory_tab(self, index: int | None = None) -> MemoryTabState:
        if not self.memory_tabs:
            raise ValueError("No memory views")
        if index is None:
            index = self.memory_index
        return self.memory_tabs[int(index)]

    def _refresh_item_tree(self, item: RegisterItem) -> None:
        if item.level != 0:
            item.read_value = format_hex(self._register_service.read32_plus(item.address_expr))
        for child in item.children:
            self._refresh_item_tree(child)

    def _write_item(self, item: RegisterItem) -> None:
        if item.write_value in {"", "NA"}:
            self._log(f"Skip {item.name}: write value is empty")
            return
        self._register_service.write32_plus(item.address_expr, item.write_value)
        item.read_value = format_hex(self._register_service.read32_plus(item.address_expr))
        self._log(f"Wrote {item.name} = {item.write_value}")

    def _iter_modify_items(self) -> list[RegisterItem]:
        items: list[RegisterItem] = []

        def walk(nodes: list[RegisterItem]) -> None:
            for node in nodes:
                items.append(node)
                walk(node.children)

        walk(self.modify_items)
        return items

    def _pick_open_file(self, file_types: tuple[str, ...]) -> str | None:
        if self.window is None:
            return None
        paths = self.window.create_file_dialog(webview.FileDialog.OPEN, directory=".", file_types=file_types)
        return self._first_path(paths)

    def _pick_save_file(self, filename: str, file_types: tuple[str, ...]) -> str | None:
        if self.window is None:
            return None
        paths = self.window.create_file_dialog(
            webview.FileDialog.SAVE,
            directory=".",
            save_filename=filename,
            file_types=file_types,
        )
        return self._first_path(paths)

    @staticmethod
    def _first_path(paths: Any) -> str | None:
        if paths is None:
            return None
        if isinstance(paths, str):
            return paths
        return str(paths[0]) if paths else None

    @staticmethod
    def _config_to_dict(config: AppConfig) -> dict[str, Any]:
        return {
            "name": config.name,
            "core": config.core,
            "tifOptions": config.tif_options,
            "selectedTif": config.selected_tif,
            "excel": config.excel,
            "sheets": config.sheets,
        }

    def _device_to_dict(self, device: DeviceNode) -> dict[str, Any]:
        return {
            "name": device.name,
            "address": device.address,
            "description": device.description,
            "children": [self._register_to_dict(item) for item in device.children],
        }

    def _register_to_dict(self, item: RegisterItem) -> dict[str, Any]:
        return {
            "name": item.name,
            "addressExpr": item.address_expr,
            "property": item.property,
            "description": item.description,
            "level": item.level,
            "writeValue": item.write_value,
            "readValue": item.read_value,
            "children": [self._register_to_dict(child) for child in item.children],
        }

    @staticmethod
    def _memory_to_dict(tab: MemoryTabState) -> dict[str, Any]:
        return {
            "name": tab.name,
            "headAddress": tab.head_address,
            "tailAddress": tab.tail_address,
            "values": tab.values,
        }

    def _log(self, message: str) -> None:
        logging.info(message)
        self.logs.append(message)
        self.logs = self.logs[-160:]

    @staticmethod
    def _ok(data: Any) -> dict[str, Any]:
        return {"ok": True, "data": data}

    def _fail(self, message: str, state: bool = False) -> dict[str, Any]:
        self._log(message)
        payload: dict[str, Any] = {"ok": False, "error": message}
        if state:
            payload["data"] = self._state()
        return payload
