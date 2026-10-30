# JK BMS（极空）接入方案

> **状态：固件未实施，面板前端已就绪**（2026-10-31 更新）。
> 接入路径与安全约束已定；`web/index.html` 的「电池健康 (JK BMS)」卡**已实现**，
> `dev-preview.py` 内置 mock 数据（`--no-bms` / `--bms-bad` / `--bms-na-temp` 三种演示态）。
> 硬件（BLE 代理 ESP32）就位后，固件只要按 §四 的实体名推数，面板直接出图。
>
> **⚠ 硬约束：只能走 BLE。** 电池已封箱、主控板在电池内部，**物理上无法接出
> UART/GPS 口**。UART-TTL 方案彻底排除（见 §二）。

## 零、前置事实

| 项 | 已知 | 影响 |
|----|------|------|
| 电池 | 48V 铁锂 **16S**，容量 **220Ah** | 单体数 = 16，面板按 4×4 网格 |
| 封装 | **已封箱，主控板在内部** | **只能 BLE**，无 UART |
| 通讯 | 有**蓝牙协议 + 官方 App**（截图已验证数据完整） | BLE 方案可行 |
| 实测一致性 | 最大压差 **0.005V** | 电池状态极好，压差阈值可设严 |
| 温度 | 截图显示 `NA` | 温度传感器未接，需确认 |

## 一、为什么值得接

电池自带 **JK（极空）BMS 控制板**，有蓝牙协议和官方 App。相比现有库仑计 TF03K，
BMS 能提供**电池健康层面的信息**，这是库仑计给不了的：

| 数据 | 库仑计 TF03K | **JK BMS** |
|------|-------------|-----------|
| SOC / 剩余容量 | ✅ | ✅（且更准，有实际容量学习） |
| 总电压 / 电流 / 功率 | ✅ | ✅ |
| **单体电压（16 节）** | ❌ | ✅ **关键** |
| **最大压差** | ❌ | ✅ **电池一致性核心指标** |
| 均衡状态 / 均衡电流 | ❌ | ✅ |
| **循环次数** | ❌ | ✅ 健康度参考 |
| 电池温度 | ❌ | ✅（截图显示 NA，需接传感器） |
| 休眠时间 / 详细日志 | ❌ | ✅ |

**最大压差是最有价值的指标**——它是判断电池组是否出现单体劣化、连接松动的最直接信号。
截图实测 **0.005V**（16S 铁锂），一致性极好。

## 二、接入方式：**只能走 BLE**（已定，无备选）

