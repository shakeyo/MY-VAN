# 能源设备集成

485 总线上的能源设备协议与集成方案。ESPHome 固件统一在 [gateway/esphome](../gateway/esphome/)（单 ESP32 集中编译），本模块只放设备协议与方案文档。

| 设备 | 485 支持 | 地址 | 文档 | 状态 |
|------|----------|------|------|------|
| MPPT（易科 Fcu） | 支持（9600，协议 V1.2） | 0x10 | [mppt-protocol.md](mppt-protocol.md) | 协议已解读，桌面验证待做 |
| 库仑计 **TF03K** | 支持（**19200，私有主动上报，非 Modbus**） | **无地址** | [coulomb-tf03k.md](coulomb-tf03k.md) | **固件已就绪**；⚠ 19200 独立 UART（只收），不并入 9600 总线 |
| DC-DC 行车充电器 | **不支持 485** | — | — | 通断控制无协议可用；切换方案（输出侧接触器）暂缓，见 [04-power-system](../../04-power-system/) |
| **JK BMS（极空，电池自带）** | — | — | [jk-bms-integration.md](jk-bms-integration.md) | **只能走 BLE**（⚠ 电池已封箱，主控板在内部，**接不到 UART**）。方案已定，暂不实施；BLE 天然电气隔离，可读 16 节单体电压/压差/循环次数 |
| **逆变器 5000W** | 私有协议（未逆向） | — | [switch-assignment.md §决6](../../04-power-system/switch-assignment.md) | **已购**；采用**继电器短接 RJ 口**控制，⚠ 直流侧 116A 需 ≥25mm² 线 |

> ⚠️ **库仑计总线独立性**：TF03K 固定 **19200 + 只发不收 + 无地址 + 8 位累加和**，与全车 9600 Modbus 总线
> （MPPT 0x10、继电器 1/2/3/5）**协议和波特率都不同，严禁同挂一根 A/B 线**。
> 必须走网关 ESP32 的**第二路 UART**（仅接收，无需 DE 方向控制）。详见 [coulomb-tf03k.md 第四节](coulomb-tf03k.md#四总线与接线)。

> 与 MPPT 相关的物理接线（DC 输出口 → 空气开关 → 汇流排 → 电池、待机断电接触器通道 额头.R6）记录在 [04-power-system/switch-assignment.md](../../04-power-system/switch-assignment.md)。
