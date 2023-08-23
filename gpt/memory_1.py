import tkinter as tk
from tkinter import ttk


class ExcelLikeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel-like GUI with Tkinter")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建一个新的sheet
        self.create_new_sheet("Sheet1")

    def create_new_sheet(self, name):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=name)
        self.notebook.select(frame)

        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        # 在header_frame中添加列号
        for col in range(10):
            label = ttk.Label(header_frame, text=str(col + 1), width=10, borderwidth=1, relief=tk.SOLID)
            label.grid(row=0, column=col, sticky="nsew")

        canvas = tk.Canvas(frame, bg="white")
        canvas.pack(fill=tk.BOTH, expand=True)

        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        for row in range(50):
            for col in range(10):
                entry = ttk.Entry(inner_frame, width=10)
                entry.grid(row=row, column=col, sticky="nsew")
                entry.insert(tk.END, f"R{row}C{col}")

        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

        def on_mousewheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")  # 对于Windows, 滚动的增量是120的倍数

        # 使用鼠标滚轮滚动
        canvas.bind("<MouseWheel>", on_mousewheel)


root = tk.Tk()
app = ExcelLikeApp(root)
root.mainloop()
