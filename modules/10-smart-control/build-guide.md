# 施工指南：智能控制系统（整车主线）

> 本文是智能控制的**执行手册**：10 个阶段按序执行，每阶段给入口条件、动作（指向细节文档）、出口验收。
> 细节不在此复述——网关怎么做看 [gateway/build-guide.md](gateway/build-guide.md)，箱体/面板/通电看 [04-power-system/build-guide.md](../04-power-system/build-guide.md)。
>
> **三条红线（任何时候）**：
> 1. 安全关键自动化只放 ESPHome 本地，不放 HA（离车模式/低温禁充/待机断电/按键联动）。
> 2. 485 总线手拉手菊花链，严禁星型/分支；终端电阻只首尾两个。
> 3. 485 模块 12V 供电正负严禁接反（模块无保护，接反即烧）。
>
> **与电力系统的接口**：本模块的供电全部来自 [04-power-system](../04-power-system/) 的 12V 常电母线（DCDC 输出，F12-1 控制回路）。04 的箱内施工（阶段 2）与面板接线（阶段 3）先于本阶段 1-3 完成。

## 阶段 0：中枢与网络

**入口**：N100、路由器到货；车内 12V 常电已就绪（04 阶段 5② 完成）。

1. N100 装 PVE 8.x（UEFI 启动、上电自动开机、关 Secure Boot）——[docs/deployment/pve-setup.md](../../docs/deployment/pve-setup.md)
2. 建 HAOS **Supervisor 虚拟机**（192.168.8.11，建议 4GB RAM 起）——**定稿是 HAOS VM**（add-on 依赖 Supervisor）；[docs/deployment/home-assistant.md](../../docs/deployment/home-assistant.md) 的 LXC+Docker 段是早期存档备选，勿采用
3. add-on 安装：Tailscale（远程访问定稿）、Mosquitto broker（MQTT .13）；集成：ESPHome、System Monitor
4. 路由器设固定 IP（DHCP 保留按 MAC 绑定）：.10 PVE / .11 HA / .20 ESP32 / .30 车机 / .100 DVR——IP 表见 [network-topology.svg](./diagrams/network-topology.svg)
5. 手机装 HA Companion（推送通知定稿渠道）

**配图**：[network-topology.svg](./diagrams/network-topology.svg)

**出口验收**：
- [ ] 手机局域网访问 HA 正常
- [ ] Tailscale 车外（手机 4G）可访问 HA
- [ ] 全部固定 IP 生效，DHCP 池 .150-250 不冲突

## 阶段 1：485 总线就绪（与 04 阶段 2/3/4 联动）

**入口**：[04-power-system/build-guide.md](../04-power-system/build-guide.md) 阶段 2（箱内接线）+ 阶段 3（面板接线）完成。

核对（不重复施工，逐项打勾）：

- [ ] 中8 模块卡在中门配电箱导轨：485 并线 + 12V 供电线已接，**F12-1 保险未插（模块未通电）**
- [ ] 中4 模块在中门柜：485 + 供电就位，保险未插
- [ ] 总线菊花链：ESP32 挂接点 → 额头 → 中8 → 中4（→ 车尾后期）；A-A、B-B，无分支
- [ ] 终端电阻 120Ω ×2：ESP32 端 + 最远端（当前中4端）；中间节点无
- [ ] 屏蔽层单端接地（ESP32 端），末端悬空
- [ ] 485 双绞线与 12V 负载线间距 ≥15cm，分槽不同管
- [ ] 14 芯线/8P 短跳线已压插头入面板插座（04 阶段 3 验收过）

**出口验收**：万用表测 ESP32 端 A-B 无对地短路；目视检查接线与 [485-bus.svg](../04-power-system/diagrams/485-bus.svg) 一致。

## 阶段 2：网关上车

**入口**：阶段 1 完成；网关面包板/桌面工作按 [gateway/build-guide.md](gateway/build-guide.md) 阶段 1-3 完成（TTL 回环 + 双 MAX3485 回环或 USB-485 双向验证）。

