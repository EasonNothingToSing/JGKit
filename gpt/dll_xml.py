import ctypes

# 加载 DLL
jlink_dll = ctypes.CDLL("C:/Program Files (x86)/SEGGER/JLink/Jlink_x64.dll")

# 定义函数原型
jlink_dll.JLINKARM_ExecCommand.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
jlink_dll.JLINKARM_ExecCommand.restype = ctypes.c_int

# 执行命令
cmd = b"JLinkDevicesXMLPath E:\\APP\\python_project\\JGKit\\JLinkDevices"
result = ctypes.create_string_buffer(256)
ret = jlink_dll.JLINKARM_ExecCommand(cmd, result, 256)
print(f"Result: {result.value.decode()}")

# 打开 J-Link
jlink_dll.JLINKARM_Open()
jlink_dll.JLINKARM_ExecCommand(b"device = Arcs", result, 256)
jlink_dll.JLINKARM_ExecCommand(b"connect", result, 256)
print(f"Connected: {result.value.decode()}")


def list_devices():
    # 打开 J-Link 连接
    ret = jlink_dll.JLINKARM_Open()
    if ret < 0:
        print(f"Failed to open J-Link: {ret}")
        return

    # 遍历设备
    devices = []
    index = 0
    while True:
        device_info = JLINKARM_DEVICE_INFO()
        ret = jlink_dll.JLINKARM_DEVICE_GetInfo(index, ctypes.byref(device_info))
        if ret < 0:  # 返回负值表示没有更多设备
            break

        # 获取设备名称（转为 Python 字符串）
        device_name = device_info.sName.decode('utf-8') if device_info.sName else "Unknown"
        devices.append({
            "index": index,
            "name": device_name,
            "description": device_info.sDescription.decode('utf-8') if device_info.sDescription else "",
            "core_id": device_info.CoreId,
            "flash_size": device_info.FlashSize,
            "ram_size": device_info.RAMSize,
            "vendor_id": device_info.VendorId
        })
        index += 1

    # 关闭 J-Link 连接
    jlink_dll.JLINKARM_Close()

    # 输出设备列表
    print(f"Loaded {len(devices)} devices:")
    for dev in devices:
        print(f"Index: {dev['index']}, Name: {dev['name']}, CoreID: {hex(dev['core_id'])}, "
              f"Flash: {dev['flash_size']} bytes, RAM: {dev['ram_size']} bytes")


# 执行
list_devices()

# # 关闭
# jlink_dll.JLINKARM_Close()