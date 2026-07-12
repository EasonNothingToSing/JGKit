# JGKit

JGKit is an upgraded version of Jlink-Chip-Test-ToolKit. The current UI is built with PyWebView and uses one local webview shell for both startup chip/TIF selection and the main register/memory workspace.

## Setup

```bash
uv sync
```

## Run

```bash
uv run python main.py
```

You can also run the PyWebView UI module directly:

```bash
uv run python -m GuiRender.WebViewUI
```

For UI smoke checks without target hardware:

```bash
JGKIT_LINK_DEBUG=1 uv run python main.py
```

You can also enable `Debug` in the toolbar and then click `Connect` to use the built-in fake link without target hardware.