1. 桌面烧录与中8 全逻辑验证（gateway 阶段 4.4-4.5）：test-485-connect → test-mid8-logic（场景循环/双控/长按/断电恢复）
2. 组装焊接（gateway 阶段 5）：扩展底板 + 485 小副板（MAX3485），按 [gateway-wiring.svg](gateway/diagrams/gateway-wiring.svg) 检查五根短导线，装 ABS 防水盒
3. 上车接线（gateway 阶段 6.1）：控+（F12-1）供电、A/B 并入箱内 485 端子排、终端电阻与屏蔽层
4. 通道映射验证（gateway 4.6）：test-channel-mapping.yaml → 16 路继电器 + 全按键只读核对

**配图**：[gateway-wiring.svg](gateway/diagrams/gateway-wiring.svg)

**出口验收**：4.6 全过（16 开关回读 + 按键日志 + 断电重启全关）。

## 阶段 3：模块通电与按键全量验证

**入口**：阶段 2 完成。

1. 插 F12-1 保险（控制电源 2A）——**此时中8/中4 模块 + ESP32 通电**
2. 烧录 prod.yaml（gateway 4.4）
3. 全按键按一轮（对照 [switch-assignment.md](../04-power-system/switch-assignment.md) 通道表）：
   - 单键：射灯/户外灯/主灯/氛围灯/风扇场景/水泵（双控两键）/水阀/冰箱/DSP
   - 场景：灯光模式循环（明亮→夜灯→全关）、离车/驻车模式、长按 2s 灯光全关
   - LED 同步：按键 LED 与负载状态一起亮一起灭；双控泵两颗 LED 同亮同灭
4. 断电重启：主灯状态恢复，水泵/水阀/风扇全关
5. **断网验证**：拔路由器 WAN / 关 WiFi——按键→负载联动、离车模式仍正常（ESPHome 本地）

**配图**：[button-wiring.svg](../04-power-system/diagrams/button-wiring.svg)（排查"两个 COM"用）

**出口验收**：
- [ ] 全部按键/场景/LED 对照表逐项通过
- [ ] 断电恢复策略正确
- [ ] 断网场景联动正常（这是三级架构的核心承诺）

## 阶段 4：全车总线改造 38400 → 9600（MPPT 上车前必做）

**入口**：阶段 3 完成（38400 下功能全部验证）。

按 [gateway/build-guide.md 4.7](gateway/build-guide.md) 执行：逐台写 0033H=1（帧已备好）→ 逐台 9600 读回 → 固件 `baud_rate` 切 9600 → 重烧 prod → 快速复验 4.6。

> 为什么在此阶段：MPPT 最高只支持 9600，全车统一降速（[energy/mppt-protocol.md §二](energy/mppt-protocol.md)）。改完此步，能源设备才有上总线的条件。

**出口验收**：4 模块 9600 读回 `00 01` + prod 复验无回归 + 总线空闲无 0x00 噪声流。

## 阶段 5：能源设备接入（MPPT / PZEM）

**入口**：阶段 4 完成；MPPT 已按 04-power-system 物理接线（DC 输出 → 空气开关 → 汇流排 → 电池）。

1. **桌面协议验证**（USB-485 直连 MPPT，9600）：0xA3 查询 → 0xC0 允许/禁止 → 0xD0 设远程控制 → **关闭输出后测待机电流与 485 存活 → 定档（协议档/硬件档）**——判定表见 [energy/mppt-protocol.md §四](energy/mppt-protocol.md)
2. LCD 设置：地址 0x10、波特率 9600（代码 4，⚠ 与继电器模块代码 1 不同）、DC 输出控制方式=远程控制
3. 上车：MPPT 485 并上总线（菊花链，终端电阻位置不变）
4. 固件：`esphome/mppt.yaml`（待建，规划见 [mppt-protocol.md §五](energy/mppt-protocol.md)）：10s 轮询 + 实体 + 自动化（待机断电/恢复充电/低温禁充/时钟同步/离线检测）
5. 联调：待机断电（发电 <5W 持续 30min）→ 晨间恢复 → 低温禁充（冰箱温度计模拟 <2°C / >5°C 回差）
6. PZEM-017（待购到货后）：48V 主回路负极串分流器（位置见 04-power-system）、地址改 0x11、集成方式定案（[pzem-017.md](energy/pzem-017.md)）
7. HA：SolarTotal 总电量 + PZEM 累计电量进能源面板

