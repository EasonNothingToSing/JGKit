import tkinter
import logging
from tkinter import ttk
from PIL import Image, ImageTk

UI_TITLE = "JGKit"

UI_FONT_SIZE_PIXEL = "15"
UI_TEXT_PADX = "10"
UI_TEXT_PADY = "4"

UI_TOTAL_WIDTH = "1600"
UI_TOTAL_HEIGHT = "1200"

UI_CONTROL_FRAME_WIDTH = UI_TOTAL_WIDTH
UI_CONTROL_FRAME_HEIGHT = "50"

UI_CONTROL_BUTTON_FRAME_WIDTH = "1400"
UI_CONTROL_BUTTON_FRAME_HEIGHT = UI_CONTROL_FRAME_HEIGHT

UI_CONTROL_DESCRIPTION_FRAME_WIDTH = "200"
UI_CONTROL_DESCRIPTION_FRAME_HEIGHT = UI_CONTROL_FRAME_HEIGHT

UI_CONTROL_DESCRIPTION_WIDTH = "200"
UI_CONTROL_DESCRIPTION_HEIGHT = UI_CONTROL_FRAME_HEIGHT

UI_DISPLAY_TREE_WIDTH = "800"
UI_DISPLAY_TREE_HEIGHT = "800"
UI_DISPLAY_TREE_MARGIN = 5

UI_DEBUG_FRAME_WIDTH = UI_TOTAL_WIDTH
UI_DEBUG_FRAME_HEIGHT = "350"

UI_COMMANDER_FRAME_WIDHT = UI_DISPLAY_TREE_WIDTH
UI_COMMANDER_FRAME_HEIGHT = UI_DEBUG_FRAME_HEIGHT

UI_LOG_FRAME_WIDHT = UI_COMMANDER_FRAME_WIDHT
UI_LOG_FRAME_HEIGHT = UI_COMMANDER_FRAME_HEIGHT


DARCULA_DEFAULT_BG = "#3C3F41"
DARCULA_DEFAULT_FG = "#A7BABA"
DARCULA_DEFAULT_SELECT_BD = "#42678D"

DARCULA_BUTTON_HOVER = "#4C5052"

UI_FONT = ("Helvetica", -int(UI_FONT_SIZE_PIXEL))


class BaseFrame(tkinter.Frame):
    def __init__(self, master, **kwargs):
        super(BaseFrame, self).__init__(master, highlightbackground=DARCULA_DEFAULT_BG, highlightcolor=DARCULA_DEFAULT_BG, bd="0", relief=tkinter.FLAT, **kwargs)


class MainFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(MainFrame, self).__init__(master, width=UI_TOTAL_WIDTH, height=UI_TOTAL_HEIGHT,  bg=DARCULA_DEFAULT_BG, **kwargs)


# "<MouseWheel>"
class EntryPopup(tkinter.Entry):
    def __init__(self, master, text, **kwargs):
        super(EntryPopup, self).__init__(master, exportselection=False, fg=DARCULA_DEFAULT_FG, bg=DARCULA_DEFAULT_BG,
                                         highlightbackground=DARCULA_DEFAULT_SELECT_BD, highlightthickness="2",
                                         highlightcolor=DARCULA_DEFAULT_SELECT_BD, font=UI_FONT, justify=tkinter.CENTER, width="250", **kwargs)
        self.insert(0, text)
        self.focus_force()
        self.bind("<Escape>", lambda *ignore: self.destroy())
        self.bind("<Control-a>", self.select_all)
        self.bind_all("<MouseWheel>", lambda *ignore: self.destroy())

    def select_all(self, *ignore):
        ''' Set selection on the whole text '''
        self.selection_range(0, 'end')

        # returns 'break' to interrupt default key-bindings
        return 'break'


class ControlFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(ControlFrame, self).__init__(master, width=UI_CONTROL_FRAME_WIDTH, height=UI_CONTROL_FRAME_HEIGHT, bg=DARCULA_DEFAULT_BG, **kwargs)


class DescriptionFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(DescriptionFrame, self).__init__(master, width=UI_CONTROL_DESCRIPTION_FRAME_WIDTH, height=UI_CONTROL_DESCRIPTION_FRAME_HEIGHT, **kwargs)


class DescriptionMessage(tkinter.Text):
    def __init__(self, master, **kwargs):
        super(DescriptionMessage, self).__init__(master,
                                                 width=int(UI_CONTROL_DESCRIPTION_WIDTH)//int(UI_FONT_SIZE_PIXEL),
                                                 height=int(UI_CONTROL_DESCRIPTION_HEIGHT)//int(UI_FONT_SIZE_PIXEL),
                                                 bg=DARCULA_DEFAULT_BG, font=UI_FONT, padx=UI_TEXT_PADX,
                                                 pady=UI_TEXT_PADY, fg=DARCULA_DEFAULT_FG,
                                                 **kwargs)
        self.bind("<Key>", self._disable_key)

    def _disable_key(self, event):
        if event.state == 12 and event.keysym == 'c':
            return
        else:
            return 'break'


class ButtonFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(ButtonFrame, self).__init__(master, width=UI_CONTROL_BUTTON_FRAME_WIDTH, height=UI_CONTROL_BUTTON_FRAME_HEIGHT, bg=DARCULA_DEFAULT_BG, **kwargs)


class StageLabel(tkinter.Label):
    def __init__(self, master, **kwargs):
        self.disconnect_image = ImageTk.PhotoImage(Image.open("./.image/.disconnect/disconnect.png").resize((16, 16), Image.ANTIALIAS))
        self.connect_image = ImageTk.PhotoImage(Image.open("./.image/.connect/connect.png").resize((16, 16), Image.ANTIALIAS))
        super(StageLabel, self).__init__(master, bg=DARCULA_DEFAULT_BG, image=self.disconnect_image, **kwargs)

    def enable(self):
        self.configure(image=self.connect_image)

    def disable(self):
        self.configure(image=self.disconnect_image)


class FlatButton(tkinter.Button):
    def __init__(self, master, **kwargs):
        super(FlatButton, self).__init__(master, relief=tkinter.FLAT, bg=DARCULA_DEFAULT_BG, activebackground=DARCULA_BUTTON_HOVER, highlightcolor=DARCULA_BUTTON_HOVER, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_level)

    def bindable(self):
        self.configure(bg=DARCULA_DEFAULT_BG)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_level)

    def unbindable(self):
        self.configure(bg=DARCULA_DEFAULT_BG)
        self.unbind("<Enter>")
        self.unbind("<Leave>")

    def _on_enter(self, event):
        self.configure(bg=DARCULA_BUTTON_HOVER)

    def _on_level(self, event):
        self.configure(bg=DARCULA_DEFAULT_BG)


class PlayButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.play_image = ImageTk.PhotoImage(Image.open("./.image/.connect/play.png").resize((16, 16), Image.ANTIALIAS))
        self.play_dark_image = ImageTk.PhotoImage(Image.open("./.image/.connect/play-dark.png").resize((16, 16), Image.ANTIALIAS))
        super(PlayButton, self).__init__(master, image=self.play_image, **kwargs)
        self.bindable()

    def enable(self):
        self.configure(image=self.play_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.play_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class StopButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.stop_image = ImageTk.PhotoImage(Image.open("./.image/.disconnect/stop.png").resize((16, 16), Image.ANTIALIAS))
        self.stop_dark_image = ImageTk.PhotoImage(Image.open("./.image/.disconnect/stop-dark.png").resize((16, 16), Image.ANTIALIAS))
        super(StopButton, self).__init__(master, image=self.stop_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.stop_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.stop_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class RefreshButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.refresh_image = ImageTk.PhotoImage(Image.open("./.image/.refresh/refresh.png").resize((16, 16), Image.ANTIALIAS))
        self.refresh_dark_image = ImageTk.PhotoImage(Image.open("./.image/.refresh/refresh-dark.png").resize((16, 16), Image.ANTIALIAS))
        super(RefreshButton, self).__init__(master, image=self.refresh_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.refresh_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.refresh_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class DarculaCheckButton(tkinter.Checkbutton):
    def __init__(self, master, **kwargs):
        super(DarculaCheckButton, self).__init__(master, bg=DARCULA_DEFAULT_BG, fg=DARCULA_DEFAULT_FG,
                                                 selectcolor=DARCULA_DEFAULT_SELECT_BD, activebackground=DARCULA_DEFAULT_BG,
                                                 **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_level)

    def bindable(self):
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_level)

    def unbindable(self):
        self.unbind("<Enter>")
        self.unbind("<Leave>")

    def _on_enter(self, event):
        self.configure(activebackground=DARCULA_BUTTON_HOVER, bg=DARCULA_BUTTON_HOVER)

    def _on_level(self, event):
        self.configure(activebackground=DARCULA_DEFAULT_BG, bg=DARCULA_DEFAULT_BG)


class AutoCheck(DarculaCheckButton):
    def __init__(self, master, **kwargs):
        super(AutoCheck, self).__init__(master, onvalue="auto", offvalue="bluntness", **kwargs)
        self.deselect()
        self.disable()

    def enable(self):
        self.configure(state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(state=tkinter.DISABLED)
        self.unbindable()


class GraySeparator(ttk.Separator):
    def __init__(self, master, **kwargs):
        super(GraySeparator, self).__init__(master, orient=tkinter.VERTICAL, **kwargs)


class GraySeparatorH(ttk.Separator):
    def __init__(self, master, **kwargs):
        super(GraySeparatorH, self).__init__(master, orient=tkinter.HORIZONTAL, **kwargs)


class TreeFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(TreeFrame, self).__init__(master, width=UI_TOTAL_WIDTH, height=UI_TOTAL_HEIGHT, bg=DARCULA_DEFAULT_BG, **kwargs)


class DisplayTreeFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(DisplayTreeFrame, self).__init__(master, width=UI_DISPLAY_TREE_WIDTH, height=UI_DISPLAY_TREE_HEIGHT, bg=DARCULA_DEFAULT_BG, **kwargs)


class DisplayTree(ttk.Treeview):
    def __init__(self, master, top_columns, top_columns_width, **kwargs):
        self._top_columns = top_columns
        self._top_columns_width = top_columns_width
        super(DisplayTree, self).__init__(master, columns=self._top_columns[1:], height=int(UI_DISPLAY_TREE_HEIGHT)//int(UI_FONT_SIZE_PIXEL)-UI_DISPLAY_TREE_MARGIN, **kwargs)

        # Edit the heading
        self.heading("#0", text=self._top_columns[0], anchor="center")
        self.column("#0", width=self._top_columns_width[0], minwidth="25", anchor="center")

        for text, width in zip(self._top_columns[1:], self._top_columns_width[1:]):
            self.heading(text, text=text, anchor="center")
            self.column(text, width=width, minwidth="25", anchor="center")


class ModifyTreeFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(ModifyTreeFrame, self).__init__(master, width=UI_DISPLAY_TREE_WIDTH, height=UI_DISPLAY_TREE_HEIGHT, bg=DARCULA_DEFAULT_BG, **kwargs)


class ModifyTree(ttk.Treeview):
    def __init__(self, master, _top_columns, _top_columns_width, **kwargs):
        self._top_columns = _top_columns
        self._top_columns_width = _top_columns_width
        super(ModifyTree, self).__init__(master, columns=self._top_columns[1:], height=int(UI_DISPLAY_TREE_HEIGHT)//int(UI_FONT_SIZE_PIXEL)-UI_DISPLAY_TREE_MARGIN, **kwargs)

        # Edit the heading
        self.heading("#0", text=self._top_columns[0], anchor="center")
        self.column("#0", width=self._top_columns_width[0], minwidth="25", anchor="center")

        for text, width in zip(self._top_columns[1:], self._top_columns_width[1:]):
            self.heading(text, text=text, anchor="center")
            self.column(text, width=width, minwidth="25", anchor="center")


class DebugFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(DebugFrame, self).__init__(master, width=UI_DEBUG_FRAME_WIDTH, height=UI_DEBUG_FRAME_HEIGHT, **kwargs)


class CommanderFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(CommanderFrame, self).__init__(master, width=UI_COMMANDER_FRAME_WIDHT, height=UI_COMMANDER_FRAME_HEIGHT, bg=DARCULA_DEFAULT_BG, **kwargs)


class Commander(tkinter.Text):
    def __init__(self, master, **kwargs):
        super(Commander, self).__init__(master,
                                        width=int(UI_COMMANDER_FRAME_WIDHT)//int(UI_FONT_SIZE_PIXEL),
                                        height=int(UI_COMMANDER_FRAME_HEIGHT)//int(UI_FONT_SIZE_PIXEL),
                                        bg=DARCULA_DEFAULT_BG, font=UI_FONT, padx=UI_TEXT_PADX,
                                        pady=UI_TEXT_PADY, fg=DARCULA_DEFAULT_FG, highlightthickness="3",
                                        highlightcolor=DARCULA_DEFAULT_SELECT_BD,
                                        highlightbackground=DARCULA_DEFAULT_BG,
                                        insertbackground=DARCULA_DEFAULT_FG, **kwargs)


class LogFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(LogFrame, self).__init__(master, width=UI_LOG_FRAME_WIDHT, height=UI_LOG_FRAME_HEIGHT, bg=DARCULA_DEFAULT_BG, **kwargs)


class Log(tkinter.Text):
    def __init__(self, master, **kwargs):
        super(Log, self).__init__(master, width=int(UI_LOG_FRAME_WIDHT)//int(UI_FONT_SIZE_PIXEL),
                                  height=int(UI_LOG_FRAME_HEIGHT)//int(UI_FONT_SIZE_PIXEL),bg=DARCULA_DEFAULT_BG,
                                  font=UI_FONT, padx=UI_TEXT_PADX, pady=UI_TEXT_PADY, fg=DARCULA_DEFAULT_FG,
                                  **kwargs)

        self.bind("<Key>", self._disable_key)

    def _disable_key(self, event):
        if event.state == 12 and event.keysym == 'c':
            return
        else:
            return 'break'


if __name__ == "__main__":
    root = tkinter.Tk()
    # EntryPopup(root, "test").pack()
    d = DisplayTree(root)
    d.grid_propagate(0)
    for i in range(100):
        d.insert("", "end", text=str(i), values=("0x12345678", "15:20", "rw"))
    d.pack()

    root.mainloop()
