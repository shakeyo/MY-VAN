# 能源设备集成

485 总线上的能源设备协议与集成方案。ESPHome 固件统一在 [gateway/esphome](../gateway/esphome/)（单 ESP32 集中编译），本模块只放设备协议与方案文档。

| 设备 | 485 支持 | 地址 | 文档 | 状态 |
|------|----------|------|------|------|
| MPPT（易科 Fcu） | 支持（9600，协议 V1.2） | 0x10 | [mppt-protocol.md](mppt-protocol.md) | 协议已解读，桌面验证待做 |
| 库仑计 PZEM-017 | 支持（9600，Modbus） | 0x11 | [pzem-017.md](pzem-017.md)（占位） | 待购；同挂 9600 总线，48V 电池电压/电流/功率监测 |
| DC-DC 行车充电器 | **不支持 485** | — | — | 通断控制无协议可用；切换方案（输出侧接触器）暂缓，见 [04-power-system](../../04-power-system/) |

> 与 MPPT 相关的物理接线（DC 输出口 → 空气开关 → 汇流排 → 电池、待机断电接触器通道 额头.R6）记录在 [04-power-system/switch-assignment.md](../../04-power-system/switch-assignment.md)。