**配图**：[smart-architecture.svg](./diagrams/smart-architecture.svg)（MPPT/PZEM 在总线中的位置）

**出口验收**：
- [ ] 能源面板数据正确（PV 电压/充电电流/总电量与 MPPT LCD 一致）
- [ ] 待机断电/低温禁充自动化触发与恢复正确（断网也生效）
- [ ] 离线检测：拔掉 MPPT 485 → SolarAlert 显示离线

## 阶段 6：传感器接入

**入口**：阶段 3 完成（HA + ESP32 在线）。

三条路径分别做（对照 [sensors-paths.svg](./diagrams/sensors-paths.svg)）：

1. **485 路径**：温湿度 ×2 + 水位 ×2 并上 485 总线——**选型硬要求 9600 8N1**（阶段 4 已统一），地址 0x20 起
2. **DI 路径**：门磁 ×2（中门/尾门）+ 漏水 ×2（底盘/窗边）接模块 DI 口——**先核对各模块 DI 占用表**（[switch-assignment.md](../04-power-system/switch-assignment.md)），COM 接电源负极（模块内部上拉）
3. **MQTT 路径**：ELM327 插 OBD 口 → 车机装 Torque 配好发布 → HA 加 MQTT 集成订阅 → 自动化（RPM>500 行车充电判定、电压跳变迎宾）

**配图**：[sensors-paths.svg](./diagrams/sensors-paths.svg)

**出口验收**：全部传感器实体在 HA 上线且数值合理；门磁开门亮灯联动生效；OBD 数据刷新（车机断电 = OBD 断，行车判定留兜底）。

## 阶段 7：显示终端

**入口**：阶段 3 完成。

1. **安卓车机**（生活区中控大屏）：壁挂安装 → 装 Fully Kiosk → 固定 IP .30 → 全屏锁定 HA Dashboard
2. **小米平板4**（副驾/后床旁快拆）：按 [tablet.md](n100-ha/tablet.md) 拆机验证直供电（12V→5V，NTC 坑待实测）→ 快拆座（磁吸触点/Type-C，供电随座走）→ Fully Kiosk 常亮
3. **手机**：Companion App 配对（推送已在阶段 0 装好）+ Tailscale 车外访问

**配图**：[network-topology.svg](./diagrams/network-topology.svg)

**出口验收**：三端同时显示 Dashboard；任一端可控制全车实体；推送通知到达手机；平板快拆换位不断电。

## 阶段 8：监控与音响

**入口**：阶段 0 完成（Frigate 可后装）；音响负载位已按 [11-entertainment](../11-entertainment/) 开孔。

1. **监控**：AHD 摄像头 ×4 安装（原车摄像头 Y 型并联）→ DVR 编码器（有线 .100，12V 保险盒取电预留位）→ N100 装 Frigate 接 RTSP → HA 告警 + 平板查看。部署细节 [docs/deployment/frigate.md](../../docs/deployment/frigate.md)
2. **音响**：R600 接线（音源 N100/蓝牙/车机 → 前门 DM65C / 后门 DM65 / PWE-S800 低音炮 / 额头柜喇叭）→ DSP 声场预设（驾驶/影院/派对）→ 驾驶室键3 经 额头.R3 切 DSP+低音炮电源
3. 调试：四路监控画面/AI 告警；三声场切换 + 低音炮相位

