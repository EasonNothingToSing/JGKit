import tkinter as tk

root = tk.Tk()
root.title("Canvas Scroll Example")
root.geometry("300x200")

# 创建滚动条
x_scroll = tk.Scrollbar(root, orient=tk.HORIZONTAL)
x_scroll.pack(fill=tk.X, side=tk.BOTTOM)

y_scroll = tk.Scrollbar(root, orient=tk.VERTICAL)
y_scroll.pack(fill=tk.Y, side=tk.RIGHT)

# 创建 Canvas 并配置滚动条
canvas = tk.Canvas(root, bg="lightgray", xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
canvas.pack(fill=tk.BOTH, expand=True)

# 关联滚动条与 Canvas
x_scroll.config(command=canvas.xview)
y_scroll.config(command=canvas.yview)

# 在 Canvas 上绘制内容
for i in range(20):
    for j in range(30):
        canvas.create_text((j*80, i*40), text=f"({i}, {j})", anchor=tk.NW)

# 设置 Canvas 的滚动区域
canvas.config(scrollregion=canvas.bbox(tk.ALL))

root.mainloop()
