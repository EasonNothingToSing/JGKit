import pandas
import os


class ExcelReader:
    def __init__(self, root):
        self.__root = root

        _, file_extension = os.path.splitext(self.__root)
        if file_extension in ['.xlsx']:
            pass
        elif file_extension in ['.xls']:
            pass
        else:
            # TODO raise error
            pass

    def sheet_names(self):
        return [key for key in pandas.read_excel(io=self.__root, sheet_name=None).keys()]

    def sheet_by_name(self, name):
        return pandas.read_excel(self.__root, sheet_name=name, header=None).values


if __name__ == "__main__":
    reader = ExcelReader("../../.data/xls/Mars_SoC_Memory_Mapping.xlsx")

    print(reader.sheet_names())
    text = reader.sheet_by_name("UART")

    for i in text:
        print(i)

