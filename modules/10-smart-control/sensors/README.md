# 传感器

温湿度、水位、门磁、漏水、OBD-II 车辆数据采集。485 传感器总线并联接入，干接点传感器走继电器模块 DI 口，不占用 ESP32 GPIO。

| 文件 | 内容 |
|------|------|
| [design.md](design.md) | 传感器列表、接入方式、跨模块引用 |
| [bom.md](bom.md) | 材料清单 |

## 边界

- 电量计（PZEM-017）已归入 [energy/](../energy/) 能源设备集成
- 设备安装位置见 [04-power-system](../../04-power-system/)
