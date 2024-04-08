import ctypes
#
my_dll = ctypes.windll.LoadLibrary("../Jlink_x64.dll")
# # Open USB
my_dll.JLINKARM_SelectUSB(0)
# Connect to JLINK
my_dll.JLINKARM_Open()

uint_var = ctypes.c_uint32()

my_dll.JLINKARM_TIF_GetAvailable(ctypes.byref(uint_var))
print(uint_var.value)

value = my_dll.JLINKARM_TIF_Select(7)
print("prv: ", ctypes.c_uint32(value).value)

# my_dll.JLINKARM_DEVICE_GetIndex("N308".encode("ascii"))
err_buf = (ctypes.c_char * 336)()
# my_dll.JLINKARM_ExecCommand("Tif = T".encode(), err_buf, 336) // error
# err_buf = ctypes.string_at(err_buf).decode()
# print("TIF:", err_buf)

my_dll.JLINKARM_ExecCommand("Device = N308".encode(), err_buf, 336)
err_buf = ctypes.string_at(err_buf).decode()
print("DEVICE:", err_buf)

result = my_dll.JLINKARM_Connect()
print("RESULT:", result)


value = my_dll.JLINKARM_ReadMem(0, 4, ctypes.byref(uint_var))
print("ret: ", value)
print("value: ", hex(uint_var.value))

my_dll.JLINKARM_Close()
