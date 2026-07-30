import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Wifi,
  Bluetooth,
  Monitor,
  Volume2,
  Globe,
  Bell,
  Shield,
  Home,
  Server,
  Check,
  X,
  Loader2,
  AlertCircle,
} from 'lucide-react'
import { setHAConfig, getHAConfig, isHAConfigured, getStates, mapHAStatesToRVData } from '../../services/haApi'
import { useSystemStore } from '../../store/useSystemStore'

interface SettingItemProps {
  icon: React.ComponentType<{ size?: number; className?: string }>
  title: string
  description: string
  children?: React.ReactNode
}

function SettingItem({ icon: Icon, title, description, children }: SettingItemProps) {
  return (
    <div className="flex items-center justify-between p-4 bg-rv-surface rounded-xl border border-rv-border">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 bg-rv-bg rounded-xl flex items-center justify-center">
          <Icon size={24} className="text-rv-primary" />
        </div>
        <div>
          <div className="text-rv-text font-semibold">{title}</div>
          <div className="text-rv-text-muted text-sm">{description}</div>
        </div>
      </div>
      {children}
    </div>
  )
}

function Toggle({ defaultOn = false }: { defaultOn?: boolean }) {
  const [on, setOn] = useState(defaultOn)

  return (
    <motion.button
      onClick={() => setOn(!on)}
      className={`
        w-14 h-8 rounded-full relative transition-colors duration-200
        ${on ? 'bg-rv-primary' : 'bg-rv-border'}
      `}
    >
      <motion.div
        className="absolute top-1 w-6 h-6 bg-white rounded-full shadow-md"
        animate={{ left: on ? '28px' : '4px' }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
      />
    </motion.button>
  )
}

// HA Connection Status Component
function HAConnectionStatus() {
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle')
  const [errorMsg, setErrorMsg] = useState('')
  const { setPower, setWater, setSystemStatus, setSwitches, switches } = useSystemStore()

  const config = getHAConfig()
  const isConnected = isHAConfigured()

  const testConnection = async () => {
    if (!config.url || !config.token) return

    setConnectionStatus('testing')
    setErrorMsg('')

    try {
      const states = await getStates()
      const rvData = mapHAStatesToRVData(states)

      // Update store with HA data
      if (rvData.batteryPercent !== undefined) {
        setPower({ batteryPercent: rvData.batteryPercent })
      }
      if (rvData.solarPower !== undefined) {
        setPower({ solarPower: rvData.solarPower })
      }
      if (rvData.freshWater !== undefined) {
        setWater({ freshWater: rvData.freshWater })
      }

      setConnectionStatus('success')

      // Save to localStorage
      localStorage.setItem('ha_url', config.url)
      localStorage.setItem('ha_token', config.token)
    } catch (error) {
      setConnectionStatus('error')
      setErrorMsg(error instanceof Error ? error.message : '连接失败')
    }
  }

  // Load saved config on mount
  useEffect(() => {
    const savedUrl = localStorage.getItem('ha_url')
    const savedToken = localStorage.getItem('ha_token')

    if (savedUrl && savedToken) {
      setHAConfig(savedUrl, savedToken)
      testConnection()
    }
  }, [])

  return (
    <div className="space-y-4">
      {/* Status Indicator */}
      <div className={`flex items-center gap-3 p-4 rounded-xl border ${
        connectionStatus === 'success' ? 'bg-rv-success/10 border-rv-success/30' :
        connectionStatus === 'error' ? 'bg-rv-danger/10 border-rv-danger/30' :
        'bg-rv-surface border-rv-border'
      }`}>
        {connectionStatus === 'testing' ? (
          <Loader2 className="text-rv-primary animate-spin" size={24} />
        ) : connectionStatus === 'success' ? (
          <Check className="text-rv-success" size={24} />
        ) : connectionStatus === 'error' ? (
          <X className="text-rv-danger" size={24} />
        ) : (
          <Server className="text-rv-text-muted" size={24} />
        )}
        <div>
          <div className="text-rv-text font-medium">
            {connectionStatus === 'testing' ? '连接中...' :
             connectionStatus === 'success' ? '已连接到 Home Assistant' :
             connectionStatus === 'error' ? '连接失败' :
             isConnected ? '已配置' : '未配置'}
          </div>
          {errorMsg && (
            <div className="text-rv-danger text-sm flex items-center gap-1">
              <AlertCircle size={14} />
              {errorMsg}
            </div>
          )}
        </div>
      </div>

      {/* Test Button */}
      {isConnected && (
        <button
          onClick={testConnection}
          disabled={connectionStatus === 'testing'}
          className="w-full py-3 bg-rv-primary/20 text-rv-primary rounded-xl hover:bg-rv-primary/30 transition-colors disabled:opacity-50"
        >
          {connectionStatus === 'testing' ? '测试连接中...' : '测试连接'}
        </button>
      )}
    </div>
  )
}

// Input Component
function ConfigInput({
  label,
  value,
  onChange,
  placeholder,
  type = 'text'
}: {
  label: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  type?: string
}) {
  return (
    <div className="space-y-2">
      <label className="text-rv-text-muted text-sm">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full px-4 py-3 bg-rv-bg border border-rv-border rounded-xl text-rv-text placeholder:text-rv-text-muted focus:outline-none focus:border-rv-primary"
      />
    </div>
  )
}

export function SettingsPage() {
  const [haUrl, setHaUrl] = useState('')
  const [haToken, setHaToken] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  // Load saved config
  useEffect(() => {
    const config = getHAConfig()
    if (config.url) setHaUrl(config.url)
    if (config.token) setHaToken(config.token)
  }, [])

  const saveHAConfig = () => {
    if (!haUrl || !haToken) return

    setIsSaving(true)
    setHAConfig(haUrl, haToken)

    // Save to localStorage
    localStorage.setItem('ha_url', haUrl)
    localStorage.setItem('ha_token', haToken)

    setTimeout(() => {
      setIsSaving(false)
    }, 500)
  }

  return (
    <div className="flex-1 p-6 overflow-auto">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Home Assistant Settings */}
        <div>
          <h3 className="text-rv-text font-semibold text-lg mb-4 flex items-center gap-2">
            <Home className="text-rv-primary" size={20} />
            Home Assistant
          </h3>
          <div className="space-y-4">
            {/* Connection Status */}
            <HAConnectionStatus />

            {/* Config Form */}
            <div className="bg-rv-surface rounded-xl p-4 border border-rv-border space-y-4">
              <ConfigInput
                label="HA 地址"
                value={haUrl}
                onChange={setHaUrl}
                placeholder="http://192.168.1.100:8123"
              />
              <ConfigInput
                label="访问令牌 (Long-Lived Access Token)"
                value={haToken}
                onChange={setHaToken}
                placeholder="请输入您的 HA Token"
              />
              <button
                onClick={saveHAConfig}
                disabled={!haUrl || !haToken || isSaving}
                className="w-full py-3 bg-rv-primary text-white rounded-xl hover:bg-rv-primary/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSaving ? '保存中...' : '保存配置'}
              </button>
            </div>

            {/* Help Text */}
            <div className="text-rv-text-muted text-sm p-4 bg-rv-bg rounded-xl">
              <p className="font-medium mb-2">如何获取 HA Token:</p>
              <ol className="list-decimal list-inside space-y-1">
                <li>打开 Home Assistant</li>
                <li>点击左下角用户名</li>
                <li>向下滚动并点击"创建令牌"</li>
                <li>给令牌命名并创建</li>
                <li>复制生成的令牌并粘贴到上方</li>
              </ol>
            </div>
          </div>
        </div>

        {/* Connection Settings */}
        <div>
          <h3 className="text-rv-text font-semibold text-lg mb-4">连接</h3>
          <div className="space-y-3">
            <SettingItem
              icon={Wifi}
              title="Wi-Fi"
              description="已连接到网络"
            >
              <Toggle defaultOn={true} />
            </SettingItem>
            <SettingItem
              icon={Bluetooth}
              title="蓝牙"
              description="已配对设备"
            >
              <Toggle defaultOn={true} />
            </SettingItem>
          </div>
        </div>

        {/* Display Settings */}
        <div>
          <h3 className="text-rv-text font-semibold text-lg mb-4">显示</h3>
          <div className="space-y-3">
            <SettingItem
              icon={Monitor}
              title="屏幕亮度"
              description="自动调节"
            >
              <div className="text-rv-text-muted text-sm">85%</div>
            </SettingItem>
            <SettingItem
              icon={Bell}
              title="息屏时间"
              description="永不熄灭"
            >
              <div className="text-rv-text-muted text-sm">30分钟</div>
            </SettingItem>
          </div>
        </div>

        {/* System Settings */}
        <div>
          <h3 className="text-rv-text font-semibold text-lg mb-4">系统</h3>
          <div className="space-y-3">
            <SettingItem
              icon={Volume2}
              title="系统音量"
              description="提示音音量"
            >
              <div className="text-rv-text-muted text-sm">60%</div>
            </SettingItem>
            <SettingItem
              icon={Globe}
              title="语言"
              description="简体中文"
            >
              <div className="text-rv-text-muted text-sm">CN</div>
            </SettingItem>
            <SettingItem
              icon={Shield}
              title="系统版本"
              description="VAN FACTORY OS"
            >
              <div className="text-rv-success text-sm">v1.0.0</div>
            </SettingItem>
          </div>
        </div>

        {/* About */}
        <motion.div
          className="bg-rv-surface rounded-xl p-6 border border-rv-border text-center"
          whileHover={{ scale: 1.01 }}
        >
          <div className="w-16 h-16 bg-gradient-to-br from-rv-primary to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-xl">VF</span>
          </div>
          <div className="text-rv-text font-semibold text-lg mb-1">VAN FACTORY</div>
          <div className="text-rv-text-muted text-sm mb-2">房车智能控制系统</div>
          <div className="text-rv-text-muted text-xs">Version 1.0.0</div>
        </motion.div>
      </div>
    </div>
  )
}
