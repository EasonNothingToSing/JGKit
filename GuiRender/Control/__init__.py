from PIL import Image, ImageTk
import tkinter
import logging
import re
from GuiRender import View
from functools import wraps


class Control:
    def __init__(self, master, **kwargs):
        # Stage machine flag
        self.control_stage_machine = "disconnected"

        self._master = master

        # Main frame
        self.master_frame = View.MainFrame(self._master)
        self.master_frame.pack(expand=True, fill=tkinter.BOTH)

        # Control Frame
        self.control_frame = View.ControlFrame(self.master_frame)
        self.control_frame.pack(expand=True, fill=tkinter.X, side=tkinter.TOP, anchor="center")

        # Control description
        self.control_description_frame = View.DescriptionFrame(self.control_frame)
        self.control_description_frame.pack(expand=True, fill=tkinter.X, side=tkinter.LEFT, anchor="center")

        self.control_description_message = View.DescriptionMessage(self.control_description_frame)
        self.control_description_message.pack(expand=True, fill=tkinter.X, anchor="center")

        # Control button frame
        self.control_button_frame = View.ButtonFrame(self.control_frame)
        self.control_button_frame.pack(expand=True, fill=tkinter.X, side=tkinter.RIGHT, anchor="n")

        # Stage label
        self.stage_label = View.StageLabel(self.control_button_frame)
        self.stage_label.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        View.GraySeparator(self.control_button_frame).pack(side=tkinter.RIGHT, anchor="e", pady="4", fill="y", padx="4")
        self.auto_check = View.AutoCheck(self.control_button_frame)
        self.auto_check.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.refresh_button = View.RefreshButton(self.control_button_frame)
        self.refresh_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        View.GraySeparator(self.control_button_frame).pack(side=tkinter.RIGHT, anchor="e", pady="4", fill="y", padx="4")
        self.stop_button = View.StopButton(self.control_button_frame)
        self.stop_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.stop_button.configure(command=self.disconnect)
        self.play_button = View.PlayButton(self.control_button_frame)
        self.play_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.play_button.configure(command=self.connect)

        # View.GraySeparatorH(self.control_button_frame).pack(side=tkinter.BOTTOM, anchor="n")

        # Tree Frame
        self.tree_frame = View.TreeFrame(self.master_frame)
        self.tree_frame.pack(expand=True, fill=tkinter.BOTH, after=self.control_frame)

        # Display Tree
        self.display_tree_frame = View.DisplayTreeFrame(self.tree_frame)
        self.display_tree_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        self.display_tree = View.DisplayTree(self.display_tree_frame)
        self.display_tree.pack(expand=True, fill=tkinter.BOTH)

        # Modify Tree
        self.modify_tree_frame = View.ModifyTreeFrame(self.tree_frame)
        self.modify_tree_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)
        self.modify_tree = View.ModifyTree(self.modify_tree_frame)
        self.modify_tree.pack(expand=True, fill=tkinter.BOTH)

        # Debug Frame
        self.debug_frame = View.DebugFrame(self.master_frame)
        self.debug_frame.pack(expand=True, fill=tkinter.BOTH, after=self.tree_frame)

        # Commander Frame
        self.commander_frame = View.CommanderFrame(self.debug_frame)
        self.commander_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        self.commander = View.Commander(self.commander_frame)
        self.commander.pack(expand=True, fill=tkinter.BOTH)

        # Log Frame
        self.log_frame = View.LogFrame(self.debug_frame)
        self.log_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)
        self.log = View.Log(self.log_frame)
        self.log.pack(expand=True, fill=tkinter.BOTH)

    def refresh(self):
        pass

    def play(self):
        pass

    def stop(self):
        self.stage_label.disable()
        self.auto_check.disable()
        self.refresh_button.disable()
        self.stop_button.disable()
        self.play_button.enable()

    def control_button_stage_machine(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.control_stage_machine == "disconnected":
                if func.__name__ == "play":
                    self.stage_label.enable()
                    self.auto_check.enable()
                    self.refresh_button.enable()
                    self.stop_button.enable()
                    self.play_button.disable()
                    if func(self, *args, **kwargs):
                        self


            elif self.control_stage_machine == "connected":
                pass
            elif self.control_stage_machine == "refreshed":
                pass
            else:
                logging.error("Undefine stage machine parameter")
