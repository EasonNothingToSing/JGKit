import logging
import struct
import SWDJlink
import logging


def __crc8_ccitt(val, buf):
    for b in buf:
        val ^= b
        val = (val << 4) ^ NvsDetector.crc8_ccitt_small_table[val >> 4]
        val &= 0xFF
        val = (val << 4) ^ NvsDetector.crc8_ccitt_small_table[val >> 4]
        val &= 0xFF
    return val


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


class NvsDetector:
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
                addr = self.__nvs_sector_advance(addr)
                ret = self.__nvs_cmp_const(addr, NvsDetector.NVS_ATE_SIZE)

                if not ret:
                    logging.debug("Find open sector in 0x%x" % (addr,))
                    break
            else:
                opened_sector += 1

        if closed_sector == self._nvs_sector_counter:
            logging.debug("Not Find open sector, and search end")
            return

        if opened_sector == self._nvs_sector_counter:
            ret = self.__nvs_cmp_const(addr, NvsDetector.NVS_ATE_SIZE)
            if not ret:
                self.__nvs_sector_advance(addr)

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


if __name__ == "__main__":
    pass
