# 软件总览

本目录包含房车智能系统的全部可运行代码和配置。

## 子项目

| 目录 | 说明 | 技术栈 |
|------|------|--------|
| [rv-dashboard](./rv-dashboard/) | 房车智能仪表盘（前端） | React 18 + TypeScript + Vite + Tailwind |
| [home-assistant-config](./home-assistant-config/) | Home Assistant 配置模板 | YAML |
| [dev-environment](./dev-environment/) | 本地开发环境（HA + MQTT） | Docker Compose |

## 快速开始

### 本地开发（无需 N100 硬件）

```bash
# 1. 启动 HA + MQTT 开发环境
cd dev-environment
docker compose up -d

# 2. 配置 HA 访问令牌，启动仪表盘
cd ../rv-dashboard
pnpm install
pnpm dev
```

### 部署到房车

详见 [modules/02-smart-control/design.md](../modules/02-smart-control/design.md) 和 [docs/deployment/](../docs/deployment/)。
