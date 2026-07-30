# 施工指导：智能控制系统

## ✅ 前置条件

- [ ] 副电瓶系统已完工，12V 常电干线已引至驾驶室和生活区
- [ ] 车内局域网（路由器）已部署，WiFi 覆盖驾驶室和生活区
- [ ] N100 已安装 HA Core，ESP32 已烧录 ESPHome（见下方步骤）

## 🔧 工具清单

| 工具 | 用途 |
|------|------|
| 万用表 | 电压测量、通断检测 |
| 电烙铁 + 焊锡 | 焊接 ESP32 与 MAX485 |
| 热缩枪/打火机 | 绝缘防护 |
| 压线钳 | 端子压接 |
| 串口调试助手（软件） | 485 通讯测试 |
| USB 数据线 | ESP32 烧录 |
| 稳压电源（可调 10-28V） | 模拟车载电压波动测试 |

## 🛠️ 硬件安装步骤

### 步骤 1：器件筛选与预处理

1. **ESP32 开发板**: 确认支持 -20℃~70℃ 宽温（普通开发板也可，避免极端环境即可）。
2. **MAX485 模块**: 确认带自动收发功能（DE/RE 已短接或有自动收发芯片）。
3. **485 继电器模块**: 确认带**物理按键输入端口**（这是维护模式的关键）。
4. **按钮测试**: 逐个按压测试通断手感，排除接触不良品。
5. **线缆检查**: 屏蔽双绞线剥线后检查屏蔽层完整性。

### 步骤 2：单板独立调试（先单后整）

**ESP32 供电调试**
- 接入 5V 稳压电源，测量 ESP32 的 3.3V 引脚输出电压，确认稳定在 3.25V~3.35V。
- 观察指示灯，无发烫、无短路。

**MAX485 模块调试**
- 单独给模块供电（**5V**，不是 3.3V），测量 A/B 空载电压差（正常 A 比 B 高 2~6V）。
- 短接 DE/RE 测试自动收发功能。

**485 继电器模块单点调试**
- 单独接入 12V 车载电压。
- 手动短接按键 IO 与 GND，测试继电器吸合/断开，观察状态指示灯。

**按钮电路调试**
- 按钮一端接 GND，另一端接模块按键输入口（模块内部自带上拉）。
- 万用表测量：静态高电平，按压低电平。

### 步骤 3：电路焊接与端口固化

**ESP32 ↔ MAX485 接线**

| ESP32 | MAX485 | 说明 |
|-------|--------|------|
| 5V | VCC | MAX485 需 5V 供电 |
| GND | GND | 共地（必须单点共地） |
| GPIO16 (RX) | TX | ESP32 接收 ← MAX485 发送 |
| GPIO17 (TX) | RX | ESP32 发送 → MAX485 接收 |
| GPIO18 | DE/RE | 自动收发控制 |

> ⚠️ **注意**: 新对话文档中写 ESP32 3.3V → MAX485 VCC，这是**错误的**。MAX485 芯片标准供电为 5V，请使用 5V 引脚供电。

**焊接要求**
- 焊点饱满，无虚焊、无连锡。
- 所有地线统一共地，单点汇聚接地，**杜绝多点接地环流**。
- 按键信号线、485 总线信号线套热缩管绝缘。
- 大功率负载引脚加粗铜线。

### 步骤 4：485 总线组网

**布线规范**
- **拓扑**: 手拉手串联，禁止分支、星型接线。
- **线缆**: RVSP 2×0.5mm² 屏蔽双绞线。
- **终端电阻**: 总线首尾两端 A/B 之间并联 **120Ω 0.5W 电阻**。
- **屏蔽层**: 单端接地（仅 ESP32 主控端接地，末端悬空）。
- **强弱电分离**: 485 信号线与 12V 负载供电线间距 ≥15cm，禁止同管走线。

**电源滤波**
- ESP32 和 MAX485 的 5V 输入端并联 **1000μF 电解电容 + 0.1μF 瓷片电容**，抑制车载电压波动。

### 步骤 5：整机联调与容错测试

1. **通讯测试**: 全系统通电，串口调试助手查看 Modbus 数据无乱码、无丢包。
2. **颠簸测试**: 模拟行车晃动线路与设备，无断电、无通讯中断、无误触发。
3. **电压波动测试**: 10V~28V 宽电压输入，系统正常工作，无重启、无死机。
4. **防水固定**: 整机装入 ABS 防水盒，减震固定。

## 💻 ESPHome 配置模板

以下为修正后的 ESPHome 配置，适配 ESP32 + MAX485 + 485继电器模块：

