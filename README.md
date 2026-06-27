# JGKit

JGKit is an upgraded version of Jlink-Chip-Test-ToolKit. The current UI is built with Flet and uses one GUI engine for both startup chip/TIF selection and the main register/memory workspace.

## Setup

```bash
uv sync
```

## Run

```bash
uv run python main.py
```

You can also run the Flet UI module directly:

```bash
uv run python -m GuiRender.FletUI
```

For UI smoke checks without target hardware:

```bash
JGKIT_LINK_DEBUG=1 uv run python main.py
```

On first run, the native Flet desktop client may need to be downloaded into `~/.flet/client`.
If it is not cached yet, JGKit starts in browser view automatically. To force a native window:

```bash
JGKIT_FLET_VIEW=desktop uv run python main.py
```

To force browser view:

```bash
JGKIT_FLET_VIEW=browser uv run python main.py
```
