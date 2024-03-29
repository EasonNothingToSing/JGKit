import global_var
import json
import os

""" core configure json file
{
    "name":"",
    "core":"",
    "tif":[],
    "excel":"",
    "sheet":[]
}
"""


class StartUpVerify:
    def __init__(self, root):
        self.__file_name = None
        self.__root = root
        self.__file_list = []

        self.__file_name = [file for file in os.listdir(self.__root) if os.path.isfile(os.path.join(self.__root, file))]

        for file in self.__file_name:
            with open(os.path.join(self.__root, file)) as f:
                load_file = json.load(f, )
                self.__file_list.append(load_file)

    def __verify(self, data):
        pass

    def get_core_list(self):
        core_list = []
        for item in self.__file_list:
            core_list.append(item['name'])
        return core_list

    def __setitem__(self, key, value):
        print(key, value)

    def __getitem__(self, key):
        for item in self.__file_list:
            if item["name"] == key:
                return item

    def __call__(self):
        return str(self.__file_list)


if __name__ == "__main__":
    verify = StartUpVerify(root=r"..\..\.data\config")

    print(verify.get_core_list())
    print(verify())
    print(verify["Arcs-A0"]["name"])
