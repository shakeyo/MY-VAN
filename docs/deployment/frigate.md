# Frigate NVR — AI 视频监控部署

Frigate 是运行在 N100 上的 AI 视频分析系统，通过 RTSP 流接入 4 路 AHD 摄像头，实现人形检测、车辆识别和录像存储。

## 架构

```
AHD 摄像头 × 4
  │  (同轴视频线)
  ├──→ 原车车机 (360 全景)
  └──→ Y型分线器 (信号并联)
         │
         └──→ AHD DVR 编码器
                │  (RTSP 网络流)
                └──→ N100 Frigate
                       │
                       ├──→ 人形/车辆 AI 识别
                       ├──→ 录像存储 (NAS/本地)
                       └──→ HA 集成 (告警推送)
```

## 硬件准备

| 设备 | 型号推荐 | 说明 |
|------|----------|------|
| AHD 摄像头 | 1080P AHD × 4 | 前后左右各一 |
| Y 型分线器 | AHD BNC 一分二 | 信号并联，原车车机 + DVR 同时看 |
| DVR 编码器 | 4路 AHD → RTSP | 关键：把模拟信号转成网络流 |
| Coral TPU (可选) | USB 版 | 加速 AI 推理（N100 纯 CPU 也可以跑） |

## LXC 容器创建

在 PVE 中创建 Debian 12 LXC：

```
CT ID:        101
Hostname:     frigate
Root Disk:    64GB (预留录像空间)
CPU:          2 cores
RAM:          2048 MB
Network:      vmbr0, static IP 192.168.8.12/24
```

开启 `Nesting` 特性，安装 Docker：

```bash
apt update && apt install -y docker.io
```

## Docker 部署

创建 `/opt/frigate/docker-compose.yml`：

```yaml
version: "3.9"
services:
  frigate:
    container_name: frigate
    restart: unless-stopped
    image: ghcr.io/blakeblackshear/frigate:stable
    privileged: true
    shm_size: "256mb"
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /opt/frigate/config:/config
      - /opt/frigate/storage:/media/frigate
      - type: tmpfs
        target: /tmp/cache
        tmpfs:
          size: 1000000000
    ports:
      - "5000:5000"      # Frigate Web UI
      - "1935:1935"      # RTMP
    environment:
      - TZ=Asia/Shanghai
      - FRIGATE_RTSP_PASSWORD=your_password
```

## 摄像头配置

创建 `/opt/frigate/config/config.yml`：

```yaml
mqtt:
  host: 192.168.8.13
  user: van
  password: !secret mqtt_password

cameras:
  front:
    ffmpeg:
      inputs:
        - path: rtsp://admin:password@192.168.8.100:554/cam/realmonitor?channel=1&subtype=0
          roles:
            - detect
            - record
    detect:
      width: 1920
      height: 1080
      fps: 5

  rear:
    ffmpeg:
      inputs:
        - path: rtsp://admin:password@192.168.8.100:554/cam/realmonitor?channel=2&subtype=0
          roles:
            - detect
            - record
    detect:
      width: 1920
      height: 1080
      fps: 5

  left:
    ffmpeg:
      inputs:
        - path: rtsp://admin:password@192.168.8.100:554/cam/realmonitor?channel=3&subtype=0
          roles:
            - detect
            - record
    detect:
      width: 1920
      height: 1080
      fps: 5

  right:
    ffmpeg:
      inputs:
        - path: rtsp://admin:password@192.168.8.100:554/cam/realmonitor?channel=4&subtype=0
          roles:
            - detect
            - record
    detect:
      width: 1920
      height: 1080
      fps: 5

record:
  enabled: true
  retain:
    days: 7
    mode: motion     # 仅录制有动作的片段

detectors:
  cpu1:
    type: cpu        # N100 使用 CPU 检测
    num_threads: 3

# 如果有 Coral USB TPU:
# detectors:
#   coral:
#     type: edgetpu
#     device: usb

objects:
  track:
    - person
    - car
    - dog

snapshots:
  enabled: true
  retain:
    default: 10

# 驻车安防：夜间检测到人，HA 自动亮灯
mqtt:
  enabled: true
  host: 192.168.8.13
  user: van
  password: !secret mqtt_password
```

## 摄像头 AHD → RTSP 编码器配置

DVR 编码器需要配置：

1. 接入 AHD 摄像头，确认 4 路信号正常
2. 设置 DVR 静态 IP：`192.168.8.100`
3. 启用 RTSP 服务，端口 `554`
4. RTSP URL 格式通常为：`rtsp://<user>:<pass>@<ip>:554/cam/realmonitor?channel=1&subtype=0`

每家的 DVR RTSP 路径略有不同，请参考自家 DVR 说明书获取准确的 URL 格式。

## HA 集成

### 安装 Frigate 集成

在 HA 中：`设置` → `设备与服务` → `添加集成` → 搜索 `Frigate`

填写 Frigate 地址：`http://192.168.8.12:5000`

### 监控画面卡片

在 HA Dashboard 中添加 `picture-glance` 卡片或 `frigate-card`：

```yaml
type: picture-glance
title: 前摄像头
camera_image: camera.front
entities:
  - binary_sensor.front_person_motion
```

### 夜间安防自动化

```yaml
automation:
  - alias: "夜间驻车安防"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_person_motion
        to: "on"
    condition:
      - condition: sun
        after: sunset
      - condition: state
        entity_id: input_select.van_mode
        state: "驻车模式"
    action:
      - service: light.turn_on
        target:
          entity_id: light.外射灯
      - service: notify.mobile_app
        data:
          message: "检测到有人靠近车辆"
          data:
            image: "{{ state_attr('camera.front', 'entity_picture') }}"
```

## 存储管理

N100 存储有限，需要控制录像占用：

```yaml
# 录像保留策略
record:
  retain:
    days: 3         # 普通录像保留 3 天
    mode: motion    # 只录有动作的片段

# 定期清理
# 在宿主机 crontab 中添加:
# 0 3 * * * find /opt/frigate/storage/recordings -mtime +3 -delete
```

## 性能优化

- **FPS 限制**: detect fps 设为 5，降低 CPU 占用
- **分辨率**: 如果 CPU 占用过高，降低 detect 分辨率为 1280×720
- **Coral TPU**: 如果预算允许，加装 USB Coral TPU 推理速度提升 10x
- **关闭不需要的 detect**: 行车时关闭检测（通过 HA 自动化控制）

## 下一步

Frigate 部署完成后，返回 [部署指南](./) 查看仪表盘部署。
