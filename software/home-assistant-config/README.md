# Home Assistant 配置模板

本目录包含 VAN-PROJECT 的 Home Assistant 配置模板。将这些文件放入 HA 的 `/config` 目录即可使用。

## 文件说明

| 文件 | 说明 |
|------|------|
| `configuration.yaml` | 主配置文件，包含 Modbus、MQTT、传感器定义 |
| `automations.yaml` | 自动化场景（驻车/离车/影院/休息模式） |
| `modbus.yaml` | RS485 Modbus 设备详细配置 |
| `esp32-buttons.yaml` | ESPhome 驾驶室按钮面板配置 |

## 使用方式

1. 将这些文件放入 HA 配置目录（默认为 `/opt/ha/config/`）
2. 根据实际硬件修改设备地址和参数
3. 重启 Home Assistant 使配置生效
