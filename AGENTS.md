# AGENTS Guide for JGKit

This file helps coding agents work safely and efficiently in this repository.

## Scope

- Python desktop toolkit using a two-stage GUI flow: pygame_menu bootstrap, then tkinter main UI.
- Core app code is in GuiRender (MVC-style structure).
- The gpt directory appears to be auxiliary/experimental scripts, not the primary runtime path.

## Start Here

Read these first before making changes:

1. [README.md](README.md)
2. [main.py](main.py)
3. [GuiRender/Control/__init__.py](GuiRender/Control/__init__.py)
4. [GuiRender/View/__init__.py](GuiRender/View/__init__.py)
5. [GuiRender/Model/StartUp_Verify.py](GuiRender/Model/StartUp_Verify.py)
6. [GuiRender/Model/SWDJlink.py](GuiRender/Model/SWDJlink.py)
7. [GuiRender/Model/ExcelReader.py](GuiRender/Model/ExcelReader.py)
8. [JGKit.spec](JGKit.spec)
9. [setup.py](setup.py)

## Common Commands

- Install (editable): python -m pip install -e .
- Run app: python main.py
- Package app:
  - pyinstaller -F main.py -n JGKit -i exchange.ico --windowed --onefile
  - or pyinstaller JGKit.spec

## Architecture Notes

- Entry flow:
  - [main.py](main.py) builds chip/TIF selection menu using pygame_menu.
  - After selection, app switches to tkinter and constructs UI via GuiRender Control/View.
- Layer responsibilities:
  - View: UI constants/widgets and image assets in [GuiRender/View](GuiRender/View).
  - Control: event orchestration in [GuiRender/Control/__init__.py](GuiRender/Control/__init__.py).
  - Model: startup config, hardware/JLink, Excel/NVS processing in [GuiRender/Model](GuiRender/Model).
- Shared runtime state uses [global_var.py](global_var.py). Preserve initialization order when refactoring startup.

## Project Conventions and Pitfalls

- Relative resource paths are assumed from repo root (examples: .data/config, .image/icon/exchange.png). Changes should keep runtime path behavior stable.
- Packaging risk: [JGKit.spec](JGKit.spec) currently has empty datas; onefile packaging may miss runtime assets unless explicitly included.
- Platform risk: hardware flow depends on DLLs (JLink and SWD listener) and is likely Windows-centric. Validate behavior before making cross-platform assumptions.
- Dependency drift risk: code imports include pygame, pygame_menu, pandas, and openpyxl-related usage, but [setup.py](setup.py) lists only part of these dependencies.
- Import-style risk in NVS package: some modules use non-relative imports in [GuiRender/Model/nvs](GuiRender/Model/nvs), which can break in package execution contexts.

## When Editing

- Keep modifications scoped to one MVC layer when possible; if crossing layers, document why in the PR/commit message.
- Prefer minimal diffs and avoid broad renames in gpt scripts unless the change explicitly targets that area.
- If touching startup, menu, resource loading, or hardware I/O, run the GUI smoke check using python main.py.

## Testing and Validation Reality

- No repository-standard test command is defined.
- No lint/format command is defined.
- For now, validate by targeted runtime smoke checks and focused manual verification of affected flows.
