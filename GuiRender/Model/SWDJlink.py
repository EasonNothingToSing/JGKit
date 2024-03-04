import os.path

import pylink
from pylink import errors
import logging
import global_var
import ctypes


__all__ = ["Link", ]

LINK_DEBUG_EN = 0


def link_debug_decorater(func):
    def wrapper(*args, **kwargs):
        if LINK_DEBUG_EN:
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


def link_debug_class_decorater(cls):
    if LINK_DEBUG_EN:
        def __deco_init__(self, *args, **kwargs):
            logging.debug("In decorater __init__")

        def __deco_del__(self, *args, **kwargs):
            logging.debug("In decorater __del__")

        cls.__init__ = __deco_init__
        cls.__del__ = __deco_del__
    else:
        pass

    return cls


@link_debug_class_decorater
class Link:
    def __init__(self):
        self.link_handler = None
        if "FTDI" in global_var.get_value("tif"):
            self.link_handler = FTDILink()
        else:
            self.link_handler = SWDJlink()

    def __del__(self):
        self.link_handler.__del__()

    @link_debug_decorater
    def read32(self, addr):
        return self.link_handler.read32(addr)

    @link_debug_decorater
    def write32(self, addr, data):
        self.link_handler.write32(addr, data)

    @link_debug_decorater
    def read_mem(self, addr, rlen):
        return self.link_handler.read_mem(addr, rlen)

    @link_debug_decorater
    def write_mem(self, addr, wdata):
        return self.link_handler.write_mem(addr, wdata)

    @link_debug_decorater
    def is_connected(self):
        return self.link_handler.is_connected()


@link_debug_class_decorater
class FTDILink:
    def __init__(self):
        self.ftdi_handler = None

        if global_var.get_value("tif") == "FTDI-SWD":
            self.__inner_mode = "SWD"
        elif global_var.get_value("tif") == "FTDI-JTAG":
            self.__inner_mode = "JTAG"

        try:
            self.ftdi_handler = ctypes.cdll.LoadLibrary(
                os.path.join(".dll", global_var.get_value("name").lower(), "SWDDRIVER2_LISTENAI.dll"))
        except Exception as exp:
            self.ftdi_handler = ctypes.cdll.LoadLibrary(
                os.path.join(".dll", global_var.get_value("name").lower(), "SWDDRIVER2_LISTENAI_x64.dll"))

        self.ftdi_handler.SPI_Connection(0)

    def __del__(self):
        self.ftdi_handler.SPI_Close()

    def read32(self, addr):
        data = ctypes.c_uint32(self.ftdi_handler.jtag_read_listenai(addr))
        return data.value

    def write32(self, addr, data):
        return self.ftdi_handler.jtag_write_listenai(addr, data)

    def read_mem(self, addr, rlen):
        pass

    def write_mem(self, addr, wdata):
        pass

    def is_connected(self):
        return True


@link_debug_class_decorater
class SWDJlink(pylink.JLink):
    def __init__(self):
        self.__jlink_dll = pylink.library.Library("JLink_x64.dll")
        super(SWDJlink, self).__init__(lib=self.__jlink_dll)
        self.core = global_var.get_value("core")
        self.open()
        if global_var.get_value("tif") == "JTAG":
            self.set_tif(pylink.enums.JLinkInterfaces.JTAG)
        elif global_var.get_value("tif") == "SWD":
            self.set_tif(pylink.enums.JLinkInterfaces.SWD)
        self.connect(self.core, verbose=True)
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
    __jlink_dll = pylink.library.Library("JLink_x64.dll")

    jtag = pylink.JLink(lib=__jlink_dll)
    jtag.open()
    jtag.set_tif(pylink.enums.JLinkInterfaces.JTAG)
    jtag.connect(chip_name="N308", verbose=True)
    print(jtag.core_id())

    print(jtag.device_family())

    print(jtag.connected()) # Ture
    print(jtag.target_connected()) # False
