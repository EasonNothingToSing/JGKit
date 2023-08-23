import tkinter as tk

def on_mousewheel(event):
    canvas.yview_scroll(-1*(event.delta//120), "units")  # 对于Windows, 滚动的增量是120的倍数

root = tk.Tk()
root.title("Canvas Scroll Without Scrollbars")
root.geometry("300x200")

canvas = tk.Canvas(root, bg="lightgray")
canvas.pack(fill=tk.BOTH, expand=True)

# 在 Canvas 上绘制内容
for i in range(20):
    for j in range(10):
        canvas.create_text((j*80, i*40), text=f"({i}, {j})", anchor=tk.NW)

# 设置 Canvas 的滚动区域
canvas.config(scrollregion=canvas.bbox(tk.ALL))

# 绑定滚轮滚动事件
canvas.bind_all("<MouseWheel>", on_mousewheel)

root.mainloop()
