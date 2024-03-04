from PIL import Image, ImageTk
import tkinter
from tkinter import ttk
from tkinter import filedialog
import logging
import re
from GuiRender import View
from GuiRender.Model import Excel2Dict
from GuiRender.Model import SWDJlink
from GuiRender.Model import WidgetLogger
from GuiRender.Model import Xlsx2Xls
from bitstring import BitArray
from functools import wraps
import json
import os
import global_var
import shutil
import time


class Control:
    def __init__(self, master, **kwargs):
        # Stage machine flag
        self.control_stage_machine = "disconnected"

        self._master = master

        self._excel = os.path.join("./.data/xls", global_var.get_value("excel"))
        self._module_sheets = global_var.get_value("sheets")

        basename, ext = os.path.splitext(global_var.get_value("excel"))
        # Check xls file or xlsx file is exists
        if os.path.exists(os.path.join("./.data/xls", basename + ".xls")):
            shutil.copy(os.path.join("./.data/xls", basename + ".xls"),
                        os.path.join("./.data/xls/.temp", basename + ".xls"))
        elif os.path.exists(os.path.join("./.data/xls", basename + ".xlsx")):
            Xlsx2Xls.xlsxfileconvert(os.path.join("./.data/xls", basename + ".xlsx"))

        self._excel = os.path.join("./.data/xls/.temp", basename + ".xls")

        # Style *************************************************************************************
        style = ttk.Style(self._master)
        style.theme_use("clam")
        style.configure('TNotebook', background=View.DARCULA_DEFAULT_BG)
        style.configure('TNotebook.Tab', foreground=View.DARCULA_DEFAULT_FG)
        style.map('TNotebook.Tab',
                  background=[('selected', View.DARCULA_DEFAULT_SELECT_BD), ('active', View.DARCULA_DEFAULT_TAB_BD)])
        style.configure("Treeview",
                        rowheight=str(int(View.UI_FONT_SIZE_PIXEL) + int(View.UI_DISPLAY_TREE_MARGIN) * 1.5),
                        fieldbackground=View.DARCULA_DEFAULT_BG, background=View.DARCULA_DEFAULT_BG,
                        foreground=View.DARCULA_DEFAULT_FG, relief="flat", highlightbackground=View.DARCULA_DEFAULT_BG,
                        highlightcolor=View.DARCULA_DEFAULT_BG)
        style.configure("Treeview.Heading", background=View.DARCULA_DEFAULT_BG, foreground=View.DARCULA_DEFAULT_FG,
                        relief="flat", highlightbackground=View.DARCULA_DEFAULT_BG,
                        highlightcolor=View.DARCULA_DEFAULT_BG)
        style.map("Treeview",
                  background=[("disabled", View.DARCULA_DEFAULT_BG),
                              ("selected", View.DARCULA_BUTTON_HOVER)
                              ],

                  foreground=[("disabled", View.DARCULA_DEFAULT_FG),
                              ],

                  relief=[('active', 'groove'),
                          ('pressed', 'sunken')
                          ],

                  highlightbackground=[('disabled', View.DARCULA_DEFAULT_BG),
                                       ],

                  highlightcolor=[("disabled", View.DARCULA_DEFAULT_BG),
                                  ],
                  )
        style.map("Treeview.Heading",
                  background=[("disabled", View.DARCULA_DEFAULT_BG),
                              ],

                  foreground=[("disabled", View.DARCULA_DEFAULT_FG),
                              ],
                  )

        # Style *************************************************************************************

        # Main frame
        self.master_frame = View.MainFrame(self._master)
        self.master_frame.pack(expand=True, fill=tkinter.BOTH)

        # Control Frame
        self.control_frame = View.ControlFrame(self.master_frame)
        self.control_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.TOP, anchor="center")

        # Control description
        self.control_description_frame = View.DescriptionFrame(self.control_frame)
        self.control_description_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT, anchor="n")

        self.control_description_message = View.DescriptionMessage(self.control_description_frame)
        self.control_description_message.pack(expand=True, fill=tkinter.BOTH, anchor="n")

        # Control button frame
        self.control_button_frame = View.ButtonFrame(self.control_frame)
        self.control_button_frame.pack(expand=True, fill=tkinter.X, side=tkinter.RIGHT, anchor="n")

        # self.control_toolchain_button_frame = View.ToolChainButtonFrame(self.control_frame)
        # self.control_toolchain_button_frame.pack(expand=True, fill=tkinter.X, side=tkinter.BOTTOM, anchor="s")

        # Stage label
        self.stage_label = View.StageLabel(self.control_button_frame)
        self.stage_label.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        View.GraySeparator(self.control_button_frame).pack(side=tkinter.RIGHT, anchor="e", pady="4", fill="y", padx="4")

        self.auto_check_value = tkinter.StringVar()
        self.auto_check = View.AutoCheck(self.control_button_frame, variable=self.auto_check_value,
                                         command=self.auto_refresh)
        self.auto_check.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.refresh_button = View.RefreshButton(self.control_button_frame, command=self.refresh)
        self.refresh_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.upload_button = View.UploadButton(self.control_button_frame, command=self.upload)
        self.upload_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        View.GraySeparator(self.control_button_frame).pack(side=tkinter.RIGHT, anchor="e", pady="4", fill="y", padx="4")

        self.stop_button = View.StopButton(self.control_button_frame)
        self.stop_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.stop_button.configure(command=self.stop)
        self.play_button = View.PlayButton(self.control_button_frame)
        self.play_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.play_button.configure(command=self.play)

        self.open_file_button = View.OpenFileButton(self.control_button_frame)
        self.open_file_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.open_file_button.configure(command=self.open_file)

        self.save_file_button = View.SaveFileButton(self.control_button_frame)
        self.save_file_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.save_file_button.configure(command=self.save_file)

        self.glimpse_file_button = View.GlimpseFileButton(self.control_button_frame)
        self.glimpse_file_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.glimpse_file_button.configure(command=self.glimpse_file)

        # Tree Frame
        self.tree_frame = View.TreeFrame(self.master_frame)
        self.tree_frame.pack(expand=True, fill=tkinter.BOTH, after=self.control_frame)

        # Display Tree
        self._top_columns_d = ("Name", "Address", "Field", "Property")
        self._top_columns_width_d = ("125", "100", "100", "75")
        self.display_tree_frame = View.DisplayTreeFrame(self.tree_frame)
        self.display_tree_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        self.display_tree = View.DisplayTree(self.display_tree_frame, self._top_columns_d, self._top_columns_width_d)
        self.display_tree.bind("<Double-1>", self._display_tree_double_click)
        self.display_tree.pack(expand=True, fill=tkinter.BOTH)

        # Modify Tree
        self._top_columns_m = ("Name", "Address | Field", "Property", "Write Value", "Read Value")
        self._top_columns_width_m = ("125", "100", "50", "62", "62")  # name, address, prop, value
        self.modify_tree_frame = View.ModifyTreeFrame(self.tree_frame)
        self.modify_tree_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)
        self.modify_tree = View.ModifyTree(self.modify_tree_frame, self._top_columns_m, self._top_columns_width_m)
        self.modify_tree.bind("<Delete>", self._modify_tree_delete_keyboard)
        self.modify_tree.bind("<Button-1>", self._modify_tree_popup_message)
        self.modify_tree.pack(expand=True, fill=tkinter.BOTH)

        # Debug Frame
        self.debug_frame = View.DebugFrame(self.master_frame)
        self.debug_frame.pack(expand=True, fill=tkinter.BOTH, after=self.tree_frame)

        # Commander Frame
        self.commander_frame = View.CommanderFrame(self.debug_frame)
        self.commander_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        self._commander_prefix = "JGKit: "
        self.commander = View.Commander(self.commander_frame)
        self.commander.bind("<Key>", self._commander_keyboard)
        self.commander.bind("<Return>", self._commander_entry)
        self.commander.pack(expand=True, fill=tkinter.BOTH)
        self.commander.insert(tkinter.INSERT, self._commander_prefix)
        self.commander_start = self.commander.index(tkinter.INSERT)
        logging.debug("Initialize position: %s" % (self.commander_start,))
        self.commander.mark_set(tkinter.INSERT, self.commander_start)

        # Log Frame
        # self.log_frame = View.LogFrame(self.debug_frame)
        # self.log_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)
        # self.log = View.Log(self.log_frame)
        # self.log.pack(expand=True, fill=tkinter.BOTH)

        # Memory Frame
        self.mem_chunk_dir = {}

        self.mem_frame = View.MemFrame(self.debug_frame)
        self.mem_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)
        self.mem_control_frame = View.MemControlFrame(self.mem_frame)
        self.mem_control_frame.pack(fill=tkinter.X, side=tkinter.TOP, padx=10, pady=10)
        # Button
        self.mem_control_add_button = View.AddFileButton(self.mem_control_frame)
        self.mem_control_add_button.pack(side=tkinter.LEFT, anchor="e", padx="4")
        self.mem_control_add_button.configure(command=self.mem_add_button_callback)

        self.mem_control_sub_button = View.SubFileButton(self.mem_control_frame)
        self.mem_control_sub_button.pack(side=tkinter.LEFT, anchor="e", padx="4")
        self.mem_control_sub_button.configure(command=self.mem_sub_button_callback)

        self.mem_control_load_button = View.LoadFileButton(self.mem_control_frame)
        self.mem_control_load_button.pack(side=tkinter.LEFT, anchor="e", padx="4")
        self.mem_control_load_button.configure(command=self.mem_import_button_callback)

        self.mem_control_store_button = View.StoreFileButton(self.mem_control_frame)
        self.mem_control_store_button.pack(side=tkinter.LEFT, anchor="e", padx="4")
        self.mem_control_store_button.configure(command=self.mem_export_button_callback)

        self.mem_control_refresh_button = View.RefreshFileButton(self.mem_control_frame)
        self.mem_control_refresh_button.pack(side=tkinter.LEFT, anchor="e", padx="4")
        self.mem_control_refresh_button.configure(command=self.mem_refresh_button_callback)

        self.memory_refresh_time = 500
        self.memory_refresh_handler = None
        self.memory = View.MemNoteBook(self.mem_frame)
        self.memory.pack(expand=True, fill=tkinter.BOTH)
        self.memory.bind("<Double-Button-1>", self._mem_sheet_double_click)
        self.memory.bind("<Delete>", self._mem_sheet_delete)

        self.mem_canvas = None
        self.mem_canvas_frame = None

        # logging.getLogger().addHandler(WidgetLogger.WidgetLogger(self.log))

        # Refersh parameter
        self.refersh_time = 100  # 100ms
        self._refresh_timer_handler = None

        # Display tree value
        self.address_base_pointer = 0
        self.current_address = 0
        self.cur_iid = None
        self.level = 0
        self.parent = ""
        self._find_indexs_pattern = re.compile(r"\[(?P<Number>[0-9]+)\]")
        self._locate_indexs_pattern = re.compile(r"<ARRAY_INDEX>")
        self._address_field_pattern = re.compile(
            r"(?P<Address>0x[0-9a-fA-F]+)[\s\|]*(?P<Field0>[0-9]*):*(?P<Field1>[0-9]*)")
        self._mid_value = []
        self._mid_value_pointer = self._mid_value

        # Modify parameter
        self.tree_root = None
        self._popup_entry_handler = None

        # Tree Traverse
        self._traverse_list = []
        self._glimpse_list = []

        # Image
        self._image_tag = (
            ImageTk.PhotoImage(Image.open("./.image/.treeview/device.png").resize((16, 16), Image.ANTIALIAS)),
            ImageTk.PhotoImage(Image.open("./.image/.treeview/register.png").resize((16, 16), Image.ANTIALIAS)),
            ImageTk.PhotoImage(Image.open("./.image/.treeview/field.png").resize((16, 16), Image.ANTIALIAS))
        )

        # SWD handler
        self.swd_handler = None

        self._swd_connected_time = 100
        self._swd_connected_handler = None

        self.display_device_render(self.device_generator())

    def device_generator(self):
        memory_header = [{"Key": "Address Start", "Level": (1,), "Priority": ("M",)},
                         {"Key": "Module", "Level": (1,), "Priority": ("L",)},
                         {"Key": "Class", "Level": (1,), "Priority": ("L",)}]
        memory_reheader = ("Address", "Name", "Class")
        memory_sheets = self._module_sheets
        memory_e2j = Excel2Dict.E2D(excel=self._excel, header=memory_header, sheets=memory_sheets,
                                    reheader=memory_reheader)
        memory_e2j.convert()

        memory_e2j_list = [i for j in memory_e2j for i in j["Level"] if i["Class"]]
        for i in memory_e2j_list:
            i["Address"] = i["Address"].replace("_", "")

        header = [{"Key": "Sub-Addr\n(Hex)", "Level": (1,), "Priority": ("H",)},
                  {"Key": "Start\nBit", "Level": (2,), "Priority": ("M",)},
                  {"Key": "End\nBit", "Level": (2,), "Priority": ("M",)},
                  {"Key": "R/W\nProperty", "Level": (2,), "Priority": ("M",)},
                  {"Key": "Register\nName", "Level": (1, 2), "Priority": ("M", "M")},
                  {"Key": "Register Description", "Level": (1, 2), "Priority": ("L", "L")}
                  ]

        reheader = ("Address", "Start", "End", "Property", "Name", "Description")

        e2j = Excel2Dict.E2D(excel=self._excel, header=header, reheader=reheader)
        e2j.convert()
        venus_device = []
        for dev in memory_e2j_list:
            for cla in e2j:
                if dev["Class"] == cla["Sheet_Name"]:
                    dev["Level"] = cla["Level"]
                    del dev["Class"]
                    venus_device.append(dev)
                    break

        def _sort_func(elem):
            return int(elem["Address"], base=16)

        venus_device.sort(key=_sort_func, reverse=False)

        return venus_device

    def modify_tree_render(self, mid_value, level):
        self.level = level
        self.tree_root = mid_value
        self.parent = ""
        self._sub_modify_tree_render(self.tree_root)
        self.parent = ""
        self.level = 0

    def _sub_modify_tree_render(self, root):
        for i in root:
            value = "NA"
            if self.level != 0:
                value = str(hex(self.read32_plus(self.parse_address(i["Address"]))))
                # Trigger error return False
                if not value:
                    return
            self._cur_iid = self.modify_tree.insert(self.parent, "end", iid=None, text=i["Name"],
                                                    image=self._image_tag[self.level],
                                                    values=(i["Address"], i["Property"], "NA", value),
                                                    tags=(self.level, i["Description"]))
            if i["Level"]:
                self.level += 1
                self.parent = self._cur_iid
                self._sub_modify_tree_render(i["Level"])
        self.parent = self.modify_tree.parent(self.parent)
        self.level -= 1

    def parse_address(self, address):
        # r"(?P<Address>0x[0-9a-fA-F]+)[\s\|]*(?P<Field0>[0-9]*):*(?P<Field1>[0-9]*)"
        rslt = self._address_field_pattern.match(address)
        addr = rslt.group("Address")
        field0 = rslt.group("Field0")
        field1 = rslt.group("Field1")
        logging.debug("The parse result: %s -> %s:%s" % (addr, field0, field1))
        return addr, field0, field1

    def display_device_render(self, root):
        for item in root:
            # Initialize
            self.address_base_pointer = int(item["Address"], base=16)
            self.parent = ""
            self.level = 0
            self.cur_iid = self.display_tree.insert(self.parent, "end", iid=None, text=item["Name"],
                                                    image=self._image_tag[self.level],
                                                    values=(hex(self.address_base_pointer), "", ""),
                                                    tags=(self.level, "", self.address_base_pointer))

            self.parent = self.cur_iid
            self._display_register_render(item["Level"])

    def _display_register_render(self, root):
        for item in root:
            self.level = 1
            try:
                self.current_address = self.address_base_pointer + int(item["Address"], base=16)
            except TypeError:
                self.current_address = self.address_base_pointer + int(item["Address"])
            if not self._expand(item):
                self.cur_iid = self.display_tree.insert(self.parent, "end", iid=None, text=item["Name"],
                                                        image=self._image_tag[self.level],
                                                        values=(hex(self.current_address), "", ""),
                                                        tags=(self.level, item["Description"], self.current_address))

                self.parent = self.cur_iid
                self._display_field_render(item["Level"])

                # Get the parent of current item
                self.parent = self.display_tree.parent(self.parent)

    def _display_field_render(self, root):
        for item in root:
            self.level = 2
            self.cur_iid = self.display_tree.insert(self.parent, "end", iid=None, text=item["Name"],
                                                    image=self._image_tag[self.level], values=(
                    "", "%d:%d" % (int(item['Start']), int(item['End'])), item["Property"]),
                                                    tags=(self.level, item["Description"], self.current_address))

    def _expand(self, item):
        rslt = self._find_indexs_pattern.search(item["Name"])

        if rslt:
            for num in range(int(rslt.group("Number"))):
                self.level = 1
                name = item["Name"][0: rslt.span()[0]] + str(num)
                self.cur_iid = self.display_tree.insert(self.parent, "end", iid=None, text=name,
                                                        image=self._image_tag[self.level],
                                                        values=(hex(self.current_address), "", ""),
                                                        tags=(self.level, item["Description"], self.current_address))
                self.parent = self.cur_iid
                self._subexpand(item["Level"], num)
                self.current_address += 4
                self.parent = self.display_tree.parent(self.parent)
            return True

        return False

    def _subexpand(self, item, num):
        for i in item:
            self.level = 2
            name = self._locate_indexs_pattern.sub(str(num), i["Name"])
            self.cur_iid = self.display_tree.insert(self.parent, "end", iid=None, text=name,
                                                    image=self._image_tag[self.level], values=(
                    "", "%d:%d" % (int(i['Start']), int(i['End'])), i["Property"]),
                                                    tags=(self.level, i["Description"], self.current_address))

    def connected(self):
        self.stage_label.enable()
        self.auto_check.enable()
        self.refresh_button.enable()
        self.stop_button.enable()
        self.play_button.disable()
        self.open_file_button.enable()
        self.save_file_button.enable()
        self.upload_button.enable()
        self.glimpse_file_button.enable()
        self.mem_control_add_button.enable()
        self.mem_control_sub_button.enable()
        self.mem_control_load_button.enable()
        self.mem_control_store_button.enable()
        self.mem_control_refresh_button.enable()

    def disconnected(self):
        self.stage_label.disable()
        self.auto_check.disable()
        self.refresh_button.disable()
        self.stop_button.disable()
        self.play_button.enable()
        self.open_file_button.disable()
        self.save_file_button.disable()
        self.upload_button.disable()
        self.glimpse_file_button.disable()
        self.mem_control_add_button.disable()
        self.mem_control_sub_button.disable()
        self.mem_control_load_button.disable()
        self.mem_control_store_button.disable()
        self.mem_control_refresh_button.disable()

    def control_button_stage_machine(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Disconnected stage
            if self.control_stage_machine == "disconnected":
                if func.__name__ == "play":
                    if func(self, *args, **kwargs):
                        logging.info("[Connected]")
                        self.connected()
                        self.control_stage_machine = "connected"
                        return True
                    else:
                        return False

                else:
                    return False

            # Connected stage
            elif self.control_stage_machine == "connected":
                if func.__name__ == "stop":
                    if func(self, *args, **kwargs):
                        logging.info("[Disconnected]")
                        self.disconnected()
                        self.control_stage_machine = "disconnected"
                        return True
                    else:
                        return False

                elif func.__name__ == "refresh" or func.__name__ == "mem_refresh":
                    if func(self, *args, **kwargs):
                        return True
                    else:
                        return False

                elif func.__name__ == "_display_tree_double_click" or "open_file" or "save_file":
                    return func(self, *args, **kwargs)

                else:
                    return False

            else:
                logging.error("Undefine stage machine parameter")

        return wrapper

    @control_button_stage_machine
    def refresh(self):
        # Get item tree and read again
        # If trigger an error when read some address, then return False
        logging.debug("<Refresh>")
        self._sub_refresh()
        return True

    @control_button_stage_machine
    def mem_refresh(self):
        chunk = self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]
        logging.debug("<Mem><Refresh> Address -> %s - %s" % (hex(chunk["head_address"]), hex(chunk["tail_address"])))
        length = chunk["tail_address"] - chunk["head_address"]
        mem_list = self.swd_handler.read_mem(chunk["head_address"], length)

        if len(mem_list) != len(chunk["value"]):
            logging.error("<MEM><Refresh> Prefetch length not equal current length")

            return False

        diff_list = []

        for i in range(len(mem_list)):
            if mem_list[i] != chunk["value"][i]:
                diff_list.append(i)

        if diff_list:
            for i in diff_list:
                address = str(chunk["head_address"] + 4*i)
                chunk["entry"][address].delete(0, tkinter.END)
                chunk["entry"][address].insert(0, hex(mem_list[i]))

        return True

    @control_button_stage_machine
    def upload(self):
        logging.debug("<Upload>")
        self._sub_upload()
        return True

    def _sub_upload(self, p=None):
        items = self.modify_tree.get_children(p)
        if not items:
            return
        for item in items:
            dct = self.modify_tree.item(item)
            if dct["tags"][0] != 0:
                if dct["values"][2] != "NA":
                    self.write32_plus(self.parse_address(dct["values"][0]), dct["values"][2])
                    value = str(hex(self.read32_plus(self.parse_address(dct["values"][0]))))
                    values = dct["values"]
                    values[-1] = value
                    # Reload
                    self.modify_tree.item(item, values=values)
            self._sub_upload(item)

    def _sub_refresh(self, p=None):
        items = self.modify_tree.get_children(p)
        if not items:
            return
        for item in items:
            dct = self.modify_tree.item(item)
            if dct["tags"][0] != 0:
                value = str(hex(self.read32_plus(self.parse_address(dct["values"][0]))))
                values = dct["values"]
                values[-1] = value
                # Reload
                self.modify_tree.item(item, values=values)
            self._sub_refresh(item)

    @control_button_stage_machine
    def play(self):
        # Connect to target
        try:
            self.swd_handler = SWDJlink.Link()
        except:
            self.swd_handler = None
            return False
        self._swd_connected_handler = self._master.after(self._swd_connected_time, self._swd_connected)
        return True

    @control_button_stage_machine
    def stop(self):
        # Disconnect to target
        self._master.after_cancel(self._swd_connected_handler)
        del self.swd_handler
        return True

    @control_button_stage_machine
    def open_file(self):
        addr = filedialog.askopenfilename(title="Load File", filetypes=[("register configuration",
                                                                         "*.regcfg")], initialdir=r".")

        if not addr:
            return

        with open(addr, mode="r", encoding="utf8") as f:
            self._traverse_list = json.load(fp=f)

        self._modify_tree_insert_file_items(self._traverse_list)

    @control_button_stage_machine
    def save_file(self):
        addr = filedialog.asksaveasfilename(title="Save File", initialdir=r".",
                                            filetypes=[("register configuration", "*.regcfg")],
                                            defaultextension=[("register configuration", "*.regcfg")])
        if not addr:
            return

        self._traverse_list = []
        self._modify_tree_get_all_items(self._traverse_list)

        with open(addr, mode="w", encoding="utf8") as f:
            json.dump(self._traverse_list, fp=f)

    @control_button_stage_machine
    def glimpse_file(self):
        addr = filedialog.asksaveasfilename(title="Glimpse File", initialdir=r".",
                                            filetypes=[("glimpse configuration", "*.glicfg")],
                                            defaultextension=[("glimpse configuration", "*.glicfg")])
        if not addr:
            return

        self._glimpse_list = []
        self._modify_tree_glimpse_all_items(self._glimpse_list)

        with open(addr, mode="w", encoding="utf8") as f:
            json.dump(self._glimpse_list, fp=f)

    def auto_refresh(self):
        # Depending the check button on or off
        # Register a timer into GUI event loop
        # Or unregister a timer
        value = self.auto_check_value.get()
        if value == "auto":
            self.open_refresh_timer()
        elif value == "bluntness":
            self.close_refresh_timer()
        else:
            logging.error("Undefine value")

    def open_refresh_timer(self):
        self._refresh_timer_handler = self.auto_check.after(self.refersh_time, self.refresh_inspection)

    def close_refresh_timer(self):
        self.auto_check.after_cancel(self._refresh_timer_handler)

    def refresh_inspection(self):
        # refresh
        logging.info("[Event] Refresh callback")
        if self.refresh():
            self._refresh_timer_handler = self.auto_check.after(self.refersh_time, self.refresh_inspection)
        else:
            self.close_refresh_timer()
            self.auto_check.deselect()

    def _item_recursive(self, items):
        if not items:
            return

        for item in items:
            info = self.display_tree.item(item)
            if not info["values"][0]:
                address = "%s | %s" % (hex(info["tags"][2]), info["values"][1])
            else:
                address = hex(info["tags"][2])

            if not info["values"][-1]:
                prop = "NA"
            else:
                prop = info["values"][-1]

            name = info["text"]
            dscp = info["tags"][1]

            pointer_parent = self._mid_value_pointer
            cur_pointer = {"Name": name, "Address": address, "Property": prop, "Description": dscp, "Level": []}
            self._mid_value_pointer.append(cur_pointer)
            # Reserve the parent pointer
            self._mid_value_pointer = cur_pointer["Level"]
            # Recursive the chlidren tree
            self._item_recursive(self.display_tree.get_children(item))
            # Restore the pointer
            self._mid_value_pointer = pointer_parent

    def _get_mask(self, lengh):
        mask = BitArray(bin(0x1 << lengh))
        mask.invert()
        mask = mask[1:]
        return mask.uint

    def _swd_connected(self):
        if self.swd_handler.is_connected():
            self._swd_connected_handler = self._master.after(self._swd_connected_time, self._swd_connected)
        else:
            self.stop()

    def write32_plus(self, tpl, data):
        if tpl[1] or tpl[2]:
            # Read address data
            mem32 = self.swd_handler.read32(int(tpl[0], base=16))
            if mem32 == -1:
                return False
            # Data & mask
            mask = self._get_mask(int(tpl[2]) - int(tpl[1]) + 1)
            logging.debug("Generate mask: %s", hex(mask))
            # If input such as 1600, treat this value as dec
            # Else jump to the exception, and treat it as hex
            try:
                data = int(data) & mask
            except ValueError:
                data = int(data, base=16) & mask
            # Mem32 clean corresponding memory field
            mem32 &= ~(mask << int(tpl[1]))
            # Mem32 | Data << base
            mem32 |= data << int(tpl[1])
            # Write the word into memory
            logging.debug("Write to the memory: %s --> %d" % (tpl[0], mem32))
            self.swd_handler.write32(int(tpl[0], base=16), mem32)
        else:
            try:
                data = int(data)
            except ValueError:
                data = int(data, base=16)

            self.swd_handler.write32(int(tpl[0], base=16), data)

    def read32_plus(self, tpl):
        mem32 = self.swd_handler.read32(int(tpl[0], base=16))
        if mem32 == -1:
            return False
        logging.debug("Read the whole register: %s" % (hex(mem32)))
        if tpl[1] or tpl[2]:
            # Have trouble
            return (mem32 >> int(tpl[1])) & self._get_mask(int(tpl[2]) - int(tpl[1]) + 1)
        return mem32

    # *************************************************************************** Event
    @control_button_stage_machine
    def _display_tree_double_click(self, event):
        logging.info("<Double Click>")
        # Get the double click information
        item = self.display_tree.focus()
        if not item:
            return "break"

        # Empty middle transmit value
        self._mid_value = []
        self._mid_value_pointer = self._mid_value
        self._item_recursive((item,))

        self.modify_tree_render(self._mid_value, self.display_tree.item(item)["tags"][0])

        return "break"

    # When any keyboard click, jump to the end of the character stream end
    def _commander_keyboard(self, event):
        # Commander position greater than insert position
        if self.commander.compare(self.commander_start, ">=", tkinter.INSERT):
            logging.debug("Change current position to the end of commander")
            self.commander.mark_set("insert", tkinter.END)
            if event.keysym == "BackSpace":
                return "break"
        else:
            logging.debug("Insert position: %s" % (self.commander.index(tkinter.INSERT),))

    def _commander_entry(self, event):
        logging.info("Get text: %s" % (self.commander.get(self.commander_start, tkinter.END),))
        self.commander.insert(tkinter.END, "\n%s" % (self._commander_prefix,))
        self.commander_start = self.commander.index(tkinter.INSERT)
        logging.info("The new position: %s" % (self.commander_start,))
        return "break"

    def _modify_tree_delete_keyboard(self, event):
        logging.info("<Delete Click>")
        item = self.modify_tree.focus()
        if item:
            self.modify_tree.delete(item)
        return "break"

    def _modify_tree_popup_message(self, event):
        logging.info("<One Click>")
        # Destroy popup entry
        if self._popup_entry_handler:
            self._popup_entry_handler.destroy()
            self._popup_entry_handler = None

        # Clear message
        self.control_description_message.delete('1.0', tkinter.END)

        # where row and column was clicked on
        rowid = self.modify_tree.identify_row(event.y)
        column = self.modify_tree.identify_column(event.x)
        if not rowid:
            return

        self.control_description_message.insert(tkinter.END, self.modify_tree.item(rowid, "tags")[1])
        item = self.modify_tree.item(rowid)
        logging.debug(item)

        if column != "#3":
            return
        tags = item["tags"]
        logging.debug("Click the row:%s, column:%s, tags:%s" % (rowid, column, str(tags)))
        if tags[0] == 0:
            return

        x, y, width, height = self.modify_tree.bbox(rowid, column)
        logging.debug("The location information --> x:%d, y:%d, width:%d, height:%d" % (x, y, width, height))

        value = list(self.modify_tree.item(rowid, "values"))

        if value[-2] == "NA":
            self._popup_entry_handler = View.EntryPopup(self.modify_tree, "")
        else:
            self._popup_entry_handler = View.EntryPopup(self.modify_tree, value[-2])

        # Get the total width
        total_width = self.modify_tree.column("#0")["width"]
        for i in self._top_columns_m[1:]:
            total_width += self.modify_tree.column(i)["width"]

        self._popup_entry_handler.place(x=x, y=y + height // 2, anchor=tkinter.W,
                                        relwidth=self.modify_tree.column("Write Value")["width"] / total_width)

        def _popup_entry_return(event):
            nonlocal value, rowid
            tpl = self.parse_address(value[0])

            write_data = self._popup_entry_handler.get()
            self.write32_plus(tpl, write_data)
            value[-1] = hex(self.read32_plus(tpl))
            value[-2] = write_data
            self.modify_tree.item(rowid, values=value)
            self._popup_entry_handler.destroy()
            self._popup_entry_handler = None

        self._popup_entry_handler.bind("<Return>", _popup_entry_return)

    def _modify_tree_get_all_items(self, traverse_list, item=None):
        tpl = None
        values = None

        if item:
            values = self.modify_tree.item(item)
            values.update({"next": []})
            traverse_list.append(values)

            tpl = self.modify_tree.get_children(item)
        else:
            tpl = self.modify_tree.get_children()

        if not tpl:
            return

        for i in tpl:
            if item:
                self._modify_tree_get_all_items(values["next"], i)
            else:
                self._modify_tree_get_all_items(traverse_list, i)

        return

    def _modify_tree_glimpse_all_items(self, traverse_list, item=None):
        tpl = None
        store_value = None

        if item:
            values = self.modify_tree.item(item)
            store_value = {"Name": values["text"], "Address": values["values"][0], "Values": "NA"}

            # Is a sheet
            if values["tags"][0] == 0:
                store_value.update({"next": []})
            else:
                # Is a device
                store_value["Values"] = hex(self.swd_handler.read32(int(store_value["Address"], base=16)))

            traverse_list.append(store_value)

            if values["tags"][0] == 1:
                return

            tpl = self.modify_tree.get_children(item)

        else:
            tpl = self.modify_tree.get_children()

        if not tpl:
            return

        for i in tpl:
            if item:
                self._modify_tree_glimpse_all_items(store_value["next"], i)
            else:
                self._modify_tree_glimpse_all_items(traverse_list, i)

        return

    def _modify_tree_insert_file_items(self, list, parent=""):
        for i in list:
            if i["values"][2] != "NA":
                self.write32_plus(self.parse_address(i["values"][0]), i["values"][2])
                # i["values"][-1] = hex(self.read32_plus(self.parse_address(i["values"][0])))

            iid = self.modify_tree.insert(parent=parent, index='end', image=i["image"], text=i["text"], open=i["open"],
                                          values=i["values"], tags=i["tags"])

            if i["next"]:
                self._modify_tree_insert_file_items(i["next"], iid)
            else:
                continue
        self.refresh()

    def _mem_sheet_double_click(self, event):
        logging.debug("[Event] Double Click")
        try:
            tab_id = self.memory.index('@%d,%d' % (event.x, event.y))
        except:
            self._mem_popup_address_entry()
            return

        label_x = int(self.memory.winfo_x())

        # 估计标签的宽度和位置
        for i in range(tab_id):
            tab_text = self.memory.tab(i, 'text')
            label_width = len(tab_text) * (int(View.UI_FONT_SIZE_PIXEL) - 5) - 3  # 假设每个字符大约7像素宽
            label_x += label_width

        tab_text = self.memory.tab(tab_id, 'text')
        label_width = len(tab_text) * (int(View.UI_FONT_SIZE_PIXEL) - 5) - 3

        # 创建一个Entry小部件来编辑工作表名字
        entry = ttk.Entry(self.memory)
        entry.insert(0, tab_text)
        entry.bind("<Return>", lambda e: self.__mem_sheet_finish_edit_name(tab_id, entry))
        entry.bind("<FocusOut>", lambda e: self.__mem_sheet_finish_edit_name(tab_id, entry))
        entry.place(x=str(label_x), y=0, width=label_width, height=30)
        entry.focus_set()

    def _mem_sheet_delete(self, event):
        current_tab = self.memory.select()
        if current_tab:
            self.memory.forget(current_tab)

    def __mem_sheet_finish_edit_name(self, tab_id, entry):
        new_text = entry.get()
        self.memory.tab(tab_id, text=new_text)
        entry.destroy()

    def _mem_create_editable_excel(self, address):
        parent = ttk.Frame(self.memory)
        self.memory.add(parent, text=hex(address))
        self.mem_chunk_dir[parent] = {"address": address, "head_address": address,
                                      "tail_address": address + View.UI_MEM_ELEMENTS_ITEM_VERTICAL_MAX * View.UI_MEM_ELEMENTS_ITEM_HORIZON_MAX * 4}

        # Create header memory
        self.mem_header_frame = View.MemHeaderFrame(parent)
        self.mem_header_frame.pack(fill=tkinter.X, side=tkinter.TOP)
        self.mem_chunk_dir[parent]["header_frame"] = self.mem_header_frame

        for col in range(View.UI_MEM_ELEMENTS_ITEM_HORIZON_MAX + 1):
            if col == 0:
                label = View.MemHeaderLab(self.mem_header_frame, text="Address")
                label.grid(row=0, column=col, sticky="nsew")
                continue

            label = View.MemHeaderLab(self.mem_header_frame, text=f"{(col - 1) * 4}-{col * 4 - 1}")
            label.grid(row=0, column=col, sticky="nsew")

        # 创建Canvas和滚动条
        self.mem_canvas = tkinter.Canvas(parent, bg=View.DARCULA_DEFAULT_BG)
        self.mem_canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.mem_chunk_dir[parent]["canvas"] = self.mem_canvas

        scrollbar_y = tkinter.Scrollbar(parent, orient="vertical", command=self.mem_canvas.yview)
        # scrollbar_y.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        self.mem_canvas.configure(yscrollcommand=scrollbar_y.set)
        self.mem_canvas.bind('<Configure>',
                             lambda e: self.mem_canvas.configure(scrollregion=self.mem_canvas.bbox('all')))

        def __on_mousewheel_callback(event):
            # logging.debug("[Event]<Mousewheel> %d" % (event.delta,))
            self.mem_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
            logging.debug("[Event]<Mousewheel> Height from %f - %f" %
                          (self.mem_canvas.yview()[0], self.mem_canvas.yview()[1]))

            # logging.debug("[Event]<Mousewheel> Canvas height: %s" % (self.mem_canvas.winfo_height(), ))

            if self.mem_canvas.yview()[1] == 1.0:
                offset = self.mem_canvas.winfo_height() // View.MemLabel.DEFAULT_SHEET_LABEL_HEIGHT
                address_offset = offset * View.UI_MEM_ELEMENTS_ITEM_HORIZON_MAX * 4 # Get whole visiable windows address diff

                # Calculate the head address depending the offset address
                head_address = self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]["tail_address"] - address_offset
                # The tail address depending the default length increase
                self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]["tail_address"] \
                    += (View.UI_MEM_ELEMENTS_ITEM_VERTICAL_MAX * View.UI_MEM_ELEMENTS_ITEM_HORIZON_MAX * 4 - address_offset)
                self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]["head_address"] = head_address

                logging.debug("[Event]<Mousewheel> To button address -> %s" %
                              (hex(self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]["head_address"])))

                # Load next chunk
                self._mem_load_next_chunk(None)

                # Move scroll
                self.mem_canvas.yview_moveto(0.0)
            elif self.mem_canvas.yview()[0] == 0.0:
                offset = self.mem_canvas.winfo_height() // View.MemLabel.DEFAULT_SHEET_LABEL_HEIGHT
                address_offset = offset * View.UI_MEM_ELEMENTS_ITEM_HORIZON_MAX * 4

                tail_address = self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())][
                                   "head_address"] + address_offset

                self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]["head_address"] \
                    -= (View.UI_MEM_ELEMENTS_ITEM_VERTICAL_MAX * View.UI_MEM_ELEMENTS_ITEM_HORIZON_MAX * 4 - address_offset)

                self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]["tail_address"] = tail_address

                # if self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]["head_address"] < 0:
                #     mem_diff = self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]["head_address"] - 0
                #     self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]["head_address"] = 0
                #
                #     self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]["tail_address"] += mem_diff

                logging.debug("[Event]<Mousewheel> To top address -> %s" %
                              (hex(self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]["head_address"])))

                # Load next chunk
                self._mem_load_next_chunk(None)

                # Move scroll
                self.mem_canvas.yview_moveto(1.0)

        def __bound_mousewheel(event):
            self.mem_canvas.bind_all("<MouseWheel>", __on_mousewheel_callback)

        def __unbound_mousewheel(event):
            self.mem_canvas.unbind_all("<MouseWheel>")

        self.mem_canvas.bind('<Enter>', __bound_mousewheel)
        self.mem_canvas.bind('<Leave>', __unbound_mousewheel)

        # 在Canvas内创建一个Frame来放置表格
        self.mem_canvas_frame = ttk.Frame(self.mem_canvas)
        self.mem_canvas.create_window((0, 0), window=self.mem_canvas_frame, anchor="nw")

        self.mem_chunk_dir[parent]["canvas_frame"] = self.mem_canvas_frame

        start = time.time()
        self._mem_load_next_chunk(parent)
        end = time.time()
        logging.debug("[TIME] Load chunk cost %f" % (end - start))

    def _mem_load_next_chunk(self, parent):
        if parent:
            chunk = self.mem_chunk_dir[parent]
        else:
            chunk = self.mem_chunk_dir[self.memory.nametowidget(self.memory.select())]
        address = chunk["head_address"]
        tail_address = chunk["tail_address"]
        length = tail_address - address
        logging.debug("Auto load next chunk from memory -> %s : %s" % (hex(address), hex(tail_address)))
        chunk["entry"] = {}
        chunk["value"] = []
        self.memory_refresh_handler = self.memory.after(self.memory_refresh_time, self._mem_auto_refresh)

        self.mem_header_frame = chunk["header_frame"]
        self.mem_canvas_frame = chunk["canvas_frame"]
        self.mem_canvas = chunk["canvas"]

        rows = int(length // (View.UI_MEM_ELEMENTS_ITEM_HORIZON_MAX * 4))
        cols = View.UI_MEM_ELEMENTS_ITEM_HORIZON_MAX

        start = time.time()
        chunk["value"] = self.swd_handler.read_mem(address, rows * cols)  # Get word
        end = time.time()
        logging.debug("[TIME] Read memory cost %f" % (end - start))

        for i in range(rows):
            for j in range(cols + 1):
                if j == 0:
                    label = View.MemLabel(self.mem_canvas_frame, text=hex(address + i * cols * 4))
                    label.grid(row=i, column=j, sticky="nsew")
                else:
                    def on_entry_change(name, index, mode):
                        entry = chunk["entry"][name]
                        entry.config(fg="red")

                    entry_var = tkinter.StringVar()
                    entry = View.MemUnit(self.mem_canvas_frame, textvariable=entry_var)
                    chunk["entry"][entry_var._name] = entry
                    try:
                        value = hex(chunk["value"][i * cols + j - 1])
                    except TypeError:
                        value = "?"

                    entry.insert(0, value)
                    entry_var.trace("w", on_entry_change)
                    entry.grid(row=i, column=j, sticky="nsew")
                    entry.bind("<Return>", lambda event, address=address + (i * cols + j - 1) * 4: self.
                               __mem_unit_entry_return_callback(event, address))
                    self.mem_canvas_frame.grid_columnconfigure(j, weight=1)

        # 设置行权重
        for i in range(rows):
            self.mem_canvas_frame.grid_rowconfigure(i, weight=1)

    def _mem_popup_address_entry(self):
        """弹出一个窗口，窗口内包含标签 'Address' 和一个输入框。"""
        top = View.TopLevelBase(self._master)  # 创建新的窗口
        top.title("Enter Address")

        # 添加 'Address' 标签和输入框
        address_label = ttk.Label(top, text="Address:")
        address_label.grid(row=0, column=0, padx=10, pady=5, sticky=tkinter.W)

        address_entry = ttk.Entry(top, width=30)
        address_entry.grid(row=0, column=1, padx=10, pady=5)
        address_entry.focus_set()

        def confirm_and_close():
            """确认并关闭窗口的函数"""
            address = address_entry.get()  # 获取输入框中的地址

            try:
                address = int(address)
            except ValueError:
                address = int(address, base=16)

            self._mem_create_editable_excel(address)
            top.destroy()  # 关闭窗口

        # 添加确认按钮
        confirm_btn = ttk.Button(top, text="Confirm", command=confirm_and_close)
        confirm_btn.grid(row=2, columnspan=2, pady=10)

    def __mem_unit_entry_return_callback(self, event, address):
        entry = event.widget
        value = entry.get()
        try:
            value = int(value)
        except ValueError:
            value = int(value, base=16)

        logging.debug("[Event]<return> Address %s -> Value %d" % (hex(address), value))
        self.swd_handler.write32(address, value)
        new_value = int(self.swd_handler.read32(address))

        entry.delete(0, tkinter.END)
        entry.insert(0, hex(new_value))

    @control_button_stage_machine
    def mem_add_button_callback(self):
        self._mem_popup_address_entry()

    @control_button_stage_machine
    def mem_sub_button_callback(self):
        self._mem_sheet_delete(None)

    @control_button_stage_machine
    def mem_import_button_callback(self):
        """弹出一个窗口，窗口内包含标签 'Address' 和一个输入框。"""
        top = View.TopLevelBase(self._master)  # 创建新的窗口
        top.title("Import Memory")

        # 添加 'Address' 标签和输入框
        address_label = ttk.Label(top, text="Address:")
        address_label.grid(row=0, column=0, padx=10, pady=5, sticky=tkinter.W)

        address_entry = ttk.Entry(top, width=20)
        address_entry.grid(row=0, column=1, padx=10, pady=5)

        import_file = ""

        # 添加 'Length' 标签和输入框
        file_label = ttk.Label(top, text="File")
        file_label.grid(row=0, column=2, padx=10, pady=5, sticky=tkinter.W)

        file_entry = ttk.Entry(top, width=20)
        file_entry.grid(row=0, column=3, padx=10, pady=5)

        def browse_button_callback():
            nonlocal import_file
            addr = filedialog.askopenfilename(title="Import File", filetypes=[("Import raw file", "*.raw")],
                                              initialdir=r".")
            file_entry.delete(0, tkinter.END)
            file_entry.insert(0, addr)
            with open(addr, mode="r", encoding="utf-8") as f:
                import_file = f.read()

        file_button = tkinter.Button(top, text="Browse...", command=browse_button_callback)
        file_button.grid(row=0, column=4, padx=10, pady=5)

        def confirm_and_close():
            nonlocal import_file
            """确认并关闭窗口的函数"""
            address = address_entry.get()  # 获取输入框中的地址

            try:
                address = int(address)
            except ValueError:
                address = int(address, base=16)

            file = import_file.replace("\n", "").split()
            file = map(lambda x: int(x, base=16), file)
            self.swd_handler.write_mem(address, list(file))

            top.destroy()  # 关闭窗口

        # 添加确认按钮
        confirm_btn = ttk.Button(top, text="Confirm", command=confirm_and_close)
        confirm_btn.grid(row=1, columnspan=2, pady=10)

    @control_button_stage_machine
    def mem_export_button_callback(self):
        top = View.TopLevelBase(self._master)  # 创建新的窗口
        top.title("Export Memory")

        cur_tab = self.memory.nametowidget(self.memory.select())
        try:
            cur_memory = cur_tab.mem_parameter["Start"]
        except:
            cur_memory = "0x0"

        def on_entry_start(*args):
            logging.info("Entry start value change to %s" % (address_start_var.get(),))
            try:
                end_address = int(address_end_var.get())
            except ValueError:
                try:
                    end_address = int(address_end_var.get(), base=16)
                except ValueError:
                    return

            try:
                start_address = int(address_start_var.get())
            except ValueError:
                try:
                    start_address = int(address_start_var.get(), base=16)
                except ValueError:
                    return

            length_var.trace_remove("write", length_cb)
            length_var.set(str(end_address - start_address))
            length_var.trace_add("write", on_entry_length)

        def on_entry_end(*args):
            logging.info("Entry end value change to %s" % (address_end_var.get()))
            try:
                end_address = int(address_end_var.get())
            except ValueError:
                try:
                    end_address = int(address_end_var.get(), base=16)
                except ValueError:
                    return

            try:
                start_address = int(address_start_var.get())
            except ValueError:
                try:
                    start_address = int(address_start_var.get(), base=16)
                except ValueError:
                    return

            try:
                length_var.trace_remove("write", length_cb)
            except:
                pass
            length_var.set(str(end_address - start_address))
            length_var.trace_add("write", on_entry_length)

        def on_entry_length(*args):
            logging.info("Entry length value change to %s" % (length_var.get()))
            try:
                start_address = int(address_start_var.get())
            except ValueError:
                try:
                    start_address = int(address_start_var.get(), base=16)
                except ValueError:
                    return

            try:
                length = int(length_var.get())
            except ValueError:
                try:
                    length = int(length_var.get(), base=16)
                except ValueError:
                    return

            address_end_var.trace_remove("write", address_end_cb)
            if address_end_var.get().find("0x") != -1:
                address_end_var.set(hex(start_address + length))
            else:
                address_end_var.set(str(start_address + length))
            address_end_var.trace_add("write", on_entry_end)

        address_start_var = tkinter.StringVar()
        address_start_cb = address_start_var.trace_add("write", on_entry_start)

        address_end_var = tkinter.StringVar()
        address_end_cb = address_end_var.trace_add("write", on_entry_end)

        length_var = tkinter.StringVar()
        length_cb = length_var.trace_add("write", on_entry_length)

        address_start_label = ttk.Label(top, text="Start Address:")
        address_start_label.grid(row=0, column=0, padx=10, pady=5, sticky=tkinter.W)

        address_start_entry = ttk.Entry(top, width=20, textvariable=address_start_var)
        address_start_entry.insert(0, cur_memory)
        address_start_entry.grid(row=0, column=1, padx=10, pady=5)

        address_end_label = ttk.Label(top, text="End Address:")
        address_end_label.grid(row=0, column=2, padx=10, pady=5, sticky=tkinter.W)

        address_end_entry = ttk.Entry(top, width=20, textvariable=address_end_var)
        address_end_entry.insert(0, cur_memory)
        address_end_entry.grid(row=0, column=3, padx=10, pady=5)

        length_label = ttk.Label(top, text="Length:")
        length_label.grid(row=0, column=4, padx=10, pady=5, sticky=tkinter.W)

        length_entry = ttk.Entry(top, width=20, textvariable=length_var)
        length_entry.grid(row=0, column=5, padx=10, pady=5, sticky=tkinter.W)

        file_label = ttk.Label(top, text="File name:")
        file_label.grid(row=1, column=0, padx=10, pady=5, sticky=tkinter.W)

        file_entry = ttk.Entry(top, width=20)
        file_entry.grid(row=1, columnspan=3, padx=10, pady=5)

        export_file = ""

        def browse_button_callback():
            nonlocal export_file
            export_file = filedialog.asksaveasfilename(title="Export File", filetypes=[("Export raw file", "*.raw")],
                                                       initialdir=r".")
            file_entry.delete(0, tkinter.END)
            file_entry.insert(0, export_file)

        file_button = tkinter.Button(top, text="Browse...", command=browse_button_callback)
        file_button.grid(row=1, column=4, padx=10, pady=5)

        def confirm_and_close():
            start_address = address_start_entry.get()
            try:
                start_address = int(start_address)
            except ValueError:
                start_address = int(start_address, base=16)

            length = length_entry.get()
            try:
                length = int(length)
            except ValueError:
                length = int(length, base=16)

            out_list = self.swd_handler.read_mem(start_address, length)

            with open(export_file, mode="w", encoding="utf8") as f:
                for num, item in enumerate(out_list):
                    num += 1
                    if num % 8 == 0:
                        ret = " \r"
                    else:
                        ret = " "

                    f.write(hex(item).replace("0x", "").rjust(8, "0") + ret)

            top.destroy()

        # 添加确认按钮
        confirm_btn = ttk.Button(top, text="Confirm", command=confirm_and_close)
        confirm_btn.grid(row=2, columnspan=2, pady=10)

    def mem_refresh_button_callback(self):
        self.mem_refresh()

    def _mem_auto_refresh(self):
        self.mem_refresh()
        self.memory_refresh_handler = self.memory.after(self.memory_refresh_time, self._mem_auto_refresh)
