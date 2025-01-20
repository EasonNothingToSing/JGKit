import tkinter
import logging
from tkinter import ttk
from PIL import Image, ImageTk


class NvsViewer(tkinter.Toplevel):
    NVS_FRAME_TITLE = "NVS Viewer"
    NVS_WRAP_LENGTH_DEF = 400

    def __init__(self, master, **kwargs):
        super(NvsViewer, self).__init__(master)

        self.title(NvsViewer.NVS_FRAME_TITLE)
        self.geometry("600x400")

        self.__scroll_canvas = tkinter.Canvas(self)
        self.__scroll_canvas.pack(side="left", fill="both", expand=True)

        self.__scrollbar_y = tkinter.Scrollbar(self, orient="vertical", command=self.__scroll_canvas.yview)
        self.__scrollbar_y.pack(side="right", fill="y")

        self.__scroll_canvas.configure(yscrollcommand=self.__scrollbar_y.set)

        self.__content_frame = tkinter.Frame(self.__scroll_canvas)

        self.__scroll_canvas.create_window((0, 0), window=self.__content_frame, anchor="nw")

        self.__content_frame.update_idletasks()
        self.__scroll_canvas.config(scrollregion=self.__scroll_canvas.bbox("all"))

    def nvs_vender_content(self, nvs_dict: dict[int, bytes]):
        row = 0
        for __id, __values in nvs_dict.items():
            __id_frame = tkinter.Frame(self.__content_frame, relief="solid", bd=2, padx=10, pady=5)
            __id_frame.grid(row=row, column=0, padx=5, pady=5, sticky="w")

            __id_label = tkinter.Label(__id_frame, text=f"{__id}:", font=("Helvetica", 10, "bold"))
            __id_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

            __hex_values = " ".join(f"0x{value:02X}" for value in __values)
            __value_label = tkinter.Label(__id_frame, text=__hex_values, font=("Courier", 9), anchor="nw", wraplength=400)
            __value_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

            row += 1

        self.__content_frame.update_idletasks()
        self.__scroll_canvas.config(scrollregion=self.__scroll_canvas.bbox("all"))


if __name__ == "__main__":
    root = tkinter.Tk()
    root.title("主界面")
    root.geometry("300x200")  # 设置主窗口的大小

    def open_hex_window():
        nvs_viewer = NvsViewer(root)

        data = {
            1: bytes([0x1A, 0x2B, 0x3C, 0x4D, 0x5E, 0x6F, 0x7A, 0x8B, 0x9C, 0xAF, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E, 0x6F, 0x7A, 0x8B, 0x9C, 0xAF, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E, 0x6F, 0x7A, 0x8B, 0x9C, 0xAF]),
            2: bytes([0x11, 0x22, 0x33, 0x44, 0x55]),
            3: bytes([0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11]),
            4: bytes([0xAB, 0xCD, 0xEF]),
            5: bytes([0x11, 0x22, 0x33, 0x44, 0x55]),
            6: bytes([0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11]),
            7: bytes([0xAB, 0xCD, 0xEF]),
            8: bytes([0x11, 0x22, 0x33, 0x44, 0x55]),
            9: bytes([0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11]),
            10: bytes([0xAB, 0xCD, 0xEF]),
            12: bytes([0x11, 0x22, 0x33, 0x44, 0x55]),
            13: bytes([0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11]),
            14: bytes([0xAB, 0xCD, 0xEF])
        }

        nvs_viewer.nvs_vender_content(data)


    # 添加一个按钮，点击后弹出显示 Hex 数组的窗口
    open_button = tkinter.Button(root, text="显示 Hex 数组", command=open_hex_window)
    open_button.pack(padx=20, pady=20)

    # 运行主窗口的 Tkinter 循环
    root.mainloop()