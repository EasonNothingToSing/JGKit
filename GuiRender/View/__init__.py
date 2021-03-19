import tkinter
import logging
from tkinter import ttk


UI_FONT_SIZE_PIXEL = "15"

UI_TOTAL_WIDTH = "1600"
UI_TOTAL_HEIGHT = "1200"
UI_DISPLAY_TREE_WIDTH = "800"
UI_DISPLAY_TREE_HEIGHT = "800"


DARCULA_DEFAULT_BG = "#3C3F41"
DARCULA_DEFAULT_FG = "#A7BABA"
DARCULA_DEFAULT_SELECT_BD = "#42678D"

UI_FONT = ("Helvetica", -int(UI_FONT_SIZE_PIXEL))


class MainFrame(tkinter.Frame):
    def __init__(self, master, **kwargs):
        super(MainFrame, self).__init__(master, **kwargs)


class EntryPopup(tkinter.Entry):
    def __init__(self, master, text, **kwargs):
        super(EntryPopup, self).__init__(master, exportselection=False, fg=DARCULA_DEFAULT_FG, bg=DARCULA_DEFAULT_BG,
                                         highlightbackground=DARCULA_DEFAULT_SELECT_BD, highlightthickness="4",
                                         highlightcolor=DARCULA_DEFAULT_SELECT_BD, font=UI_FONT, **kwargs)

        self.insert(0, text)
        self.focus_force()


class DisplayTree(ttk.Treeview):
    def __init__(self, master, **kwargs):
        self._top_columns = ("Name", "Address", "Field", "Property")
        self._top_columns_width = ("250", "200", "200", "150")
        super(DisplayTree, self).__init__(master, columns=self._top_columns, height=int(UI_DISPLAY_TREE_HEIGHT)/int(UI_FONT_SIZE_PIXEL), **kwargs)

        # Edit the heading
        self.heading("#0", text=self._top_columns[0], anchor="center")
        self.column("#0", width=self._top_columns_width[0], minwidth="25", anchor="center")

        for text, width in zip(self._top_columns[1:], self._top_columns_width[1:]):
            self.heading(text, text=text, anchor="center")
            self.column(text, width=width, minwidth="25", anchor="center")


if __name__ == "__main__":
    root = tkinter.Tk()
    # EntryPopup(root, "test").pack()
    d = DisplayTree(root)
    d.grid_propagate(0)
    for i in range(100):
        d.insert("", "end", text=str(i), values=("0x12345678", "15:20", "rw"))
    d.pack()

    root.mainloop()
