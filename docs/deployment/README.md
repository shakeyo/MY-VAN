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
4. **[Windows 调试机与核显直通](./n100-windows-gpu-passthrough.md)** — 车内调试 485 的 Windows 终端（RDP 远程 + HDMI 直显）
5. **[车机面板](./dashboard.md)** — ESP32 自托管深蓝 UI（`/dashboard`，离线可用）

## 网络规划

### 车内局域网（终局）

```
子网: 192.168.10.0/24（车内 Cudy 路由器 LAN；家里是 192.168.5.0/24，互不冲突）

  192.168.10.1    — GL.iNet 路由器 (网关 + DHCP)
  192.168.10.10   — N100 PVE 管理 IP
  192.168.10.11   — Home Assistant (HAOS 虚拟机)
  192.168.10.12   — Frigate (LXC)
  192.168.10.13   — Mosquitto MQTT (LXC)
  192.168.10.20   — ESP32 控制板
  192.168.10.30   — 安卓车机 (Dashboard)
  192.168.10.100  — DVR 编码器

DHCP 池: 192.168.10.150-192.168.10.250
```

选 `192.168.10.0/24` 为车内网段的理由：**与家里 `192.168.5.0/24` 不冲突**（Tailscale 前置硬约束），
且 ESP32 / PVE 等固定地址都放在 DHCP 池外。**换网络（家里 WiFi / 手机热点 / 4G CPE）只影响 WAN，
车内拓扑与 IP 不变**——这就是"不用折腾"的关键。

### 三张网必须互不冲突（Tailscale 前置约束）

| 场景 | SSID | 网段 | 状态 |
|------|------|------|------|
| 家里 | `ooxx` | `192.168.5.0/24` | 已用 |
| 车上（当前/终局） | `FORAGER`（Cudy LAN） | `192.168.10.0/24` | **使用中**：PVE 静态 `.10`、Windows 调试机 DHCP（当前 `.101`，建议 Cudy 按 MAC 绑定） |
| 手机热点（应急） | — | `172.20.10.0/24` | 应急备用，与上面两者不冲突 |
| Tailscale 虚拟网 | — | `100.64.0.0/10` | Tailscale 自管，**不要动** |

> **当前网络说明**：车内网段定为 `192.168.10.0/24`（Cudy LAN），家里 `192.168.5.0/24`，互不冲突。
> N100 PVE **静态** `192.168.10.10`；Windows 调试机用 **DHCP**（当前 `192.168.10.101`，建议在 Cudy 里按 MAC 绑定固定）。
> 以后 Cudy 改路由模式（WAN 接家里 WiFi/热点/4G）时，LAN 保持 `192.168.10.0/24` 不变，车内设备 IP 全部不动
> （见 [Windows 调试机与核显直通](./n100-windows-gpu-passthrough.md)）。

> ⚠️ **硬约束：家里与车里的局域网网段必须不同。**
> 若两边都是 `192.168.10.0/24`，Tailscale 子网路由会因路由表无法区分
> 「同一个 `192.168.10.x` 属于哪一边」而**必然冲突**，这是 Tailscale
> 最经典的翻车点。本项目家里 `192.168.5.x` / 车里 `192.168.10.x` 天然满足。
>
> iPhone 个人热点的 `172.20.10.x` 也与此二者不冲突，可放心作为车上过渡网络。

### 远程访问：Cudy 自带 **ZeroTier**（定稿，替代 Tailscale）

> **决策变更（2026-10）**：车内路由器由 GL.iNet 换成 **Cudy TR3000**，其固件**自带 ZeroTier**
> （VPN → ZeroTier），无需刷机即可实现"外网直连车内全部设备"。
> 因此 **远程组网不装 Tailscale，也不用在任何 N100/PVE 上装客户端**——符合"网络交给网络、算力交给算力"。

配置要点：
1. `my.zerotier.com` 建 Network，记下 Network ID（Private，节点需手动 Authorize）
2. Cudy → VPN → ZeroTier → 启用，填 Network ID；
   **`客户端访问 = 互联网和本地局域网`**（这就是内置的"子网路由/网关"，让客户端访问 `192.168.10.0/24`）
3. 授权 Cudy 节点；手机/笔记本装 ZeroTier One 加入同一 Network 并授权
4. 若客户端访问不到 `192.168.10.x`：在 ZeroTier 后台加 **Managed Route** `192.168.10.0/24`
   → Via 填 Cudy 节点的 ZeroTier IP，并在客户端勾选 **Allow Managed Routes**

远程可访问：PVE `https://192.168.10.10:8006`、Windows RDP `192.168.10.101:3389`、
路由器 `192.168.10.1`、后续 HA `.11` / Frigate `.12` 等 —— **整个网段，无需逐条端口映射**。

> 保留 Tailscale 方案作为备选：若将来换回 GL.iNet/OpenWrt 路由器，可在路由器上装 Tailscale +
> 子网路由（广告 `192.168.10.0/24`）。原则不变：**VPN 装在路由器，不装在 PVE**。

### ESP32 固件的网络约定

- **不要设 `use_address`**：写死 IP 会让 OTA 在换网段后失效（如在家 `192.168.5.18`
  写的固件拿到车上 `192.168.10.x` 就连不上）。留空时 ESPHome 自动用 mDNS
  `${name}.local`（本机为 `myvan-485-gateway.local`），**任何网段都能 OTA**。
- **SSID/密码集中在 `secrets.yaml`**（`modules/10-smart-control/gateway/esphome/`，
  权限 `600`，已在 `.gitignore` 中排除）。当前 4 份固件共用 `wifi_home_*`、
  `wifi_phone_*`、`wifi_van_*` 三组变量，按 `networks:` 顺序依次尝试。
- 路由器到位后：改 `secrets.yaml` 的 `wifi_van_*`，再取消 4 份 yaml 里
  `wifi_van_*` 两行的注释（**共 4 处，一处不漏**，与 `baud_rate` 改造同理）。
- **首次烧录必须 USB**：设备联网后才能走 OTA；改 WiFi 配置的那一次也需 USB。

## 快速开发环境

如果只是想先在笔记本上体验和开发，不需要 N100 硬件：

```bash
# 进入 dev-environment 目录
cd software/dev-environment

# 启动 HA + MQTT 开发环境
docker compose up -d

# HA 访问 http://localhost:8123
# MQTT 端口 localhost:1883
```

> 车机面板本身由 ESP32 自托管（见 [车机面板](./dashboard.md)），无需单独的仪表盘前端；
> 本地开发环境仅用于调试 HA 自动化 / MQTT，不承担面板托管。

详细说明见 [dev-environment 开发环境](../../software/dev-environment/)。
