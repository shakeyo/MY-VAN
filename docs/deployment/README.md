# 部署指南

本文档涵盖 VAN-PROJECT 智能控制系统从零搭建的完整流程。

## 架构总览

```
┌─────────────────────────────────────────────────┐
│                  N100 迷你主机 (PVE)               │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ HA HAOS  │  │ Frigate  │  │ Mosquitto    │   │
│  │ (中控)   │  │ (AI监控) │  │ (MQTT Broker)│   │
│  └────┬─────┘  └────┬─────┘  └──────┬───────┘   │
│       │              │               │            │
└───────┼──────────────┼───────────────┼────────────┘
        │              │               │
   ┌────▼────┐    ┌────▼────┐    ┌─────▼──────┐
   │ RS485   │    │ AHD攝像 │    │ ESP32      │
   │ 继电器   │    │ DVR編碼 │    │ 控制板     │
   │ 灯光水泵 │    │ RTSP流  │    │ 物理開關   │
   └─────────┘    └─────────┘    └────────────┘
```

## 硬件清单

| 设备 | 推荐型号 | 用途 |
|------|----------|------|
| 计算主机 | N100 迷你主机 (16G RAM, 512G SSD) | PVE 虚拟化平台 |
| 路由器 | GL.iNet MT3000 / Cudy WR3000 | 车内局域网 + 4G/5G 上网 |
| 485 网关 | ESP32-S3 + MAX3485（ESPHome） | 485 总线桥接 HA（原生，非 USB-485） |
| 继电器模块 | 485 继电器模块化：额头8/中8/中4/车尾4（9600 8N1） | 全车灯光/水泵/风扇控制 + 按键 DI |
| 摄像头 | AHD 1080P × 4 | 四路监控 |
| DVR 编码器 | AHD → RTSP 网络编码器 | 模拟摄像头数字化 |
| OBD-II | ELM327 蓝牙版 | 车辆数据读取（蓝牙→车机→MQTT） |

## 部署步骤

按以下顺序部署，每一步都依赖前一步：

1. **[PVE 基础环境](./pve-setup.md)** — 安装 Proxmox VE，配置网络与存储
2. **[Home Assistant](./home-assistant.md)** — 安装 HA，接入 RS485/Modbus 设备
3. **[Frigate NVR](./frigate.md)** — AI 视频监控部署
4. **[仪表盘](./dashboard.md)** — 部署 rv-smart-dashboard

## 网络规划

### 车内局域网（终局）

```
子网: 192.168.8.0/24 (GL.iNet 路由器默认)

  192.168.8.1    — GL.iNet 路由器 (网关 + DHCP)
  192.168.8.10   — N100 PVE 管理 IP
  192.168.8.11   — Home Assistant (HAOS 虚拟机)
  192.168.8.12   — Frigate (LXC)
  192.168.8.13   — Mosquitto MQTT (LXC)
  192.168.8.20   — ESP32 控制板
  192.168.8.30   — 安卓车机 (Dashboard)
  192.168.8.100  — DVR 编码器

DHCP 池: 192.168.8.150-192.168.8.250
```

选 `192.168.8.0/24` 的理由：**GL.iNet 路由器默认网段，开箱即用无需改**；
且 ESP32 的 `.20` 在 DHCP 池外，与自动分配地址不会冲突。

### 三张网必须互不冲突（Tailscale 前置约束）

| 场景 | SSID | 网段 | 状态 |
|------|------|------|------|
| 家里 | `ooxx` | `192.168.5.0/24` | 已用 |
| 车上（过渡） | `iWife`（手机热点） | `172.20.10.0/24` | 已用，无路由器时 |
| 车上（终局） | GL.iNet | `192.168.8.0/24` | 待部署 |
| Tailscale 虚拟网 | — | `100.64.0.0/10` | Tailscale 自管，**不要动** |

> ⚠️ **硬约束：家里与车里的局域网网段必须不同。**
> 若两边都是 `192.168.8.0/24`，Tailscale 子网路由会因路由表无法区分
> 「同一个 `192.168.8.x` 属于哪一边」而**必然冲突**，这是 Tailscale
> 最经典的翻车点。本项目家里 `192.168.5.x` / 车里 `192.168.8.x` 天然满足。
>
> iPhone 个人热点的 `172.20.10.x` 也与此二者不冲突，可放心作为车上过渡网络。

### Tailscale 接法：用子网路由，**不要改局域网网段**

在 **GL.iNet 路由器**上安装 Tailscale，并开启 **Subnet Router**，
对外广告车内网段 `192.168.8.0/24`：

```
家中设备 ──连上 Tailscale──▶ 直连 192.168.8.11 (HA) / .20 (ESP32) / .10 (PVE)
```

这样在家里就能直接访问车内全部设备，**无需修改任何设备的 IP 或网段**。
把 Tailscale 装在路由器而非 N100 上，是为了「网络转发」与「智能计算」分离
（重启 PVE 不会中断远程连接，见 [archive/ai-conversations.md](../../archive/ai-conversations.md)）。

> **HA 侧还有第二个 Tailscale 入口**：本项目 HA 为 **HAOS（Supervisor 版）PVE 虚拟机**
> （定稿见 [n100-ha/design.md](../../modules/10-smart-control/n100-ha/design.md)），
> 其 Tailscale 走 **add-on** 安装——这是**独立的第二条路径**，与路由器的子网路由并存：
> 路由器那条负责访问车内**局域网设备**（N100/ESP32/摄像头），HA add-on 这条负责
> 访问 **HA 本体**。两者认证到同一个 tailnet，互不冲突。

### ESP32 固件的网络约定

- **不要设 `use_address`**：写死 IP 会让 OTA 在换网段后失效（如在家 `192.168.5.18`
  写的固件拿到车上 `192.168.8.x` 就连不上）。留空时 ESPHome 自动用 mDNS
  `${name}.local`（本机为 `myvan-485-gateway.local`），**任何网段都能 OTA**。
- **SSID/密码集中在 `secrets.yaml`**（`modules/10-smart-control/gateway/esphome/`，
  权限 `600`，已在 `.gitignore` 中排除）。当前 4 份固件共用 `wifi_home_*`、
  `wifi_phone_*`、`wifi_van_*` 三组变量，按 `networks:` 顺序依次尝试。
- 路由器到位后：改 `secrets.yaml` 的 `wifi_van_*`，再取消 4 份 yaml 里
  `wifi_van_*` 两行的注释（**共 4 处，一处不漏**，与 `baud_rate` 改造同理）。
- **首次烧录必须 USB**：设备联网后才能走 OTA；改 WiFi 配置的那一次也需 USB。

## 快速开发环境

如果只是想先在笔记本上体验和开发仪表盘，不需要 N100 硬件：

```bash
# 进入 dev-environment 目录
cd software/dev-environment

# 启动 HA + MQTT 开发环境
docker compose up -d

# HA 访问 http://localhost:8123
# MQTT 端口 localhost:1883

# 然后启动仪表盘
cd ../rv-smart-dashboard
pnpm install && pnpm dev
```

详细说明见 [dev-environment 开发环境](../../software/dev-environment/)。
