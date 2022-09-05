import tkinter
from GuiRender import View
from GuiRender import Control
import logging
import global_var
import json


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s - %(funcName)s - %(filename)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    with open("configure.json") as f:
        global_var.init()
        dct = json.load(f, )
        for key in dct.keys():
            global_var.set_value(str(key), dct[key])

    tk = tkinter.Tk()
    tk.title(View.UI_TITLE)
    tk.geometry(View.UI_TOTAL_WIDTH + "x" + View.UI_TOTAL_HEIGHT)
    tk.iconphoto(True, tkinter.PhotoImage(file="./.image/icon/exchange.png"))
    Control.Control(tk)
    tk.mainloop()

