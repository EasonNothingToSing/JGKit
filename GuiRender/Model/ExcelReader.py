import pandas
import os


class ExcelReader:
    def __init__(self, root):
        self.__root = root
        self.excel_handler = None

        _, file_extension = os.path.splitext(self.__root)
        if (file_extension in ['.xlsx']) or (file_extension in ['.xls']):
            self.excel_handler = pandas.read_excel(self.__root, sheet_name=None, header=None)
        else:
            # TODO raise error
            pass

    def sheet_names(self):
        return [key for key in self.excel_handler.keys()]

    def sheet_by_name(self, name):
        return self.excel_handler[name].values


if __name__ == "__main__":
    reader = ExcelReader("../../.data/xls/Mars_SoC_Memory_Mapping.xlsx")

    print(reader.sheet_names())
    text = reader.sheet_by_name("UART")

    for i in text:
        print(i)

