from PIL import Image, ImageTk
import tkinter
import logging
import re
from GuiRender import View
from GuiRender.Model import Excel2Dict
from GuiRender.Model import SWDJlink
from bitstring import BitArray
from functools import wraps


class Control:
    def __init__(self, master, **kwargs):
        # Stage machine flag
        self.control_stage_machine = "disconnected"

        self._master = master

        # Main frame
        self.master_frame = View.MainFrame(self._master)
        self.master_frame.pack(expand=True, fill=tkinter.BOTH)

        # Control Frame
        self.control_frame = View.ControlFrame(self.master_frame)
        self.control_frame.pack(expand=True, fill=tkinter.X, side=tkinter.TOP, anchor="center")

        # Control description
        self.control_description_frame = View.DescriptionFrame(self.control_frame)
        self.control_description_frame.pack(expand=True, fill=tkinter.X, side=tkinter.LEFT, anchor="center")

        self.control_description_message = View.DescriptionMessage(self.control_description_frame)
        self.control_description_message.pack(expand=True, fill=tkinter.X, anchor="center")

        # Control button frame
        self.control_button_frame = View.ButtonFrame(self.control_frame)
        self.control_button_frame.pack(expand=True, fill=tkinter.X, side=tkinter.RIGHT, anchor="n")

        # Stage label
        self.stage_label = View.StageLabel(self.control_button_frame)
        self.stage_label.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        View.GraySeparator(self.control_button_frame).pack(side=tkinter.RIGHT, anchor="e", pady="4", fill="y", padx="4")

        self.auto_check_value = tkinter.IntVar()
        self.auto_check = View.AutoCheck(self.control_button_frame, variable=self.auto_check_value, command=self.auto_refresh)
        self.auto_check.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.refresh_button = View.RefreshButton(self.control_button_frame, command=self.refresh)
        self.refresh_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        View.GraySeparator(self.control_button_frame).pack(side=tkinter.RIGHT, anchor="e", pady="4", fill="y", padx="4")

        self.stop_button = View.StopButton(self.control_button_frame)
        self.stop_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.stop_button.configure(command=self.stop)
        self.play_button = View.PlayButton(self.control_button_frame)
        self.play_button.pack(side=tkinter.RIGHT, anchor="e", padx="4")
        self.play_button.configure(command=self.play)

        # View.GraySeparatorH(self.control_button_frame).pack(side=tkinter.BOTTOM, anchor="n")

        # Tree Frame
        self.tree_frame = View.TreeFrame(self.master_frame)
        self.tree_frame.pack(expand=True, fill=tkinter.BOTH, after=self.control_frame)

        # Display Tree
        self.display_tree_frame = View.DisplayTreeFrame(self.tree_frame)
        self.display_tree_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        self.display_tree = View.DisplayTree(self.display_tree_frame)
        self.display_tree.bind("<Double-1>", self._display_tree_double_click)
        self.display_tree.pack(expand=True, fill=tkinter.BOTH)

        # Modify Tree
        self.modify_tree_frame = View.ModifyTreeFrame(self.tree_frame)
        self.modify_tree_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)
        self.modify_tree = View.ModifyTree(self.modify_tree_frame)
        self.modify_tree.pack(expand=True, fill=tkinter.BOTH)

        # Debug Frame
        self.debug_frame = View.DebugFrame(self.master_frame)
        self.debug_frame.pack(expand=True, fill=tkinter.BOTH, after=self.tree_frame)

        # Commander Frame
        self.commander_frame = View.CommanderFrame(self.debug_frame)
        self.commander_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        self.commander = View.Commander(self.commander_frame)
        self.commander.pack(expand=True, fill=tkinter.BOTH)

        # Log Frame
        self.log_frame = View.LogFrame(self.debug_frame)
        self.log_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)
        self.log = View.Log(self.log_frame)
        self.log.pack(expand=True, fill=tkinter.BOTH)

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
        self._address_field_pattern = re.compile(r"(?P<Address>0x[0-9a-fA-F]+)[\s\|]*(?P<Field0>[0-9]*):*(?P<Field1>[0-9]*)")
        self._mid_value = []
        self._mid_value_pointer = self._mid_value

        # Modify parameter
        self.tree_root = None

        # Image
        self._image_tag = (
            ImageTk.PhotoImage(Image.open("./.image/.treeview/device.png").resize((20, 20), Image.ANTIALIAS)),
            ImageTk.PhotoImage(Image.open("./.image/.treeview/register.png").resize((20, 20), Image.ANTIALIAS)),
            ImageTk.PhotoImage(Image.open("./.image/.treeview/field.png").resize((20, 20), Image.ANTIALIAS))
        )

        # SWD handler
        self.swd_handler = None

        self.display_device_render(self.device_generator())

    def device_generator(self):
        memory_header = [{"Key": "Address Start", "Level": (1,), "Priority": ("M",)},
                         {"Key": "Module", "Level": (1,), "Priority": ("L",)},
                         {"Key": "Class", "Level": (1,), "Priority": ("L",)}]
        memory_reheader = ("Address", "Name", "Class")
        memory_sheets = ("AP Peripheral AddrMapping", "CP Peripheral AddrMapping")
        memory_e2j = Excel2Dict.E2D(excel="Venus_SoC_Memory_Mapping.xls", header=memory_header, sheets=memory_sheets,
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

        e2j = Excel2Dict.E2D(excel="Venus_SoC_Memory_Mapping.xls", header=header, reheader=reheader)
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
            self._cur_iid = self.modify_tree.insert(self.parent, "end", iid=None, text=i["Name"], image=self._image_tag[self.level], values=(i["Address"], i["Property"], value), tags=(self.level, i["Description"]))
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
            self.cur_iid = self.display_tree.insert(self.parent, "end", iid=None, text=item["Name"], image=self._image_tag[self.level], values=(hex(self.address_base_pointer), "", ""), tags=(self.level, "", self.address_base_pointer))

            self.parent = self.cur_iid
            self._display_register_render(item["Level"])

    def _display_register_render(self, root):
        for item in root:
            self.level = 1
            self.current_address = self.address_base_pointer + int(item["Address"], base=16)
            if not self._expand(item):
                self.cur_iid = self.display_tree.insert(self.parent, "end", iid=None, text=item["Name"], image=self._image_tag[self.level], values=(hex(self.current_address), "", ""), tags=(self.level, item["Description"], self.current_address))

                self.parent = self.cur_iid
                self._display_field_render(item["Level"])

                # Get the parent of current item
                self.parent = self.display_tree.parent(self.parent)

    def _display_field_render(self, root):
        for item in root:
            self.level = 2
            self.cur_iid = self.display_tree.insert(self.parent, "end", iid=None, text=item["Name"], image=self._image_tag[self.level], values=("", "%d:%d" % (int(item['Start']), int(item['End'])), item["Property"]), tags=(self.level, item["Description"], self.current_address))

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
                                                    image=self._image_tag[self.level], values=("", "%d:%d" % (int(i['Start']), int(i['End'])), i["Property"]),
                                                    tags=(self.level, i["Description"], self.current_address))

    def connected(self):
        self.stage_label.enable()
        self.auto_check.enable()
        self.refresh_button.enable()
        self.stop_button.enable()
        self.play_button.disable()

    def disconnected(self):
        self.stage_label.disable()
        self.auto_check.disable()
        self.refresh_button.disable()
        self.stop_button.disable()
        self.play_button.enable()

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

                elif func.__name__ == "refresh":
                    if func(self, *args, **kwargs):
                        return True
                    else:
                        return False

                elif func.__name__ == "_display_tree_double_click":
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
        return True

    @control_button_stage_machine
    def play(self):
        # Connect to target
        try:
            self.swd_handler = SWDJlink.SWDJlink()
        except:
            self.swd_handler = None
            return False
        return True

    @control_button_stage_machine
    def stop(self):
        # Disconnect to target
        del self.swd_handler
        return True

    def auto_refresh(self):
        # Depending the check button on or off
        # Register a timer into GUI event loop
        # Or unregister a timer
        if self.auto_check_value:
            self.open_refresh_timer()
        else:
            self.close_refresh_timer()

    def open_refresh_timer(self):
        self._refresh_timer_handler = self._master.after(self.refersh_time, self.refresh_inspection)

    def close_refresh_timer(self):
        self._master.after_cancel(self._refresh_timer_handler)

    def refresh_inspection(self):
        # refresh
        logging.info("[Callback]")
        if self.refresh():
            self._refresh_timer_handler = self._master.after(self.refersh_time, self.refresh_inspection)
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
        self._item_recursive((item, ))

        self.modify_tree_render(self._mid_value, self.display_tree.item(item)["tags"][0])

        return "break"

    def _get_mask(self, lengh):
        mask = BitArray(bin(0x1 << lengh))
        mask.invert()
        mask = mask[1:]
        return mask.uint

    def write32_plus(self, tpl, data):
        if tpl[1] or tpl[2]:
            # Read address data
            mem32 = self.swd_handler.read32(int(tpl[0], base=16))
            if not mem32:
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
            self.swd_handler.write32(int(tpl[0], base=16), data)

    def read32_plus(self, tpl):
        mem32 = self.swd_handler.read32(int(tpl[0], base=16))
        if not mem32:
            return False
        logging.debug("Read the whole register: %s" % (hex(mem32)))
        if tpl[1] or tpl[2]:
            # Have trouble
            return (mem32 >> int(tpl[1])) & self._get_mask(int(tpl[2]) - int(tpl[1]) + 1)
        return mem32
