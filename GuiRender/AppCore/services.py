from __future__ import annotations

import json
import logging
import os
import re
import warnings
from pathlib import Path
from typing import Any

from GuiRender.Model import Excel2Dict
from GuiRender.Model import StartUp_Verify
import global_var

from .models import AppConfig, DeviceNode, MemoryTabState, RegisterItem, clone_register_item


warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def parse_number(value: str | int) -> int:
    if isinstance(value, int):
        return value
    text = str(value).strip()
    try:
        return int(text)
    except ValueError:
        return int(text, base=16)


def format_hex(value: int | bool | None) -> str:
    if value is False or value is None:
        return "?"
    return hex(int(value))


class StartupService:
    def __init__(self, config_root: str = ".data/config"):
        self.config_root = config_root

    def load_configs(self) -> list[AppConfig]:
        verifier = StartUp_Verify.StartUpVerify(self.config_root)
        configs: list[AppConfig] = []
        for name in verifier.get_core_list():
            raw = verifier[name]
            if raw:
                configs.append(AppConfig.from_raw(raw))
        return configs

    def activate_config(self, config: AppConfig) -> None:
        global_var.init()
        for key, value in config.raw.items():
            if key == "tif":
                global_var.set_value("tif", config.selected_tif)
            else:
                global_var.set_value(str(key), value)


class DeviceTreeService:
    _find_indexes_pattern = re.compile(r"\[(?P<Number>[0-9]+)\]")
    _locate_indexes_pattern = re.compile(r"<ARRAY_INDEX>")

    def __init__(self, xls_root: str = ".data/xls"):
        self.xls_root = xls_root

    def load_device_tree(self, config: AppConfig) -> list[DeviceNode]:
        excel_path = self._resolve_excel_path(config.excel)
        memory_header = [
            {"Key": "Address Start", "Level": (1,), "Priority": ("M",)},
            {"Key": "Module", "Level": (1,), "Priority": ("L",)},
            {"Key": "Class", "Level": (1,), "Priority": ("L",)},
        ]
        memory_reheader = ("Address", "Name", "Class")
        memory_e2j = Excel2Dict.E2D(
            excel=excel_path,
            header=memory_header,
            sheets=config.sheets,
            reheader=memory_reheader,
        )
        memory_e2j.convert()

        memory_list = [item for sheet in memory_e2j for item in sheet["Level"] if item["Class"]]
        for item in memory_list:
            item["Address"] = str(item["Address"]).replace("_", "")

        register_header = [
            {"Key": "Sub-Addr\n(Hex)", "Level": (1,), "Priority": ("H",)},
            {"Key": "Start\nBit", "Level": (2,), "Priority": ("M",)},
            {"Key": "End\nBit", "Level": (2,), "Priority": ("M",)},
            {"Key": "R/W\nProperty", "Level": (2,), "Priority": ("M",)},
            {"Key": "Register\nName", "Level": (1, 2), "Priority": ("M", "M")},
            {"Key": "Register Description", "Level": (1, 2), "Priority": ("L", "L")},
        ]
        register_reheader = ("Address", "Start", "End", "Property", "Name", "Description")
        register_e2j = Excel2Dict.E2D(excel=excel_path, header=register_header, reheader=register_reheader)
        register_e2j.convert()

        devices: list[DeviceNode] = []
        for memory_item in memory_list:
            for register_sheet in register_e2j:
                if memory_item["Class"] == register_sheet["Sheet_Name"]:
                    base_address = parse_number(memory_item["Address"])
                    devices.append(
                        DeviceNode(
                            name=str(memory_item["Name"]),
                            address=hex(base_address),
                            children=self._build_registers(base_address, register_sheet["Level"]),
                        )
                    )
                    break

        devices.sort(key=lambda item: parse_number(item.address))
        return devices

    def _resolve_excel_path(self, excel_name: str) -> str:
        configured = Path(self.xls_root) / excel_name
        if configured.exists():
            return str(configured)
        for suffix in (".xlsx", ".xls"):
            candidate = configured.with_suffix(suffix)
            if candidate.exists():
                logging.warning("Excel file %s not found; using %s", configured, candidate)
                return str(candidate)
        return str(configured)

    def _build_registers(self, base_address: int, registers: list[dict[str, Any]]) -> list[RegisterItem]:
        rendered: list[RegisterItem] = []
        for register in registers:
            try:
                current_address = base_address + parse_number(register["Address"])
            except TypeError:
                current_address = base_address + int(register["Address"])

            expanded = self._expand_register(register, current_address)
            if expanded:
                rendered.extend(expanded)
                continue

            rendered.append(
                RegisterItem(
                    name=str(register["Name"]),
                    address_expr=hex(current_address),
                    description=str(register.get("Description", "")),
                    level=1,
                    children=self._build_fields(register.get("Level", []), current_address),
                )
            )
        return rendered

    def _expand_register(self, register: dict[str, Any], address: int) -> list[RegisterItem]:
        match = self._find_indexes_pattern.search(str(register["Name"]))
        if not match:
            return []

        expanded: list[RegisterItem] = []
        count = int(match.group("Number"))
        stem = str(register["Name"])[0 : match.span()[0]]
        for index in range(count):
            current_address = address + index * 4
            expanded.append(
                RegisterItem(
                    name=f"{stem}{index}",
                    address_expr=hex(current_address),
                    description=str(register.get("Description", "")),
                    level=1,
                    children=self._build_fields(register.get("Level", []), current_address, index),
                )
            )
        return expanded

    def _build_fields(
        self,
        fields: list[dict[str, Any]],
        current_address: int,
        array_index: int | None = None,
    ) -> list[RegisterItem]:
        rendered: list[RegisterItem] = []
        for field in fields:
            name = str(field["Name"])
            if array_index is not None:
                name = self._locate_indexes_pattern.sub(str(array_index), name)
            start = int(field["Start"])
            end = int(field["End"])
            rendered.append(
                RegisterItem(
                    name=name,
                    address_expr=f"{hex(current_address)} | {start}:{end}",
                    property=str(field.get("Property", "NA")),
                    description=str(field.get("Description", "")),
                    level=2,
                )
            )
        return rendered


