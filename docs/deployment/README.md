# 部署指南

本文档涵盖 VAN-PROJECT 智能控制系统从零搭建的完整流程。

## 架构总览

```
┌─────────────────────────────────────────────────┐
│                  N100 迷你主机 (PVE)               │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ HA LXC   │  │ Frigate  │  │ Mosquitto    │   │
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
| USB-485 | CH340/FT232 + MAX485 | RS485 总线接入 HA |
| 继电器模块 | 10路 RS485 Modbus RTU | 全车灯光/水泵/风扇控制 |
| 摄像头 | AHD 1080P × 4 | 四路监控 |
| DVR 编码器 | AHD → RTSP 网络编码器 | 模拟摄像头数字化 |
| ESP32 | ESP32-DevKitC | 驾驶室自复位按钮接入 |
| OBD-II | ELM327 蓝牙版 | 车辆数据读取 |

## 部署步骤

按以下顺序部署，每一步都依赖前一步：

1. **[PVE 基础环境](./pve-setup.md)** — 安装 Proxmox VE，配置网络与存储
2. **[Home Assistant](./home-assistant.md)** — 安装 HA，接入 RS485/Modbus 设备
3. **[Frigate NVR](./frigate.md)** — AI 视频监控部署
4. **[仪表盘](./dashboard.md)** — 部署 rv-smart-dashboard

## 网络规划

```
子网: 192.168.8.0/24 (GL.iNet 路由器默认)

  192.168.8.1    — GL.iNet 路由器 (网关 + DHCP)
  192.168.8.10   — N100 PVE 管理 IP
  192.168.8.11   — Home Assistant (LXC)
  192.168.8.12   — Frigate (LXC)
  192.168.8.13   — Mosquitto MQTT (LXC)
  192.168.8.20   — ESP32 控制板
  192.168.8.30   — 安卓车机 (Dashboard)
  192.168.8.100  — DVR 编码器

DHCP 池: 192.168.8.150-192.168.8.250
```

## 快速开发环境

如果只是想先在笔记本上体验和开发仪表盘，不需要 N100 硬件：

```bash
# 进入 docker-compose 目录
cd software/docker-compose

# 启动 HA + MQTT 开发环境
docker compose up -d

# HA 访问 http://localhost:8123
# MQTT 端口 localhost:1883

# 然后启动仪表盘
cd ../rv-smart-dashboard
pnpm install && pnpm dev
```

详细说明见 [docker-compose 开发环境](../../software/docker-compose/README.md)。
