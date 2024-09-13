import pylink
import pyaudio
import numpy as np
import wave
import struct
import ctypes


#
# class RTTRANS_INTERFACE_t(ctypes.Structure):
#     _pack_ = 1  # 强制1字节对齐
#     _fields_ = [
#         ("b_length", ctypes.c_uint32),
#         ("type", ctypes.c_uint32),
#         ("b_endpoint_address", ctypes.c_uint8),
#         ("control", ctypes.c_uint8),
#     ]
#
# # 解析字节流：先解析固定部分
# def parse_rttrans_interface(byte_stream):
#     # 先解析固定长度的部分 (b_length, type, b_endpoint_address, control)
#     fixed_size = ctypes.sizeof(RTTRANS_INTERFACE_t)
#     fixed_part = byte_stream[:fixed_size]
#
#     # 初始化 RTTRANS_INTERFACE_t 结构体
#     rttrans_fixed = RTTRANS_INTERFACE_t.from_buffer_copy(fixed_part)
#
#     # 动态解析 data 部分，根据 b_length 计算实际 data 的长度
#     data_size = rttrans_fixed.b_length - fixed_size
#     data_part = byte_stream[fixed_size:fixed_size + data_size]
#
#     # 定义一个新的动态结构体，包括实际的 data 长度
#     class DynamicRTTRANS_INTERFACE_t(ctypes.Structure):
#         _pack_ = 1  # 强制1字节对齐
#         _fields_ = [
#             ("b_length", ctypes.c_uint32),
#             ("type", RTTRANS_TYPE_t),
#             ("b_endpoint_address", ctypes.c_uint8),
#             ("control", ctypes.c_uint8),
#             ("data", ctypes.c_uint8 * data_size)
#         ]
#
#     # 使用字节流重新填充结构体，包含动态 data 长度
#     # complete_stream = byte_stream[:fixed_size + data_size]
#     rttrans_complete = DynamicRTTRANS_INTERFACE_t.from_buffer_copy(byte_stream)
#
#     return rttrans_complete
#
# # 假设接收到的字节流
# byte_stream = b'\x0D\x00\x00\x00'  # b_length = 10
# byte_stream += b'\x01\x00\x00\x00'  # type = 1
# byte_stream += b'\x81'  # b_endpoint_address = 0x81
# byte_stream += b'\x01'  # control = 0x1
# byte_stream += b'\x01\x02\x03'  # data = [0x01, 0x02, 0x03]
# # 测试解析
# rttrans_instance = parse_rttrans_interface(byte_stream)
# print("b_length:", rttrans_instance.b_length)
# print("type:", rttrans_instance.type)
# print("b_endpoint_address:", rttrans_instance.b_endpoint_address)
# print("control:", rttrans_instance.control)
# print("data:", list(rttrans_instance.data))

# 设置音频流参数
FORMAT = pyaudio.paInt16  # 数据格式 (这里假设是 16-bit)
CHANNELS = 1              # 声道 (单声道)
RATE = 16000              # 采样率 (每秒44100个采样点)

# 初始化pyaudio
p = pyaudio.PyAudio()

# 打开流进行播放
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True)

# 创建J-Link对象
jlink = pylink.JLink()

# 连接到目标设备
jlink.open()
jlink.connect('N308')  # 根据实际的目标芯片设置

# 启动RTT
jlink.rtt_start(int('0x8ae8', base=16))

with open("rawdata", mode="wb") as f:
    while True:
        # 从RTT通道读取数据 (通道0)
        data_read = jlink.rtt_read(0, 640)  # 从通道0读取最多1024字节的数据

        if data_read:
            print(", ".join([hex(item) for item in data_read]))

            num_samples = len(data_read) // 2  # 每个样本是2个字节
            fmt = f'<{num_samples}h'  # 解释为小端16位有符号整数
            audio_data = struct.unpack(fmt, bytes(data_read))

            audio_array = np.array(audio_data, dtype=np.int16)
            f.write(bytes(data_read))

            stream.write(audio_array.tobytes())
            print("write")
        else:
            pass
