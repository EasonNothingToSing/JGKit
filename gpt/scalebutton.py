import tkinter as tk


def toggle_slider(event):
    # 获取当前滑块位置
    current_value = slider.get()

    # 根据当前值切换滑块位置
    new_value = 1 if current_value == 0 else 0

    # 设置新的滑块位置
    slider.set(new_value)


# 创建主窗口
root = tk.Tk()
root.title("Toggle Slider")

# 创建滑块
slider = tk.Scale(root, from_=0, to=1, orient="horizontal", length=200, showvalue=False)
slider.pack(pady=20)

# 绑定鼠标点击事件
slider.bind("<Button-1>", toggle_slider)

# 运行主循环
root.mainloop()
