# AGENTS Guide for JGKit

This file helps coding agents work safely and efficiently in this repository.

## Scope

- Python desktop toolkit with a PyWebView primary UI for startup chip/TIF selection and the main register/memory workspace.
- Core app code is in GuiRender. The primary runtime UI lives in [GuiRender/WebViewUI](GuiRender/WebViewUI).
- [GuiRender/Control](GuiRender/Control) and [GuiRender/View](GuiRender/View) are legacy UI modules and are not part of the main entry path.
- The gpt directory appears to be auxiliary/experimental scripts, not the primary runtime path.

## Start Here

Read these first before making changes:

1. [README.md](README.md)
2. [main.py](main.py)
3. [GuiRender/WebViewUI/app.py](GuiRender/WebViewUI/app.py)
4. [GuiRender/WebViewUI/api.py](GuiRender/WebViewUI/api.py)
5. [GuiRender/WebViewUI/view.py](GuiRender/WebViewUI/view.py)
6. [GuiRender/Model/StartUp_Verify.py](GuiRender/Model/StartUp_Verify.py)
7. [GuiRender/Model/SWDJlink.py](GuiRender/Model/SWDJlink.py)
8. [GuiRender/Model/ExcelReader.py](GuiRender/Model/ExcelReader.py)
9. [JGKit.spec](JGKit.spec)
10. [setup.py](setup.py)

## Common Commands

- Install/sync: uv sync
- Run app: uv run python main.py
- Run PyWebView module directly: uv run python -m GuiRender.WebViewUI
- Run without target hardware: JGKIT_LINK_DEBUG=1 uv run python main.py
- Package app:
  - pyinstaller -F main.py -n JGKit -i exchange.ico --windowed --onefile
  - or pyinstaller JGKit.spec

## Architecture Notes

- Entry flow:
  - [main.py](main.py) delegates to [GuiRender/WebViewUI](GuiRender/WebViewUI).
  - PyWebView renders both the chip/TIF selection page and the main workspace.
- Layer responsibilities:
  - WebViewUI: PyWebView window setup in [GuiRender/WebViewUI/app.py](GuiRender/WebViewUI/app.py), Python bridge methods in [GuiRender/WebViewUI/api.py](GuiRender/WebViewUI/api.py), and local HTML/CSS/JS in [GuiRender/WebViewUI/view.py](GuiRender/WebViewUI/view.py).
  - AppCore: shared startup config, Excel device tree generation, JLink access, register/config/memory services in [GuiRender/AppCore](GuiRender/AppCore).
  - Model: startup config, hardware/JLink, Excel/NVS processing in [GuiRender/Model](GuiRender/Model).
- Shared runtime state uses [global_var.py](global_var.py). Preserve initialization order when refactoring startup.

## Project Conventions and Pitfalls

- Relative resource paths are assumed from repo root (examples: .data/config, .image/icon/exchange.png). Changes should keep runtime path behavior stable.
- Packaging risk: [JGKit.spec](JGKit.spec) currently has empty datas; onefile packaging may miss runtime assets unless explicitly included.
- Platform risk: hardware flow depends on DLLs (JLink and SWD listener) and is likely Windows-centric. Validate behavior before making cross-platform assumptions.
- Dependency drift risk: keep [pyproject.toml](pyproject.toml), [uv.lock](uv.lock), and [setup.py](setup.py) aligned.
- Import-style risk in NVS package: some modules use non-relative imports in [GuiRender/Model/nvs](GuiRender/Model/nvs), which can break in package execution contexts.

## When Editing

- Keep modifications scoped to one MVC layer when possible; if crossing layers, document why in the PR/commit message.
- Prefer minimal diffs and avoid broad renames in gpt scripts unless the change explicitly targets that area.
- If touching startup, menu, resource loading, or hardware I/O, run the GUI smoke check using `JGKIT_LINK_DEBUG=1 uv run python main.py`.

## Testing and Validation Reality

- No repository-standard test command is defined.
- No lint/format command is defined.
- For now, validate with `uv sync`, `uv pip check --python .venv/bin/python`, `uv run python -m compileall -q .`, targeted runtime smoke checks, and focused manual verification of affected flows.
