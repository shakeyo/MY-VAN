# ESP32 485 网关

ESP32-S3 + MAX3485 单板网关，ESPHome 固件统一集中编译，负责 485 总线（继电器模块、能源设备）与 HA/物理按键之间的桥接。

| 文件 | 内容 |
|------|------|
| [design.md](design.md) | 架构、485 总线规范、ESP32↔MAX3485 接线、供电 |
| [build-guide.md](build-guide.md) | 制作步骤、烧录与调试、总线改造操作 |
| [bom.md](bom.md) | 材料清单 |
| [esphome/](esphome/) | 固件 YAML（base/prod/forehead/mid4/mid8/scenes/测试件） |

## 边界

- 继电器模块通道分配见 [04-power-system/switch-assignment.md](../../04-power-system/switch-assignment.md)
- MPPT 协议与能源设备集成见 [energy/](../energy/)，MPPT 固件规划 [esphome/mppt.yaml](esphome/mppt.yaml)（待建）
