# Docker Compose 开发环境

在本地笔记本上快速搭建 Home Assistant + MQTT 后端，用于 HA 自动化 / MQTT 联调。**不需要 N100 硬件**。

## 一键启动

```bash
cd software/docker-compose
docker compose up -d
```

## 服务列表

| 服务 | 地址 | 说明 |
|------|------|------|
| Home Assistant | http://localhost:8123 | 智能家居中控 |
| Mosquitto MQTT | localhost:1883 | MQTT 消息代理 |

## 首次配置

1. 访问 http://localhost:8123
2. 创建 HA 账号
3. 进入 `个人设置` → `长期访问令牌` → 创建令牌（如需在 HA 自动化/脚本中调用外部服务）

> 车机面板已由 ESP32 自托管（`http://<esp32-ip>/dashboard`，见
> [gateway/esphome/README.md](../../modules/10-smart-control/gateway/esphome/README.md)），
> 不依赖本开发环境，也无需单独的仪表盘前端。

## 模拟设备数据

HA 启动后没有任何设备。使用 MQTT 模拟工具发送测试数据：

```bash
# 安装 mosquitto-clients
brew install mosquitto  # macOS
# 或 apt install mosquitto-clients  # Linux

# 发送模拟电量数据
mosquitto_pub -h localhost -t "van/sensor/battery_percent" -m "85"

# 发送模拟温度数据
mosquitto_pub -h localhost -t "van/sensor/indoor_temp" -m "24.5"

# 模拟开关状态
mosquitto_pub -h localhost -t "van/switch/main_light" -m "ON"
```

## 停止环境

```bash
docker compose down        # 停止容器
docker compose down -v     # 停止并删除数据卷（重置 HA）
```
