import tkinter
from GuiRender import View
from GuiRender import Control
from GuiRender.Model import StartUp_Verify
import logging
import global_var
import json
import os
import time

import pygame
import pygame_menu

__CHIP_CONFIG_FILE__ = r".data/config"
__CHIP_MENU__ = []
__CHIP_TIF__ = []
xls_config_name = ""
chip_tif_name = ""
modify_widget_selector = None


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s - %(funcName)s - %(filename)s[line:%(lineno)d]"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    startup_handler = StartUp_Verify.StartUpVerify(__CHIP_CONFIG_FILE__)

    pygame.init()
    surface = pygame.display.set_mode((600, 400))
    pygame.display.set_icon(pygame.image.load("./.image/icon/exchange.png"))
    pygame.display.set_caption("JGKit!!!")

    def set_chip_config(value, xls_name):
        global xls_config_name
        global modify_widget_selector
        global chip_tif_name
        logging.debug(("%s-%s" % (value, xls_name)))
        xls_config_name = value[0][0]
        __CHIP_TIF__ = startup_handler[xls_config_name]["tif"]
        chip_tif_name = __CHIP_TIF__[0]
        modify_widget_selector.update_items([(option, index) for index, option in enumerate(__CHIP_TIF__)])
        modify_widget_selector.set_default_value(0)

    def set_tif_config(value, tif_name):
        global chip_tif_name
        logging.debug(("%s-%s" % (value, tif_name)))
        chip_tif_name = value[0][0]

    def start_the_game():
        global menu
        global_var.init()
        for key in startup_handler[xls_config_name].keys():
            if key == "tif":
                global_var.set_value('tif', chip_tif_name)
                continue
            global_var.set_value(str(key), startup_handler[xls_config_name][key])
        logging.debug(global_var.get_value("name"))
        logging.debug(global_var.get_value("core"))
        logging.debug(global_var.get_value("tif"))
        logging.debug(global_var.get_value("excel"))
        logging.debug(global_var.get_value("sheets"))
        pygame.quit()

    menu = pygame_menu.Menu('Welcome', 600, 400,
                            theme=pygame_menu.themes.THEME_BLUE)

    __CHIP_MENU__ = startup_handler.get_core_list()
    xls_config_name = __CHIP_MENU__[0]
    __CHIP_TIF__ = startup_handler[xls_config_name]["tif"]
    chip_tif_name = __CHIP_TIF__[0]

    menu.add.selector('Chip :', [(option, index) for index, option in enumerate(__CHIP_MENU__)],
                      onchange=set_chip_config)
    modify_widget_selector = menu.add.selector("TIF :",
                                               [(option, index) for index, option in enumerate(__CHIP_TIF__)],
                                               onchange=set_tif_config)
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

