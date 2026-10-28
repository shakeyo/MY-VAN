# N100 Windows 调试机 · 核显直通与远程访问

N100 上跑一台 **Windows 10 LTSC 虚拟机**，作为车内设备（485 总线、继电器模块、MPPT 等）的
调试终端，偶尔兼作影音播放。本文记录 **Intel N100 核显直通 + HDMI 输出 + RDP 远程访问**
的完整配置、验证方法与踩坑记录。

> **一句话结论**：单核显直通到 Windows 可行，但**必须保留虚拟显卡（`vga: std`）作兜底**——
> 直通失败时 RDP / PVE noVNC 仍可进；HDMI 物理上屏则靠核显直通实现。

## 1. 目标与验收标准

| 目标 | 验收方式 |
|---|---|
| 车内用平板/笔记本远程进 Windows 调 485 | `mstsc`/Windows App 连 Windows 的当前 IP（DHCP，实测 `192.168.10.101`）`:3389` 成功登录 |
| N100 的 HDMI 直接显示 Windows | 显示器出现 Windows 桌面 |
| 核显真正直通（不是虚拟显卡） | PVE 宿主机 `lspci -k -s 00:02.0` 显示 `vfio-pci`；guest 内 `Intel(R) UHD Graphics`、`Problem=CM_PROB_NONE`、模式 `3840x2160@60` |
| 重启后自动恢复 | 整机重启后 VM 自动启动、直通生效、RDP 可达 |

## 2. 硬件与软件基线

| 项 | 值 |
|---|---|
| 主机 | N100 迷你主机，4 核 / **8GB DDR4-3200 单槽（本机上限 8G）** |
| 存储 | 141G thin pool，**剩余约 82G**（已删除 `win11-UNAVALIABLE`，释放约 39G） |
| 核显 | Intel Alder Lake-N UHD Graphics `[8086:46d1]`，IOMMU 独占 group 0 |
| 宿主机 | Proxmox VE **8.4.0**，kernel `6.8.12-9-pve` |
| Guest | VM **102 `win10`**：Windows 10 Enterprise LTSC 2021，q35 + OVMF，4 vCPU / **4G RAM**（2026-10 由 5G 下调） |
| 显示 | HDMI 4K 显示器（核显输出） |
| 网段 | 车内 Cudy LAN `192.168.10.0/24`（家里 `192.168.5.0/24`，互不冲突）；PVE 静态 `.10`、Windows **DHCP**（当前 `.101`） |

### 车内 IP 规划（192.168.10.0/24，定稿）

| IP | 设备 | 分配方式 |
|---|---|---|
| `.1` | Cudy TR3000（网关/DHCP） | 固定 |
| **`.10`** | **N100 PVE** | 静态 |
| `.11` | HAOS | 静态 |
| `.12` | Frigate LXC | 静态 |
| `.13` | Mosquitto | 静态 |
| `.20` | ESP32 485 网关 | 静态 |
| `.21` / `.22` | 安卓车机 / 小米平板4 | DHCP MAC 绑定 |
| `.30~39` | 预留 | — |
| `.100` | DVR 编码器 | 静态 |
| **`.101`** | **Windows 调试机** | DHCP + Cudy MAC 绑定（`BC:24:11:88:DC:75`） |
| `.150~249` | DHCP 池 | — |

> 原则：基础设施（PVE/HA/摄像头）静态；终端类（Windows/车机/平板）DHCP + 路由器 MAC 绑定。
> ZeroTier 客户端（手机/笔记本）走 **Managed Route** 访问整个 `192.168.10.0/24`。

> ⚠️ **8GB 内存是硬约束**：Windows 5G + PVE 自身 ~1.5G 后只剩几百 MB，HAOS 跑不起来。
> 由于单槽上限 8G 无法升级，**Windows 与 HA 只能二选一常开**。
> 建议把 Windows 降到 **4096MB**，给 HAOS(1G) 留出空间；Frigate 与 Windows 不可同时跑。

