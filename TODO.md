# VAN-PROJECT: Master Todo List

此列表记录了项目的整体进展，包括硬件、软件及工程模块。

## 📊 总体进度摘要

- **规划层**: 🟢 已完成 (100%)
- **设计层**: 🟡 进行中 (65%)
- **工程层**: 🟡 进行中 (45%)
- **软件层**: 🟡 进行中 (30%)

***

## 📅 详细任务列表

### 1. 规划与技术规范 (Planning & Specifications)

- [x] 制定改造方案大纲 ([modules/00-vehicle-layout/build-guide.md](modules/00-vehicle-layout/build-guide.md))
- [x] 建立项目预算表 ([docs/budget.xlsx](docs/budget.xlsx))
- [x] 智能化终极方案 ([modules/02-smart-control/design.md](modules/02-smart-control/design.md))
- [x] 全屋智能控制逻辑 ([modules/02-smart-control/design.md](modules/02-smart-control/design.md))
- [x] 淋浴模块设计方案 ([modules/04-shower-module/design.md](modules/04-shower-module/design.md))
- [x] 电力系统与智能化硬件 ([modules/01-power-system/design.md](modules/01-power-system/design.md))
- [x] 车顶平台与太阳能系统 ([modules/06-roof-platform/design.md](modules/06-roof-platform/design.md))
- [x] 多功能折叠卡座模块设计 ([modules/05-foldable-seat/design.md](modules/05-foldable-seat/design.md))

### 2. 底盘与基础处理 (Chassis & Foundation)

- [x] 底盘整备：全车防锈、钣金修复 ([modules/00-vehicle-layout/build-guide.md](modules/00-vehicle-layout/build-guide.md))
- [x] 基础防锈：打磨除锈、喷铁锈转化剂、环氧底漆
- [x] 驾驶室基础处理：止震、保温、TPE 脚垫铺设
- [ ] 车辆外部喷漆与翻新 (全车喷漆、轮毂修复) - **待办**

### 3. 车内基础设施 (Interior Infrastructure)

- [x] 地板施工：铺设龙骨、止震、XPS 保温、SPC 地板 ([modules/00-vehicle-layout/build-guide.md](modules/00-vehicle-layout/build-guide.md))
- [x] 两侧与吊顶保温隔热：三明治结构 (XPS + 聚酯棉 + 吸音棉)
- [ ] 吊顶翻毛皮包覆与拓展系统 (吊包轨道) - **进行中**
- [ ] 模块化框架施工：铝型材结构件组装 - **进行中**

### 4. 电力与智能化 (Electrical & Smart System)

- [x] 48V 电力系统架构规划
- [ ] 电池模块、分电模块、充电模块组装 - **进行中**
- [ ] 485 总线布线与继电器模块调试 - **进行中**（桌面按键链路已验收：单按/连击/快速连按均 1:1，无漏无双动。关键结论见 [build-guide §6.4 第 8~11 条](modules/10-smart-control/gateway/build-guide.md)：**不要加周期性 485 轮询**（10Hz 会把模块打挂）、**DI 模板传感器不要挂 filter**；已加模块断电后 0031H 上传使能保活。
  ✅ ~~临时测试固件（中8 X4 直切主灯）~~ **已回退并刷入设备**：`relay-mid-8ch.yaml` 的 `bs_door_camp` 已恢复 `- script.execute: act_camp`（X4 = 离车/驻车场景键），2026-10-28 经 web_server OTA 刷写成功并重启验证。
  待办：4 模块统一上总线核对地址 1/2/3/5、16DO LED 验收、38400→9600 改造）
