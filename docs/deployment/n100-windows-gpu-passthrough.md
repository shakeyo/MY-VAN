# N100 Windows 调试机 · 核显直通与远程访问

N100 上跑一台 **Windows 10 LTSC 虚拟机**，作为车内设备（485 总线、继电器模块、MPPT 等）的
调试终端，偶尔兼作影音播放。本文记录 **Intel N100 核显直通 + HDMI 输出 + RDP 远程访问**
的完整配置、验证方法与踩坑记录。

> **一句话结论**：单核显直通到 Windows 可行，但**必须保留虚拟显卡（`vga: std`）作兜底**——
> 直通失败时 RDP / PVE noVNC 仍可进；HDMI 物理上屏则靠核显直通实现。

## 1. 目标与验收标准

| 目标 | 验收方式 |
|---|---|
| 车内用平板/笔记本远程进 Windows 调 485 | `mstsc`/Windows App 连 `192.168.43.210:3389` 成功登录 |
| N100 的 HDMI 直接显示 Windows | 显示器出现 Windows 桌面 |
| 核显真正直通（不是虚拟显卡） | PVE 宿主机 `lspci -k -s 00:02.0` 显示 `vfio-pci`；guest 内 `Intel(R) UHD Graphics`、`Problem=CM_PROB_NONE`、模式 `3840x2160@60` |
| 重启后自动恢复 | 整机重启后 VM 自动启动、直通生效、RDP 可达 |

## 2. 硬件与软件基线

| 项 | 值 |
|---|---|
| 主机 | N100 迷你主机，4 核 / **8GB DDR4-3200 单槽（本机上限 8G）** |
| 存储 | 141G thin pool（Windows 80G + Win11 100G 两个 VM 已占 ~92G） |
| 核显 | Intel Alder Lake-N UHD Graphics `[8086:46d1]`，IOMMU 独占 group 0 |
| 宿主机 | Proxmox VE **8.4.0**，kernel `6.8.12-9-pve` |
| Guest | VM **102 `win10`**：Windows 10 Enterprise LTSC 2021，q35 + OVMF，4 vCPU / 5G RAM |
| 显示 | HDMI 4K 显示器（核显输出） |
| 网段 | 过渡期：FORAGER 路由器/手机热点 `192.168.43.0/24`（终局规划 `192.168.8.0/24`） |

> ⚠️ **8GB 内存是硬约束**：Windows 5G + PVE 自身 ~1.5G 后只剩几百 MB，HAOS 跑不起来。
> 由于单槽上限 8G 无法升级，**Windows 与 HA 只能二选一常开**。
> 建议把 Windows 降到 **4096MB**，给 HAOS(1G) 留出空间；Frigate 与 Windows 不可同时跑。

## 3. 架构

```
N100 (PVE 8.4)
├── VM 102  win10 LTSC ── 直通 0000:00:02.0 (UHD Graphics) ──→ HDMI 4K 显示器
│     ├── RDP 3389 ←── 车内平板/笔记本（192.168.43.210）
│     ├── virtio 网卡（vmbr0，静态 192.168.43.210）
│     └── USB 直通：键盘 413c:2105 / 预留 USB-485 转换器
├── VM 101  ha（停用，内存不足）
├── VM 100  win11-UNAVALIABLE（停用，占 39G，可删）
└── 宿主机 vfio-pci 接管核显，自身控制台改走 SSH / 网页
```

## 4. 关键设计决策

