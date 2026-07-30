# Home Assistant 部署与集成

Home Assistant 是 VAN-PROJECT 智能控制的核心中枢，负责设备接入、自动化逻辑和状态聚合。

## 安装方式选择

| 方式 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| **HA OS (VM)** | 开箱即用、Add-on 商店 | 资源占用大(~2GB) | 如果不用 PVE 跑其他服务 |
| **HA Container (LXC)** | 轻量(~512MB)、灵活 | 需手动装 Add-on | **本项目推荐** |
| **HA Supervised (LXC)** | 完整功能 | 安装复杂 | 需要 Add-on 但不想用 VM |

本项目推荐 **HA Container** 方式：在 PVE 上创建一个 Debian 12 LXC，然后用 Docker 运行 HA。

## 方式一：LXC + Docker（推荐）

### 创建 LXC 容器

在 PVE Web UI 中：

1. 点击 `Create CT`
2. 配置：
   ```
   CT ID:        100
   Hostname:     ha
   Template:     debian-12-standard
   Root Disk:    32GB
   CPU:          2 cores
   RAM:          2048 MB
   Swap:         512 MB
   Network:      vmbr0, static IP 192.168.8.11/24, Gateway 192.168.8.1
   ```
3. 创建后，进入容器的 `Options` → `Features`：
   - 开启 `Nesting` (Docker 需要)
   - 开启 `keyctl`

### 容器内安装 Docker

```bash
# SSH 进入 LXC 容器
lxc-attach 100

# 安装 Docker
apt update && apt install -y docker.io docker-compose-v2

# 创建 HA 目录
mkdir -p /opt/ha/config
```

### 启动 Home Assistant

创建 `/opt/ha/docker-compose.yml`：

```yaml
version: '3'
services:
  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: homeassistant
    restart: unless-stopped
    network_mode: host
    privileged: true
    volumes:
      - /opt/ha/config:/config
      - /etc/localtime:/etc/localtime:ro
      - /run/dbus:/run/dbus:ro
    environment:
      - TZ=Asia/Shanghai
```

```bash
cd /opt/ha
docker compose up -d
```

HA 启动后访问 `http://192.168.8.11:8123`。

### USB 设备直通

RS485 转换器和其它 USB 设备需要直通到 LXC：

```bash
# 在 PVE 宿主机上，查看 USB 设备
lsusb
# 记录 USB-485 转换器的 vendor:product ID，如 1a86:7523

# 编辑 LXC 配置文件 /etc/pve/lxc/100.conf
# 添加：
lxc.cgroup2.devices.allow: c 188:* rwm
lxc.cgroup2.devices.allow: c 166:* rwm
lxc.mount.entry: /dev/ttyUSB0 dev/ttyUSB0 none bind,optional,create=file
```

## 方式二：HA OS 虚拟机（备选）

如果希望使用 Supervisor Add-on 商店（如 Mosquitto、Node-RED 集成安装）：

1. 下载 HA OS 镜像：`https://github.com/home-assistant/operating-system/releases`
2. 在 PVE 中创建 VM，导入 qcow2 镜像
3. VM 配置：4GB RAM, 2 cores, 32GB disk

## RS485/Modbus 集成

### 硬件连接

```
USB-to-RS485 转换器:
  A+  ──→  继电器模块 A (黄/绿)
  B-  ──→  继电器模块 B (蓝/白)
  GND ──→  继电器模块 GND (黑)
```

### HA 配置

编辑 `/opt/ha/config/configuration.yaml`：

```yaml
# Modbus 继电器模块
modbus:
  - name: van_relay
    type: tcp      # 如果是 USB-485 用 serial
    host: 192.168.8.11
    port: 502
    # 如果是直接串口连接:
    # type: serial
    # method: rtu
    # port: /dev/ttyUSB0
    # baudrate: 9600
    # parity: N
    # stopbits: 1
    # bytesize: 8

    switches:
      # 灯光
      - name: "主灯"
        address: 0
        write_type: coil
      - name: "氛围灯"
        address: 1
        write_type: coil
      - name: "睡眠灯"
        address: 2
        write_type: coil
      # 通风
      - name: "排风扇1"
        address: 3
        write_type: coil
      - name: "排风扇2"
        address: 4
        write_type: coil
      # 水路
      - name: "上水泵"
        address: 5
        write_type: coil
      - name: "放水泵"
        address: 6
        write_type: coil
      # 安全
      - name: "车内锁"
        address: 7
        write_type: coil
      - name: "电动踏步"
        address: 8
        write_type: coil

    sensors:
      - name: "库仑计电压"
        address: 0
        input_type: holding
        unit_of_measurement: V
        device_class: voltage
        slave: 1
      - name: "库仑计电流"
        address: 1
        input_type: holding
        unit_of_measurement: A
        device_class: current
        slave: 1
      - name: "库仑计功率"
        address: 2
        input_type: holding
        unit_of_measurement: W
        device_class: power
        slave: 1
```

