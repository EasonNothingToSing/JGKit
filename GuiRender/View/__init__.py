import tkinter
import logging
from tkinter import ttk
from PIL import Image, ImageTk

UI_TITLE = "JGKit"

UI_FONT_SIZE_PIXEL = "15"
UI_TEXT_PADX = "10"
UI_TEXT_PADY = "4"

UI_TOTAL_WIDTH = "800"
UI_TOTAL_HEIGHT = "500"

UI_CONTROL_FRAME_WIDTH = UI_TOTAL_WIDTH
UI_CONTROL_FRAME_HEIGHT = "25"

UI_CONTROL_BUTTON_FRAME_WIDTH = "700"
UI_CONTROL_BUTTON_FRAME_HEIGHT = UI_CONTROL_FRAME_HEIGHT # str(int(UI_CONTROL_FRAME_HEIGHT)/2)

# UI_CONTROL_TOOLCHAIN_BUTTON_FRAME_WIDTH = "1400"
# UI_CONTROL_TOOLCHAIN_BUTTON_FRAME_HEIGHT = str(int(UI_CONTROL_FRAME_HEIGHT)/2)

UI_CONTROL_DESCRIPTION_FRAME_WIDTH = "100"
UI_CONTROL_DESCRIPTION_FRAME_HEIGHT = UI_CONTROL_FRAME_HEIGHT

UI_CONTROL_DESCRIPTION_WIDTH = "100"
UI_CONTROL_DESCRIPTION_HEIGHT = UI_CONTROL_FRAME_HEIGHT

UI_DISPLAY_TREE_WIDTH = "400"
UI_DISPLAY_TREE_HEIGHT = "300"
UI_DISPLAY_TREE_MARGIN = 5

UI_DEBUG_FRAME_WIDTH = UI_TOTAL_WIDTH
UI_DEBUG_FRAME_HEIGHT = "175"

UI_COMMANDER_FRAME_WIDTH = UI_DISPLAY_TREE_WIDTH
UI_COMMANDER_FRAME_HEIGHT = UI_DEBUG_FRAME_HEIGHT

UI_LOG_FRAME_WIDTH = UI_COMMANDER_FRAME_WIDTH
UI_LOG_FRAME_HEIGHT = UI_COMMANDER_FRAME_HEIGHT

UI_MEM_FRAME_WIDTH = UI_COMMANDER_FRAME_WIDTH
UI_MEM_FRAME_HEIGHT = UI_COMMANDER_FRAME_HEIGHT
UI_MEM_ELEMENTS_WIDTH = 20
UI_MEM_ELEMENTS_ITEM_VERTICAL_MAX = 40
UI_MEM_ELEMENTS_ITEM_HORIZON_MAX = 4

UI_MEM_CONTROL_FRAME_WIDTH = UI_MEM_FRAME_WIDTH
UI_MEM_CONTROL_FRAME_HEIGHT = "20"

# BG
DARCULA_DEFAULT_BG = "#282c34"
DARCULA_DEFAULT_SEC_BG = "#2e323a"

# FG
DARCULA_DEFAULT_FG = "#abb2bf"
DARCULA_DEFAULT_SEC_FG = "#848c96"

# Hover
DARCULA_BUTTON_HOVER = "#3e4451"

# Active
DARCULA_BUTTON_ACTIVE = "#4a90d9"

# Hover
DARCULA_BUTTON_WARNING = "#e06c75"

# Confirm
DARCULA_BUTTON_CONFIRM = "#98c379"

DARCULA_DEFAULT_SELECT_BD = "#42678D"

DARCULA_DEFAULT_TAB_BD = "lightblue"

UI_FONT = ("Helvetica", -int(UI_FONT_SIZE_PIXEL))


class BaseFrame(tkinter.Frame):
    def __init__(self, master, **kwargs):
        super(BaseFrame, self).__init__(master, highlightbackground=DARCULA_DEFAULT_BG,
                                        highlightcolor=DARCULA_DEFAULT_BG, bd="0", relief=tkinter.FLAT, **kwargs)


class MainFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(MainFrame, self).__init__(master, width=UI_TOTAL_WIDTH, height=UI_TOTAL_HEIGHT, bg=DARCULA_DEFAULT_BG,
                                        **kwargs)


