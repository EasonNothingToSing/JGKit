import tkinter as tk


class ByteTableApp:
    def __init__(self, master, data):
        self.master = master
        self.master.title("Bytes Table Display")

        # 使用传入的 1D 数组
        self.data = data
        self.num_bytes = 16  # 每行最多显示16个字节
        self.columns = 5  # 显示 5 列：分别是0-3, 4-7, 8-11, 12-15的字节值
        self.num_rows = (len(data) + self.num_bytes - 1) // self.num_bytes  # 计算行数

        # 创建一个框架来包裹所有的表格
        self.main_frame = tk.Frame(self.master, bd=2, relief="solid")
        self.main_frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # 创建表格
        self.create_table()

    def create_table(self):
        # 创建一个表格
        frame = tk.Frame(self.main_frame, bd=2, relief="solid")
        frame.grid(row=0, column=0, padx=5, pady=5)

        # 在表格上方添加ID标签
        id_label = tk.Label(frame, text="Table-1")
        id_label.grid(row=0, column=0, padx=5, pady=5)

        # 创建列头：0-3, 4-7, 8-11, 12-15
        for col in range(self.columns):
            byte_position_label = tk.Label(frame, text=f"{col * 4}-{col * 4 + 3}")
            byte_position_label.grid(row=1, column=col + 1, padx=5, pady=5)

        # 创建表格的内容：第一列是偏移地址，接下来是每行的bytes数据
        for row in range(self.num_rows):
            # 第一列是偏移地址
            offset_label = tk.Label(frame, text=f"0x{row * self.num_bytes:03X}")
            offset_label.grid(row=row + 2, column=0, padx=5, pady=5)

            # 每一列是bytes数据（分别显示0-3, 4-7, 8-11, 12-15字节）
            for col in range(self.columns):
                start_index = row * self.num_bytes + col * 4
                end_index = start_index + 4
                byte_values = self.data[start_index:end_index]
                byte_values_str = " ".join([f"0x{b:02X}" for b in byte_values])

                byte_label = tk.Label(frame, text=byte_values_str)
                byte_label.grid(row=row + 2, column=col + 1, padx=5, pady=5)


if __name__ == "__main__":
    # 示例数据，传入的一维数组
    sample_data = [
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F,
        # 继续添加更多数据...
    ]

    root = tk.Tk()
    app = ByteTableApp(root, sample_data)
    root.mainloop()
