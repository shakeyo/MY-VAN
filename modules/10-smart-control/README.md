# 智能控制系统

三级智能控制架构：**N100 Home Assistant 中枢 → ESP32 RS485 总线网关 → 分布式继电器终端**。传统房车控制要么全手动（开关直接控制负载，无远程无自动化），要么全集中（一个弱 MCU 管所有，单点故障全车瘫痪）。本方案取两者之长：自动化分层——安全关键自动化在边缘（ESPHome 本地跑，断网可用）、展示与高阶能力在中枢（HA Dashboard、历史统计、远程访问、通知）、执行在终端（继电器模块带物理按钮冗余）。

**核心逻辑**：**本地自动化优先、中枢增强不接管**。HA 挂掉不影响物理按钮开关灯、不影响 ESPHome 本地自动化（按键联动/离车模式/低温禁充/待机断电）；485 总线断线不影响已下发的继电器状态；手机/平板/安卓车机三个 Dashboard 互为备份。

**HA 角色边界**（定稿原则见 [n100-ha/design.md](n100-ha/design.md)）：统一 UI、历史与能源面板、远程访问入口、推送通知、非关键高阶自动化、多源汇聚。**HA 不承载安全关键自动化**——此原则固定，避免后期自动化放置混乱。

## 子系统

| 目录 | 内容 | 状态 |
|------|------|------|
| [n100-ha/](n100-ha/) | N100 主机、HA Core、网络、安卓车机 | 设计中 |
| [gateway/](gateway/) | ESP32-S3 网关、MAX3485、485 总线、ESPHome 固件、继电器模块集成 | 调试中 |
| [energy/](energy/) | 能源设备 485 集成：MPPT（易科）、库仑计 PZEM-017 | 设计中 |
| [sensors/](sensors/) | 温湿度、水位、门磁、漏水、OBD-II | 设计中 |
| [media/](media/) | 监控（DVR/Frigate）+ 音响（Alpine DSP） | 设计中 |

## 实施顺序

1. 网络与中枢搭建（N100 + 路由器 + HA）
2. 485 总线与继电器模块安装
3. ESP32 网关部署与 ESPHome 烧录
4. 驾驶室按钮面板安装
5. 传感器接入与 HA 集成（Dashboard/能源面板/通知，自动化边界见 n100-ha/design.md）
6. 安卓车机 + Dashboard + 音响调试

## 图片

<script setup>
const loaders = Object.values(import.meta.glob('./assets/*.{png,jpg,jpeg,PNG,JPG,JPEG,webp}', { eager: false }))
</script>

<AutoGallery :loaders="loaders" />
