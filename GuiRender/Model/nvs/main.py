# from encoder import Encoder
#
# example_data = {10: bytes.fromhex('1122334455'),
#                 20: bytes.fromhex('A5A5A5A5')}
# nvs_sector_size = 1024
# nvs = Encoder(nvs_sector_size).dump(example_data)
# print([hex(i) for i in nvs])

from decoder import Decoder

with open("./memory.bin", 'rb') as nvs_dump:
    binary_content = nvs_dump.read()
    content = Decoder(0x1000).load(binary_content)
    for key, value in content.items():
        print(key, [hex(i) for i in value])
