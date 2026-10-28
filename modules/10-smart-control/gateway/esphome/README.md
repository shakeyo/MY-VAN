# ESPHome 固件

单 ESP32-S3 集中编译，packages 按区域拆分。生产固件 = `prod.yaml` 组装，测试件按阶段独立。

> 源文件以仓库为准；构建站点时 `.esphome/` 编译产物不随站发布。

## 生产文件

| 文件 | 内容 |
|------|------|
| `rs485.yaml` | **485 写帧公共件**：DE/RE 方向时序 + 参数化 `rs485_write` 脚本 |
| `base.yaml` | 基础：网络/串口/上电策略/场景状态/DI 上传驱动解析/LED 全灭 |
| `relay.yaml` | **继电器模块汇总入口**：include 下面 4 个子模块，并附「模块×站号×路数」索引表。站号因与帧 CRC 绑定，实际值仍写在各自子文件里 |
| └ `relay-forehead-8ch.yaml` | 额头 8 路（地址 0x01）：负载 + 按键 |
| └ `relay-mid-8ch.yaml` | 中门 8 路（地址 0x02）：纯负载 7 路 + 1 预留 |
| └ `relay-mid-4ch.yaml` | 中门 4 路（地址 0x03）：低功率负载 3 路 + 1 预留 + 读键5-6 |
| └ `relay-mid-16do.yaml` | **中门 16DO（地址 0x05）：全部 LED（12 现用 + 4 预留）** |
| `mppt.yaml` | **光伏控制器（地址 0x10）**：监控实体 + 控制 + 时钟同步 + 应答解析 |
| `pzem-tf03k.yaml` | **库仑计 TF03K**：独立第二路 UART（19200 只收）+ 16 字节帧解析（见下） |
| `scenes.yaml` | 场景自动化（灯光模式/离车驻车/排气扇/长按全关） |
| `scene-state.yaml` | 场景档位传感器（把 globals 的 light/camp/fan_scene 暴露成 REST 可读的 sensor） |
| `system.yaml` | **系统与维护**：WiFi 状态（SSID/IP/信号）+ 重启按钮（供面板设置页） |
| `panel.yaml` | **手机控制面板**：挂载自定义组件 + 指定页面文件与路由（见下） |
| `web/index.html` | 面板页面本体（自包含深蓝 UI，SSE 订阅 + REST 命令，随固件打进 Flash） |
| `components/forager_panel/` | 自定义 external_component（C++，serve index.html 到 `/dashboard`） |
| `prod.yaml` | 生产主文件（以上 packages 的组装） |

### 手机控制面板（/dashboard）

自 2026-10-27 起，固件内置一个**自包含手机控制面板**，复刻 RV Dashboard（React）的深蓝
FORAGER 主题，但彻底零依赖、离线可用。

- **机制**：自定义组件 `forager_panel`（见 `components/`）在 `web_server_base` 上额外注册一条
  HTTP handler，把 `web/index.html` gzip 后打进 Flash，serve 到 **`/dashboard`**。
  页面用 **ESPHome 原生 SSE 流（`/events`）** 订阅实时状态与日志，**命令**走 REST（`POST /switch/<name>/toggle`），
  **页面与数据都在 ESP32 本地**，不依赖任何 CDN/HA/N100。
- **实时日志 / 调试**：面板底部「调试」页通过 `EventSource('/events')` 订阅 `log` 事件，实时滚动显示
  ESP32 日志（485 按键 `[di]`、轮询计数 `[stat]`、MPPT 告警等），带「暂停 / 清空 / 自动滚底」。初期排查
  485 模块不稳定时，手机打开即可看日志，无需插电脑。
- **设置页**：底部「设置」页分三块——①光伏充电控制（充电输出开关、允许充电开关、充电限流滑块 0~40A、
  4 个维护按钮：远程控制/时钟同步/读参数/消音，均来自 `mppt.yaml` 已有实体）；②系统与维护（WiFi SSID/IP/信号
  显示 + 一键重启 ESP32 + 跳原生 OTA 页，来自 `system.yaml` 新增实体）；③面板偏好（日志自动滚动开关，存
  localStorage，不落 ESP32）。
- **为什么是自定义组件**：ESPHome 原生 `web_server` 的 `/` 被 `<esp-app>`（官方 Lit 前端）锁死，
  `js_include`/`css_include` 只能**叠加**在原生界面上、不能替换整页，且与 `local: true` 互斥。
  要「打开就是自己的界面 + 完全离线 + 自由布局」，唯一干净的路是外部组件自己注册路由
  （详见 [build-guide.md §6.5](../build-guide.md)）。
