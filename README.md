# 🚐 VAN-PROJECT — 现代化房车智能改装开源项目

基于 **上汽大通 V80** 的房车（Vanlife）自制改装项目。从底盘防锈、铝型材框架到全车 RS485 智能控制、Home Assistant 中控和 React 仪表盘，完整记录了一台"智能 Van"从零到一的改造过程。

## ✨ 核心亮点

- **智能控制总线** — 基于 RS485/Modbus RTU 的全车灯光、水泵、排风扇集中控制，物理开关与 HA 双向同步，网络离线也不影响生存
- **模块化结构** — 铝型材骨架 + 海洋板柜体，所有家具可拆卸以应对年审和维护；淋浴模块、卡座折叠机构均为独立可拆单元
- **能源与监控** — 48V/12V 双电系统，PZEM-017 库仑计实时监测，AHD 摄像头经 Frigate 进行 AI 人形/车辆识别
- **软件全部开源** — React + Vite + Tailwind 智能仪表盘，Home Assistant 自动化配置，ESP32/485 固件逻辑均可自行修改

## 📁 目录结构

```
van-project/
├── README.md
├── TODO.md                        # 项目进度追踪
├── modules/                       # 功能模块（设计 + 施工 + 材料）
│   ├── 00-vehicle-layout/         # 整车布局、保温、框架
│   ├── 01-power-system/           # 48V/12V 电力系统
│   ├── 02-smart-control/          # RS485、HA、控制面板、仪表盘
│   ├── 03-water-system/           # 水箱、水泵、水路
│   ├── 04-shower-module/          # 淋浴模块
│   ├── 05-foldable-seat/          # 多功能折叠卡座
│   ├── 06-roof-platform/          # 车顶平台 + 太阳能
│   ├── 07-overhead-cabinet/       # 额头柜
│   └── 08-hvac/                   # 空调、暖风、通风
├── docs/                          # 规范层：部署指南、设计参考
│   ├── deployment/                # PVE、HA、Frigate、Dashboard 部署
│   ├── design/                    # 工业设计参考
│   └── dependency-graph.md        # 模块依赖关系
├── software/                      # 代码层
│   ├── rv-dashboard/              # React 智能仪表盘
│   ├── home-assistant-config/     # HA 配置模板
│   └── dev-environment/           # Docker 本地开发环境
└── archive/                       # 归档：历史草稿、AI 对话
```

## 🛠️ 技术栈

### 硬件层

| 类别 | 方案 | 说明 |
|------|------|------|
| 计算主机 | N100 迷你主机 (PVE 虚拟化) | 运行 HA、Frigate、MQTT Broker |
| 控制总线 | RS485 (Modbus RTU) | 全车灯光、水泵、风扇的集中控制 |
| 能源系统 | 48V 主电 + 12V 副电 | PZEM-017 库仑计实时监测 |
| 视觉监控 | 4 路 AHD → RTSP → Frigate | AI 人形/车辆识别 |
| 网络 | GL.iNet/Cudy 4G/5G 路由器 | Tailscale 远程访问 |
| 音响 | 阿尔派 Alpine R600 DSP | 8 路 DSP，行车/影院多声场切换 |

### 软件层

| 类别 | 方案 |
|------|------|
| 中控平台 | Home Assistant |
| 前端仪表盘 | React 18 + TypeScript + Vite + Tailwind CSS |
| 状态管理 | Zustand |
| 图表 | Recharts |
| 构建工具 | Vite 6 + pnpm |

## 🚀 快速开始

1. **浏览模块** — 从 `modules/README.md` 查看各模块状态，找到当前在施工的模块
2. **查看部署** — 参考 [`docs/deployment/`](docs/deployment/) 搭建 PVE、HA、Frigate
3. **启动仪表盘** — `cd software/rv-dashboard && pnpm install && pnpm dev`
4. **开发环境** — 使用 [`software/dev-environment/`](software/dev-environment/) 一键启动 HA + MQTT 调试环境

## 📐 设计原则

- **模块化** — 硬件结构必须可拆卸，以应对年审和维护
- **冗余设计** — 关键功能（水、电、灯）保留物理手动开关，防止系统崩溃导致无法生活
- **单一事实来源 (SSOT)** — 所有技术决策沉淀为 `docs/specs/` 下的 PRD 文档
- **轻量化** — 结构件优先使用铝型材与海洋板，减轻车重

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。参与前请阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## 📜 License

本项目代码遵循 [MIT License](./LICENSE)。硬件设计与文档遵循 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)。
