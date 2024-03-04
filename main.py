import tkinter
from GuiRender import View
from GuiRender import Control
import logging
import global_var
import json
import os
import time

import pygame
import pygame_menu

__CHIP_CONFIG_FILE__ = "configure.json"
__CHIP_MENU__ = []
__CHIP_TIF__ = []
xls_config_name = ""
chip_tif_name = ""
modify_widget_selector = None


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s - %(funcName)s - %(filename)s[line:%(lineno)d]"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    pygame.init()
    surface = pygame.display.set_mode((600, 400))
    pygame.display.set_icon(pygame.image.load("./.image/icon/exchange.png"))
    pygame.display.set_caption("JGKit!!!")

    def set_chip_config(value, xls_name):
        global xls_config_name
        global modify_widget_selector
        global chip_tif_name
        logging.debug(("%s-%s" % (value, xls_name)))
        xls_config_name = xls_name
        __CHIP_TIF__ = []
        for item in load_file[value[0][0]]["TIF"]:
            __CHIP_TIF__.append([item, item])
        chip_tif_name = __CHIP_TIF__[0][0]
        modify_widget_selector.update_items(__CHIP_TIF__)
        modify_widget_selector.set_default_value(0)

    def set_tif_config(value, tif_name):
        global chip_tif_name
        logging.debug(("%s-%s" % (value, tif_name)))
        chip_tif_name = tif_name

    def start_the_game():
        global menu
        with open(os.path.join("./.data/config", xls_config_name)) as f:
            global_var.init()
            dct = json.load(f, )
            for key in dct.keys():
                global_var.set_value(str(key), dct[key])
            global_var.set_value("tif", chip_tif_name)
        logging.debug(global_var.get_value("name"))
        logging.debug(global_var.get_value("core"))
        logging.debug(global_var.get_value("tif"))
        logging.debug(global_var.get_value("excel"))
        logging.debug(global_var.get_value("sheets"))
        pygame.quit()

    menu = pygame_menu.Menu('Welcome', 600, 400,
                            theme=pygame_menu.themes.THEME_BLUE)

    with open(os.path.join("./.data/config", __CHIP_CONFIG_FILE__)) as f:
        load_file = json.load(f, )
        for item in load_file.keys():
            __CHIP_MENU__.append([item, load_file[item]["ConfigFile"]])

        xls_config_name = __CHIP_MENU__[0][1]
        for item in load_file[__CHIP_MENU__[0][0]]["TIF"]:
            __CHIP_TIF__.append([item, item])
        chip_tif_name = __CHIP_TIF__[0][0]

    menu.add.selector('Chip :', __CHIP_MENU__, onchange=set_chip_config)
    modify_widget_selector = menu.add.selector("TIF :", __CHIP_TIF__, onchange=set_tif_config)
    menu.add.button('Set', start_the_game)
    menu.add.button('Quit', pygame_menu.events.EXIT)

try:
    menu.mainloop(surface)
except Exception as exp:
    logging.debug("Exception -> %s", str(exp))
finally:
    tk = tkinter.Tk()
    tk.title(View.UI_TITLE + "-" + global_var.get_value("name"))
    tk.geometry(View.UI_TOTAL_WIDTH + "x" + View.UI_TOTAL_HEIGHT)
    tk.iconphoto(True, tkinter.PhotoImage(file="./.image/icon/exchange.png"))
    Control.Control(tk)
    tk.mainloop()