社区成熟组件：[`syssi/esphome-jk-bms`](https://github.com/syssi/esphome-jk-bms)
（fork：`jamesnzfix`、`EasilyBoredEngineer`），支持 **BLE** 与 **UART-TTL** 两种模式。

### ⚠ UART 方案已不可行（2026-10-30 用户确认）

> **电池已封箱，主控板在电池内部，物理上无法接出 GPS/UART 口。**
> 因此 UART-TTL 方案**彻底排除**，连"加隔离模块"的前提都不存在。

这个约束反而**消除了一个安全风险**。原本 UART 方案有个严重隐患：

> `GPS` 口的 **GND 直接连电池 `B-`**（[JK-B 官方文档](https://raw.githubusercontent.com/Sleeper85/esphome-yambms/3419f7ccc5174167fe67760b228b384008bfbbee/documents/README/BMS_JK-B.md)）。
> 即使 BMS 处于保护/停止状态，该 GND 与 `B+` 之间仍能测到**全电压（56V）**。
> 若 ESP32 的地与其他设备（逆变器、库仑计分流器）共地，会**绕过 BMS 保护（P-）**，有危险。

**BLE 是无线连接，零电气接触 → 天然满足隔离要求，不存在上述风险。**

### BLE 方案的唯一缺点：稳定性

| 项 | 说明 |
|---|---|
| 稳定性 | ⚠️ 组件实测有掉线问题（[#659](https://github.com/syssi/esphome-jk-bms/issues/659)、[#235](https://github.com/syssi/esphome-jk-bms/discussions/235)），社区持续修 |
| 连接方式 | **主动连接**（非广播监听），需持续维持 BLE 链路 |
| 应对 | ① 组件内置重连；② 面板显示"最后更新时间"，掉线可感知；③ 用**独立 ESP32** 专跑，不与其他 BLE 任务抢射频 |

> **BLE 掉线时的兜底**：库仑计 TF03K 走独立 19200 UART 只收，与 BLE 互不影响。
> BMS 掉线时面板继续显示库仑计数据（两者并列展示，不互相覆盖），**不会因为 BLE 断了就看不到电量**。

## 三、架构

```
JK BMS ──BLE──→ ESP32（独立 BLE 代理，跑 esphome-jk-bms）
                          │ WiFi
                          ├──→ 主网关 /dashboard（面板展示）
                          └──→ HA（N100，长期记录）
```

⚠ **关键限制**：`esphome-jk-bms` 的 BLE 模式需要**主动连接**（非广播监听），
这与 `bluetooth_proxy`（被动代理广播）**不是一回事**，两者**不能在同一台 ESP32 上共存良好**。
故 BLE 代理若同时要收温湿度广播，**需评估是否分两台**，或用组件的 `uart` 模式。

> 待实测确认：同一台 ESP32 能否既跑 `jk_bms`(BLE 连接) 又跑 `bluetooth_proxy`。
> 若不能，建议：**BMS 专用一台**（数据重要、要稳定），温湿度仍用另一台代理。

## 四、面板展示设计（**已实现**）

用户已确认：**完整展示，含 16 节单体电压**；与库仑计**两个都显示，不互相覆盖**。
代码位置：`gateway/esphome/web/index.html`
（映射 `BMS_SENSORS` / `BMS_BINARY` / `BMS_TEXT`，渲染 `renderBms()`）。

### 电池页「电池健康 (JK BMS)」卡

```
┌─ 电池健康 (JK BMS)              3s 前 ─┐   ← 右上角常驻「数据龄」，BLE 掉线可感知
│ SOC 57.0%   52.95V  30.74A  1627.7W    │
│ 剩余/总容量 124.9/220Ah   循环次数 0 次  │
│ 最大压差 0.005V ●良好    均衡电流 -0.39A │
│ 运行状态 充电中           电池温度 28.5°C│
│ 充电 MOS ON   放电 MOS ON               │
│ 告警 无告警              有效帧 1024     │
├─ 单体电压 16S ─────────────────────────┤
│  01 3.309  05 3.308  09 3.310  13 3.313│  ← 4×4 列优先
│  02 3.308  06 3.309  10 3.310  14 3.310│
│  03 3.308  07 3.308  11 3.310  15 3.310│
│  04 3.308  08 3.309  12 3.310  16 3.309│
│  最高 #13 3.313V        最低 #02 3.308V │
└────────────────────────────────────────┘
```

- **单体电压 4×4 网格**（`grid-auto-flow: column`，读图顺序 01→04 竖排），每格序号 + 3 位小数
- **压差着色**：`<0.02V` 绿（良好）/ `0.02~0.05V` 黄（留意）/ `>0.05V` 红（异常）
- **最高单体标蓝、最低标黄**：最高用于发现充电时先过压的电芯，最低则是限制整包容量的那节
- **压差优先用 `BmsDelta`**；该实体缺失时由已收到的单体实时算，保证与上方网格一致
- **不覆盖库仑计**：库仑计卡保留且仍是**主电量来源**（硬线、离线可靠、不依赖 BLE），
  BMS 的 SOC 作为对照——两者差值本身就是校准/接线问题的信号
- **未上线占位**：一帧都没收到时只显示一行「JK BMS 未上线 · 等待 BLE 代理数据」，
  不铺一排空的 `--`；掉线后卡片**变灰但保留最后数值**，并显示「数据陈旧 / 数据中断」
- **温度报 `NA` 时显示 `--°C`**，不会误显示成 0

### 实体命名约定（固件按此实现）

沿用现有 `<前缀> <中文名>` 风格，前缀用 `Bms`：

| 实体名 | 域 | 说明 |
|--------|----|------|
| `BmsSoc 电量` | sensor | SOC % |
| `BmsVolt 总电压` | sensor | V |
| `BmsCurr 电流` | sensor | A（正=充电 / 负=放电） |
| `BmsPower 功率` | sensor | W |
| `BmsCap 剩余容量` | sensor | Ah |
| `BmsTotalCap 总容量` | sensor | Ah（本车 220） |
| `BmsCycles 循环次数` | sensor | 次 |
| **`BmsFrames 有效帧数`** | sensor | **必填**，每收到一帧 +1（理由见下） |
| `BmsDelta 最大压差` | sensor | V |
| `BmsBalCurr 均衡电流` | sensor | A |
| `BmsTemp 电池温度` | sensor | °C（传感器未接会报 `NA`） |
| `BmsCell1..16 单体电压N` | sensor | V，共 16 个，编号即串号 |
| `BmsChgMos 充电MOS` | binary_sensor | ON/OFF |
| `BmsDchgMos 放电MOS` | binary_sensor | ON/OFF |
| `BmsState 运行状态` | text_sensor | 充电中 / 放电中 / 待机 |
| `BmsAlarm 告警` | text_sensor | 无告警 / 具体告警文本 |

> **⚠ 为什么 `BmsFrames 有效帧数` 是必填**：ESPHome 的 `web_server` **只在值变化时**推 SSE。
> 电池静止（电流/电压/单体都不变）时不会有任何事件到达，面板无法区分
> 「BLE 链路断了」和「数值恰好没变」——这正是本卡最需要判断的事。
> 让一个计数器每帧 +1，就保证了心跳。库仑计用 `CoulombDiag 有效帧数` 是同一个套路。
>
> ⚠ 实现时这些 `name:` 必须与 `web/index.html` 的 `BMS_*` 映射逐字一致，
> 自查方法见 [gateway/README.md §实体名路由](../gateway/esphome/README.md)。

### 本地预览

固件未就位时可先用 mock 数据打磨面板：

```bash
cd modules/10-smart-control/gateway/esphome/web
python3 dev-preview.py            # 正常态（16 节单体 + 压差 0.005V）
python3 dev-preview.py --no-bms   # 未上线占位态
python3 dev-preview.py --bms-bad  # 压差 0.051V → 红色「异常」+ 告警
python3 dev-preview.py --bms-na-temp   # 温度 NA → 显示 --
```

## 五、实施步骤（等硬件到位）

1. **确认 BMS 型号与蓝牙名**（截图未显示型号；JK 常见 `JK-B2A24S`、`JK-BD6A24S` 等）
   用手机 App（JK 官方 App 或第三方如 `JK BMS Monitor`）扫描 BLE 设备，记下广播名/MAC
2. 用手机 App 确认能正常读出全部数据（**已有截图，说明 BLE 协议通、数据完整**）
3. 在**独立 BLE 代理** ESP32 上加 `jk_bms` 组件（`source: github://syssi/esphome-jk-bms`，
   `ble_client` 模式需填 MAC 地址）
4. BLE 连接测试：稳定性、断线重连、数据刷新率、**车内距离/金属壳对信号的影响**
5. 主网关不直接加（Flash 与故障隔离考虑）；主网关用 `http_request` 拉 BLE 代理的
   ESPHome REST，映射成 §四 的 `Bms*` 实体（面板零改动，代理掉线只影响这张卡）
6. ~~面板加「电池健康」卡~~ → **✅ 已完成**（2026-10-31）：卡片、16 节网格、压差着色、
   数据龄、未上线占位均已实现，并配 `dev-preview.py` mock（见 §四）

> **UART 兜底不存在**（电池已封箱）。若 BLE 稳定性无法接受，可选的改进方向是：
> ① 调整 BLE 代理天线的位置/朝向；② 组件参数调优（连接间隔、超时重连）；
> ③ 等待组件修正（[#659](https://github.com/syssi/esphome-jk-bms/issues/659) 等）；
> ④ **退回只用库仑计**（TF03K 已就绪，只是看不到单体电压）。

## 六、待确认清单

- [ ] BMS 具体型号（决定协议变体）
- [ ] BMS 持续放电电流额定值（**5000W 逆变器需 116A**，见
      [switch-assignment.md §决6](../../04-power-system/switch-assignment.md)）
- [ ] 电池温度传感器是否接（截图显示 NA）
- [ ] 同一 ESP32 能否并存 `jk_bms`(BLE) 与 `bluetooth_proxy`
- [ ] BLE 实测刷新率与稳定性
- [ ] **BLE 广播名/MAC**（`ble_client` 配置必填）
- [ ] 电池外壳对 BLE 信号的衰减（金属壳会明显削弱 2.4G）
- [x] ~~UART 接入~~ → **已排除**：电池封箱，接不到 GPS 口

## 参考

- [syssi/esphome-jk-bms](https://github.com/syssi/esphome-jk-bms) — ESPHome 组件（BLE / UART）
- [JK-B BMS 文档（YamBMS）](https://raw.githubusercontent.com/Sleeper85/esphome-yambms/3419f7ccc5174167fe67760b228b384008bfbbee/documents/README/BMS_JK-B.md) — 接线与隔离警告（**本车上不适用**，因无法接 UART）
- [Issue #659](https://github.com/syssi/esphome-jk-bms/issues/659) — BLE 稳定性改进