## MQTT Broker 安装

### 方式 A：Docker（推荐）

```bash
# 在 HA LXC 容器内
mkdir -p /opt/mosquitto/config

cat > /opt/mosquitto/config/mosquitto.conf << 'EOF'
listener 1883
allow_anonymous false
password_file /mosquitto/config/passwd
EOF

# 创建用户密码
docker run -it --rm -v /opt/mosquitto/config:/config eclipse-mosquitto mosquitto_passwd -c /config/passwd van

# 添加到 docker-compose.yml
```

在 `/opt/ha/docker-compose.yml` 中添加：

```yaml
  mosquitto:
    image: eclipse-mosquitto:2
    container_name: mosquitto
    restart: unless-stopped
    network_mode: host
    volumes:
      - /opt/mosquitto/config:/mosquitto/config
      - /opt/mosquitto/data:/mosquitto/data
      - /opt/mosquitto/log:/mosquitto/log
```

### 方式 B：LXC 独立容器

创建一个新的 Debian 12 LXC（IP: 192.168.8.13），安装 Mosquitto：

```bash
apt install -y mosquitto mosquitto-clients
```

### HA 配置 MQTT

在 `configuration.yaml` 添加：

```yaml
mqtt:
  broker: 192.168.8.13
  port: 1883
  username: van
  password: !secret mqtt_password
```

## OBD-II 车辆数据接入

### 数据链路

```
汽车 OBD 口 → ELM327 蓝牙 → 安卓车机 (Torque Pro) → MQTT → HA
```

### 安卓车机 Torque 配置

1. 安装 Torque Pro
2. 配对 ELM327 蓝牙
3. 在 Torque 中启用 MQTT Plugin
4. MQTT 设置：`192.168.8.13:1883`，topic 前缀 `van/obd/`

### HA 接收 OBD 数据

在 `configuration.yaml` 添加 MQTT 传感器：

```yaml
mqtt:
  sensor:
    - name: "发动机转速"
      state_topic: "van/obd/rpm"
      unit_of_measurement: "rpm"
    - name: "车速"
      state_topic: "van/obd/speed"
      unit_of_measurement: "km/h"
    - name: "冷却液温度"
      state_topic: "van/obd/coolant_temp"
      unit_of_measurement: "°C"
    - name: "原车电瓶电压"
      state_topic: "van/obd/battery_voltage"
      unit_of_measurement: "V"
```

### 行车充电自动启停

```yaml
automation:
  - alias: "行车充电自动启停"
    trigger:
      - platform: numeric_state
        entity_id: sensor.发动机转速
        above: 500
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.行车充电器
```

## ESP32 控制板接入

### 固件

使用 ESPhome 固件，在 HA 中直接管理和 OTA 更新。在 `configuration.yaml` 中无需额外配置，ESPhome 设备会被自动发现。

ESPhome 配置示例见 [软件配置目录](../../software/ha-config/esp32-buttons.yaml)。

## secrets.yaml

创建 `/opt/ha/config/secrets.yaml`：

```yaml
# MQTT
mqtt_password: "your_mqtt_password"

# Tailscale (远程访问)
tailscale_auth_key: "tskey-xxxx"

# 外部 API
weather_api_key: "your_api_key"
```

## 自动化场景

完整的自动化配置见 [software/ha-config/automations.yaml](../../software/ha-config/automations.yaml)，包含：

- **驻车模式** — 关闭行车相关设备，开启生活区灯光
- **离车模式** — 关闭所有非必要设备，锁车+收回踏步
- **影院模式** — 调暗灯光，切换音响 DSP 到后声场
- **休息模式** — 仅保留水泵和逆变器，关闭所有灯光

## 下一步

HA 部署完成后，继续搭建 [Frigate 视频监控](./frigate.md)。
