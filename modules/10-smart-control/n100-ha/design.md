# N100 中枢与网络

## HA 角色定义（定稿原则，改动需在本文显式更新）

三层分工，边界固定——**HA 不承载安全关键自动化**：

| 层 | 职责 | 挂了会怎样 |
|----|------|-----------|
| ESPHome（ESP32，边缘） | 数据采集 + **安全关键自动化**：按键联动、离车模式、低温禁充、待机断电、场景循环 | 这些全在 ESP32 本地，断网照跑 |
| HA（N100，中枢） | 统一 Dashboard（手机/平板/车机）、中控台机器人（语音/表情/动作入口，见 [robot/](../robot/)）、历史与能源面板（MPPT 总电量、PZEM 电量计）、**远程访问入口**、推送通知、非关键高阶自动化（天气/日程/回家检测）、多源汇聚（BLE 传感器、Frigate、车机） | 只丢 UI/远程/通知，物理按键与本地自动化不受影响 |
| 物理按键（机械） | 最终冗余 | — |

**原则**：自动化本地优先；HA 接入是纯增量（ESPHome native API 自动发现实体，现有固件零改动）。

### 待定决策（后续在此补结论，不另起文档）

- [x] **远程访问方式**：Tailscale（定稿；add-on 安装见 软件清单）
- [ ] **中枢常开策略**：倾向 7×24 常开（离车远程监看 + 中控台机器人依赖；N100 待机约 5-10W，太阳能可补；装机后实测功耗补数）
- [x] **通知渠道**：HA Companion App 推送（定稿）
- [ ] **Dashboard 布局**：生活区控制 / 能源 / 监控 分页方案
- [x] **语音控制**：中控台机器人走 HA Assist 管线（定稿），见 [robot/](../robot/)

## N100 主机

- **规格**: 16G RAM / 512G SSD
- **平台**: PVE 虚拟化
- **核心服务**:
  - HAOS（PVE 虚拟机，Supervisor 管理）— Dashboard、历史/能源统计、远程访问、通知、高阶自动化（非安全关键）
  - Tailscale（add-on）— 远程访问
  - Mosquitto（add-on）— MQTT 消息总线
  - Frigate（后期）— AI 视频监控
- **供电**: 副电瓶常电（见 [04-power-system](../../04-power-system/)）

## 软件清单（必装）

| 软件 | 类型 | 用途 | 状态 |
|------|------|------|------|
| HAOS（Supervisor 版） | 系统 | HA 本体，PVE 虚拟机 | 已装 |
| Tailscale | add-on | 远程访问（定稿，见待定决策） | 待装 |
| Mosquitto broker | add-on | MQTT 消息总线（OBD-II 车机数据、传感器、ESPHome 备选通道） | 待装 |
| ESPHome | 集成 | ESP32 网关 native API，上线后自动发现实体 | 待装 |
| System Monitor | 集成 | 系统状态卡片（CPU/磁盘/网络） | 待装 |
| HA Companion | 手机 App | 通知推送 + 移动控制 | 待装 |
| Fully Kiosk | 安卓 App | 车机/平板固定显示 Dashboard（见 安卓车机、tablet.md） | 待装 |

**依赖关系**：Tailscale/Mosquitto 为 add-on（HAOS Supervisor 必装），ESPHome/System Monitor 为内置集成（无需商店），Companion/Fully Kiosk 为客户端。安装顺序：系统 → add-on → 集成 → 客户端。

## 网络

- **路由器**: GL.iNet/Cudy（MT3000 / WR3000），4G/5G CPE，副电瓶常电供电
- **WAN 接入**: 4G/5G CPE 或手机热点
- **LAN 节点**:
  - 有线：N100 (HA)、DVR 编码器
  - 无线（固定 IP）：安卓车机、小米平板4、ESP32

## 安卓车机

- **规格**: 10–13寸，方易通 7862 方案
- **安装**: 壁挂，运行 Fully Kiosk
- **用途**: 生活区中控屏，显示 HA Dashboard

## 小米平板4（移动中控板）

- **用途**: 副驾驶位监控（Frigate）+ 全车控制 Dashboard；快拆可移到后床旁
- **改造**: 拆电池改直供电（副电瓶 12V→5V），Fully Kiosk 常亮
- 方案与待办见 [tablet.md](tablet.md)

## 后期规划占位（接入时展开）

- **能源面板**：MPPT 总电量（0xA3，total_increasing）、PZEM-017 电量计 → HA Energy dashboard；数据源已定，接入后补
- **监控集成**：Frigate + DVR 编码器
- **传感器接入**：温湿度/水位/门磁/漏水/OBD-II（见 [sensors/](../sensors/)）
