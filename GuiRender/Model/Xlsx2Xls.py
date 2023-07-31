import pandas
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


def xlsxfileconvert(file_name):
    basename, ext = os.path.splitext(file_name)
    if ext != ".xlsx":
        raise TypeError("Parameter extend is't a xlsx file")

    xlsx = pandas.read_excel(file_name, engine="openpyxl", sheet_name=None)

    with pandas.ExcelWriter(os.path.join("./.data/xls/.temp", os.path.split(basename)[-1] + ".xls"), engine="xlwt") as writer:
        for sheet_name, df in xlsx.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == "__main__":
    print("Running path: ", os.getcwd())
    os.chdir(r"E:\APP\python_project\JGKit")
    print("Running path: ", os.getcwd())

    xlsxfileconvert(r".\.data\xls\ARCS-B_SoC_Memory_Mapping.xlsx")
