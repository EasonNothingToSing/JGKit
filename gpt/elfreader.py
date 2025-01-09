from elftools.elf.elffile import ELFFile

# 打开ELF文件
with open('nos_test.elf', 'rb') as f:
    elffile = ELFFile(f)

    # 查找符号表段
    symtab_section = elffile.get_section_by_name('.symtab')

    if symtab_section:
        print("Symbol Table:")
        for symbol in symtab_section.iter_symbols():
            print(f"  {symbol.name}: {hex(symbol['st_value'])} (size: {symbol['st_size']})")
    else:
        print("No symbol table found.")