## 3. 架构

```
N100 (PVE 8.4)
├── VM 102  win10 LTSC ── 直通 0000:00:02.0 (UHD Graphics) ──→ HDMI 4K 显示器
│     ├── RDP 3389 ←── 车内平板/笔记本（DHCP，实测 .101）
│     ├── virtio 网卡（vmbr0，DHCP；可选静态 .210）
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

> `pve-blacklist.conf` 只需保留 `i915` / `snd_hda_intel`（防止宿主抢核显/音频）；
> **不要** blacklist `vfio` / `vfio_pci` / `vfio_iommu_type1`（没必要，PVE 会显式加载）。
>
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
    address 192.168.10.10/24
    gateway 192.168.10.1
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
qm set 102 --hostpci1 "0000:00:14.0;0000:00:14.2"  # 整个 USB 控制器直通（键鼠/485/U盘即插即用）
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
hostpci1: 0000:00:14.0;0000:00:14.2
```

> **为什么按 VID:PID 而不是端口**：端口号（`host=1-3`）一换 USB 口就失效，VID:PID 只要求设备插着。

## 7. Windows 侧配置

### 7.1 网络（静态 IP）

虚拟机原来 DHCP 失败只拿到 `169.254.x.x`（APIPA），必须手动固定：

**推荐 DHCP**（车内/家里/热点都能自动适配）：

```powershell
Set-NetIPInterface -InterfaceAlias '以太网 2' -Dhcp Enabled
Set-DnsClientServerAddress -InterfaceAlias '以太网 2' -ResetServerAddresses
ipconfig /renew
```

> 想固定地址：**在上游路由器里按 MAC 绑定**（比在 Windows 里写死更稳，换路由器/网段不失效）。
> 一定要静态时的写法：`New-NetIPAddress -InterfaceIndex <idx> -IPAddress <ip> -PrefixLength 24 -DefaultGateway <gw>`。

### 7.2 开启 RDP（LTSC 自带 RDP Host）

```powershell
Set-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server' fDenyTSConnections 0
Enable-NetFirewallRule -Name 'RemoteDesktop-UserMode-In-TCP','RemoteDesktop-UserMode-In-UDP'
Set-Service TermService -StartupType Automatic
Start-Service TermService
```

> 中文系统上**不要用 `-DisplayGroup 'Remote Desktop'`**（显示名被本地化成"远程桌面"会报错），
> 用语言无关的规则名 `-Name RemoteDesktop-UserMode-In-TCP`。

### 7.2.1 自动登录（免密码进桌面）

```powershell
# 管理员 PowerShell
$k='HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon'
Set-ItemProperty $k AutoAdminLogon '1'
Set-ItemProperty $k DefaultUserName 'fung'
Set-ItemProperty $k DefaultPassword '<你的密码>'
Set-ItemProperty $k DefaultDomainName $env:COMPUTERNAME
Set-ItemProperty $k ForceAutoLogon '1'
```

> 好处：整机重启 → 保险自动重启 VM 后直接进桌面；RDP 也不受登录状态影响。
> 代价：物理接触 N100 的人可直接进桌面（房车单人使用可接受）。

### 7.3 核显驱动

Windows Update 会在核显直通后**自动装好 Intel 驱动**（实测 `32.0.101.7088`），
无需手动下载。装好后 HDMI 输出 4K，`Win32_VideoController` 里出现两块适配器：

```
Microsoft 基本显示适配器   1280 x 800     ← 虚拟 std VGA（兜底）
Intel(R) UHD Graphics      3840 x 2160    ← 直通的核显（HDMI 物理屏）
```

### 7.4 显示模式（**本机命名是反的，实测**）

| 命令 | 实际效果（本机） |
|---|---|
| `DisplaySwitch.exe /internal` | **物理 HDMI 屏（核显）**单独显示 —— Windows 把核显输出当"内部屏" |
| `DisplaySwitch.exe /external` | **虚拟屏（std VGA）**单独显示（物理屏黑） |
| `DisplaySwitch.exe /extend` | 双屏扩展（虚拟屏默认变成主屏 → 应用会跑到虚拟屏） |
| `DisplaySwitch.exe /clone` | 双屏同画面 |

