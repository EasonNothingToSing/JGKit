import pylink
import pyaudio
import numpy as np
import wave
import struct

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
jlink.rtt_start(int('0xa400', base=16))

while True:
    data_read = jlink.rtt_read(0, 16)

    if data_read:
        print(data_read)

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
