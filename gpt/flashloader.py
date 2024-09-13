import pylink
import ctypes

# jlink_dll_path = "../JLinkARM.dll"
my_dll = ctypes.windll.LoadLibrary("../JLinkARM.dll")
# 创建JLink对象
jlink = pylink.JLink()

# 连接到J-Link设备
jlink.open()
jlink.connect('N308')  # 替换为你的设备类型

# 加载J-Link设备配置文件
# jlink.set_device_xml('tools/flash_tool/JLinkDevices.xml')

my_dll.JLINKARM_SetDeviceXML("tools/flash_tool/JLinkDevices.xml")

# 打开二进制文件
with open('mars/pmu.bin', 'rb') as f:
    data = f.read()

# 编程Flash
jlink.flash_write(0x30000000, data)

# 验证编程
read_data = jlink.memory_read(0x30000000, len(data))
assert data == read_data, "Verification failed!"

# 关闭连接
jlink.close()