> **推荐配置：只保留物理屏**（`/internal`）。此时所有应用只可能在物理屏打开，
> **虚拟屏不再参与显示**（PVE noVNC 会黑，但 **RDP 完全不受影响**）。
> 若保留扩展模式，Windows 会把"上次在虚拟屏打开的应用"继续开在虚拟屏（`设置` 最典型）——
> 需要时用 `Win+Shift+←/→` 把窗口移到物理屏，或干脆断开虚拟屏。

> **把物理屏设为扩展模式下的主屏**（需要双屏时）：用 `ChangeDisplaySettingsEx` 先对所有屏
> 以 `CDS_UPDATEREGISTRY | CDS_NORESET` 设置坐标（物理屏 `(0,0)`、虚拟屏 `(1920,0)`），
> 再 `ChangeDisplaySettingsEx(NULL, NULL, …, CDS_UPDATEREGISTRY)` 应用。
> ⚠️ `CDS_SET_PRIMARY` 标志在 `ChangeDisplaySettingsEx` 里**不被支持**（返回成功但不生效），别用。

> ⚠️ **分辨率建议：优先 `1920×1080@60`，别用 4K。**
> 4K60 对 HDMI 线材/显示器带宽要求高，这套直通下**在线切分辨率或 4K 高带宽模式极易花屏**；
> 车内屏幕 1080p 完全够用。设分辨率后**不要在线反复切换**——改完冷启动一次 VM 让其按保存的模式重新初始化。
> 另：Windows 里把「屏幕和睡眠」设为**从不关闭显示器**，避免休眠唤醒时重新 modeset 导致花屏。

> ⚠️ **显示器按需开关 = 每次上电都会触发 HPD + EDID 重读 + modeset**，这是本方案花屏的最常见触发点
> （实测：显示器是独立供电、按需开机，VM 先起/显示器后开、或显示器关掉再开时容易花屏）。
> 使用顺序：**先开显示器，再开/重启 VM**；显示器开关后花屏 → 冷启动 VM。
> **一劳永逸的硬件解法：加一个 HDMI EDID 模拟器（"假负载"，约 ¥20–40）**串在 N100 与显示器之间，
> 让 Windows 始终认为显示器在线，显示器随便开关都不再触发重新协商——车载/房车 HTPC 常见做法。

## 8. USB 直通（**整控制器直通，推荐**）

### 8.1 结论：把整个 USB 控制器给 Windows，而不是逐个抓设备

```bash
qm set 102 --hostpci1 "0000:00:14.0;0000:00:14.2"   # xHCI + 同组 Shared SRAM，IOMMU group 3
```

- 之后 Windows 里**任意** USB 设备即插即用：换键鼠、插 USB-485、U 盘、读卡器……都自动识别，**无需再改配置**
- 宿主机因此**没有任何 USB**（管理走 SSH / 8006 网页，不依赖 USB）
- 启动日志 `vfio: Cannot reset device 0000:00:14.0/14.2, no available reset mechanism` 属正常告警（PCH 设备无复位机制）

> 关键：`00:14.0` 与 `00:14.2` 属同一 IOMMU group（group 3），必须**一起**直通；PVE 也支持网页操作：
> VM → 硬件 → 添加 → PCI 设备 → 选 `00:14.0` + 勾「所有功能」。

### 8.2 备用方案：按 VID:PID 抓单个设备（不推荐）

```bash
qm set 102 --usb0 host=<vid:pid>    # 例：键盘 413c:2105、鼠标 093a:2510
```

缺点：换设备就失效、要改配置；只有无法整控制器直通时才用。
⚠️ `qm set` 只改配置，运行中的 VM 不生效——需重启 VM，或用 `qm monitor` 热插
（`printf "device_add usb-host,id=usb1,hostbus=1,hostport=1,bus=ehci.0\n" | qm monitor 102`，hostport 查 `lsusb -t`）。