- **入口**：手机打开 `http://<esp32-ip>/dashboard`（兜底 AP `http://192.168.4.1/dashboard`）。
  原生 `web_server` 前端照旧在 `/`，两者并存、互不干扰。
- **实体名路由**：`web_server` 用实体的 `name`（而非 `id`）做 URL 匹配，故 `web/index.html`
  里的 `ENTITIES`/`SCENE_SENSORS` 记录了每个 key 的**精确中文 name**。改任何实体的 `name:`
  后，必须同步改 `web/index.html` 里的对应映射，否则该开关在面板上会读不到。
- **场景档位**：`light_scene`/`camp_scene`/`fan_scene` 本是 `base.yaml` 的 globals（非实体、
  REST 读不到），由 `scene-state.yaml` 用 3 个 template sensor（`SceneLight`/`SceneCamp`/`SceneFan`）
  每 1s 读出真实值，面板借此显示真实档位。
- **水位显示已移除**：面板不含水位刻度（固件暂无可读的水箱液位传感器——现用的房车水箱探头为
  模拟/机械式、读不到连续数值）。清水/灰水/黑水的**水位显示**已从面板删除；**上水泵 / 电控水阀**
  等真实 RS485 继电器开关仍保留。等换上 485 数字液位传感器（0x20 起）后，再在面板补 `sensor` 映射。

### 485 地址占用

| 地址 | 设备 |
|------|------|
| 0x01 | 额头模块（8 路，未买） |
| 0x02 | 中门 8 路（纯负载） |
| 0x03 | 中门 4 路（未来负载扩展） |
| 0x05 | **中门 16DO（全部 LED，已到货）** |
| 0x10 | MPPT（易科 Fcu，**固件已就绪**，见 `mppt.yaml`） |
| — | **TF03K 库仑计**（无地址、非 Modbus、19200 独立 UART，不在此总线） |
| 0x11 | （空出，原 PZEM-017 规划已作废） |
| 0x20+ | 485 传感器（建议） |

> 0x04 原规划给车尾模块，**该模块已取消**（倒车灯并进 中8.Y7），如未来要加设备可用 0x04。

### 写帧方式

通道动作只需给一条帧，DE 时序由 `rs485_write` 统一处理：

```yaml
on_turn_on:
  - script.execute:
      id: rs485_write
      frame: [0x02, 0x05, 0x00, 0x00, 0xFF, 0x00, 0x8C, 0x09]
```

帧格式 = `站号 FC 线圈地址高 低 值高 值低 CRC低 CRC高`（Modbus RTU，CRC16-Modbus 低字节在前）。
线圈地址：**通道 N = 地址 N-1**（Y1=0x0000）。

## 测试文件

| 文件 | 阶段 | 内容 |
|------|------|------|
| `test-485-connect.yaml` | 阶段2 桌面 | 485 连通性（手动帧 + 总线监听） |
| `test-mid8-logic.yaml` | 桌面（4.5） | 中8 全逻辑（场景循环/双控/长按/断电恢复） |
| `test-channel-mapping.yaml` | 上车第一步（4.6） | 4 模块全部通道映射（按键只读） |

## 独立固件（另一台 ESP32）

| 文件 | 用途 | 说明 |
|------|------|------|
| `ble-proxy.yaml` | **BLE 蓝牙代理**（收温湿度等 BLE 广播转 HA） | **独立一台 ESP32**，不并入 prod。理由与实测资源见 [sensors/ble-sensors.md](../../sensors/ble-sensors.md) |

> 为什么独立：BLE 协议栈约需 1.2MB Flash。并入主网关会让 Flash 从 53% 涨到 **75%**（偏紧），
> 且 BLE 故障会牵连承担安全关键自动化的主网关。独立后主网关保持 53%，故障隔离。

## ⚠ 波特率（MPPT 的硬前置）

当前全部固件为 **38400**（继电器模块出厂默认，桌面联调阶段）。全车终局为 **9600**
（MPPT 最高只支持 9600，见 [build-guide.md §4.7](../build-guide.md)）。

**MPPT 一挂上总线，就必须先完成 §4.7 改造**：4 个继电器模块改 9600 + 固件 4 处
`baud_rate` 改 9600。否则 MPPT（只有 9600）与继电器模块（38400）在同一条总线上
互相乱码，两边都用不了。

