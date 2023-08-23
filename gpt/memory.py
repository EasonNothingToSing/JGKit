import tkinter as tk
from tkinter import ttk

# ... 其他导入 ...

class ExcelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel-like App with Tkinter")

        self.create_tabs()

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<Double-Button-1>", self.on_tab_double_click)

        for i in range(3):
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=f"Sheet {i + 1}")
            self.create_editable_grid(frame, 30, 10)

    def on_tab_double_click(self, event):
        # 获取当前工作表(sheet)的名字
        tab_id = self.notebook.index('@%d,%d' % (event.x, event.y))
        tab_text = self.notebook.tab(tab_id, 'text')

        # 估计标签的宽度和位置
        label_width = len(tab_text) * 7  # 假设每个字符大约7像素宽
        label_x = event.x - (label_width // 2)

        # 创建一个Entry小部件来编辑工作表名字
        entry = ttk.Entry(self.notebook)
        entry.insert(0, tab_text)
        entry.bind("<Return>", lambda e: self.finish_edit_tab_name(tab_id, entry))
        entry.bind("<FocusOut>", lambda e: self.finish_edit_tab_name(tab_id, entry))
        entry.place(x=label_x, y=self.notebook.winfo_y(), width=label_width)
        entry.focus_set()

    def finish_edit_tab_name(self, tab_id, entry):
        new_text = entry.get()
        self.notebook.tab(tab_id, text=new_text)
        entry.destroy()

    def create_editable_grid(self, parent, rows, cols):
        # 创建Canvas和滚动条
        canvas = tk.Canvas(parent)
        canvas.grid(row=0, column=0, sticky="nsew")

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        scrollbar_y = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        scrollbar_x = tk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        # 在Canvas内创建一个Frame来放置表格
        grid_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=grid_frame, anchor="nw")

        for i in range(rows + 1):
            for j in range(cols + 1):
                if i == 0 and j == 0:
                    label = tk.Label(grid_frame, text="", width=10, bg="#D3D3D3", relief="solid", padx=3, pady=3)
                elif i == 0:
                    label = tk.Label(grid_frame, text=f"Col {j}", width=10, bg="#D3D3D3", relief="solid", padx=3, pady=3)
                elif j == 0:
                    label = tk.Label(grid_frame, text=f"Row {i}", width=10, bg="#D3D3D3", relief="solid", padx=3, pady=3)
                else:
                    entry = tk.Entry(grid_frame, borderwidth=1, relief="solid", width=10)
                    entry.grid(row=i, column=j, sticky="nsew")
                    grid_frame.grid_columnconfigure(j, weight=1)
                    continue
                label.grid(row=i, column=j, sticky="nsew")

        # 设置行权重
        for i in range(rows + 1):
            grid_frame.grid_rowconfigure(i, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")
    app = ExcelApp(root)
    root.mainloop()
