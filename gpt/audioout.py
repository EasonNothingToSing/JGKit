import pyaudio
import wave

# 设置音频流参数
FORMAT = pyaudio.paInt16  # 数据格式 (这里假设是 16-bit)
CHANNELS = 1              # 声道 (单声道)
RATE = 16000              # 采样率 (每秒44100个采样点)
CHUNK = 1024              # 每次读取的帧数

# 初始化pyaudio
p = pyaudio.PyAudio()

# 打开流进行播放
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True)

# 打开原始音频文件 (.raw)
with open('audio.raw', 'rb') as f:
    # 每次读取1024字节（即1个chunk），直到文件结束
    data = f.read(CHUNK)
    while data:
        stream.write(data)  # 播放数据
        data = f.read(CHUNK)

# 停止流
stream.stop_stream()
stream.close()

# 关闭 PyAudio
p.terminate()
