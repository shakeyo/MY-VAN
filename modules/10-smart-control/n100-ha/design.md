# N100 中枢与网络

## N100 主机

- **规格**: 16G RAM / 512G SSD
- **平台**: PVE 虚拟化
- **核心服务**:
  - Home Assistant Core — 自动化中枢、场景引擎
  - Frigate — AI 视频监控
  - MQTT Broker — 消息总线
- **供电**: 副电瓶常电（见 [04-power-system](../../04-power-system/)）

## 网络

- **路由器**: GL.iNet/Cudy（MT3000 / WR3000），4G/5G CPE，副电瓶常电供电
- **WAN 接入**: 4G/5G CPE 或手机热点
- **LAN 节点**:
  - 有线：N100 (HA)、DVR 编码器
  - 无线（固定 IP）：安卓车机、ESP32

## 安卓车机

- **规格**: 10–13寸，方易通 7862 方案
- **安装**: 壁挂，运行 Fully Kiosk
- **用途**: 生活区中控屏，显示 HA Dashboard
