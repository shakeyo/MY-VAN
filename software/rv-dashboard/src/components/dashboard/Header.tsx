import { useEffect } from 'react'
import { Bluetooth, Wifi, Signal } from 'lucide-react'
import { useSystemStore } from '../../store/useSystemStore'

export function Header() {
  const { status, setSystemStatus, startSimulation } = useSystemStore()

  useEffect(() => {
    // Initialize time
    const now = new Date()
    setSystemStatus({
      time: now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
      date: now.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
    })

    // Start simulation
    startSimulation()

    return () => {
      // Cleanup handled by store
    }
  }, [setSystemStatus, startSimulation])

  return (
    <header className="h-[60px] bg-rv-surface/80 backdrop-blur-md border-b border-rv-border flex items-center justify-between px-6">
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-gradient-to-br from-rv-primary to-blue-600 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-sm">VF</span>
        </div>
        <span className="text-rv-text font-semibold text-lg tracking-wide">VAN FACTORY</span>
      </div>

      {/* Status Indicators */}
      <div className="flex items-center gap-6">
        {/* Temperature */}
        <div className="flex items-center gap-4 text-rv-text-muted">
          <div className="flex items-center gap-2">
            <span className="text-xs">室内</span>
            <span className="text-rv-text font-mono font-medium">{status.indoorTemp}°C</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs">室外</span>
            <span className="text-rv-text font-mono font-medium">{status.outdoorTemp}°C</span>
          </div>
        </div>

        {/* Connectivity */}
        <div className="flex items-center gap-3">
          {/* Bluetooth */}
          <div className={`flex items-center gap-1.5 ${status.bluetoothConnected ? 'text-rv-primary' : 'text-rv-text-muted'}`}>
            <Bluetooth size={16} />
            <span className="text-xs">BT</span>
          </div>

          {/* WiFi */}
          <div className={`flex items-center gap-1.5 ${status.wifiConnected ? 'text-rv-success' : 'text-rv-text-muted'}`}>
            <Wifi size={16} />
            <Signal size={14} className="text-rv-success" />
            <span className="text-xs text-rv-text">{status.wifiSignal}%</span>
          </div>
        </div>

        {/* Time & Date */}
        <div className="flex items-center gap-3 text-rv-text">
          <span className="font-mono text-lg font-medium">{status.time}</span>
          <span className="text-rv-text-muted text-sm">{status.date}</span>
        </div>
      </div>
    </header>
  )
}
