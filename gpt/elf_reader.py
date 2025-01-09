import elftools.elf.sections
from elftools.elf.elffile import ELFFile


def read_symbols(file_path):
    with open(file_path, 'rb') as f:
        elffile = ELFFile(f)
        # 查找符号表
        for section in elffile.iter_sections():
            if isinstance(section, elftools.elf.sections.SymbolTableSection):
                print(f"Section: {section.name}")
                for symbol in section.iter_symbols():
                    if symbol['st_size'] != 0:
                        print(f"Symbol Name: {symbol.name}, Address: {hex(symbol['st_value'])}, Size: {symbol['st_size']}")

# 调用函数并提供 symbol 文件路径
read_symbols('cache')
