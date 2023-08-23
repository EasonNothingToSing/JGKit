import pylink
from pylink import errors
import logging
import global_var


__all__ = ["SWDJlink", ]


class SWDJlink(pylink.JLink):
    def __init__(self):
        self.__jlink_dll = pylink.library.Library("JLink_x64.dll")
        super(SWDJlink, self).__init__(lib=self.__jlink_dll)
        self.core = global_var.get_value("core")
        self.open()
        self.set_tif(pylink.enums.JLinkInterfaces.SWD)
        self.connect(self.core)
        if self.connected():
            logging.debug("Connect to the target")
        else:
            logging.error("Disconnect to the target")

    def __del__(self):
        self.close()

    def read32(self, addr):
        self.clear_error()
        try:
            return self.memory_read32(addr, num_words=1)[0]
        except errors.JLinkReadException:
            return -1

    def write32(self, addr, data):
        self.clear_error()
        try:
            self.memory_write32(addr, [data])
        except errors.JLinkWriteException:
            return False

    def read_mem(self, addr, rlen):
        self.clear_error()
        try:
            return self.memory_read32(addr, rlen)
        except errors.JLinkReadException:
            return False

    def write_mem(self, addr, wdata):
        self.clear_error()
        try:
            return self.memory_write32(addr, wdata)
        except errors.JLinkWriteException:
            return False

    def is_connected(self):
        return self.connected()


if __name__ == "__main__":
    swd = SWDJlink()