### 8.3 USB-485 转换器（调试 485 用）

整控制器直通后**即插即用**：插上 USB-485 转换器 → Windows 设备管理器出现 COM 口 →
用模块厂家 PC 软件（总线监视器）即可调试。无需再执行任何 PVE 命令。

> 485 调试流程详见 [10-smart-control/gateway/build-guide.md](../../modules/10-smart-control/gateway/build-guide.md) §4.3.1。

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
ssh -p 2222 root@192.168.10.10

# 3) 逐项检查
lspci -k -s 00:02.0 | grep "driver in use"   # vfio-pci
qm status 102                                 # running（onboot 自动启动）
ls /sys/class/net/vmbr0/brif/                 # 必须有 tap102i0
nc -z <Windows当前IP> 3389                    # RDP 通（DHCP，实测 192.168.10.101）
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
> 已开启 **Windows 自动登录**：保险重启后直接进桌面。
> 曾尝试「登录时自动执行显示重置脚本」来免除重启，**实测无效**（模式切换救不回花屏），已删除该计划任务。
> 如需进一步压缩开机时间，只能是硬件侧（HDMI EDID 模拟器/换原生 VBIOS）。
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

- [ ] **USB-485 转换器直通**（插上后按 §8.2 加；这是调试 485 的最后一环）
- [x] 鼠标直通（`093a:2510`，已加进 VM 配置）
- [x] **自动登录**（`AutoAdminLogon`，开机免密码进桌面）
- [x] **显示布局**：只保留物理屏（`DisplaySwitch /internal`），应用全部开在物理屏；虚拟屏断开（noVNC 黑，RDP 正常）
- [x] **内存 4096MB**（原 5120；本机 8G 上限，给 HAOS 留空间）
- [x] **删除 `win11-UNAVALIABLE` VM**（磁盘剩余 43G → 82G）
- [x] **软件清理**：已卸载 ShtermClient / aTrust / NAC Client
- [ ] ⚠️ **奇安信天擎（"广电运通防病毒"）**：静默卸载失败，需公司 IT 卸载密码或管理控制台下发；否则只能**新建干净 Windows VM**（旧 VM 留备份，按本文档重配，约 1 小时）
- [ ] 其余非系统软件待定：Chrome / PotPlayer / GPU-Z / virtio 安装器 / 驱动人生
- [ ] 可选：HDMI EDID 模拟器（假负载，¥20–40）——显示器按需开关/热插拔更稳
- [x] 车内网段/IP 划分定稿：`192.168.10.0/24`，PVE `.10`、Windows DHCP `.101`（路由器 MAC 绑定）
- [ ] 出门远程：**Cudy TR3000 自带 ZeroTier**（VPN→ZeroTier，客户端访问=互联网和本地局域网），PVE/Windows **不装任何 VPN 客户端**（网算分离）
- [x] 网段定稿：车内 `192.168.10.0/24`（家里 `192.168.5.0/24`），PVE 静态 `.10`、Windows DHCP（建议 Cudy 绑定 MAC）
- [ ] Win10 LTSC 激活（右下角水印，不影响功能；需产品密钥或 KMS 地址）
- [ ] 升级 PVE 前先确认核显直通是否修复（PVE 9 已知回归）

## 参考

- [PVE 8.2 核显直通到 Windows10（薄荷屋）](https://www.meowpass.com/pages/4bd3bc/) — 本方案 VBIOS 与 `legacy-igd` 参数出处
- [PVE 9 N100 核显直通回归讨论](https://forum.proxmox.com/threads/updated-to-pve-9-0-then-gpu-passthrough-stopped-working-on-windows.169296/)
- [N100 安装 PVE 核显直通问题（V2EX）](https://global.v2ex.co/t/1094384) — VT-d 未开的典型症状
