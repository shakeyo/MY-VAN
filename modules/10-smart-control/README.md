# 智能控制系统

三级智能控制架构：**N100 Home Assistant 中枢 → ESP32 RS485 总线网关 → 分布式继电器终端**。传统房车控制要么全手动（开关直接控制负载，无远程无自动化），要么全集中（一个弱 MCU 管所有，单点故障全车瘫痪）。本方案取两者之长：自动化分层——安全关键自动化在边缘（ESPHome 本地跑，断网可用）、展示与高阶能力在中枢（HA Dashboard、历史统计、远程访问、通知）、执行在终端（继电器模块带物理按钮冗余）。

**核心逻辑**：**本地自动化优先、中枢增强不接管**。HA 挂掉不影响物理按钮开关灯、不影响 ESPHome 本地自动化（按键联动/离车模式/低温禁充/待机断电）；485 总线断线不影响已下发的继电器状态；手机/平板/安卓车机三个 Dashboard 互为备份；中控台机器人（语音/表情/动作）是第四个交互入口，大脑同样在 N100。

**HA 角色边界**（定稿原则见 [n100-ha/design.md](n100-ha/design.md)）：统一 UI、历史与能源面板、远程访问入口、推送通知、非关键高阶自动化、多源汇聚。**HA 不承载安全关键自动化**——此原则固定，避免后期自动化放置混乱。

**先看图**：

- [smart-architecture.svg](./diagrams/smart-architecture.svg) — 三级架构总图（中枢/边缘/终端 + 全部交互入口）
- [network-topology.svg](./diagrams/network-topology.svg) — 车内网络与 IP 规划
- 485 总线物理拓扑见 [04-power-system/485-bus.svg](../04-power-system/diagrams/485-bus.svg)，按键接线见 [04-power-system/button-wiring.svg](../04-power-system/diagrams/button-wiring.svg)

## 📖 施工阅读指南（按顺序读）

| 顺序 | 文档 | 看什么 |
|------|------|--------|
| 1 | [build-guide.md](build-guide.md) | **施工主线**：10 个阶段按序执行，每阶段有入口条件 / 验收点 / 配图 |
| 2 | [n100-ha/design.md](n100-ha/design.md) | HA 角色边界（定稿）、N100/网络/车机/平板方案 |
| 3 | [gateway/design.md](gateway/design.md) + [gateway/build-guide.md](gateway/build-guide.md) | 网关架构 + 485 总线规范（9600 定稿）+ 制作/烧录/总线改造全流程 |
| 4 | [energy/](energy/) | MPPT 协议速查与自动化规划、PZEM-017 集成 |
| 5 | [sensors/](sensors/) · [media/](media/) · [robot/](robot/) | 传感器三路径、监控/音响链路、机器人架构（均含定稿边界） |
| 6 | 各子目录 `bom.md` | 材料清单（按阶段采购） |

## 🏗️ 施工主线（详见 [build-guide.md](build-guide.md)）

| 阶段 | 目标 | 出口验收 |
|------|------|----------|
| 0 中枢与网络 | N100 PVE + HAOS + add-on + 路由器 + 固定 IP | HA 可访问、Tailscale 车外可达 |
| 1 485 总线就绪 | 模块就位（中8/中4 已接线未通电）、总线菊花链 + 120Ω | 与 [04-power-system 阶段 2/4](../04-power-system/build-guide.md) 验收一致 |
| 2 网关上车 | 面包板自测 → 烧录 → 桌面中8 全逻辑 → 组装 → 车上接线 | gateway/build-guide 4.6 通道映射通过 |
| 3 模块通电与按键 | 插 F12-1 保险 → prod.yaml → 全按键/场景验证（含断网） | 按键/场景/断电恢复全过 |
| 4 总线改造 9600 | 逐台改波特率 + 固件切 9600（**MPPT 上车前必做**） | 4 模块 9600 读回通过，prod 复验 |
| 5 能源设备 | MPPT 桌面协议验证 → 上车 → mppt.yaml → 待机断电/低温禁充联调 | HA 能源面板有数据，自动化生效 |
| 6 传感器 | DI（门磁/漏水）+ 485（温湿度/水位）+ OBD（蓝牙→MQTT） | 全部实体在 HA 上线 |
| 7 显示终端 | 车机 Fully Kiosk、平板直供电改造、手机 Companion | 三端可看可控 + 推送到达 |
| 8 监控音响 | DVR 四路 + Frigate；音响接线 + 声场预设 | 监控画面/告警 + 三声场切换 |
| 9 机器人（后期） | 选型 → 表情屏/舵机 → HA Assist 语音管线 | 语音控制全车 |

## 子系统

| 目录 | 内容 | 状态 |
|------|------|------|
| [n100-ha/](n100-ha/) | N100 主机、HA Core、网络、安卓车机、平板移动中控 | 设计中 |
| [gateway/](gateway/) | ESP32-S3 网关、MAX3485、485 总线（9600 定稿）、ESPHome 固件、继电器模块集成 | 调试中 |
| [energy/](energy/) | 能源设备 485 集成：MPPT（易科）、库仑计 PZEM-017 | 设计中 |
| [sensors/](sensors/) | 温湿度、水位、门磁、漏水、OBD-II（三条接入路径） | 设计中 |
| [media/](media/) | 监控（DVR/Frigate）+ 音响（Alpine DSP） | 设计中 |
| [robot/](robot/) | 中控台 DIY 表情机器人：语音（HA Assist）+ 表情 + 舵机动作控制全车 | 设计中（待选型） |

## 配图索引

| 图 | 文件 | 什么时候看 |
|----|------|-----------|
| 三级架构总图 | [diagrams/smart-architecture.svg](./diagrams/smart-architecture.svg) | 开工前理解全局 + 分工边界 |
| 车内网络拓扑 | [diagrams/network-topology.svg](./diagrams/network-topology.svg) | 阶段 0：网络布线/IP 分配 |
| 传感器三条接入路径 | [diagrams/sensors-paths.svg](./diagrams/sensors-paths.svg) | 阶段 6：传感器选型/接线 |
| 监控与音响链路 | [diagrams/media-chain.svg](./diagrams/media-chain.svg) | 阶段 8：监控/音响施工 |
| 网关硬件接线 | [gateway/diagrams/gateway-wiring.svg](gateway/diagrams/gateway-wiring.svg) | 阶段 2：网关组装焊接 |
| 485 总线拓扑 | [../04-power-system/diagrams/485-bus.svg](../04-power-system/diagrams/485-bus.svg) | 阶段 1：总线布线 |
| 单按键 3 回路 | [../04-power-system/diagrams/button-wiring.svg](../04-power-system/diagrams/button-wiring.svg) | 阶段 3：按键排查 |

> 施工过程照片拍摄规范见 [build-guide.md §十](build-guide.md#十、施工照片拍摄规范)。

## 图片

<script setup>
const loaders = Object.values(import.meta.glob('./assets/*.{png,jpg,jpeg,PNG,JPG,JPEG,webp}', { eager: false }))
</script>

<AutoGallery :loaders="loaders" />