```yaml
esphome:
  name: rv-485-gateway
  friendly_name: "房车485网关"
  platform: ESP32
  board: esp32dev

# WiFi 配置（修改为你的实际信息）
wifi:
  ssid: "你的WiFi名称"
  password: "你的WiFi密码"
  manual_ip:
    static_ip: 192.168.8.20
    gateway: 192.168.8.1
    subnet: 255.255.255.0

# Home Assistant API
api:
  encryption:
    key: "你的加密密钥"

ota:
  password: "你的OTA密码"

logger:
  level: INFO

# 485 串口配置
uart:
  id: uart_485
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 9600
  parity: NONE
  stop_bits: 1

# 485 收发控制（DE/RE 使能）
switch:
  - platform: gpio
    pin: GPIO18
    name: "485收发使能"
    internal: true
    restore_mode: ALWAYS_ON

# ====================== Modbus 配置 ======================
modbus:
  id: modbus_485
  uart_id: uart_485
  # 发送前自动拉高 DE/RE，发送后自动拉低
  flow_control_pin: GPIO18

# ====================== 继电器控制（示例4路） ======================
# 请根据你的 485 继电器模块实际地址和寄存器修改
switch:
  - platform: modbus_controller
    modbus_controller_id: relay_ctrl
    name: "房车顶灯"
    id: rv_light_top
    register_type: coil
    address: 0x0000
    restore_mode: RESTORE_DEFAULT_OFF

  - platform: modbus_controller
    modbus_controller_id: relay_ctrl
    name: "房车水泵"
    id: rv_water_pump
    register_type: coil
    address: 0x0001
    restore_mode: RESTORE_DEFAULT_OFF

  - platform: modbus_controller
    modbus_controller_id: relay_ctrl
    name: "房车换气扇"
    id: rv_fan
    register_type: coil
    address: 0x0002
    restore_mode: RESTORE_DEFAULT_OFF

  - platform: modbus_controller
    modbus_controller_id: relay_ctrl
    name: "逆变器总开关"
    id: rv_inverter
    register_type: coil
    address: 0x0003
    restore_mode: RESTORE_DEFAULT_OFF

# Modbus 控制器定义（地址根据模块拨码设置）
modbus_controller:
  - id: relay_ctrl
    address: 0x01
    modbus_id: modbus_485
    setup_priority: -10
    command_throttle: 50ms
    update_interval: 2s

# ====================== 传感器拓展（可选） ======================
# 温湿度传感器（485型，地址0x02）
sensor:
  - platform: modbus_controller
    modbus_controller_id: env_sensor
    name: "车内温度"
    id: indoor_temp
    register_type: holding
    address: 0x0001
    unit_of_measurement: "°C"
    accuracy_decimals: 1
    value_type: U_WORD
    filters:
      - multiply: 0.1

  - platform: modbus_controller
    modbus_controller_id: env_sensor
    name: "车内湿度"
    id: indoor_humidity
    register_type: holding
    address: 0x0002
    unit_of_measurement: "%"
    accuracy_decimals: 1
    value_type: U_WORD
    filters:
      - multiply: 0.1

modbus_controller:
  - id: env_sensor
    address: 0x02
    modbus_id: modbus_485
    update_interval: 5s
```

> **重要**: 以上配置中 `modbus_controller` 平台的寄存器地址需根据你购买的 485 继电器模块的实际说明书修改。不同厂商的 Modbus 地址和指令格式不同。

## 🏠 Home Assistant 配置要点

1. **自动发现**: ESP32 上线后，HA 会自动发现设备，一键添加。
2. **实体命名**: 在 ESPHome 中设置的 `name` 会作为 HA 实体名称，建议使用中文以便识别。
3. **自动化示例**:
   ```yaml
   # 高温自动开风扇
   alias: "高温自动通风"
   trigger:
     - platform: numeric_state
       entity_id: sensor.房车485网关_车内温度
       above: 28
   action:
     - service: switch.turn_on
       target:
         entity_id: switch.房车485网关_房车换气扇

   # 离家模式关闭所有负载
   alias: "离家模式"
   trigger:
     - platform: state
       entity_id: input_button.leave_mode
   action:
     - service: switch.turn_off
       target:
         entity_id:
           - switch.房车485网关_房车顶灯
           - switch.房车485网关_房车水泵
           - switch.房车485网关_房车换气扇
           - switch.房车485网关_逆变器总开关
   ```

## 🔍 调试步骤

1. **ESP32 烧录**: 将配置粘贴至 ESPHome Dashboard，编译并无线烧录。
2. **日志检查**: 烧录后查看 ESP32 日志，确认 WiFi 连接、Modbus 初始化无报错。
3. **HA 接入**: 在 HA 的"集成"页面确认 ESP32 设备已发现，添加后检查实体列表。
4. **单路测试**: 在 HA 中逐个开关每一路继电器，观察继电器吸合声和指示灯。
5. **按钮测试**: 按压物理按钮，观察继电器动作和 HA 面板状态是否同步更新。
6. **断电记忆测试**: 关闭某路负载后断电 5 分钟，重新上电检查状态是否保持。

## ⚠️ 故障排查

| 现象 | 排查方向 |
|------|----------|
| 状态不同步 | 检查 485 总线共地、终端电阻、Modbus 地址是否冲突 |
| 远程控制无响应 | 检查 ESP32 WiFi 状态、HA API 连接、485 接线松动 |
| 按键误触发 | 检查线路干扰，确认模块自带硬件防抖 |
| 设备掉线 | 检查车载供电稳定性，加固总线接头，优化屏蔽接地 |
| Modbus 通讯失败 | 检查波特率、地址、寄存器地址是否与模块说明书一致 |
| ESP32 发热 | 检查供电是否为 5V（非 12V 直供），检查短路 |

## 📝 问题记录

（施工过程中遇到的问题和解决办法，请在此处补充）

---

**日期**: ____
**问题**: ____
**原因**: ____
**解决办法**: ____

---

**日期**: ____
**问题**: ____
**原因**: ____
**解决办法**: ____
