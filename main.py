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

from threading import Thread


__CHIP_CONFIG_FILE__ = "configure.json"
__CHIP_MENU__ = []
xls_config_name = ""


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s - %(funcName)s - %(filename)s[line:%(lineno)d]"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    pygame.init()
    surface = pygame.display.set_mode((600, 400))
    pygame.display.set_icon(pygame.image.load("./.image/icon/exchange.png"))
    pygame.display.set_caption("JGKit!!!")

    def set_chip_config(value, xls_name):
        global xls_config_name
        print("%s-%s" % (value, xls_name))
        xls_config_name = xls_name

    def start_the_game():
        global menu
        def run_window():
            with open(os.path.join("./.data/config", xls_config_name)) as f:
                global_var.init()
                dct = json.load(f, )
                for key in dct.keys():
                    global_var.set_value(str(key), dct[key])
            logging.debug(global_var.get_value("name"))
            logging.debug(global_var.get_value("core"))
            logging.debug(global_var.get_value("tif"))
            logging.debug(global_var.get_value("excel"))
            logging.debug(global_var.get_value("sheets"))

            tk = tkinter.Tk()
            tk.title(View.UI_TITLE + "-" + global_var.get_value("name"))
            tk.geometry(View.UI_TOTAL_WIDTH + "x" + View.UI_TOTAL_HEIGHT)
            tk.iconphoto(True, tkinter.PhotoImage(file="./.image/icon/exchange.png"))
            Control.Control(tk)
            tk.mainloop()

        Thread(target=run_window).start()
        time.sleep(5)
        menu.close()
        pygame.quit()

    menu = pygame_menu.Menu('Welcome', 600, 400,
                            theme=pygame_menu.themes.THEME_BLUE)

    with open(os.path.join("./.data/config", __CHIP_CONFIG_FILE__)) as f:
        __CHIP_MENU__ = json.load(f, )

    xls_config_name = __CHIP_MENU__[0][1]
    menu.add.selector('Chip :', __CHIP_MENU__, onchange=set_chip_config)
    menu.add.button('Set', start_the_game)
    menu.add.button('Quit', pygame_menu.events.EXIT)

    menu.mainloop(surface)