**配图**：[media-chain.svg](./diagrams/media-chain.svg)

**出口验收**：四路画面全端可达 + 人形告警推送；三声场切换正常，键3 切电源正常。

## 阶段 9：中控台机器人（后期，待选型）

**入口**：阶段 3 + 7 完成（HA 在线 + Dashboard 成熟）；BOM 选型完成（[robot/bom.md](robot/bom.md)）。

1. 结构：表情屏 + 麦克风阵列 + 喇叭 + 舵机 ×N（转头/手臂）+ 3D 打印外壳，中控台固定（防倒）
2. 身体桥：ESP32（USB-CDC 倾向）→ 舵机 PWM/触摸/状态灯 → HA
3. 大脑（N100）：HA Assist 语音管线（openWakeWord 本地唤醒 → STT → 意图 → 实体控制 → TTS）+ 表情渲染（状态映射：待机/聆听/思考/说话/报警）
4. 联动：主动播报（低电量/待机断电/离车未锁 → 语音+表情）

**边界**：机器人是**操作入口**（与手机/平板/车机平级），不是安全关键执行者；依赖 N100 常开——N100 关机机器人变摆设，但全车安全功能不受影响（[robot/design.md](robot/design.md)）。

**出口验收**：唤醒词本地唤醒 → 语音控制全车实体 → TTS 回复；状态表情映射正确。

## 十、施工照片拍摄规范

配图分两类：**电路/架构 SVG**（本模块 `diagrams/`，随设计更新）和**施工照片**（实物证据，放 `assets/photos/`）。按阶段拍，命名 `阶段-对象.png`：

| 阶段 | 必拍 | 拍法 |
|------|------|------|
| 0 | N100 + 路由器上架 | 带网口接线 + IP 标签，正面 |
| 0 | 固定 IP 配置界面 | 路由器 DHCP 保留列表截图 |
| 2 | 网关 ABS 盒内 | 扩展板 + 副板 + 5 根短导线，开盖特写 |
| 2 | 盒侧三个进线孔 | 12V/485 双绞/USB 各一 |
| 3 | 面板按键全亮 | 正面全貌（场景状态 LED） |
| 4 | 厂家软件波特率设置界面 | 写 9600 + 读回 00 01 同框 |
| 5 | MPPT LCD 设置页 | 地址 0x10 / 9600 / 远程控制方式 |
| 5 | MPPT 485 接线 | 并线点特写（A-A/B-B + 屏蔽层） |
| 6 | 传感器安装位 | 门磁/漏水/温湿度各一张，带环境参照 |
| 7 | 三端 Dashboard 同框 | 车机+平板+手机合影 |
| 8 | DVR + 摄像头位置 | 编码器接线 + 四路机位 |
| 8 | R600 接线 | 功放背板特写（音源+喇叭+电源） |
| 9 | 机器人正脸 + 侧拆 | 表情屏点亮 + 舵机结构 |

**技巧**（与 04 模块同规）：光线充足侧上方打光；关键部件标签/箭头标出；每阶段完成立刻拍，别攒到最后（视角会被后续工件封死）。

**嵌入文档**：照片放 `assets/photos/`，正文用相对路径引用，如 `![网关盒内](./assets/photos/2-网关-ABS盒内.png)`。README 底部 AutoGallery 只收 `assets/` 一级目录，想上模块首页的照片直接放 `assets/` 根。

## 后期扩展（零拆改）

- **车尾 4 路模块**：新导轨 → 485 末端并线 → 车尾保险盒供电 → 倒车灯就近出线 → 终端电阻移到车尾端（[switch-assignment.md §十二](../04-power-system/switch-assignment.md)）
- **485 传感器扩容**：总线末端并线 + 0x20 起分配地址（9600）
- **能源面板**：PZEM-017 到货后补入 HA Energy dashboard（[pzem-017.md](energy/pzem-017.md)）