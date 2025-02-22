from miio import Gateway
gateway = Gateway("10.31.1.21", "4a7a547067626a674976794d4a646d63")
devices = gateway.devices()  # 获取所有设备
for device in devices:
    if "temperature" in device.capabilities:
        print(f"设备名称：{device.name}, 温度：{device.temperature}°C, 湿度：{device.humidity}%")