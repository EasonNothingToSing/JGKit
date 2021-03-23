import tkinter
from GuiRender import View
from GuiRender import Control
import logging


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s - %(funcName)s - %(filename)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    tk = tkinter.Tk()
    tk.title(View.UI_TITLE)
    tk.geometry(View.UI_TOTAL_WIDTH + "x" + View.UI_TOTAL_HEIGHT)
    # tk.resizable(width=False, height=False)
    Control.Control(tk)
    tk.mainloop()

