import tkinter
from GuiRender import View
from GuiRender import Control


if __name__ == "__main__":
    tk = tkinter.Tk()
    tk.title(View.UI_TITLE)
    tk.geometry(View.UI_TOTAL_WIDTH + "x" + View.UI_TOTAL_HEIGHT)
    # tk.resizable(width=False, height=False)
    Control.Control(tk)
    tk.mainloop()

