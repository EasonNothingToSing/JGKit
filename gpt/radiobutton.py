import tkinter as tk

def on_select():
    selected_option = var.get()
    if selected_option == 1:
        print("Selected AP")
    elif selected_option == 2:
        print("Selected CP")

# 创建主窗口
root = tk.Tk()
root.title("单选按钮示例")

# 创建一个 IntVar 用于存储选项值
var = tk.IntVar()

# 创建 AP 和 CP 单选按钮
rb_ap = tk.Radiobutton(root, text="AP", variable=var, value=1, command=on_select)
rb_cp = tk.Radiobutton(root, text="CP", variable=var, value=2, command=on_select)

# 布局单选按钮
rb_ap.pack(side=tk.LEFT, padx=20, pady=20)
rb_cp.pack(side=tk.RIGHT, padx=20, pady=20)

# 运行主循环
root.mainloop()
