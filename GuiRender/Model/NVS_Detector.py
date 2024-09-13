import struct

# id -> short
# offset -> short
# len -> short
# future -> bytes
# crc8 -> bytes
# nouse -> 24 bytes
ate_struct_format = "<HHHBB24x"
crc8_struct_format = "<BBBBBBB"

crc8_ccitt_small_table = [
    0x00, 0x07, 0x0E, 0x09, 0x1C, 0x1B, 0x12, 0x15,
    0x38, 0x3F, 0x36, 0x31, 0x24, 0x23, 0x2A, 0x2D
]


def __crc8_ccitt(val, buf):
    for b in buf:
        val ^= b
        val = (val << 4) ^ crc8_ccitt_small_table[val >> 4]
        val &= 0xFF
        # val = (val << 4) ^ crc8_ccitt_small_table[val >> 4]
        val &= 0xFF
    return val


class NvsDetector:
    def __init__(self):
        pass

    def nvs_detect(self, file):
        pass