from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AppConfig:
    name: str
    core: str
    tif_options: list[str]
    selected_tif: str
    excel: str
    sheets: list[str]
    raw: dict[str, Any]

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "AppConfig":
        tif_options = list(raw.get("tif", []))
        selected_tif = tif_options[0] if tif_options else ""
        return cls(
            name=str(raw.get("name", "")),
            core=str(raw.get("core", "")),
            tif_options=tif_options,
            selected_tif=selected_tif,
            excel=str(raw.get("excel", "")),
            sheets=list(raw.get("sheets", [])),
            raw=dict(raw),
        )

    def with_tif(self, tif: str) -> "AppConfig":
        return AppConfig(
            name=self.name,
            core=self.core,
            tif_options=self.tif_options,
            selected_tif=tif,
            excel=self.excel,
            sheets=self.sheets,
            raw=self.raw,
        )

    @property
    def core_options(self) -> list[str]:
        tif_config = self.raw.get(self.selected_tif)
        if isinstance(tif_config, dict):
            return [str(key) for key in tif_config.keys()]
        return []


@dataclass
class RegisterItem:
    name: str
    address_expr: str
    property: str = "NA"
    description: str = ""
    level: int = 1
    write_value: str = "NA"
    read_value: str = "NA"
    children: list["RegisterItem"] = field(default_factory=list)


@dataclass
class DeviceNode:
    name: str
    address: str
    description: str = ""
    children: list[RegisterItem] = field(default_factory=list)

    def as_register_item(self) -> RegisterItem:
        return RegisterItem(
            name=self.name,
            address_expr=self.address,
            property="NA",
            description=self.description,
            level=0,
            children=[clone_register_item(item) for item in self.children],
        )


@dataclass
class MemoryTabState:
    name: str
    head_address: int
    tail_address: int
    values: list[int] = field(default_factory=list)


def clone_register_item(item: RegisterItem) -> RegisterItem:
    return RegisterItem(
        name=item.name,
        address_expr=item.address_expr,
        property=item.property,
        description=item.description,
        level=item.level,
        write_value=item.write_value,
        read_value=item.read_value,
        children=[clone_register_item(child) for child in item.children],
    )