| 决策 | 选择 | 理由 |
|---|---|---|
| 虚拟显卡是否保留 | **保留 `vga: std`** | 单核显直通一旦失败，RDP/noVNC 仍是唯一入口；保留虚拟显卡 = 永远有一条后路 |
| 直通参数 | `hostpci0` + `x-igd-opregion` + `romfile` | Gen12 核显 Windows 驱动依赖 VBT/opregion，缺了会 Code 43 |
| 是否用 `legacy-igd` | **不可行（已实测）** | 教程（PVE 8.x 时代）可用的 `legacy-igd=1 + i440fx + vga:none`，在 PVE 8.4 / qemu 9.2 上启动直接报 `IGD device 0000:00:02.0 is unsupported in legacy mode, try SandyBridge or newer` —— ADL-N 核显不支持 legacy 模式 |
| 是否用 SR-IOV | 否 | N100 场景收益低，且 Windows 驱动对 VF 支持不稳 |
| PVE 版本 | 锁定 **8.4.x，不升 9** | 已知 [PVE 9 上 N100 核显直通回归](https://forum.proxmox.com/threads/updated-to-pve-9-0-then-gpu-passthrough-stopped-working-on-windows.169296/)（同一内核版本，8.4.9 正常、9.0.3 Code 43） |
| 远程协议 | RDP | LTSC 自带 RDP Host；延迟最低，无需额外装软件 |

## 5. 宿主机配置（PVE）

### 5.1 前提：BIOS 打开 VT-d

N100 主板 BIOS 里必须开 **VT-d / Intel Virtualization for Directed I/O**（部分小厂主板默认关、
客服会谎称"默认开启"——实测 `dmesg | grep -i DMAR` 有输出、`/sys/kernel/iommu_groups/` 有分组才算真开）。

### 5.2 内核参数 `/etc/default/grub`

```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet intel_iommu=on iommu=pt initcall_blacklist=sysfb_init"
```

- `intel_iommu=on iommu=pt`：显式开启 IOMMU + 直通性能模式
- `initcall_blacklist=sysfb_init`：**阻止宿主 simpledrm/efifb 占用核显 framebuffer**，
  否则宿主控制台和 guest 抢同一块显存（副作用：宿主本机控制台不再有画面，管理走 SSH/8006）

```bash
update-grub
```

### 5.3 vfio 绑定（**不要开机预绑定**）

**结论：不要**用 `vfio.conf` 的 `ids=` + `/etc/modules` 在开机阶段就把核显绑给 vfio-pci。
让 PVE 在**启动 VM 时**自己绑定即可（`qm start` 会自动 unbind/bind 该 IOMMU group）。

```bash
# 保持默认即可，不需要建 vfio.conf、不需要把 vfio* 写进 /etc/modules
# 仅保留黑名单（i915 等）
cat /etc/modprobe.d/pve-blacklist.conf   # blacklist i915 / snd_hda_intel ...
```

> 为什么：实测**开机预绑定 vfio 会让 guest 首次显示初始化失败（彩色雪花）**的概率明显变高——
> 相当于把"固件刚初始化过、又被 vfio 提前接管"的 GPU 状态交给 guest。去掉预绑定后，
> 首次启动花屏从"必现"降到"偶发"（仍需二次启动保险，见 §10）。

> ⚠️ **不要**把 `8086:54c8`（PCH HD Audio）直通：它和 `00:1f.0/1f.4/1f.5`
> 同属一个 IOMMU group，单独直通会因"group 不独立"失败；HDMI 音频本方案不直通。

### 5.4 准备 VBIOS ROM

```bash
# 来源：薄荷屋 PVE8.2 核显直通教程附带的 N100 VBIOS（约 105KB）
cp n100.rom /usr/share/kvm/n100.rom
```

> 日志里 `vfio-pci 0000:00:02.0: Invalid PCI ROM header signature ... got 0x87af` 是 QEMU 读宿主
> ROM 失败的提示，**不影响本方案**（guest 侧 opregion + Intel 驱动工作正常，已实测 4K 输出）。

### 5.5 宿主机固定 IP（避免重启换 IP 失联）

```bash
# /etc/network/interfaces
auto vmbr0
iface vmbr0 inet static
    address 192.168.43.185/24
    gateway 192.168.43.1
    bridge-ports enp3s0
    bridge-stp off
    bridge-fd 0
```

## 6. 虚拟机配置（VM 102）

```bash
qm set 102 --hostpci0 "0000:00:02.0,romfile=n100.rom"
qm set 102 --args "-set device.hostpci0.x-igd-opregion=on -set device.hostpci0.x-igd-gms=0x2"
qm set 102 --vga std            # 保留虚拟显卡作兜底（关键）
qm set 102 --onboot 1           # 随 PVE 自启
qm set 102 --memory 4096        # 8G 上限下的建议值（原 5120）
qm set 102 --usb0 host=413c:2105  # 物理键盘按 VID:PID 绑定（不用端口号）
qm set 102 --usb1 host=093a:2510  # 鼠标按 VID:PID 绑定
```

最终关键字段：

```
args: -set device.hostpci0.x-igd-opregion=on -set device.hostpci0.x-igd-gms=0x2
hostpci0: 0000:00:02.0,romfile=n100.rom
machine: pc-q35-9.2+pve1
bios: ovmf
vga: std
memory: 4096
onboot: 1
usb0: host=413c:2105
usb1: host=093a:2510
```

> **为什么按 VID:PID 而不是端口**：端口号（`host=1-3`）一换 USB 口就失效，VID:PID 只要求设备插着。

## 7. Windows 侧配置

### 7.1 网络（静态 IP）

虚拟机原来 DHCP 失败只拿到 `169.254.x.x`（APIPA），必须手动固定：

```powershell
# 管理员 PowerShell
Get-NetAdapter | ft ifIndex,Name,Status -AutoSize
New-NetIPAddress -InterfaceIndex <idx> -IPAddress 192.168.43.210 -PrefixLength 24 -DefaultGateway 192.168.43.1
Set-DnsClientServerAddress -InterfaceIndex <idx> -ServerAddresses 192.168.43.1
```

### 7.2 开启 RDP（LTSC 自带 RDP Host）

```powershell
Set-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server' fDenyTSConnections 0
Enable-NetFirewallRule -Name 'RemoteDesktop-UserMode-In-TCP','RemoteDesktop-UserMode-In-UDP'
Set-Service TermService -StartupType Automatic
Start-Service TermService
```

> 中文系统上**不要用 `-DisplayGroup 'Remote Desktop'`**（显示名被本地化成"远程桌面"会报错），
> 用语言无关的规则名 `-Name RemoteDesktop-UserMode-In-TCP`。

### 7.3 核显驱动

Windows Update 会在核显直通后**自动装好 Intel 驱动**（实测 `32.0.101.7088`），
无需手动下载。装好后 HDMI 输出 4K，`Win32_VideoController` 里出现两块适配器：

```
Microsoft 基本显示适配器   1280 x 800     ← 虚拟 std VGA（兜底）
Intel(R) UHD Graphics      3840 x 2160    ← 直通的核显（HDMI 物理屏）
```

### 7.4 显示模式

- `Win+P` →「扩展」：双屏（虚拟 1280×800 + HDMI 4K）
- `Win+P` →「仅第二屏幕」：Windows 全屏输出到 HDMI，虚拟屏变黑（**正常，RDP 不受影响**）
- 命令行等价：`DisplaySwitch.exe /extend | /external | /clone | /internal`

> ⚠️ **分辨率建议：优先 `1920×1080@60`，别用 4K。**
> 4K60 对 HDMI 线材/显示器带宽要求高，这套直通下**在线切分辨率或 4K 高带宽模式极易花屏**；
> 车内屏幕 1080p 完全够用。设分辨率后**不要在线反复切换**——改完冷启动一次 VM 让其按保存的模式重新初始化。
> 另：Windows 里把「屏幕和睡眠」设为**从不关闭显示器**，避免休眠唤醒时重新 modeset 导致花屏。

> ⚠️ **显示器按需开关 = 每次上电都会触发 HPD + EDID 重读 + modeset**，这是本方案花屏的最常见触发点
> （实测：显示器是独立供电、按需开机，VM 先起/显示器后开、或显示器关掉再开时容易花屏）。
> 使用顺序：**先开显示器，再开/重启 VM**；显示器开关后花屏 → 冷启动 VM。
> **一劳永逸的硬件解法：加一个 HDMI EDID 模拟器（"假负载"，约 ¥20–40）**串在 N100 与显示器之间，
> 让 Windows 始终认为显示器在线，显示器随便开关都不再触发重新协商——车载/房车 HTPC 常见做法。

## 8. USB 直通

### 8.1 键盘/鼠标

```bash
qm set 102 --usb0 host=413c:2105     # Dell 键盘（VID:PID，换 USB 口也不失效）
qm set 102 --usb1 host=093a:2510     # PixArt USB Optical Mouse（实测）
```

⚠️ **`qm set` 只改配置，运行中的 VM 不会自动生效**（本次踩坑）。
两种生效方式：

1. **重启 VM**（最干净，配置按 VID:PID 解析后直通）
2. **热插拔**（保留当前会话）：
   ```bash
   printf "device_add usb-host,id=usb1,hostbus=1,hostport=1,bus=ehci.0\ninfo usb\n" | qm monitor 102
   ```
   `hostport` 用 `lsusb -t` 查（如鼠标在 `Port 1` → `1-1`）；先 `info usb` 确认设备是否已在。

### 8.2 USB-485 转换器（调试 485 用）

```bash
lsusb                 # 找到转换器，如 1a86:7523 (CH340) / 0403:6001 (FT232)
qm set 102 --usb1 host=1a86:7523
qm set 102 --delete usb1     # 拔掉时删除，否则下次开机会启动失败
```

> 模块厂家 PC 软件（总线监视器）+ USB-485 转换器 = 现成的 485 总线分析仪，
> 详见 [10-smart-control/gateway/build-guide.md](../../modules/10-smart-control/gateway/build-guide.md) §4.3.1。

## 9. 验证清单（4 层）

```bash
# ① 宿主机：核显已被 vfio 接管
lspci -k -s 00:02.0 | grep "driver in use"     # 必须 vfio-pci
lsmod | grep vfio                               # vfio_pci 在

# ② QEMU 参数：直通 + opregion 都已下发
tr '\0' '\n' < /proc/$(cat /var/run/qemu-server/102.pid)/cmdline | grep -E "vfio-pci|igd"

# ③ guest 内（PowerShell）：设备正常无错误码
Get-PnpDevice -Class Display | ft Status,Problem,FriendlyName -AutoSize
#   OK  CM_PROB_NONE  Intel(R) UHD Graphics
Get-CimInstance Win32_VideoController | ft Name,DriverVersion,VideoModeDescription -AutoSize
#   Intel(R) UHD Graphics  32.0.101.7088  3840 x 2160

# ④ 物理：HDMI 显示器出 Windows 桌面
```

## 10. 重启后如何验证（整机 vs 单 VM）

| 重启范围 | 验证什么 | 预期 |
|---|---|---|
| 只重启 VM 102（`qm reboot 102`） | guest 内 IP/RDP/驱动是否持久 | 静态 IP、RDP 保持；Intel 驱动保持；但**手动热插的 USB 会掉**，需重启后才按配置直通 |
| **整机重启 N100（推荐）** | 全部持久化：grub、vfio、网桥、VM 自启、hostpci | 见下方流程 |

**整机重启验证流程**（本次已完成，耗时约 2 分钟）：

```bash
# 1) 优雅关机
qm shutdown 102 --timeout 90 --forceStop 1
systemctl reboot

# 2) ~60s 后 SSH 回来（IP 已固定，不会变）
ssh -p 2222 root@192.168.43.185

# 3) 逐项检查
lspci -k -s 00:02.0 | grep "driver in use"   # vfio-pci
qm status 102                                 # running（onboot 自动启动）
ls /sys/class/net/vmbr0/brif/                 # 必须有 tap102i0
nc -z 192.168.43.210 3389                     # RDP 通
```

- HDMI 显示器：开机后先黑（宿主控制台已禁用）→ VM 启动 + Intel 驱动初始化后出现 Windows 登录界面（约 1 分钟）
- 若 `tap` 不在网桥里：`ip link set tap102i0 master vmbr0 && ip link set tap102i0 up`（见踩坑 1）

> ⚠️ **整机重启后首次启动必/常花屏**（实测多次：彩色雪花，偶发轻微到"能看到一点画面"）：
> 主机刚启动时 iGPU 还带着固件/半初始化状态，guest 第一次显示初始化会失败。
> `Win+Ctrl+Shift+B`（重启显卡驱动）、`Win+P`、拔插 HDMI 都救不回来。
>
> **两种有效恢复方式**（实测）：
> 1. **重启 VM**（QEMU 进程重启，`qm stop/start`）—— 必定有效，但慢
> 2. **在 guest 内重新应用一次显示模式**（`ChangeDisplaySettingsEx`，把分辨率重设成 1920×1080@60）—— 有效且快
>    （本机脚本存于 PVE `/root/fixdisplay.ps1`；登录后 `iex(iwr http://<PVE>:8080/…/fixdisplay.ps1 -UseBasicParsing)` 执行，
>    执行后 Windows 会把 HDMI 设为主屏、虚拟屏变黑，属正常）
>
> **当前自动方案 = 二次启动保险**：`/usr/local/sbin/vm102-second-pass.sh` + `vm102-second-pass.service`
> 在主机启动、VM 自启后约 25 秒自动 `qm shutdown/stop → qm start` 一次，
> 保证第二次启动显示正常。**整机重启到可正常显示约 1 分 20 秒**（第一次启动画面是花的，会自动重启一次）。
>
> 可选升级（更快，需权衡）：**开启 Windows 自动登录** + 「登录时执行 fixdisplay 脚本」的计划任务，
> 可把开机到画面正常压到约 1 分钟，但 VM 控制台将免密码自动进桌面。
>
> 试过但**无效**的改进：加大自启延迟 30s→120s、去掉 `initcall_blacklist=sysfb_init`、
> 去掉开机 vfio 预绑定（只降低概率）、启动前用 i915 预热 GPU（只改变花屏形态）、
> 把保存的显示模式先改成 1080p（首启仍会花）。仍可选：HDMI EDID 模拟器（假负载）。

## 11. 踩坑记录

| # | 现象 | 根因 | 解决 |
|---|---|---|---|
| 1 | VM 运行中突然断网，guest 拿 `169.254.x.x` | **重载 PVE 网络配置（改 IP/ifreload）会把运行中 VM 的 tap 从网桥摘掉** | 重新 `ip link set tap102i0 master vmbr0`；以后改网络后重启 VM |
| 2 | `qm set --usb0 host=...` 后键鼠还是没反应 | 配置已改，但运行中的 QEMU 仍挂旧端口 | 重启 VM，或用 `qm monitor` 热插（§8.1） |
| 3 | 键鼠插上宿主机能看到、Windows 里没有 | USB 直通是"按端口/VID:PID 抓取"，不是 USB 自动透传 | 加 `usbN: host=VID:PID` |
| 4 | `New-NetIPAddress` 报"拒绝访问" | 非管理员 PowerShell | `Start-Process powershell -Verb RunAs` 走 UAC |
| 5 | 中文 Windows 里 `Enable-NetFirewallRule -DisplayGroup 'Remote Desktop'` 报错 | DisplayGroup 被本地化 | 改用 `-Name RemoteDesktop-UserMode-In-TCP` |
| 6 | `qm start` 报 IOMMU 相关错误（PVE 9 / 部分主板） | BIOS VT-d 没开，或 PVE 9 回归 | 开 VT-d；PVE 锁 8.4.x |
| 7 | 日志 `Invalid PCI ROM header signature` | QEMU 读宿主 iGPU ROM 失败 | 不影响本方案，忽略 |
| 8 | 宿主控制台黑屏 | `initcall_blacklist=sysfb_init` + 核显被 vfio 占用 | 预期行为，管理走 SSH / `https://IP:8006` |
| 9 | 整机重启后 HDMI **花屏** | VM 自启时显示器/核显尚未就绪，首次显示初始化失败 | `qm stop 102 && qm start 102` 冷启动恢复；加 `startup: order=1,up=30` 延迟自启 |
| 10 | HDMI 分辨率不对（模糊/被拉伸/字太小） | 显示模式沿用了虚拟屏的 1280×800，或未设缩放 | 显示设置里把 HDMI 那块屏设为 `1920×1080`（推荐）或 `3840×2160`，缩放 100–150%；`Win+P` 选「扩展/仅第二屏幕」 |
| 11 | **运行中花屏**（改分辨率、显示器休眠唤醒、切模式后） | 动态 modeset 下核显输出不稳定（VBT/带宽/EDID 因素） | 不要在线反复改分辨率；固定 1080p；关显示器休眠；花屏后**冷启动 VM**（`qm stop 102 && qm start 102`，或 PVE 界面「关机→启动」） |
| 12 | 去掉 `romfile` 后 HDMI **完全无输出**（RDP 正常） | 核显显示输出依赖 ROM 里的 VBIOS 初始化；无 ROM 则 guest 无有效 VBT | **romfile 必须保留**（实测结论，别信"核显当副显卡不需要 ROM"） |
| 13 | `legacy-igd=1` 启动报 `IGD device ... unsupported in legacy mode` | ADL-N 核显不支持 legacy IGD 模式（qemu 9.2 限制） | 放弃 legacy-igd 路线；用 q35 + `vga: std` + 核显副显卡方案 |
| 14 | `qm set` 加 USB 后键鼠无反应 | 同 #2（运行中 VM 不生效） | `qm monitor` 热插或重启 VM；鼠标 `093a:2510` / 键盘 `413c:2105` |
| 15 | 显示器按需开关后无画面（不是花屏） | 显示器切输入/断电后再开，Windows 认为显示器断开且不再收到 HPD | 拔插 HDMI 线触发 HPD；或 `Win+P` 强制重新检测；不行冷启动 VM |
| 16 | **整机重启后首次启动彩色雪花**（核心问题） | iGPU 首次显示初始化失败（固件/半初始化状态） | 见 §10：**VM 重启**（不是 guest 重启）才有效；已装二次启动保险 |
| 17 | 花屏时 `Win+Ctrl+Shift+B` / `Win+P` / 拔插 HDMI 都无反应 | 坏的是 GPU 输出层，驱动级重置无效 | 只能 `qm stop/start`；RDP 不受影响 |
| 18 | 开机预绑定 vfio（`vfio.conf`+`/etc/modules`） | 首次花屏概率明显变高 | **不要**预绑定，让 PVE 在 VM 启动时绑定（§5.3） |

## 12. 回滚

```bash
# 去掉直通（VM 停机后）
qm set 102 --delete hostpci0
qm set 102 --delete args
qm set 102 --vga std

# 恢复宿主使用核显
rm /etc/modprobe.d/vfio.conf
# 从 /etc/modules 删除 vfio* 三行
# /etc/default/grub 去掉 initcall_blacklist=sysfb_init
update-grub && update-initramfs -u -k all && reboot
```

## 13. 已知约束与待办

- [ ] **USB-485 转换器直通**（插上后按 §8.2 加）
- [ ] 鼠标直通（插上后按 §8.1 加，键鼠预留）
- [ ] Windows 降内存到 4096MB（给 HAOS 留空间）
- [ ] 删除 `win11-UNAVALIABLE` VM（释放约 39G）
- [ ] 出门远程：FORAGER 路由器装 Tailscale 做子网路由（车内网段 `192.168.43.0/24`）
- [ ] 终局迁网段：`192.168.8.0/24` 定稿后，PVE `.10` / Windows `.210` / HA `.11` 一并迁移
- [ ] Win10 LTSC 激活（右下角水印，不影响功能）
- [ ] 升级 PVE 前先确认核显直通是否修复（PVE 9 已知回归）

## 参考

- [PVE 8.2 核显直通到 Windows10（薄荷屋）](https://www.meowpass.com/pages/4bd3bc/) — 本方案 VBIOS 与 `legacy-igd` 参数出处
- [PVE 9 N100 核显直通回归讨论](https://forum.proxmox.com/threads/updated-to-pve-9-0-then-gpu-passthrough-stopped-working-on-windows.169296/)
- [N100 安装 PVE 核显直通问题（V2EX）](https://global.v2ex.co/t/1094384) — VT-d 未开的典型症状
