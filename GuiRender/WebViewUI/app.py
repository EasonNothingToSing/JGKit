from __future__ import annotations

import logging
import os
from pathlib import Path

import webview

from .api import JGKitApi
from .view import HTML


APP_TITLE = "JGKit"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 820


def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s - %(funcName)s - %(filename)s[line:%(lineno)d]",
    )
    api = JGKitApi()
    icon_path = Path("exchange.ico").resolve()
    window = webview.create_window(
        APP_TITLE,
        html=HTML,
        js_api=api,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(1024, 680),
        background_color="#101418",
        text_select=True,
    )
    api.window = window
    webview.start(
        debug=os.environ.get("JGKIT_WEBVIEW_DEBUG", "").lower() in {"1", "true", "yes", "on"},
        icon=str(icon_path) if icon_path.exists() else None,
    )