class FakeLink:
    def __init__(self):
        self.memory: dict[int, int] = {}
        self.connected_flag = True

    def read32(self, addr: int) -> int:
        return self.memory.get(addr, 0)

    def write32(self, addr: int, data: int) -> bool:
        self.memory[addr] = int(data) & 0xFFFFFFFF
        return True

    def read_mem(self, addr: int, rlen: int, nbits: int = 32) -> list[int]:
        step = max(nbits // 8, 1)
        mask = (1 << nbits) - 1
        return [self.memory.get(addr + index * step, 0) & mask for index in range(int(rlen))]

    def write_mem(self, addr: int, wdata: bytes | list[int], nbits: int = 32) -> bool:
        step = max(nbits // 8, 1)
        for index, value in enumerate(wdata):
            self.memory[addr + index * step] = int(value) & ((1 << nbits) - 1)
        return True

    def is_connected(self) -> bool:
        return self.connected_flag

    def close(self) -> None:
        self.connected_flag = False


class LinkService:
    def __init__(self):
        self.handler: Any | None = None

    @property
    def is_debug(self) -> bool:
        return os.environ.get("JGKIT_LINK_DEBUG", "").lower() in {"1", "true", "yes", "on"}

    def connect(self, core: str | None = None) -> bool:
        if self.is_debug:
            self.handler = FakeLink()
            return True
        from GuiRender.Model import SWDJlink

        self.handler = SWDJlink.Link(core)
        connected = self.handler is not None and self.handler.is_connected()
        if not connected:
            self.disconnect()
        return connected

    def disconnect(self) -> None:
        if self.handler is None:
            return
        handler = self.handler
        self.handler = None
        self._close_handler(handler)

    @staticmethod
    def _close_handler(handler: Any) -> None:
        targets = [handler]
        inner_handler = getattr(handler, "link_handler", None)
        if inner_handler is not None:
            targets.append(inner_handler)

        for target in targets:
            close = getattr(target, "close", None)
            if callable(close):
                try:
                    close()
                except Exception:
                    logging.exception("Link close failed")
                return

        for target in targets:
            destructor = getattr(target, "__del__", None)
            if callable(destructor):
                try:
                    destructor()
                except Exception:
                    logging.exception("Link destructor failed")
                return

    def is_connected(self) -> bool:
        return self.handler is not None and bool(self.handler.is_connected())


class RegisterService:
    _address_field_pattern = re.compile(
        r"(?P<Address>0x[0-9a-fA-F]+)[\s\|]*(?P<Field0>[0-9]*):*(?P<Field1>[0-9]*)"
    )

    def __init__(self, link_service: LinkService):
        self.link_service = link_service

    @property
    def link(self) -> Any:
        if self.link_service.handler is None:
            raise RuntimeError("Target is not connected")
        return self.link_service.handler

    def parse_address(self, address_expr: str) -> tuple[str, str, str]:
        result = self._address_field_pattern.match(str(address_expr).strip())
        if not result:
            raise ValueError(f"Invalid address expression: {address_expr}")
        return result.group("Address"), result.group("Field0"), result.group("Field1")

    def read32_plus(self, address_expr: str) -> int | bool:
        address, field0, field1 = self.parse_address(address_expr)
        mem32 = self.link.read32(int(address, base=16))
        if mem32 == -1:
            return False
        if field0 or field1:
            return (mem32 >> int(field0)) & self._get_mask(int(field1) - int(field0) + 1)
        return mem32

    def write32_plus(self, address_expr: str, data: str | int) -> bool:
        address, field0, field1 = self.parse_address(address_expr)
        addr = int(address, base=16)
        if field0 or field1:
            mem32 = self.link.read32(addr)
            if mem32 == -1:
                return False
            mask = self._get_mask(int(field1) - int(field0) + 1)
            value = parse_number(data) & mask
            mem32 &= ~(mask << int(field0))
            mem32 |= value << int(field0)
            self.link.write32(addr, mem32)
            return True
        self.link.write32(addr, parse_number(data))
        return True

    @staticmethod
    def _get_mask(length: int) -> int:
        return (1 << int(length)) - 1


class ConfigFileService:
    def register_items_to_regcfg(self, items: list[RegisterItem]) -> list[dict[str, Any]]:
        return [self._item_to_legacy(item) for item in items]

    def regcfg_to_register_items(self, data: list[dict[str, Any]]) -> list[RegisterItem]:
        return [self._legacy_to_item(item) for item in data]

    def write_regcfg(self, path: str, items: list[RegisterItem]) -> None:
        with open(path, mode="w", encoding="utf8") as handler:
            json.dump(self.register_items_to_regcfg(items), handler, indent=2)

    def read_regcfg(self, path: str) -> list[RegisterItem]:
        with open(path, mode="r", encoding="utf8") as handler:
            data = json.load(handler)
        return self.regcfg_to_register_items(data)

    def write_glicfg(self, path: str, items: list[RegisterItem], register_service: RegisterService) -> None:
        with open(path, mode="w", encoding="utf8") as handler:
            json.dump(self._items_to_glimpse(items, register_service), handler, indent=2)

    def _item_to_legacy(self, item: RegisterItem) -> dict[str, Any]:
        return {
            "text": item.name,
            "values": [item.address_expr, item.property, item.write_value, item.read_value],
            "tags": [item.level, item.description],
            "open": True,
            "image": "",
            "next": [self._item_to_legacy(child) for child in item.children],
        }

    def _legacy_to_item(self, data: dict[str, Any]) -> RegisterItem:
        values = list(data.get("values", []))
        tags = list(data.get("tags", []))
        return RegisterItem(
            name=str(data.get("text", data.get("Name", ""))),
            address_expr=str(values[0] if len(values) > 0 else data.get("Address", "")),
            property=str(values[1] if len(values) > 1 else data.get("Property", "NA")),
            write_value=str(values[2] if len(values) > 2 else "NA"),
            read_value=str(values[3] if len(values) > 3 else "NA"),
            level=int(tags[0] if tags else data.get("Level", 0)),
            description=str(tags[1] if len(tags) > 1 else data.get("Description", "")),
            children=[self._legacy_to_item(child) for child in data.get("next", [])],
        )

    def _items_to_glimpse(
        self,
        items: list[RegisterItem],
        register_service: RegisterService,
    ) -> list[dict[str, Any]]:
        glimpse: list[dict[str, Any]] = []
        for item in items:
            record = {"Name": item.name, "Address": item.address_expr, "Values": "NA"}
            if item.level == 0:
                record["next"] = self._items_to_glimpse(item.children, register_service)
            else:
                try:
                    record["Values"] = format_hex(register_service.read32_plus(item.address_expr))
                except Exception:
                    record["Values"] = "?"
            glimpse.append(record)
        return glimpse


class MemoryService:
    def __init__(self, link_service: LinkService):
        self.link_service = link_service

    @property
    def link(self) -> Any:
        if self.link_service.handler is None:
            raise RuntimeError("Target is not connected")
        return self.link_service.handler

    def create_tab(self, address: int, rows: int = 40, columns: int = 4) -> MemoryTabState:
        tab = MemoryTabState(
            name=hex(address),
            head_address=address,
            tail_address=address + rows * columns * 4,
        )
        self.refresh_tab(tab, columns=columns)
        return tab

    def refresh_tab(self, tab: MemoryTabState, columns: int = 4) -> MemoryTabState:
        length = int((tab.tail_address - tab.head_address) / 4)
        tab.values = list(self.link.read_mem(tab.head_address, length))
        return tab

    def shift_tab(self, tab: MemoryTabState, byte_delta: int, columns: int = 4) -> MemoryTabState:
        block_size = tab.tail_address - tab.head_address
        next_head = tab.head_address + byte_delta
        next_tail = tab.tail_address + byte_delta
        if next_head < 0:
            next_head = 0
            next_tail = block_size
        if next_tail > 0x100000000:
            next_tail = 0x100000000
            next_head = next_tail - block_size
        tab.head_address = next_head
        tab.tail_address = next_tail
        return self.refresh_tab(tab, columns=columns)

    def write_word(self, address: int, value: str | int) -> int:
        parsed = parse_number(value)
        self.link.write32(address, parsed)
        return int(self.link.read32(address))

    def import_raw_or_bin(self, address: int, path: str) -> None:
        source = Path(path)
        if source.suffix.lower() == ".bin":
            self.link.write_mem(address, source.read_bytes(), nbits=8)
            return

        content = source.read_text(encoding="utf8")
        values: list[int] = []
        for token in content.replace("\n", " ").split():
            cleaned = token.strip().replace("0x", "")
            if len(cleaned) == 4:
                values.append(int(cleaned[0:2], 16))
                values.append(int(cleaned[2:4], 16))
            elif len(cleaned) == 2:
                values.append(int(cleaned, 16))
        self.link.write_mem(address, values, nbits=8)

    def export_raw(self, start_address: int, length: int, path: str) -> None:
        out_list = self.link.read_mem(start_address, length, nbits=8)
        with open(path, mode="w", encoding="utf8") as handler:
            chunk = ""
            for index, item in enumerate(out_list, start=1):
                chunk += hex(item).replace("0x", "").rjust(2, "0")
                if index % 16 == 0:
                    handler.write(chunk + " \r")
                    chunk = ""
                elif index % 2 == 0:
                    handler.write(chunk + " ")
                    chunk = ""
            if chunk:
                handler.write(chunk)


def flatten_items(items: list[RegisterItem]) -> list[RegisterItem]:
    flat: list[RegisterItem] = []
    for item in items:
        flat.append(item)
        flat.extend(flatten_items(item.children))
    return flat


def clone_items(items: list[RegisterItem]) -> list[RegisterItem]:
    return [clone_register_item(item) for item in items]
