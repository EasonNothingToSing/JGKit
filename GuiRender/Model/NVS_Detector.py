import logging
import struct
import SWDJlink
import logging
from collections import namedtuple
import global_var


class NvsError(Exception):
    NVS_ModError = 101
    NVS_PageError = 102

    def __init__(self, message="", error=None):
        super().__init__(message)
        self.__message = message
        self.__error = error

    def __str__(self):
        if self.__error == NvsError.NVS_ModError:
            return f"Error {self.__error}<NVS MOD ERROR>: {self.__message}"


def ate_format(entry):
    unpacked_data = struct.unpack(NvsDetector.ate_struct_format, bytes(entry))
    ate = NvsDetector.ATE_STRUCT(id=unpacked_data[0], offset=unpacked_data[1], len=unpacked_data[2],
                                 future=unpacked_data[3], crc8=unpacked_data[4])
    return ate


class NvsDetector:
    # id -> short
    # offset -> short
    # len -> short
    # future -> bytes
    # crc8 -> bytes
    # nouse -> 24 bytes
    ate_struct_format = "<HHHBB24x"
    ATE_STRUCT = namedtuple("ATE", ["id", "offset", "len", "future", "crc8"],
                            defaults=[0xFFFF, 0xFFFF, 0xFFFF, 0xFF, 0xFF])
    crc8_struct_format = "<BBBBBBB"

    crc8_ccitt_small_table = [
        0x00, 0x07, 0x0E, 0x09, 0x1C, 0x1B, 0x12, 0x15,
        0x38, 0x3F, 0x36, 0x31, 0x24, 0x23, 0x2A, 0x2D
    ]

    NVS_PAGE_SIZE = 256

    NVS_ATE_SIZE = 32

    def __init__(self, address, length, handler=None, sector_size=4096, erase_value=0xff, block_size=32):
        self._nvs_address = address

        self._nvs_length = length

        self.__handler = handler

        self._nvs_sector_size = sector_size

        if self._nvs_sector_size % NvsDetector.NVS_PAGE_SIZE:
            raise NvsError(error=NvsError.NVS_PageError)

        self._nvs_erase_value = int(erase_value)

        self._nvs_block_size = block_size

        if self._nvs_length % self._nvs_sector_size:
            raise NvsError("%d %% %d" % (self._nvs_length, self._nvs_sector_size), NvsError.NVS_ModError)

        self._nvs_sector_counter = int(self._nvs_length / self._nvs_sector_size)

        self.__data_wra = 0
        self.__ate_wra = 0

        self.__sect_mask = (~(self._nvs_sector_size - 1) & 0xFFFFFFFF)
        self.__sect_shift = self._nvs_sector_size.bit_length() - 1
        self.__offs_mask = self._nvs_sector_size - 1

        logging.info("sect mask: %s; sect shift: %d; offset mask: %s" % (hex(self.__sect_mask), self.__sect_shift,
                                                                         hex(self.__offs_mask)))

        self.__sector_select = 0

        self.__sector_manager = [{"flag": True} for _ in range(self._nvs_sector_counter)]

        self.nvs_recover()

    def nvs_recover(self):

        closed_sector = 0
        opened_sector = 0
        addr = self._nvs_address
        for i in range(self._nvs_sector_counter):
            # Get the CLOSE ATE address
            addr = self._nvs_address + i * self._nvs_sector_size + self._nvs_sector_size - NvsDetector.NVS_ATE_SIZE

            # Check the close ate have been written?
            ret = self.__nvs_cmp_const(addr, NvsDetector.NVS_ATE_SIZE)

            # The current sector must
            if ret:
                closed_sector += 1
                self.__sector_manager[i]["flag"] = False
                addr = self.__nvs_sector_advance(addr)
                ret = self.__nvs_cmp_const(addr, NvsDetector.NVS_ATE_SIZE)

                if not ret:
                    self.__sector_select = (i + 1) % self._nvs_sector_counter
                    logging.info("Find open sector in 0x%x" % (addr,))
                    break
            else:
                opened_sector += 1
                self.__sector_manager[i]["flag"] = True

        if closed_sector == self._nvs_sector_counter:
            logging.info("Not Find open sector, and search end")
            return

        if opened_sector == self._nvs_sector_counter:
            self.__sector_select = 0
            ret = self.__nvs_cmp_const(addr, NvsDetector.NVS_ATE_SIZE)
            if not ret:
                addr = self.__nvs_sector_advance(addr)

        addr = self.__nvs_ate_recover(addr - NvsDetector.NVS_ATE_SIZE)

        self.__ate_wra = addr
        self.__data_wra = addr & self.__sect_mask

        logging.info("ATE recover ate: %s; data: %s" % (hex(self.__ate_wra), hex(self.__data_wra)))

    def __is_closed_ate(self, addr):
        if ((addr & self.__offs_mask) + 31) != self.__offs_mask:
            return 0

        packet = self.__nvs_get_ate(addr)
        if packet:
            ate = packet[0]

            if ate.id == 0xFFFF and ate.len == 0:
                return 1

        return 0

    def __is_gc_ate(self, addr):
        pass

    # Returns 0 if all data in NVS is equal to value, 1 if not equal,
    def __nvs_cmp_const(self, address, length):
        mem_buf = self.__handler.read_mem(address, length, nbits=8)
        for i in mem_buf:
            if i != self._nvs_erase_value:
                return 1
        return 0

    def __nvs_sector_advance(self, address):
        address += self._nvs_sector_size  # Advance address
        if int((address - self._nvs_address) / self._nvs_sector_size) == self._nvs_sector_counter:
            return address - self._nvs_length

        return address

    #  return 1 if crc8 and offset valid, 0 otherwise
    def __nvs_ate_valid(self, entry):
        def __crc8_ccitt(val, buf):
            for b in buf:
                val ^= b
                val = (val << 4) ^ NvsDetector.crc8_ccitt_small_table[val >> 4]
                val &= 0xFF
                val = (val << 4) ^ NvsDetector.crc8_ccitt_small_table[val >> 4]
                val &= 0xFF
            return val
        ate = ate_format(entry)
        position = ate.offset + ate.len
        crc8 = __crc8_ccitt(0xff, struct.unpack(NvsDetector.crc8_struct_format, bytes(entry[:7])))
        if (crc8 != ate.crc8) or (position >= (self._nvs_sector_size - NvsDetector.NVS_ATE_SIZE)):
            return 0

        return 1

    def __nvs_ate_recover(self, address):
        ate_end_addr = address
        data_end_addr = address & self.__sect_mask
        while ate_end_addr > data_end_addr:
            mem_buf = self.__handler.read_mem(ate_end_addr, NvsDetector.NVS_ATE_SIZE, nbits=8)

            if self.__nvs_ate_valid(mem_buf):
                ate = ate_format(mem_buf)
                data_end_addr = data_end_addr & self.__sect_mask
                data_end_addr += (ate.offset + ate.len)
                address = ate_end_addr

            ate_end_addr -= NvsDetector.NVS_ATE_SIZE

        return address

    def nvs_search_ate(self, address):
        pass

    def __nvs_get_ate(self, address):
        ate_end_addr = address
        data_end_addr = address & self.__sect_mask
        mem_buf = self.__handler.read_mem(ate_end_addr, NvsDetector.NVS_ATE_SIZE, nbits=8)
        if self.__nvs_ate_valid(mem_buf):
            ate = ate_format(mem_buf)
            data_end_addr += ate.offset

            if ate.len:
                mem_buf = self.__handler.read_mem(data_end_addr, ate.len, nbits=8)
            else:
                mem_buf = None

            return [ate, mem_buf]

        return None


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s - %(funcName)s - %(filename)s[line:%(lineno)d]"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    global_var.set_value("core", "RV32")
    global_var.set_value("tif", "JTAG")
    global_var.set_value("JTAG", {"AP": [0, 0, 5, 1, 5], "CP": [5, 1, 0, 0, 5]})

    link_handler = SWDJlink.Link("AP")

    print(hex(link_handler.read32(0x30000000)))

    nvs_handler = NvsDetector(0x30001000, 4096, link_handler, 1024)

