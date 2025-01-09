import elftools.elf.sections
from elftools.elf.elffile import ELFFile
import math


class ElfReader:
    def __init__(self, file_name):
        self._cache_line_size_b = None
        self._cache_ways = None
        self._cache_size_b = None
        self._cache_line_number = None

        self._cache_crash_array = None

        with open(file_name, "rb") as f_handler:
            self.__elf_file = ELFFile(f_handler)

            self.__symbol = self._get_file_symbol()

    def _get_file_symbol(self):
        symbol_array = []

        for section in self.__elf_file.iter_sections():
            if isinstance(section, elftools.elf.sections.SymbolTableSection):
                for symbol in section.iter_symbols():
                    if symbol['st_size'] != 0:
                        symbol_array.append({"name": symbol.name, "address": hex(symbol['st_value']),
                                             "size": symbol['st_size']})

        return symbol_array

    def cache_crash_calculate(self, cache_size_b, calc_region, cache_line_size_b=32, cache_ways=2):
        self._cache_line_size_b = cache_line_size_b
        self._cache_ways = cache_ways
        self._cache_size_b = cache_size_b
        self._cache_line_number = int(self._cache_size_b / self._cache_line_size_b / self._cache_ways)

        print("Cache module initialize: %d, %d, %d, %d" % (self._cache_line_size_b, self._cache_line_number,
                                                           self._cache_ways, self._cache_size_b))

        self._cache_crash_array = [[] for i in range(self._cache_line_number)]

        for symbol in self.__symbol:
            if calc_region[0] <= int(symbol["address"], 16) <= calc_region[1]:
                self.__cache_line_position(symbol)

        return self._cache_crash_array

    def __cache_line_position(self, symbol):

        def __insert_index_in_crash_array(in_i, in_symbol):
            if self._cache_crash_array[in_i]:
                self._cache_crash_array[in_i].append(in_symbol["name"])
            else:
                self._cache_crash_array[in_i] = [in_symbol["name"]]

        address = int(symbol["address"], 16)
        size = int(symbol["size"])

        pos_offset = int(math.log(32, 2))
        cache_mask = (self._cache_line_number - 1) << pos_offset

        cache_line_index_s = (address & cache_mask) >> pos_offset
        cache_line_index_e = ((address + size) & cache_mask) >> pos_offset

        if cache_line_index_s > cache_line_index_e:
            for i in range(cache_line_index_s, self._cache_line_number):
                __insert_index_in_crash_array(i, symbol)
            for i in range(0, cache_line_index_e):
                __insert_index_in_crash_array(i, symbol)

        elif cache_line_index_s == cache_line_index_e:
            __insert_index_in_crash_array(cache_line_index_s, symbol)
        else:
            for i in range(cache_line_index_s, cache_line_index_e):
                __insert_index_in_crash_array(i, symbol)


if __name__ == "__main__":
    file_name = "fhost_good"

    elf = ElfReader(file_name)
    cache_crash = elf.cache_crash_calculate(16384, [0x30000000, 0x38000000])

    # with open("%s.sym.txt" % (file_name, ), "w") as f:
    #     f.write(str(cache_crash))

    for num, i in enumerate(cache_crash):
        print("Line %d ---->  " % (num, ), i)