# "<MouseWheel>"
class EntryPopup(tkinter.Entry):
    def __init__(self, master, text, **kwargs):
        super(EntryPopup, self).__init__(master, exportselection=False, fg=DARCULA_DEFAULT_FG, bg=DARCULA_DEFAULT_BG,
                                         highlightbackground=DARCULA_DEFAULT_SELECT_BD, highlightthickness="2",
                                         highlightcolor=DARCULA_DEFAULT_SELECT_BD, font=UI_FONT, justify=tkinter.CENTER,
                                         width="250", **kwargs)
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
        super(ControlFrame, self).__init__(master, width=UI_CONTROL_FRAME_WIDTH, height=UI_CONTROL_FRAME_HEIGHT,
                                           bg=DARCULA_DEFAULT_BG, **kwargs)


class DescriptionFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(DescriptionFrame, self).__init__(master, width=UI_CONTROL_DESCRIPTION_FRAME_WIDTH,
                                               height=UI_CONTROL_DESCRIPTION_FRAME_HEIGHT, **kwargs)


class DescriptionMessage(tkinter.Text):
    def __init__(self, master, **kwargs):
        super(DescriptionMessage, self).__init__(master,
                                                 width=int(UI_CONTROL_DESCRIPTION_WIDTH) // int(UI_FONT_SIZE_PIXEL),
                                                 height=int(UI_CONTROL_DESCRIPTION_HEIGHT) // int(UI_FONT_SIZE_PIXEL),
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
        super(ButtonFrame, self).__init__(master, width=UI_CONTROL_BUTTON_FRAME_WIDTH,
                                          height=UI_CONTROL_BUTTON_FRAME_HEIGHT, bg=DARCULA_DEFAULT_BG, **kwargs)


class ToolChainButtonFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(ToolChainButtonFrame, self).__init__(master, width=UI_CONTROL_TOOLCHAIN_BUTTON_FRAME_WIDTH,
                                                   height=UI_CONTROL_TOOLCHAIN_BUTTON_FRAME_HEIGHT,
                                                   bg=DARCULA_DEFAULT_BG, **kwargs)


class StageLabel(tkinter.Label):
    def __init__(self, master, **kwargs):
        self.disconnect_image = ImageTk.PhotoImage(
            Image.open("./.image/.disconnect/disconnect.png").resize((16, 16), Image.LANCZOS))
        self.connect_image = ImageTk.PhotoImage(
            Image.open("./.image/.connect/connect.png").resize((16, 16), Image.LANCZOS))
        super(StageLabel, self).__init__(master, bg=DARCULA_DEFAULT_BG, image=self.disconnect_image, **kwargs)

    def enable(self):
        self.configure(image=self.connect_image)

    def disable(self):
        self.configure(image=self.disconnect_image)


class FlatButton(tkinter.Button):
    def __init__(self, master, **kwargs):
        # Get tip text and pop corresponding key from kwargs
        if "tip_text" in kwargs.keys():
            self.tip_text = kwargs["tip_text"]
            kwargs.pop("tip_text")
        else:
            self.tip_text = None

        super(FlatButton, self).__init__(master, relief=tkinter.FLAT, bg=DARCULA_DEFAULT_BG,
                                         activebackground=DARCULA_BUTTON_HOVER, highlightcolor=DARCULA_BUTTON_HOVER, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_level)
        self.tip_window = None

    def bindable(self):
        self.configure(bg=DARCULA_DEFAULT_BG)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_level)

    def unbindable(self):
        self.configure(bg=DARCULA_DEFAULT_BG)
        self.unbind("<Enter>")
        self.unbind("<Leave>")
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

    def on_enter(self, event):
        self.configure(bg=DARCULA_BUTTON_HOVER)
        if self.tip_text:
            self.tip_window = TopTipBase(self)
            TopTipLabelBase(self.tip_window, text=self.tip_text).pack(ipadx=1)

    def on_level(self, event):
        self.configure(bg=DARCULA_DEFAULT_BG)
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None


class PlayButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.play_image = ImageTk.PhotoImage(Image.open("./.image/.connect/play.png").resize((16, 16), Image.LANCZOS))
        self.play_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.connect/play-dark.png").resize((16, 16), Image.LANCZOS))
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
        self.stop_image = ImageTk.PhotoImage(
            Image.open("./.image/.disconnect/stop.png").resize((16, 16), Image.LANCZOS))
        self.stop_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.disconnect/stop-dark.png").resize((16, 16), Image.LANCZOS))
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
        self.refresh_image = ImageTk.PhotoImage(
            Image.open("./.image/.refresh/refresh.png").resize((16, 16), Image.LANCZOS))
        self.refresh_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.refresh/refresh-dark.png").resize((16, 16), Image.LANCZOS))
        super(RefreshButton, self).__init__(master, image=self.refresh_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.refresh_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.refresh_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class UploadButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.upload_image = ImageTk.PhotoImage(
            Image.open("./.image/.refresh/upload.png").resize((16, 16), Image.LANCZOS))
        self.upload_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.refresh/upload-dark.png").resize((16, 16), Image.LANCZOS))
        super(UploadButton, self).__init__(master, image=self.upload_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.upload_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.upload_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class OpenFileButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.open_image = ImageTk.PhotoImage(
            Image.open("./.image/.file/open.png").resize((16, 16), Image.LANCZOS))
        self.open_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.file/open_dark.png").resize((16, 16), Image.LANCZOS))
        super(OpenFileButton, self).__init__(master, image=self.open_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.open_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.open_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class SaveFileButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.save_image = ImageTk.PhotoImage(
            Image.open("./.image/.file/save.png").resize((16, 16), Image.LANCZOS))
        self.save_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.file/save_dark.png").resize((16, 16), Image.LANCZOS))
        super(SaveFileButton, self).__init__(master, image=self.save_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.save_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.save_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class GlimpseFileButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.glimpse_image = ImageTk.PhotoImage(
            Image.open("./.image/.file/glimpse.png").resize((16, 16), Image.LANCZOS))
        self.glimpse_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.file/glimpse_dark.png").resize((16, 16), Image.LANCZOS))
        super(GlimpseFileButton, self).__init__(master, image=self.glimpse_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.glimpse_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.glimpse_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class NvsViewerPopButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.nvs_viewer_image = ImageTk.PhotoImage(
            Image.open("./.image/.nvs/nvs_viewer.png").resize((16, 16), Image.LANCZOS))
        self.nvs_viewer_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.nvs/nvs_viewer_dark.png").resize((16, 16), Image.LANCZOS))
        super(NvsViewerPopButton, self).__init__(master, image=self.nvs_viewer_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.nvs_viewer_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.nvs_viewer_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class DarculaCheckButton(tkinter.Checkbutton):
    def __init__(self, master, **kwargs):
        # Get tip text and pop corresponding key from kwargs
        if "tip_text" in kwargs.keys():
            self.tip_text = kwargs["tip_text"]
            kwargs.pop("tip_text")
        else:
            self.tip_text = None
        super(DarculaCheckButton, self).__init__(master, bg=DARCULA_DEFAULT_BG, fg=DARCULA_DEFAULT_FG,
                                                 selectcolor=DARCULA_DEFAULT_SELECT_BD,
                                                 activebackground=DARCULA_DEFAULT_BG,
                                                 **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_level)
        self.tip_window = None

    def bindable(self):
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_level)

    def unbindable(self):
        self.unbind("<Enter>")
        self.unbind("<Leave>")
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

    def on_enter(self, event):
        self.configure(activebackground=DARCULA_BUTTON_HOVER, bg=DARCULA_BUTTON_HOVER)
        if self.tip_text:
            self.tip_window = TopTipBase(self)
            TopTipLabelBase(self.tip_window, text=self.tip_text).pack(ipadx=1)

    def on_level(self, event):
        self.configure(activebackground=DARCULA_DEFAULT_BG, bg=DARCULA_DEFAULT_BG)
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None


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
        super(TreeFrame, self).__init__(master, width=UI_TOTAL_WIDTH, height=UI_TOTAL_HEIGHT, bg=DARCULA_DEFAULT_BG,
                                        **kwargs)


class DisplayTreeFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(DisplayTreeFrame, self).__init__(master, width=UI_DISPLAY_TREE_WIDTH, height=UI_DISPLAY_TREE_HEIGHT,
                                               bg=DARCULA_DEFAULT_BG, **kwargs)


class DisplayTree(ttk.Treeview):
    def __init__(self, master, top_columns, top_columns_width, **kwargs):
        self._top_columns = top_columns
        self._top_columns_width = top_columns_width
        super(DisplayTree, self).__init__(master, columns=self._top_columns[1:],
                                          height=int(UI_DISPLAY_TREE_HEIGHT) // int(
                                              UI_FONT_SIZE_PIXEL) - UI_DISPLAY_TREE_MARGIN, **kwargs)

        # Edit the heading
        self.heading("#0", text=self._top_columns[0], anchor="center")
        self.column("#0", width=self._top_columns_width[0], minwidth="25", anchor="center")

        for text, width in zip(self._top_columns[1:], self._top_columns_width[1:]):
            self.heading(text, text=text, anchor="center")
            self.column(text, width=width, minwidth="25", anchor="center")


class ModifyTreeFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(ModifyTreeFrame, self).__init__(master, width=UI_DISPLAY_TREE_WIDTH, height=UI_DISPLAY_TREE_HEIGHT,
                                              bg=DARCULA_DEFAULT_BG, **kwargs)


class ModifyTree(ttk.Treeview):
    def __init__(self, master, _top_columns, _top_columns_width, **kwargs):
        self._top_columns = _top_columns
        self._top_columns_width = _top_columns_width
        super(ModifyTree, self).__init__(master, columns=self._top_columns[1:],
                                         height=int(UI_DISPLAY_TREE_HEIGHT) // int(
                                             UI_FONT_SIZE_PIXEL) - UI_DISPLAY_TREE_MARGIN, **kwargs)

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
        super(CommanderFrame, self).__init__(master, width=UI_COMMANDER_FRAME_WIDTH, height=UI_COMMANDER_FRAME_HEIGHT,
                                             bg=DARCULA_DEFAULT_BG, **kwargs)


class Commander(tkinter.Text):
    def __init__(self, master, **kwargs):
        super(Commander, self).__init__(master,
                                        width=int(UI_COMMANDER_FRAME_WIDTH) // int(UI_FONT_SIZE_PIXEL),
                                        height=int(UI_COMMANDER_FRAME_HEIGHT) // int(UI_FONT_SIZE_PIXEL),
                                        bg=DARCULA_DEFAULT_BG, font=UI_FONT, padx=UI_TEXT_PADX,
                                        pady=UI_TEXT_PADY, fg=DARCULA_DEFAULT_FG, highlightthickness="3",
                                        highlightcolor=DARCULA_DEFAULT_SELECT_BD,
                                        highlightbackground=DARCULA_DEFAULT_BG,
                                        insertbackground=DARCULA_DEFAULT_FG, **kwargs)


class LogFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(LogFrame, self).__init__(master, width=UI_LOG_FRAME_WIDTH, height=UI_LOG_FRAME_HEIGHT,
                                       bg=DARCULA_DEFAULT_BG, **kwargs)


class Log(tkinter.Text):
    def __init__(self, master, **kwargs):
        super(Log, self).__init__(master, width=int(UI_LOG_FRAME_WIDTH) // int(UI_FONT_SIZE_PIXEL),
                                  height=int(UI_LOG_FRAME_HEIGHT) // int(UI_FONT_SIZE_PIXEL), bg=DARCULA_DEFAULT_BG,
                                  font=UI_FONT, padx=UI_TEXT_PADX, pady=UI_TEXT_PADY, fg=DARCULA_DEFAULT_FG,
                                  **kwargs)

        self.bind("<Key>", self._disable_key)

    def _disable_key(self, event):
        if event.state == 12 and event.keysym == 'c':
            return
        else:
            return 'break'


class MemFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(MemFrame, self).__init__(master, width=UI_MEM_FRAME_WIDTH, height=UI_MEM_FRAME_HEIGHT,
                                       bg=DARCULA_DEFAULT_BG, **kwargs)


class MemControlFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super(MemControlFrame, self).__init__(master, width=UI_MEM_CONTROL_FRAME_WIDTH,
                                              height=UI_MEM_CONTROL_FRAME_HEIGHT,
                                              bg=DARCULA_DEFAULT_BG, **kwargs)


class MemNoteBook(ttk.Notebook):
    def __init__(self, master, **kwargs):
        super(MemNoteBook, self).__init__(master, **kwargs)


class Memsheet(tkinter.Frame):
    def __init__(self, master, **kwargs):
        super(Memsheet, self).__init__(master, bg=DARCULA_DEFAULT_BG, **kwargs)


class MemHeaderFrame(tkinter.Frame):
    def __init__(self, master, **kwargs):
        super(MemHeaderFrame, self).__init__(master, bg=DARCULA_DEFAULT_SEC_BG, **kwargs)


class MemHeaderLab(tkinter.Label):
    DEFAULT_SHEET_HEADER_LABEL_WIDTH = UI_MEM_ELEMENTS_WIDTH
    DEFAULT_SHEET_HEADER_LABEL_MARGING = 3
    DEFAULT_SHEET_HEADER_LABEL_BW = 1

    def __init__(self, master, **kwargs):
        super(MemHeaderLab, self).__init__(master, fg=DARCULA_DEFAULT_SEC_FG, bg=DARCULA_DEFAULT_SEC_BG,
                                           width=MemLabel.DEFAULT_SHEET_LABEL_WIDTH,
                                           relief="raised", padx=MemLabel.DEFAULT_SHEET_LABEL_MARGING,
                                           borderwidth = MemHeaderLab.DEFAULT_SHEET_HEADER_LABEL_BW,
                                           pady=MemLabel.DEFAULT_SHEET_LABEL_MARGING, **kwargs)


class MemLabel(tkinter.Label):
    DEFAULT_SHEET_LABEL_WIDTH = UI_MEM_ELEMENTS_WIDTH
    DEFAULT_SHEET_LABEL_MARGING = 3
    DEFAULT_SHEET_LABEL_HEIGHT = 27

    def __init__(self, master, **kwargs):
        super(MemLabel, self).__init__(master, fg=DARCULA_DEFAULT_FG, bg=DARCULA_DEFAULT_BG,
                                       width=MemLabel.DEFAULT_SHEET_LABEL_WIDTH, relief="raised",
                                       padx=MemLabel.DEFAULT_SHEET_LABEL_MARGING,
                                       pady=MemLabel.DEFAULT_SHEET_LABEL_MARGING, **kwargs)


class MemUnit(tkinter.Entry):
    DEFAULT_SHEET_UNIT_WIDTH = UI_MEM_ELEMENTS_WIDTH
    DEFAULT_SHEET_UNIT_MARGING = 3
    DEFAULT_SHEET_UNIT_BW = 2

    def __init__(self, master, **kwargs):
        super(MemUnit, self).__init__(master, fg=DARCULA_DEFAULT_FG, bg=DARCULA_DEFAULT_SELECT_BD,
                                      borderwidth=MemUnit.DEFAULT_SHEET_UNIT_BW, relief="solid",
                                      width=MemUnit.DEFAULT_SHEET_UNIT_WIDTH, **kwargs)


class LoadFileButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.load_image = ImageTk.PhotoImage(
            Image.open("./.image/.memory/load.png").resize((16, 16), Image.LANCZOS))
        self.load_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.memory/load_dark.png").resize((16, 16), Image.LANCZOS))
        super(LoadFileButton, self).__init__(master, image=self.load_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.load_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.load_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class StoreFileButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.store_image = ImageTk.PhotoImage(
            Image.open("./.image/.memory/store.png").resize((16, 16), Image.LANCZOS))
        self.store_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.memory/store_dark.png").resize((16, 16), Image.LANCZOS))
        super(StoreFileButton, self).__init__(master, image=self.store_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.store_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.store_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class AddFileButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.add_image = ImageTk.PhotoImage(
            Image.open("./.image/.memory/add.png").resize((16, 16), Image.LANCZOS))
        self.add_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.memory/add_dark.png").resize((16, 16), Image.LANCZOS))
        super(AddFileButton, self).__init__(master, image=self.add_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.add_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.add_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class SubFileButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.sub_image = ImageTk.PhotoImage(
            Image.open("./.image/.memory/sub.png").resize((16, 16), Image.LANCZOS))
        self.sub_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.memory/sub_dark.png").resize((16, 16), Image.LANCZOS))
        super(SubFileButton, self).__init__(master, image=self.sub_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.sub_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.sub_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class RefreshFileButton(FlatButton):
    def __init__(self, master, **kwargs):
        self.refresh_image = ImageTk.PhotoImage(
            Image.open("./.image/.refresh/refresh.png").resize((16, 16), Image.LANCZOS))
        self.refresh_dark_image = ImageTk.PhotoImage(
            Image.open("./.image/.refresh/refresh-dark.png").resize((16, 16), Image.LANCZOS))
        super(RefreshFileButton, self).__init__(master, image=self.refresh_dark_image, state=tkinter.DISABLED, **kwargs)
        self.unbindable()

    def enable(self):
        self.configure(image=self.refresh_image, state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(image=self.refresh_dark_image, state=tkinter.DISABLED)
        self.unbindable()


class TopLevelBase(tkinter.Toplevel):
    def __init__(self, master, **kwargs):
        super(TopLevelBase, self).__init__(master=master, **kwargs)
        self.attributes("-topmost", True)

        x = (master.winfo_screenwidth() // 2)
        y = (master.winfo_screenheight() // 2)

        self.geometry(f"+{x}+{y}")


class TopTipLabelBase(tkinter.Label):
    def __init__(self, master, **kwargs):
        super(TopTipLabelBase, self).__init__(master, justify=tkinter.LEFT, background="#ffffe0",
                                              relief=tkinter.SOLID, borderwidth=1, font=UI_FONT, **kwargs)


class TopTipBase(tkinter.Toplevel):
    DEFAULT_TOPTIP_MARGING_WIDTH = 20
    DEFAULT_TOPTIP_MARGING_HEIGHT = 20

    def __init__(self, master, **kwargs):
        super(TopTipBase, self).__init__(master=master, **kwargs)
        self.wm_overrideredirect(True)
        self.wm_geometry("+%d+%d" % ((self.master.winfo_rootx() + TopTipBase.DEFAULT_TOPTIP_MARGING_WIDTH),
                                     (self.master.winfo_rooty() + self.master.winfo_height() +
                                      TopTipBase.DEFAULT_TOPTIP_MARGING_HEIGHT)))


class RadioButtonBase(tkinter.Radiobutton):
    DEFAULT_RADIOBUTTON_BG_COLOR = DARCULA_DEFAULT_BG
    DEFAULT_RADIOBUTTON_FG_COLOR = DARCULA_DEFAULT_FG
    DEFAULT_RADIOBUTTON_FONT = UI_FONT
    DEFAULT_RADIOBUTTON_PADX = 2
    DEFAULT_RADIOBUTTON_PADY = 2
    DEFAULT_RADIOBUTTON_WIDTH = 5
    DEFAULT_RADIOBUTTON_HEIGHT = 5

    def __init__(self, master, **kwargs):
        # Get tip text and pop corresponding key from kwargs
        if "tip_text" in kwargs.keys():
            self.tip_text = kwargs["tip_text"]
            kwargs.pop("tip_text")
        else:
            self.tip_text = None

        super(RadioButtonBase, self).__init__(master=master, bg=RadioButtonBase.DEFAULT_RADIOBUTTON_BG_COLOR,
                                              fg=RadioButtonBase.DEFAULT_RADIOBUTTON_FG_COLOR, indicatoron=0,
                                              font=RadioButtonBase.DEFAULT_RADIOBUTTON_FONT, **kwargs)

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_level)
        self.tip_window = None

    def bindable(self):
        self.configure(bg=DARCULA_DEFAULT_BG)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_level)

    def unbindable(self):
        self.configure(bg=DARCULA_DEFAULT_BG)
        self.unbind("<Enter>")
        self.unbind("<Leave>")
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

    def enable(self):
        self.configure(state=tkinter.NORMAL)
        self.bindable()

    def disable(self):
        self.configure(state=tkinter.DISABLED)
        self.unbindable()

    def on_enter(self, event):
        self.configure(bg=DARCULA_BUTTON_HOVER)
        if self.tip_text:
            self.tip_window = TopTipBase(self)
            TopTipLabelBase(self.tip_window, text=self.tip_text).pack(ipadx=1)

    def on_level(self, event):
        self.configure(bg=DARCULA_DEFAULT_BG)
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None


if __name__ == "__main__":
    root = tkinter.Tk()
    # EntryPopup(root, "test").pack()
    d = DisplayTree(root)
    d.grid_propagate(0)
    for i in range(100):
        d.insert("", "end", text=str(i), values=("0x12345678", "15:20", "rw"))
    d.pack()

    root.mainloop()