- [ ] 面板线缆改中门柜汇总方案（全车统一 14P + 统一色序） - **待办**
- [ ] 床头面板（后床 2 键：通风模式 + 灯光模式，双色）+ 床头 4DI+4DO 模块 + 车顶 8 芯屏蔽网线 485 主干 - **规划中，暂不实施**，方案见 [modules/04-power-system/switch-assignment.md](modules/04-power-system/switch-assignment.md) §三之二
- [ ] **加装电动踏板：关门后偶发自动伸出** - **待排查**。踏板靠「门碰开关信号线」触发（开门伸/关门缩），症状=中门关着、门没动、踏板自己伸出 → 是「门状态检测信号」偶发误脉冲，非车门故障。根因排查：①门碰信号线极性接反/虚接（被门/踏板机构挤压、行驶震动偶发通断）②原车门碰开关氧化/进水 ③控制器抗干扰差。排查顺序：先量信号线电平是否稳定（区分「信号线问题」还是「控制器误动作」），再查极性+虚接，最后换控制器/加滤波电容。
- [ ] **踏板的独立兜底开关（物理切断触发信号线）** - **方案已定，待实施**。在「门碰信号线 → 踏板控制器」之间串一个手动开关：断开=踏板不自动伸缩（彻底防止误伸出），闭合=正常联动。**只动自己加装的触发线、不碰原车安全电路、强电（40A 主电瓶线）不进面板**。开关装进**入口面板第 4 键**（与排水/上水泵/离车驻车并排凑 4 键）。接线方案见 [switch-assignment.md §决策更新](modules/04-power-system/switch-assignment.md)。
- [ ] **入口面板 4 键定案**（排水 + 上水泵 + 离车驻车 + 踏板兜底切信号线）+ **户外灯移驾驶室（负载侧直连）** + **中控 6 键取消** + **16DO 退役** - **方案已定，待施工**。全部决策见 [switch-assignment.md §决策更新](modules/04-power-system/switch-assignment.md)。
- [ ] **大功率负载统一「两级切换」分级**（>10A/48V 用大继电器/接触器，模块 DO 只切线圈；≤10A 直切）— 电动踏板40A、DSP+低音炮40A、车头射灯30~40A、48V泵+MPPT 63A 接触器（已有）。方案见 [switch-assignment.md §决策更新·决5](modules/04-power-system/switch-assignment.md)。**待逐个实测额定电流后定档**。
- [ ] **能源系统三件套：逆变器 / MPPT / 行车发电（DC-DC）接入面板** - **部分前置已明确**。① **逆变器**：🟢 **已购 5000W**，方案已定——**继电器短接 RJ 口两根线**（不走私有协议），见 [switch-assignment.md §决6](modules/04-power-system/switch-assignment.md)。⚠ **施工前必须实测 RJ 口是无源干接点还是带电压**（决定继电器选型）；⚠ **直流侧 116A** 需 ≥25mm² 线 + 150~200A 保险 + **就近装电池旁**；⚠ 需确认 JK BMS 持续放电额定。② **MPPT**：协议档未实测定档（协议档 vs 硬件档 63A 接触器，见 [mppt-protocol.md §四](modules/10-smart-control/energy/mppt-protocol.md)）；**光控/时控暂不加**——`0x0C` 与远程控制互斥，且远程开关尚未经总线改造验证，见 [gateway/README.md](modules/10-smart-control/gateway/esphome/README.md)。③ **行车发电**：DC-DC **不支持 485**，无协议可控，输出侧接触器方案暂缓。⚠ 面板已在「开关页 → 能源系统」组预留 3 张**置灰占位卡**（不可点击），定档后填 `ENTITIES` 即可启用。
- [ ] **JK BMS（极空）接入** —— ⚠ **只能走 BLE**：电池已封箱，主控板在电池内部，**物理上接不到 UART/GPS 口**（UART 方案彻底排除）。可读 **16 节单体电压/最大压差/循环次数/均衡状态**（库仑计给不了，压差是电池健康核心指标；实测 0.005V，一致性极好）。**方案已定，暂不实施**。用独立 BLE 代理 ESP32 跑 [syssi/esphome-jk-bms](https://github.com/syssi/esphome-jk-bms)（`ble_client` 模式，需 MAC）；BLE 天然电气隔离、零接线。⚠ BLE 稳定性是唯一风险（组件有掉线 issue），**掉线时面板退回库仑计显示**，不会看不到电量。面板设计：电池页新增「电池健康」卡，**16 节单体 4×4 网格 + 压差着色**；与库仑计**两个都显示不覆盖**。待确认：BLE 广播名/MAC、电池金属壳对 2.4G 的衰减、温度传感器是否接、BMS 持续放电额定（5000W 逆变需 116A）。方案见 [jk-bms-integration.md](modules/10-smart-control/energy/jk-bms-integration.md)。
- [ ] N100 部署 PVE/HA/Frigate 环境 - **进行中**（PVE 8.4 已装；Windows 调试机 + 核显直通 + RDP 已通，见 [docs/deployment/n100-windows-gpu-passthrough.md](docs/deployment/n100-windows-gpu-passthrough.md)；HAOS/Frigate 因 8G 内存上限待排期）
- [ ] 360 影像扩展与后视镜监控集成 - **待办**

### 5. 功能模块实现 (Functional Modules)

- [ ] 车尾可移副箱 + 中门/尾门双加水口（加水/用水自由切换）：量柜下净空 → 买快拆自封件、双注水口、副箱 → 阶段 1A 预制与安装 - **设计完成，待下料**，方案见 [modules/05-water-system/design-tank-portability.md](modules/05-water-system/design-tank-portability.md)
- [ ] **阀D 夏季旁路（必装·与热水支路同期）**：冷水主干 → 热水主干（阀O之后）；不装则夏季关H/O后**水槽热水口断水**、恒温阀热入口不出水 - **已定必做，不得延后**，见 [build-guide 5.3.1](modules/05-water-system/build-guide.md)
- [ ] 淋浴模块：不锈钢接水盆安装与防水测试 - **待办**
- [ ] 车尾横向淋浴帐（无立腿版）：实测车高/尾门/尾梯尺寸 → 挂臂与挂轨 → 1000 宽顶框 + 整根后横杆（左 90° 活动件 + 右快拆搭扣） → 卷袋与接水盘 - **设计完成，待下料**，方案见 [modules/02-external/design-shower-tent-noleg.md](modules/02-external/design-shower-tent-noleg.md)（含 [3D 收折动画](modules/02-external/assets/shower-frame-3d.html)）
- [ ] 户外厨房：重型滑轨与 IGT 模块集成 - **待办**
- [ ] 智能化排风扇系统 (PWM 调速、亚克力固定) - **待办**
- [ ] 影音系统：Alpine R600 DSP 调试与扬声器安装 - **待办**
- [ ] 多功能折叠卡座：铝型材框架组装与翻板测试 - **待办**
- [ ] 抽拉/上翻冰箱集成与电路连接 - **待办**

### 6. 软件应用开发 (Software Apps)

- [x] 车机控制面板 (ESP32 自托管深蓝 UI，仿原 React 仪表盘主题，`/dashboard` 离线可用) — 原 rv-dashboard (React) 已删除，由 ESP32 面板取代
- [ ] 接入 TF03K 库仑计 / 水箱液位传感器，面板补真实水箱与电量数据 - **待办**
- [ ] 设计”驾驶/影院/营地”场景切换逻辑 - **待办**
- [ ] 优化监控画面与能源监测图表 - **待办**

***

## 📝 备注

- 任务状态标记：\[ ] 待办, \[/] 进行中, \[x] 已完成。
- 详细施工工艺请参考 [modules/00-vehicle-layout/build-guide.md](modules/00-vehicle-layout/build-guide.md)。
- 各模块设计决策见 [modules/](modules/)。

