import ctypes
import pylink

class RTTRANS_INTERFACE_t(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("b_length", ctypes.c_uint32),
        ("type", ctypes.c_uint32),
    ]


class RTTRANS_INTERFACE_AUDIO_DATA_t(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("control", ctypes.c_uint32),
    ]


class RTTRANS_INTERFACE_AUDIO_CONFIG_t(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("chunk", ctypes.c_uint16),
        ("endpoint", ctypes.c_uint8),
        ("channel", ctypes.c_uint8),
        ("frequence", ctypes.c_uint16),
        ("format", ctypes.c_uint32),
    ]


class RTTRANS_INTERFACE_AUDIO_START_t(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("name_length", ctypes.c_uint8),
    ]


class RttransParse:
    RTTRANS_PROFILE_TYPE_AUDIO = 0
    RTTRANS_PROFILE_TYPE_LOG = 1

    def __init__(self):
        pass

    def parse_rttrans_interface(self, byte_stream):
        fixed_size = ctypes.sizeof(RTTRANS_INTERFACE_t)
        fixed_part = byte_stream[:fixed_size]
        b_stream = byte_stream[fixed_size:]

        # Get rttheader
        rttrans_fixed = RTTRANS_INTERFACE_t.from_buffer_copy(fixed_part)

        data_size = rttrans_fixed.b_length - fixed_size
        if rttrans_fixed.type == RttransParse.RTTRANS_PROFILE_TYPE_AUDIO:
            print("audio")
            fixed_size = ctypes.sizeof(RTTRANS_INTERFACE_AUDIO_DATA_t)
            fixed_part = b_stream[: fixed_size]
            b_stream = b_stream[fixed_size:]

            rttrans_fixed = RTTRANS_INTERFACE_AUDIO_DATA_t.from_buffer_copy(fixed_part)
            if rttrans_fixed.control == 0:
                print("audio configure")
                fixed_size = ctypes.sizeof(RTTRANS_INTERFACE_AUDIO_CONFIG_t)
                fixed_part = b_stream[: fixed_size]
                b_stream = b_stream[fixed_size:]

                rttrans_fixed = RTTRANS_INTERFACE_AUDIO_CONFIG_t.from_buffer_copy(fixed_part)

                print("channel: %d;  format: %d;  frequence: %d" % (rttrans_fixed.channel, rttrans_fixed.format,
                                                                    rttrans_fixed.frequence))
            elif rttrans_fixed.control == 1:
                print("audio start")
            elif rttrans_fixed.control == 2:
                print("audio stop")

        elif rttrans_fixed.type == RttransParse.RTTRANS_PROFILE_TYPE_LOG:
            pass


if __name__ == "__main__":
    rtt = RttransParse()

    jlink = pylink.JLink()

    # 连接到目标设备
    jlink.open()
    jlink.connect('N308')  # 根据实际的目标芯片设置

    # 启动RTT
    jlink.rtt_start(int('0xa408', base=16))

    while True:
        data_read = jlink.rtt_read(0, 640)

        if data_read:
            b_stream = bytes(data_read)
            rtt.parse_rttrans_interface(b_stream)

