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

    def on_entry_return(self, event):
        """回调函数，打印Entry组件中的内容"""
        print(event.widget.get())

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

        # 创建一个Canvas并配置垂直滚动条
        canvas = tk.Canvas(frame, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.config(yscrollcommand=v_scrollbar.set)

        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        for row in range(50):
            for col in range(10):
                # 创建可编辑的表格单元
                entry = ttk.Entry(inner_frame, width=10)
                entry.grid(row=row, column=col, sticky="nsew")
                entry.insert(tk.END, f"R{row + 1}C{col + 1}")
                # 为每个Entry绑定<Return>事件
                entry.bind("<Return>", self.on_entry_return)

        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # 使用鼠标滚轮滚动
        canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(-1 * (event.delta // 120), "units"))


root = tk.Tk()
app = ExcelLikeApp(root)
root.mainloop()
