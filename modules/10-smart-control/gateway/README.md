# ESP32 485 网关

ESP32-S3 + MAX3485 单板网关，ESPHome 固件统一集中编译，负责 485 总线（继电器模块、能源设备）与 HA/物理按键之间的桥接。

| 文件 | 内容 |
|------|------|
| [design.md](design.md) | 架构、485 总线规范、ESP32↔MAX3485 接线、供电 |
| [build-guide.md](build-guide.md) | 制作步骤、烧录与调试、总线改造操作 |
| [bom.md](bom.md) | 材料清单 |
| [esphome/](esphome/) | 固件 YAML（rs485/base/prod/forehead/mid4/mid8/do16/scenes/panel/scene-state/测试件）+ 自包含手机面板 |

## 边界

- 继电器模块通道分配见 [04-power-system/switch-assignment.md](../../04-power-system/switch-assignment.md)
- MPPT 协议与能源设备集成见 [energy/](../energy/)，MPPT 固件规划 `esphome/mppt.yaml`（待建，见 [esphome/](esphome/) 目录页）

## 手机控制面板（`http://<esp32-ip>/dashboard`）

固件内置一个自包含深蓝 UI（复刻 RV Dashboard 主题），由 ESP32 直接 serve，离线可用。
开关/光伏/场景档位均为真实数据（页面 fetch 轮询 ESPHome 原生 REST）。

- 机制与入口：见 [esphome/README.md](esphome/README.md)「手机控制面板」小节
- 如何重编译/重烧：见 [build-guide.md §6.5](build-guide.md)
