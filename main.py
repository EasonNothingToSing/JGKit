import tkinter
from GuiRender import View
from GuiRender import Control
import logging
import global_var
import json
import os

import pygame
import pygame_menu


__CHIP_MENU__ = [("Venus", "venus-configure.json"), ("Vega", "vega-configure.json"), ("VegaP", "vegap-configure.json"), ("Arcs", "arcs-configure.json")]
xls_config_name = __CHIP_MENU__[0][1]


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s - %(funcName)s - %(filename)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    pygame.init()
    surface = pygame.display.set_mode((600, 400))


    def set_chip_config(value, xls_name):
        global xls_config_name
        print("%s-%s" % (value, xls_name))
        xls_config_name = xls_name

    def start_the_game():
        global menu
        menu.disable()
        with open(os.path.join("./.data/config", xls_config_name)) as f:
            global_var.init()
            dct = json.load(f, )
            for key in dct.keys():
                global_var.set_value(str(key), dct[key])
        logging.debug(global_var.get_value("name"))
        logging.debug(global_var.get_value("core"))
        logging.debug(global_var.get_value("excel"))
        logging.debug(global_var.get_value("sheets"))

        tk = tkinter.Tk()
        tk.title(View.UI_TITLE + "-" + global_var.get_value("name"))
        tk.geometry(View.UI_TOTAL_WIDTH + "x" + View.UI_TOTAL_HEIGHT)
        tk.iconphoto(True, tkinter.PhotoImage(file="./.image/icon/exchange.png"))
        Control.Control(tk)
        tk.mainloop()

    menu = pygame_menu.Menu('Welcome', 400, 300,
                            theme=pygame_menu.themes.THEME_BLUE)

    menu.add.selector('Chip :', __CHIP_MENU__, onchange=set_chip_config)
    menu.add.button('Set', start_the_game)
    menu.add.button('Quit', pygame_menu.events.EXIT)

    menu.mainloop(surface)
