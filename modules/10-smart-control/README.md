# 智能控制系统

三级智能控制架构：**N100 Home Assistant 中枢 → ESP32 RS485 总线网关 → 分布式继电器终端**。传统房车控制要么全手动（开关直接控制负载，无远程无自动化），要么全集中（一个弱 MCU 管所有，单点故障全车瘫痪）。本方案取两者之长：计算在中枢（HA 自动化、Dashboard、语音）、控制在边缘（ESP32 本地逻辑不依赖网络）、执行在终端（继电器模块带物理按钮冗余）。

**核心逻辑**：计算中心化、控制去中心化、冗余机械化。HA 挂掉不影响物理按钮开关灯；485 总线断线不影响已下发的继电器状态；手机/平板/安卓车机三个 Dashboard 互为备份。

## 子系统

| 目录 | 内容 | 状态 |
|------|------|------|
| [n100-ha/](n100-ha/) | N100 主机、HA Core、网络、安卓车机 | 设计中 |
| [esp32-485/](esp32-485/) | ESP32 网关、MAX485、485 总线、ESPHome 固件 | 设计中 |
| [relays/](relays/) | 485 继电器模块、物理按钮、双控逻辑 | 设计中 |
| [sensors/](sensors/) | 温湿度、电量计、水位、门磁、漏水、OBD-II | 设计中 |
| [media/](media/) | 监控（DVR/Frigate）+ 音响（Alpine DSP） | 设计中 |

## 实施顺序

1. 网络与中枢搭建（N100 + 路由器 + HA）
2. 485 总线与继电器模块安装
3. ESP32 网关部署与 ESPHome 烧录
4. 驾驶室按钮面板安装
5. 传感器接入与 HA 自动化
6. 安卓车机 + Dashboard + 音响调试

## 图片

<script setup>
const loaders = Object.values(import.meta.glob('./assets/*.{png,jpg,jpeg,PNG,JPG,JPEG,webp}', { eager: false }))
</script>

<AutoGallery :loaders="loaders" />