> ⚠ 波特率代码两家不同：**MPPT 的 9600 = 代码 4**（`0xDE` 群控或 LCD 设），
> **继电器模块的 9600 = 代码 1**（FC06 写 0033H）。

## MPPT 固件说明（mppt.yaml）

- **轮询**：每 10s 发 `0xA3/02` 查实时数据（协议要求间隔 ≥1s），38 字节应答
- **解析**：`solar_read` 每 100ms 扫 UART 缓冲，按「地址 0x10 + 命令码 + 已知帧长」
  定位并做 **CRC + 帧长双校验**，通过后交给 `solar_parse` 按偏移发布
- **实体**：8 路 sensor（PV/电池电压、充电电流、发电功率、日/总发电量、控制器/电池温度）
  + 2 路 text_sensor（充电状态、告警）+ 充电输出/允许充电开关 + 充电限流 number
- **维护按钮**：设为远程控制 / 时钟同步 / 读设置参数 / 蜂鸣器消音
- **本地自动化**：见 [energy/mppt-protocol.md §三](../../energy/mppt-protocol.md)

> **待实测定档**（见 mppt-protocol.md §四）：关闭 DC 输出后控制器待机电流是否归零、
> 485 是否仍响应——决定走「协议档」还是「硬件档（加 63A 接触器，额头.R6 驱动）」。
> 本文件目前实现了**协议档**的监控与控制骨架；定档后如需硬件档再补 R6 驱动逻辑。

## 库仑计固件说明（pzem-tf03k.yaml）

**TF03K 库仑计**，2026-10-28 新增。实物经查为 TF03K（原规划 PZEM-017 作废）。

- **接口**：独立**第二路 UART**（`coulomb_uart`，**19200**，TX=GPIO5 / RX=GPIO4，实际只用 RX）
- **协议**：私有主动上报，**16 字节/次，1 次/秒**，无地址、非 Modbus、**8 位累加和**（非 CRC16）
- **只收不发**：TF03K 的 RXD 无接收功能，固件不含任何写帧，**不调用 `rs485_write`、不做 DE 切换**
- **帧解析**：`coulomb_read` 每 200ms 扫 UART 缓冲 → 找 `0xA5` 帧头 → 验累加和 → 解析发布；
  残帧跨 tick 保留（与 `base.yaml` 的 `read_upload` 同思路）
- **实体**：6 个 sensor（SOC%/电压/剩余容量/电流/剩余时间/功率）+ 2 个诊断计数

### 帧结构（16 字节）

| 字节 | 内容 | 换算 |
|------|------|------|
| 1 | 帧头 `0xA5` | — |
| 2 | 电量百分比 | 直取 % |
| 3-4 | 电压 | 大端 16，÷100 → V |
| 5-8 | 剩余容量 | 大端 32，mAh ÷1000 → Ah |
| 9-12 | 电流 | 大端 32 有符号（补码），mA ÷1000 → A |
| 13-15 | 剩余时间 | 大端 24，秒 |
| 16 | 校验和 | 前 15 字节 8 位累加和 |

### ⚠ 接线与总线隔离

- **严禁与 9600 Modbus 总线同挂**：波特率、协议、方向、寻址全都不同。
- TF03K RS485 A/B → MAX3485 → ESP32 RX；**MAX3485 的 DE/RE 接 GND（常接收）**，不要接 GPIO。
- TF03K **内部已含 120Ω 终端电阻**；网关侧 MAX3485 若也带终端，仅在总线两端各保留一颗、避免过量匹配。
- **待实测确认**：电流正负方向（协议只写"负值为补码"，未说明充/放哪边为正）。

### 关于 UART 列表化（base.yaml 已改）

引入第二路 UART 时发现：ESPHome packages 合并时**映射写法与列表写法不能共存**，
若 base 用 `uart:` 映射、本文件用 `uart:` 列表，base 那一路会被覆盖（报 `Couldn't find ID 'rs485_bus'`）。
故 `base.yaml` 的 uart 已统一改为**列表形式**（**只改写法，485 引脚/波特率不变**，行为与改动前一致）。
实测 `esphome config` + `esphome compile` 通过，两路并存：`rs485_bus` 38400 / `coulomb_uart` 19200。

## 规划

- ~~`pzem.yaml`（待建）：PZEM-017~~ → **已改为 `pzem-tf03k.yaml`（已建成）**：
  实物为 TF03K 库仑计（非 PZEM-017），协议完全不同，见 [energy/pzem-017.md](../../energy/pzem-017.md)
