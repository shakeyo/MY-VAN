# Docker Compose 开发环境

在本地笔记本上快速搭建 Home Assistant + MQTT 后端，用于仪表盘开发调试。**不需要 N100 硬件**。

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
3. 进入 `个人设置` → `长期访问令牌` → 创建令牌
4. 复制令牌，在仪表盘 `.env` 中设置 `VITE_HA_TOKEN`
5. 启动仪表盘：`cd ../rv-smart-dashboard && pnpm dev`

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
