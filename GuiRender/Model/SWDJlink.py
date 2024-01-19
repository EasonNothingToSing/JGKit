import pylink
from pylink import errors
import logging
import global_var


__all__ = ["SWDJlink", ]

SWD_DEBUG_EN = 0


def swd_debug_decorater(func):
    def wrapper(*args, **kwargs):
        if SWD_DEBUG_EN:
            if func.__name__ == "read32":
                return 0
            elif func.__name__ == "write32" or func.__name__ == "write_mem" or func.__name__ == "is_connected":
                return True
            elif func.__name__ == "read_mem":
                try:
                    return [0] * kwargs["rlen"]
                except KeyError:
                    return [0] * args[2]
            elif func.__name__ == "__init__":
                return object()
            else:
                pass
        else:
            return func(*args, **kwargs)

    return wrapper


def swd_debug_class_decorater(cls):
    if SWD_DEBUG_EN:
        def __deco_init__(self, *args, **kwargs):
            logging.debug("In decorater __init__")

        def __deco_del__(self, *args, **kwargs):
            logging.debug("In decorater __del__")

        cls.__init__ = __deco_init__
        cls.__del__ = __deco_del__
    else:
        pass

    return cls


@swd_debug_class_decorater
class SWDJlink(pylink.JLink):
    def __init__(self):
        self.__jlink_dll = pylink.library.Library("JLink_x64.dll")
        super(SWDJlink, self).__init__(lib=self.__jlink_dll)
        self.core = global_var.get_value("core")
        self.open()
        if global_var.get_value("tif") == "JTAG":
            self.set_tif(pylink.enums.JLinkInterfaces.JTAG)
        else:
            self.set_tif(pylink.enums.JLinkInterfaces.SWD)
        self.connect(self.core, verbose=True)
        if self.connected():
            logging.debug("Connect to the target")
        else:
            logging.error("Disconnect to the target")

    def __del__(self):
        self.close()

    @swd_debug_decorater
    def read32(self, addr):
        self.clear_error()
        try:
            return self.memory_read32(addr, num_words=1)[0]
        except errors.JLinkReadException:
            return -1

    @swd_debug_decorater
    def write32(self, addr, data):
        self.clear_error()
        try:
            self.memory_write32(addr, [data])
        except errors.JLinkWriteException:
            return False

    @swd_debug_decorater
    def read_mem(self, addr, rlen):
        self.clear_error()
        try:
            return self.memory_read32(addr, rlen)
        except errors.JLinkReadException:
            return False

    @swd_debug_decorater
    def write_mem(self, addr, wdata):
        self.clear_error()
        try:
            return self.memory_write32(addr, wdata)
        except errors.JLinkWriteException:
            return False

    @swd_debug_decorater
    def is_connected(self):
        return self.connected()


if __name__ == "__main__":
    __jlink_dll = pylink.library.Library("JLink_x64.dll")

    jtag = pylink.JLink(lib=__jlink_dll)
    jtag.open()
    jtag.set_tif(pylink.enums.JLinkInterfaces.JTAG)
    jtag.connect(chip_name="N308", verbose=True)
    print(jtag.core_id())

    print(jtag.device_family())

    print(jtag.connected()) # Ture
    print(jtag.target_connected()) # False
