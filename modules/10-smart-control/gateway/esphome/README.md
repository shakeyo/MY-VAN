# ESPHome 固件

单 ESP32-S3 集中编译，packages 按区域拆分。生产固件 = `prod.yaml` 组装，测试件按阶段独立。

> 源文件以仓库为准；构建站点时 `.esphome/` 编译产物不随站发布。

## 生产文件

| 文件 | 内容 |
|------|------|
| `base.yaml` | 基础：网络/串口/上电策略/场景状态/DI 上传驱动解析 |
| `forehead.yaml` | 额头模块（地址 0x01）：通道 + 按键 |
| `mid8.yaml` | 中门 8 路（地址 0x02） |
| `mid4.yaml` | 中门 4 路（地址 0x03） |
| `scenes.yaml` | 场景自动化（灯光模式/离车驻车/排气扇/长按全关） |
| `prod.yaml` | 生产主文件（以上 packages 的组装） |

## 测试文件

| 文件 | 阶段 | 内容 |
|------|------|------|
| `test-485-connect.yaml` | 阶段2 桌面 | 485 连通性（手动帧 + 总线监听） |
| `test-mid8-logic.yaml` | 桌面（4.5） | 中8 全逻辑（场景循环/双控/长按/断电恢复） |
| `test-channel-mapping.yaml` | 上车第一步（4.6） | 3 模块 16 路继电器 + 按键映射（按键只读） |

## 规划

- `mppt.yaml`（待建）：MPPT 485 轮询 + 实体 + 自动化，见 [energy/mppt-protocol.md](../energy/mppt-protocol.md)
