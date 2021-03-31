import xlrd
import logging

__all__ = ["E2D", ]


class E2D:
    """
    excel = A widnows excel file
    header = Like this [{"Key": "Address Start", "Level": (1, ), "Priority": ("M", )},
                        {"Key": "Module", "Level": (1, ), "Priority": ("M", )},
                        {"Key": "Class", "Level": (1, ), "Priority": ("M", )}]
    reheader = Like this ("Address", "Name", "Class")
    sheets = The excel sheets name or 'all' which include all excel sheets
    exclude = Which sheets you don't want
    """

    def __init__(self, excel, header, reheader, sheets='all', exclude=None):
        self._xlrd_handler = None
        self._dist = []
        self._pointer_stack = []
        # excel not None
        if excel:
            self._format = xlrd.inspect_format(excel)
            self.excel_path = excel
            self._xlrd_handler = xlrd.open_workbook(self.excel_path)
        else:
            logging.error("Excel handler is None")
            raise ValueError("Excel handler不能为None")

        # Register the parameter
        self.header = header
        self.reheader = reheader

        if sheets == "all":
            # Get all excel sheets
            self.sheets = self._xlrd_handler.sheet_names()
        else:
            self.sheets = sheets

        if exclude:
            for i in exclude:
                try:
                    # Remove sheets you don't want
                    self.sheets.remove(i)
                except ValueError:
                    pass

        # TODO Priority and Level list check, length equal
        if len(self.header) != len(self.reheader):
            raise ValueError("Header 和 Reheader 长度不一致")

        for dic in self.header:
            if len(dic["Priority"]) != len(dic["Level"]):
                raise ValueError("Priority 和 Level 长度不一致")

        # Reference list indicate the excel sheet row belong to which level
        self._ref_list = []
        for _ in range(max(tuple(j for i in self.header for j in i["Level"]))):
            self._ref_list.append([])
        for i in self.header:
            for level, priority in zip(i["Level"], i["Priority"]):
                self._ref_list[int(level) - 1].append(priority)

        # Init stack
        self._pointer_stack = [None for _ in range(1 + max(tuple(j for i in self.header for j in i["Level"])))]

    def convert(self):
        # Convert excel to dict
        self._xl2strc()

    # In level check machine, have 3 priority for each level
    # High, Middle, Low
    # High priority, indicate this row belong corresponding level immediately
    # Middle, normal priority, the column must have, but not immediately confirm this row belong corresponding level
    # Low, level need this column data but this column will not influence corresponding row belong which level
    def _state_machine_level_check(self, row):
        # A temporary list
        rslt_list = []
        for _ in range(max(tuple(j for i in self.header for j in i["Level"]))):
            rslt_list.append([])

        # Add each level column into their stack
        for dct in self.header:
            for j, p in zip(dct["Level"], dct["Priority"]):
                # corresponding cell have value
                if row[dct["Num"]].value != "":
                    rslt_list[int(j) - 1].append(p)
                else:
                    rslt_list[int(j) - 1].append(None)

        # According to flow chart to indicate current row belong which level
        for rslt, ref, num in zip(rslt_list, self._ref_list, range(len(rslt_list))):
            if self._sub_state_machine_level_check(rslt, ref):
                return num + 1

    def _sub_state_machine_level_check(self, rslt, ref):
        ret = True
        for s, f in zip(rslt, ref):
            if not s:
                if f == "H":
                    return False
                elif f == "M":
                    ret &= False
                elif f == "L":
                    pass
                else:
                    raise ValueError("Level 状态机获得无效参数")
            else:
                if f == "H":
                    return True
                elif f == "M":
                    ret &= True
                elif f == "L":
                    ret &= True
                else:
                    raise ValueError("Level 状态机获得无效参数")

        return ret

    # 核心思想：发现同级别的数据单元时，将栈中同级的数据块填写到上一级块中的缓存单元中
    # eg：当前到Level2，又发现一个符合Level2的单元时，将当前的Level2压入上一层的Level1中的Level list中
    # The excel like below:
    # Level 1
    #   Level 2
    #       Level 3
    #       Level 3
    #       Level 3
    #       Level 3
    #       Level 3
    #       Level 3
    #   Level 2
    #       Level 3
    #       Level 3
    #       Level 3
    #   Level 2
    #       Level 3
    #   Level 2
    #       Level 3
    #       Level 3
    #       Level 3
    #       Level 3

    def _state_machine(self, rows):
        # Ignore first row
        next(rows)
        # Traverse all row in current sheet
        for row in rows:
            # For each row, should verify it's level
            level = self._state_machine_level_check(row)
            # Confirm level
            if level:
                # Current level have data
                # 主要决定当前的LEVEL是否需要继续添加数据
                # 如果已经存在数据，则表明需要将数据移走
                if self._pointer_stack[level]:
                    try:
                        # This traverse from the max level
                        for i in reversed(range(1 + max(tuple(j for i in self.header for j in i["Level"])))):
                            if i == level:
                                # Add old dictionary to upper level list
                                self._pointer_stack[level - 1]["Level"].append(self._pointer_stack[level])
                                break
                            # Which mean the level it's not belong bottom level, we shold
                            else:
                                self._pointer_stack[i - 1]["Level"].append(self._pointer_stack[i])
                                self._pointer_stack[i] = {}

                    except IndexError:
                        pass
                # Current level is None, so Add a new dictionary {}
                self._pointer_stack[level] = {}

                # get item of each header and corresponding number
                for dct, redct, num in zip(self.header, self.reheader,
                                           range(max(len(self.header), len(self.reheader)))):
                    # check each item Level
                    if level in dct["Level"]:
                        # add an item to corresponding dictionary
                        self._pointer_stack[level].update({redct: row[dct["Num"]].value})

                self._pointer_stack[level].update({"Level": []})

            else:
                raise ValueError("Excel 存在问题行，无法确认行的归属")

        # The sheet traverse over, nead add all pointer stack data into self _dict
        for i in reversed(range(1 + max(tuple(j for i in self.header for j in i["Level"])))):
            if i == 0:
                self._dist.append(self._pointer_stack[i])
            else:
                self._pointer_stack[i - 1]["Level"].append(self._pointer_stack[i])

        return True

    def _locate_key(self, sheet):
        for f_num, dct in enumerate(self.header):
            for num, cell in enumerate(sheet.row(0)):
                if dct["Key"] == cell.value:
                    if "Num" in self.header[f_num].keys():
                        self.header[f_num]["Num"] = num
                    else:
                        self.header[f_num].update({"Num": num})
                    break
            else:
                # Not locate the key
                return False
        return True

    def _xl2strc(self):
        for sheet in self.sheets:
            # sheet handler
            handler = self._xlrd_handler.sheet_by_name(sheet)
            # locate all key
            if not self._locate_key(handler):
                continue

            # Configure all pointer stack to None
            for item in range(1 + max(tuple(j for i in self.header for j in i["Level"]))):
                self._pointer_stack[item] = None

            # add the dict into stack level0
            self._pointer_stack[0] = {"Sheet_Name": sheet, "Level": []}
            # state machine
            if not self._state_machine(handler.get_rows()):
                return False

        return True

    def __getitem__(self, item):
        return self._dist[item]


if __name__ == "__main__":
    header = [{"Key": "Sub-Addr\n(Hex)", "Level": (1,), "Priority": ("H",)},
              {"Key": "Start\nBit", "Level": (2,), "Priority": ("M",)},
              {"Key": "End\nBit", "Level": (2,), "Priority": ("M",)},
              {"Key": "R/W\nProperty", "Level": (2,), "Priority": ("M",)},
              {"Key": "Register\nName", "Level": (2, 1), "Priority": ("M", "M")},
              {"Key": "Register Description", "Level": (2,), "Priority": ("L",)}
              ]

    reheader = ("Address", "Start", "End", "Property", "Name", "Description")

    e2d = E2D(excel="Venus_SoC_Memory_Mapping.xls", header=header, reheader=reheader)
    e2d.convert()
    for i in e2d:
        print(i)
