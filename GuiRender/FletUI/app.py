from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Callable

import flet as ft

from .models import AppConfig, DeviceNode, MemoryTabState, RegisterItem
from .services import (
    ConfigFileService,
    DeviceTreeService,
    LinkService,
    MemoryService,
    RegisterService,
    StartupService,
    clone_items,
    format_hex,
    parse_number,
)


APP_TITLE = "JGKit"
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 720


class JGKitFletApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.startup_service = StartupService()
        self.device_tree_service = DeviceTreeService()
        self.link_service = LinkService()
        self.register_service = RegisterService(self.link_service)
        self.config_file_service = ConfigFileService()
        self.memory_service = MemoryService(self.link_service)

        self.file_picker = ft.FilePicker()
        self.page.services.append(self.file_picker)

        self.configs: list[AppConfig] = []
        self.current_config: AppConfig | None = None
        self.device_nodes: list[DeviceNode] = []
        self.modify_items: list[RegisterItem] = []
        self.memory_tabs: list[MemoryTabState] = []
        self.memory_index = 0
        self.core_value: str | None = None
        self.connected = False
        self.connection_watch = False
        self.auto_refresh = False
        self.description_text = ft.Text("", selectable=True, size=12)
        self.status_text = ft.Text("Disconnected", size=12)
        self.log_lines: list[str] = []

    def start(self) -> None:
        self._setup_page()
        try:
            self.configs = self.startup_service.load_configs()
        except Exception as exc:
            self._show_error(f"Failed to load startup config: {exc}")
            self.configs = []
        self.current_config = self.configs[0] if self.configs else None
        self.render_selection()

    def _setup_page(self) -> None:
        self.page.title = APP_TITLE
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window.width = WINDOW_WIDTH
        self.page.window.height = WINDOW_HEIGHT
        self.page.window.min_width = 900
        self.page.window.min_height = 600
        self.page.padding = 0
        self.page.spacing = 0

    def render_selection(self) -> None:
        self.page.clean()
        if not self.configs:
            self.page.add(
                self._screen_shell(
                    ft.Column(
                        [
                            ft.Text("JGKit", size=30, weight=ft.FontWeight.BOLD),
                            ft.Text("No chip configuration found in .data/config."),
                        ],
                        spacing=16,
                    )
                )
            )
            self.page.update()
            return

        config = self.current_config or self.configs[0]
        chip_dropdown = ft.Dropdown(
            label="Chip",
            value=config.name,
            options=[ft.DropdownOption(key=item.name, text=item.name) for item in self.configs],
            width=320,
            on_select=self._on_select_chip,
        )
        tif_dropdown = ft.Dropdown(
            label="TIF",
            value=config.selected_tif,
            options=[ft.DropdownOption(key=item, text=item) for item in config.tif_options],
            width=220,
            on_select=self._on_select_tif,
        )

        self.page.add(
            self._screen_shell(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Image(src="icon/exchange.png", width=48, height=48),
                                ft.Column(
                                    [
                                        ft.Text("JGKit", size=30, weight=ft.FontWeight.BOLD),
                                        ft.Text("Chip register and memory toolkit", size=13),
                                    ],
                                    spacing=2,
                                ),
                            ],
                            spacing=14,
                        ),
                        ft.Divider(),
                        ft.Row([chip_dropdown, tif_dropdown], spacing=16),
                        ft.Row(
                            [
                                ft.FilledButton("Launch", icon=ft.Icons.PLAY_ARROW, on_click=self._launch_workspace),
                                ft.OutlinedButton("Quit", icon=ft.Icons.CLOSE, on_click=self._quit_app),
                            ],
                            spacing=12,
                        ),
                    ],
                    spacing=18,
                    width=600,
                )
            )
        )
        self.page.update()

    def _screen_shell(self, content: ft.Control) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                [content],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            expand=True,
            padding=40,
        )

    def _on_select_chip(self, event: ft.Event) -> None:
        selected = str(event.control.value)
        self.current_config = next((item for item in self.configs if item.name == selected), self.current_config)
        self.render_selection()

    def _on_select_tif(self, event: ft.Event) -> None:
        if self.current_config is None:
            return
        self.current_config = self.current_config.with_tif(str(event.control.value))
        self.render_selection()

    def _launch_workspace(self, _event: ft.Event) -> None:
        if self.current_config is None:
            self._show_error("Select a chip first.")
            return
        self.startup_service.activate_config(self.current_config)
        self.core_value = self.current_config.core_options[0] if self.current_config.core_options else None
        self._set_busy("Loading Excel mapping...")
        try:
            self.device_nodes = self.device_tree_service.load_device_tree(self.current_config)
        except Exception as exc:
            self._show_error(f"Failed to load device tree: {exc}")
            self.render_selection()
            return
        self.connected = False
        self.modify_items = []
        self.memory_tabs = []
        self.memory_index = 0
        self._log(f"Loaded {self.current_config.name} / {self.current_config.selected_tif}")
        self.render_workspace()

    def _quit_app(self, _event: ft.Event) -> None:
        self.page.window.close()

    def _set_busy(self, message: str) -> None:
        self.page.clean()
        self.page.add(
            self._screen_shell(
                ft.Row([ft.ProgressRing(width=22, height=22), ft.Text(message)], spacing=14)
            )
        )
        self.page.update()

    def render_workspace(self) -> None:
        self.page.clean()
        self.status_text = ft.Text(
            "Connected" if self.connected else "Disconnected",
            size=12,
            color=ft.Colors.GREEN_300 if self.connected else ft.Colors.RED_300,
        )
        self.page.add(
            ft.Column(
                [
                    self._toolbar(),
                    ft.Divider(height=1),
                    ft.Row(
                        [
                            self._device_panel(),
                            ft.VerticalDivider(width=1),
                            self._modify_panel(),
                        ],
                        expand=6,
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.Divider(height=1),
                    self._bottom_panel(),
                ],
                expand=True,
                spacing=0,
            )
        )
        self.page.update()

    def _toolbar(self) -> ft.Control:
        core_controls: list[ft.Control] = []
        if self.current_config and self.current_config.core_options:
            core_controls = [
                ft.Text("Core", size=12),
                ft.SegmentedButton(
                    segments=[
                        ft.Segment(value=core, label=ft.Text(core))
                        for core in self.current_config.core_options
                    ],
                    selected=[self.core_value or self.current_config.core_options[0]],
                    disabled=self.connected,
                    on_change=self._on_core_change,
                ),
            ]

        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.INFO,
                                color=ft.Colors.GREEN_300 if self.connected else ft.Colors.RED_300,
                                size=18,
                            ),
                            self.status_text,
                            ft.Text(self._title_suffix(), size=12),
                        ],
                        spacing=8,
                    ),
                    ft.Row(core_controls, spacing=8),
                    ft.Row(
                        [
                            self._icon_button(ft.Icons.PLAY_ARROW, "Connect", self._connect, disabled=self.connected),
                            self._icon_button(ft.Icons.STOP, "Disconnect", self._disconnect, disabled=not self.connected),
                            self._icon_button(ft.Icons.REFRESH, "Refresh", self._refresh_modify, disabled=not self.connected),
                            self._icon_button(ft.Icons.UPLOAD_FILE, "Upload", self._upload_modify, disabled=not self.connected),
                            self._icon_button(ft.Icons.FOLDER_OPEN, "Open regcfg", self._open_regcfg, disabled=not self.connected),
                            self._icon_button(ft.Icons.SAVE, "Save regcfg", self._save_regcfg, disabled=not self.connected),
                            self._icon_button(ft.Icons.DOWNLOAD, "Glimpse", self._save_glicfg, disabled=not self.connected),
                            ft.Checkbox(
                                label="Auto",
                                value=self.auto_refresh,
                                disabled=not self.connected,
                                on_change=self._toggle_auto_refresh,
                            ),
                        ],
                        spacing=2,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    def _title_suffix(self) -> str:
        if self.current_config is None:
            return ""
        return f"{self.current_config.name} / {self.current_config.selected_tif}"

    def _icon_button(
        self,
        icon: ft.IconData,
        tooltip: str,
        handler: Callable[[ft.Event], None],
        disabled: bool = False,
    ) -> ft.IconButton:
        return ft.IconButton(icon=icon, tooltip=tooltip, on_click=handler, disabled=disabled)

    def _on_core_change(self, event: ft.Event) -> None:
        selected = list(event.control.selected)
        if selected:
            self.core_value = selected[0]
            self._log(f"Core switched to {self.core_value}")

    def _device_panel(self) -> ft.Control:
        controls: list[ft.Control] = [
            self._panel_header("Device Tree", f"{len(self.device_nodes)} devices"),
        ]
        for device in self.device_nodes:
            controls.append(self._device_tile(device))
        return ft.Container(
            width=460,
            padding=8,
            content=ft.ListView(controls=controls, expand=True, spacing=2, auto_scroll=False),
            expand=True,
        )

    def _device_tile(self, device: DeviceNode) -> ft.Control:
        return ft.ExpansionTile(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.MEMORY, size=16),
                    ft.Text(device.name, expand=True, size=13),
                    ft.Text(device.address, size=12, color=ft.Colors.BLUE_200),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip="Add device",
                        on_click=lambda event, item=device.as_register_item(): self._add_modify_item(item),
                    ),
                ],
                spacing=6,
            ),
            controls=[self._register_tile(register) for register in device.children],
            dense=True,
        )

    def _register_tile(self, register: RegisterItem) -> ft.Control:
        if not register.children:
            return self._field_list_tile(register)
        return ft.ExpansionTile(
            title=ft.Row(
                [
                    ft.Text(register.name, expand=True, size=12),
                    ft.Text(register.address_expr, size=11, color=ft.Colors.BLUE_200),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip="Add register",
                        on_click=lambda event, item=register: self._add_modify_item(item),
                    ),
                ],
                spacing=6,
            ),
            controls=[self._field_list_tile(field) for field in register.children],
            dense=True,
        )

    def _field_list_tile(self, field: RegisterItem) -> ft.Control:
        return ft.ListTile(
            dense=True,
            title=ft.Row(
                [
                    ft.Text(field.name, expand=True, size=12),
                    ft.Text(field.address_expr, size=11, color=ft.Colors.BLUE_200),
                    ft.Text(field.property, size=11),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip="Add field",
                        on_click=lambda event, item=field: self._add_modify_item(item),
                    ),
                ],
                spacing=6,
            ),
            on_click=lambda event, item=field: self._show_description(item.description),
        )

    def _modify_panel(self) -> ft.Control:
        controls = [
            self._panel_header("Modify Tree", f"{len(self.modify_items)} tracked"),
            self._modify_header_row(),
        ]
        for item in self.modify_items:
            controls.extend(self._modify_rows(item, 0, self.modify_items))
        return ft.Container(
            padding=8,
            expand=True,
            content=ft.ListView(controls=controls, expand=True, spacing=2),
        )

    def _modify_header_row(self) -> ft.Control:
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=4, horizontal=8),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            content=ft.Row(
                [
                    ft.Text("Name", width=210, size=12, weight=ft.FontWeight.BOLD),
                    ft.Text("Address | Field", width=150, size=12, weight=ft.FontWeight.BOLD),
                    ft.Text("Property", width=70, size=12, weight=ft.FontWeight.BOLD),
                    ft.Text("Write", width=110, size=12, weight=ft.FontWeight.BOLD),
                    ft.Text("Read", width=110, size=12, weight=ft.FontWeight.BOLD),
                    ft.Text("Actions", width=120, size=12, weight=ft.FontWeight.BOLD),
                ],
                spacing=8,
            ),
        )

    def _modify_rows(
        self,
        item: RegisterItem,
        depth: int,
        siblings: list[RegisterItem],
    ) -> list[ft.Control]:
        rows = [self._modify_row(item, depth, siblings)]
        for child in item.children:
            rows.extend(self._modify_rows(child, depth + 1, item.children))
        return rows

    def _modify_row(self, item: RegisterItem, depth: int, siblings: list[RegisterItem]) -> ft.Control:
        writable = item.level != 0 and self.connected
        write_field = ft.TextField(
            value="" if item.write_value == "NA" else item.write_value,
            dense=True,
            width=110,
            height=36,
            disabled=not writable,
            on_change=lambda event, target=item: self._set_write_value(target, event.control.value),
            on_submit=lambda event, target=item: self._write_item(target),
        )
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=2, horizontal=8),
            on_click=lambda event, target=item: self._show_description(target.description),
            content=ft.Row(
                [
                    ft.Text(("  " * depth) + item.name, width=210, size=12, no_wrap=True),
                    ft.Text(item.address_expr, width=150, size=11, color=ft.Colors.BLUE_200),
                    ft.Text(item.property, width=70, size=11),
                    write_field,
                    ft.Text(item.read_value, width=110, size=11),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.REFRESH,
                                tooltip="Read",
                                disabled=not writable,
                                on_click=lambda event, target=item: self._read_item(target),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.UPLOAD_FILE,
                                tooltip="Write",
                                disabled=not writable,
                                on_click=lambda event, target=item: self._write_item(target),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.REMOVE,
                                tooltip="Remove",
                                on_click=lambda event, target=item, parent=siblings: self._remove_modify_item(target, parent),
                            ),
                        ],
                        width=120,
                        spacing=0,
                    ),
                ],
                spacing=8,
            ),
        )

    def _bottom_panel(self) -> ft.Control:
        return ft.Container(
            height=230,
            padding=8,
            content=ft.Row(
                [
                    self._commander_panel(),
                    ft.VerticalDivider(width=1),
                    self._description_panel(),
                    ft.VerticalDivider(width=1),
                    self._memory_panel(),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )

    def _commander_panel(self) -> ft.Control:
        log_controls = [ft.Text(line, size=11, selectable=True) for line in self.log_lines[-80:]]
        command = ft.TextField(
            prefix="JGKit: ",
            dense=True,
            height=38,
            on_submit=self._commander_submit,
        )
        return ft.Container(
            width=330,
            padding=6,
            content=ft.Column(
                [
                    self._panel_header("Commander", ""),
                    ft.ListView(log_controls, expand=True, auto_scroll=True),
                    command,
                ],
                expand=True,
                spacing=4,
            ),
        )

    def _description_panel(self) -> ft.Control:
        return ft.Container(
            width=260,
            padding=6,
            content=ft.Column(
                [
                    self._panel_header("Description", ""),
                    ft.Container(content=self.description_text, expand=True, padding=6),
                ],
                expand=True,
            ),
        )

    def _memory_panel(self) -> ft.Control:
        selected_tab = self.memory_tabs[self.memory_index] if self.memory_tabs else None
        controls: list[ft.Control] = [
            ft.Row(
                [
                    self._panel_header("Memory", ""),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip="Add memory view",
                        disabled=not self.connected,
                        on_click=self._show_add_memory_dialog,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.REMOVE,
                        tooltip="Remove memory view",
                        disabled=not self.memory_tabs,
                        on_click=self._remove_memory_tab,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        tooltip="Rename memory view",
                        disabled=not self.memory_tabs,
                        on_click=self._show_rename_memory_dialog,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.FOLDER_OPEN,
                        tooltip="Import raw/bin",
                        disabled=not self.connected,
                        on_click=self._import_memory,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SAVE,
                        tooltip="Export raw",
                        disabled=not self.connected,
                        on_click=self._show_export_memory_dialog,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_UPWARD,
                        tooltip="Previous memory block",
                        disabled=not (self.connected and selected_tab),
                        on_click=lambda event: self._shift_memory_tab(-1),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_DOWNWARD,
                        tooltip="Next memory block",
                        disabled=not (self.connected and selected_tab),
                        on_click=lambda event: self._shift_memory_tab(1),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Refresh memory",
                        disabled=not (self.connected and selected_tab),
                        on_click=self._refresh_memory_tab,
                    ),
                ],
                spacing=0,
            )
        ]
        if self.memory_tabs:
            controls.append(
                ft.SegmentedButton(
                    segments=[
                        ft.Segment(value=str(index), label=ft.Text(tab.name))
                        for index, tab in enumerate(self.memory_tabs)
                    ],
                    selected=[str(self.memory_index)],
                    on_change=self._on_memory_tab_change,
                )
            )
        controls.append(self._memory_grid(selected_tab))
        return ft.Container(
            expand=True,
            padding=6,
            content=ft.Column(controls, expand=True, spacing=6),
        )

    def _memory_grid(self, tab: MemoryTabState | None) -> ft.Control:
        if tab is None:
            return ft.Container(
                content=ft.Text("No memory views", size=12),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )
        rows: list[ft.Control] = []
        columns = 4
        for row_index in range(0, len(tab.values), columns):
            address = tab.head_address + row_index * 4
            row_controls: list[ft.Control] = [ft.Text(hex(address), width=90, size=11)]
            for column_index in range(columns):
                value_index = row_index + column_index
                if value_index >= len(tab.values):
                    break
                word_address = tab.head_address + value_index * 4
                row_controls.append(
                    ft.TextField(
                        value=hex(tab.values[value_index]),
                        dense=True,
                        width=92,
                        height=34,
                        disabled=not self.connected,
                        on_submit=lambda event, addr=word_address: self._write_memory_word(addr, event.control.value),
                    )
                )
            rows.append(ft.Row(row_controls, spacing=4))
        return ft.ListView(rows, expand=True, spacing=2)

    def _panel_header(self, title: str, subtitle: str) -> ft.Control:
        texts: list[ft.Control] = [ft.Text(title, size=13, weight=ft.FontWeight.BOLD)]
        if subtitle:
            texts.append(ft.Text(subtitle, size=11, color=ft.Colors.GREY_500))
        return ft.Column(texts, spacing=0)

    def _add_modify_item(self, item: RegisterItem) -> None:
        cloned = clone_items([item])[0]
        if self.connected:
            self._refresh_item_tree(cloned)
        self.modify_items.append(cloned)
        self._log(f"Added {item.name}")
        self.render_workspace()

    def _remove_modify_item(self, item: RegisterItem, siblings: list[RegisterItem]) -> None:
        try:
            siblings.remove(item)
        except ValueError:
            return
        self.render_workspace()

    def _set_write_value(self, item: RegisterItem, value: str) -> None:
        item.write_value = value if value else "NA"

    def _read_item(self, item: RegisterItem) -> None:
        self._refresh_item_tree(item)
        self.render_workspace()

    def _refresh_item_tree(self, item: RegisterItem) -> None:
        if item.level != 0:
            try:
                item.read_value = format_hex(self.register_service.read32_plus(item.address_expr))
            except Exception as exc:
                item.read_value = "?"
                self._log(f"Read failed: {exc}")
        for child in item.children:
            self._refresh_item_tree(child)

    def _write_item(self, item: RegisterItem) -> None:
        if item.write_value == "NA" or item.write_value == "":
            self._log(f"Skip {item.name}: write value is empty")
            return
        try:
            self.register_service.write32_plus(item.address_expr, item.write_value)
            item.read_value = format_hex(self.register_service.read32_plus(item.address_expr))
            self._log(f"Wrote {item.name} = {item.write_value}")
        except Exception as exc:
            self._log(f"Write failed: {exc}")
        self.render_workspace()

    async def _connect(self, _event: ft.Event) -> None:
        self._log("Connecting...")
        try:
            connected = await asyncio.to_thread(self.link_service.connect, self.core_value)
        except Exception as exc:
            logging.exception("Connect failed")
            self.connected = False
            self._log(f"Connect failed: {exc}")
        else:
            self.connected = connected
            self._log("Connected" if connected else "Connect failed")
            if connected:
                self.connection_watch = True
                self.page.run_task(self._connection_watch_loop)
        self.render_workspace()

    def _disconnect(self, _event: ft.Event) -> None:
        self.auto_refresh = False
        self.connection_watch = False
        self.link_service.disconnect()
        self.connected = False
        self._log("Disconnected")
        self.render_workspace()

    async def _connection_watch_loop(self) -> None:
        while self.connection_watch and self.connected:
            await asyncio.sleep(0.5)
            try:
                alive = self.link_service.is_connected()
            except Exception:
                alive = False
            if not alive:
                self.connection_watch = False
                self.auto_refresh = False
                self.connected = False
                self.link_service.disconnect()
                self._log("Target disconnected")
                self.render_workspace()
                return

    def _refresh_modify(self, _event: ft.Event | None = None) -> None:
        for item in self._iter_modify_items():
            if item.level == 0:
                continue
            try:
                item.read_value = format_hex(self.register_service.read32_plus(item.address_expr))
            except Exception:
                item.read_value = "?"
        self._log("Modify tree refreshed")
        self.render_workspace()

    def _upload_modify(self, _event: ft.Event | None = None) -> None:
        for item in self._iter_modify_items():
            if item.level == 0 or item.write_value in {"", "NA"}:
                continue
            try:
                self.register_service.write32_plus(item.address_expr, item.write_value)
                item.read_value = format_hex(self.register_service.read32_plus(item.address_expr))
            except Exception as exc:
                self._log(f"Upload failed for {item.name}: {exc}")
        self._log("Upload complete")
        self.render_workspace()

    def _iter_modify_items(self) -> list[RegisterItem]:
        items: list[RegisterItem] = []

        def walk(nodes: list[RegisterItem]) -> None:
            for node in nodes:
                items.append(node)
                walk(node.children)

        walk(self.modify_items)
        return items

    async def _open_regcfg(self, _event: ft.Event) -> None:
        files = await self.file_picker.pick_files(
            dialog_title="Open register configuration",
            initial_directory=".",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["regcfg"],
        )
        if not files:
            return
        path = files[0].path
        if not path:
            self._show_error("Selected file has no local path.")
            return
        try:
            items = self.config_file_service.read_regcfg(path)
            self.modify_items = items
            for item in self._iter_modify_items():
                if item.level != 0 and item.write_value not in {"", "NA"}:
                    self.register_service.write32_plus(item.address_expr, item.write_value)
            self._refresh_modify()
            self._log(f"Opened {path}")
        except Exception as exc:
            self._show_error(f"Open failed: {exc}")

    async def _save_regcfg(self, _event: ft.Event) -> None:
        path = await self.file_picker.save_file(
            dialog_title="Save register configuration",
            file_name="jgkit.regcfg",
            initial_directory=".",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["regcfg"],
        )
        if not path:
            return
        try:
            self.config_file_service.write_regcfg(path, self.modify_items)
            self._log(f"Saved {path}")
        except Exception as exc:
            self._show_error(f"Save failed: {exc}")

    async def _save_glicfg(self, _event: ft.Event) -> None:
        path = await self.file_picker.save_file(
            dialog_title="Save glimpse configuration",
            file_name="jgkit.glicfg",
            initial_directory=".",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["glicfg"],
        )
        if not path:
            return
        try:
            self.config_file_service.write_glicfg(path, self.modify_items, self.register_service)
            self._log(f"Saved {path}")
        except Exception as exc:
            self._show_error(f"Glimpse failed: {exc}")

    def _toggle_auto_refresh(self, event: ft.Event) -> None:
        self.auto_refresh = bool(event.control.value)
        if self.auto_refresh:
            self.page.run_task(self._auto_refresh_loop)
        self.render_workspace()

    async def _auto_refresh_loop(self) -> None:
        while self.auto_refresh and self.connected:
            await asyncio.sleep(0.5)
            try:
                for item in self._iter_modify_items():
                    if item.level != 0:
                        item.read_value = format_hex(self.register_service.read32_plus(item.address_expr))
                for tab in self.memory_tabs:
                    self.memory_service.refresh_tab(tab)
            except Exception as exc:
                self.auto_refresh = False
                self._log(f"Auto refresh stopped: {exc}")
            self.render_workspace()

    def _commander_submit(self, event: ft.Event) -> None:
        value = str(event.control.value).strip()
        if value:
            self._log(f"JGKit: {value}")
        event.control.value = ""
        self.render_workspace()

    def _show_description(self, text: str) -> None:
        self.description_text.value = text
        self.page.update(self.description_text)

    def _show_add_memory_dialog(self, _event: ft.Event) -> None:
        address_field = ft.TextField(label="Address", value="0x0", autofocus=True)

        def confirm(event: ft.Event) -> None:
            self.page.pop_dialog()
            try:
                tab = self.memory_service.create_tab(parse_number(address_field.value))
                self.memory_tabs.append(tab)
                self.memory_index = len(self.memory_tabs) - 1
                self._log(f"Added memory tab {tab.name}")
                self.render_workspace()
            except Exception as exc:
                self._show_error(f"Add memory failed: {exc}")

        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Add Memory View"),
                content=address_field,
                actions=[
                    ft.TextButton("Cancel", on_click=lambda event: self.page.pop_dialog()),
                    ft.FilledButton("Add", on_click=confirm),
                ],
            )
        )

    def _remove_memory_tab(self, _event: ft.Event) -> None:
        if not self.memory_tabs:
            return
        self.memory_tabs.pop(self.memory_index)
        self.memory_index = max(0, min(self.memory_index, len(self.memory_tabs) - 1))
        self.render_workspace()

    def _show_rename_memory_dialog(self, _event: ft.Event) -> None:
        if not self.memory_tabs:
            return
        tab = self.memory_tabs[self.memory_index]
        name_field = ft.TextField(label="Name", value=tab.name, autofocus=True)

        def confirm(event: ft.Event) -> None:
            self.page.pop_dialog()
            value = str(name_field.value).strip()
            if value:
                tab.name = value
            self.render_workspace()

        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Rename Memory View"),
                content=name_field,
                actions=[
                    ft.TextButton("Cancel", on_click=lambda event: self.page.pop_dialog()),
                    ft.FilledButton("Rename", on_click=confirm),
                ],
            )
        )

    def _on_memory_tab_change(self, event: ft.Event) -> None:
        selected = list(event.control.selected)
        if selected:
            self.memory_index = int(selected[0])
            self.render_workspace()

    def _refresh_memory_tab(self, _event: ft.Event | None = None) -> None:
        if not self.memory_tabs:
            return
        try:
            self.memory_service.refresh_tab(self.memory_tabs[self.memory_index])
            self._log(f"Memory refreshed {self.memory_tabs[self.memory_index].name}")
        except Exception as exc:
            self._log(f"Memory refresh failed: {exc}")
        self.render_workspace()

    def _shift_memory_tab(self, direction: int) -> None:
        if not self.memory_tabs:
            return
        tab = self.memory_tabs[self.memory_index]
        byte_delta = (tab.tail_address - tab.head_address) * direction
        try:
            self.memory_service.shift_tab(tab, byte_delta)
            self._log(f"Memory block moved to {tab.name}")
        except Exception as exc:
            self._log(f"Memory block move failed: {exc}")
        self.render_workspace()

    def _write_memory_word(self, address: int, value: str) -> None:
        try:
            self.memory_service.write_word(address, value)
            self._refresh_memory_tab()
        except Exception as exc:
            self._show_error(f"Memory write failed: {exc}")

    async def _import_memory(self, _event: ft.Event) -> None:
        if not self.memory_tabs:
            self._show_error("Add a memory view first.")
            return
        files = await self.file_picker.pick_files(
            dialog_title="Import memory",
            initial_directory=".",
            allowed_extensions=["raw", "bin"],
            file_type=ft.FilePickerFileType.CUSTOM,
        )
        if not files:
            return
        path = files[0].path
        if not path:
            self._show_error("Selected file has no local path.")
            return
        address_field = ft.TextField(
            label="Address",
            value=hex(self.memory_tabs[self.memory_index].head_address),
        )

        def confirm(event: ft.Event) -> None:
            self.page.pop_dialog()
            try:
                self.memory_service.import_raw_or_bin(parse_number(address_field.value), path)
                self._refresh_memory_tab()
                self._log(f"Imported {path}")
            except Exception as exc:
                self._show_error(f"Import failed: {exc}")

        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Import Memory"),
                content=ft.Column([ft.Text(path, size=12), address_field], tight=True),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda event: self.page.pop_dialog()),
                    ft.FilledButton("Import", on_click=confirm),
                ],
            )
        )

    def _show_export_memory_dialog(self, _event: ft.Event) -> None:
        if not self.memory_tabs:
            self._show_error("Add a memory view first.")
            return
        tab = self.memory_tabs[self.memory_index]
        start_field = ft.TextField(label="Start Address", value=hex(tab.head_address))
        length_field = ft.TextField(label="Length", value=str(tab.tail_address - tab.head_address))

        async def choose_path(event: ft.Event) -> None:
            path = await self.file_picker.save_file(
                dialog_title="Export memory",
                file_name=f"{tab.name.replace('0x', '')}.raw",
                initial_directory=".",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["raw"],
            )
            if not path:
                return
            try:
                self.memory_service.export_raw(
                    parse_number(start_field.value),
                    parse_number(length_field.value),
                    path,
                )
                self.page.pop_dialog()
                self._log(f"Exported {path}")
            except Exception as exc:
                self._show_error(f"Export failed: {exc}")

        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Export Memory"),
                content=ft.Column([start_field, length_field], tight=True),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda event: self.page.pop_dialog()),
                    ft.FilledButton("Choose File", on_click=choose_path),
                ],
            )
        )

    def _log(self, message: str) -> None:
        logging.info(message)
        self.log_lines.append(message)
        self.log_lines = self.log_lines[-120:]

    def _show_error(self, message: str) -> None:
        self._log(message)
        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("JGKit"),
                content=ft.Text(message),
                actions=[ft.TextButton("OK", on_click=lambda event: self.page.pop_dialog())],
            )
        )


def main(page: ft.Page) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s - %(funcName)s - %(filename)s[line:%(lineno)d]",
    )
    app = JGKitFletApp(page)
    app.start()


def _select_app_view() -> ft.AppView:
    requested = os.environ.get("JGKIT_FLET_VIEW", "").strip().lower()
    if requested in {"app", "desktop", "flet_app"}:
        return ft.AppView.FLET_APP
    if requested in {"web", "browser", "web_browser"}:
        return ft.AppView.WEB_BROWSER

    try:
        import flet_desktop.version

        client_root = Path.home() / ".flet" / "client"
        cached = any(client_root.glob(f"flet-desktop-*-{flet_desktop.version.version}"))
    except Exception:
        cached = False

    if cached or os.environ.get("FLET_VIEW_PATH"):
        return ft.AppView.FLET_APP

    print(
        "Flet desktop client is not cached; starting JGKit in browser view. "
        "Set JGKIT_FLET_VIEW=desktop to force the native Flet window.",
        flush=True,
    )
    return ft.AppView.WEB_BROWSER


def run() -> None:
    ft.run(main, assets_dir=".image", view=_select_app_view())
