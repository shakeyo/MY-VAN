# 软件总览

本目录包含房车智能系统的全部可运行代码和配置。

## 子项目

| 目录 | 说明 | 技术栈 |
|------|------|--------|
| [home-assistant-config](./home-assistant-config/) | Home Assistant 配置模板 | YAML |
| [dev-environment](./dev-environment/) | 本地开发环境（HA + MQTT） | Docker Compose |

> 车机控制面板（深蓝 UI）已并入 ESP32 固件、由 ESP32 自托管（离线可用），
> 见 [modules/10-smart-control/gateway/esphome/web/index.html](../modules/10-smart-control/gateway/esphome/web/index.html)，
> 不再作为独立前端项目维护。

## 快速开始

### 本地开发（无需 N100 硬件）

```bash
# 启动 HA + MQTT 开发环境
cd dev-environment
docker compose up -d
```

### 部署到房车

详见 [modules/10-smart-control/](../modules/10-smart-control/) 和 [docs/deployment/](../docs/deployment/)。
