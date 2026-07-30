import { motion } from 'framer-motion'
import { Battery, Zap, Sun, Plug, Power } from 'lucide-react'
import { useSystemStore } from '../../store/useSystemStore'

export function PowerMonitor() {
  const { power, toggleInverter } = useSystemStore()

  const batteryColor = power.batteryPercent > 50
    ? '#4ADE80'
    : power.batteryPercent > 20
      ? '#FBBF24'
      : '#EF4444'

  const getEstimatedTime = () => {
    if (power.batteryPercent >= 100) return '已充满'
    if (!power.inverterOn) return '--'
    const hours = Math.floor(power.batteryPercent / 10 * 24)
    const mins = Math.floor((power.batteryPercent % 10) * 2.4 * 60)
    return `${hours}小时${mins}分钟`
  }

  return (
    <div className="bg-rv-surface rounded-2xl p-5 border border-rv-border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-rv-text font-semibold text-lg flex items-center gap-2">
          <Battery className="text-rv-success" size={20} />
          电力管理
        </h3>
        <span className="text-rv-text-muted text-xs">
          磷酸铁锂 12.8V
        </span>
      </div>

      {/* Main Battery Display */}
      <div className="flex gap-6 mb-6">
        {/* Battery Gauge */}
        <div className="relative w-32 h-32 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="56"
              fill="none"
              stroke="#374151"
              strokeWidth="8"
            />
            <motion.circle
              cx="64"
              cy="64"
              r="56"
              fill="none"
              stroke={batteryColor}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 56}`}
              initial={{ strokeDashoffset: 2 * Math.PI * 56 }}
              animate={{
                strokeDashoffset: 2 * Math.PI * 56 * (1 - power.batteryPercent / 100),
              }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold text-rv-text font-mono">
              {Math.round(power.batteryPercent)}
            </span>
            <span className="text-xs text-rv-text-muted">%</span>
          </div>
        </div>

        {/* Power Details */}
        <div className="flex-1 grid grid-cols-2 gap-3">
          <div className="bg-rv-bg rounded-xl p-3">
            <div className="text-rv-text-muted text-xs mb-1">电压</div>
            <div className="text-rv-text font-mono font-semibold">{power.voltage.toFixed(1)}V</div>
          </div>
          <div className="bg-rv-bg rounded-xl p-3">
            <div className="text-rv-text-muted text-xs mb-1">电流</div>
            <div className={`font-mono font-semibold ${power.current >= 0 ? 'text-rv-success' : 'text-rv-danger'}`}>
              {power.current >= 0 ? '+' : ''}{power.current.toFixed(1)}A
            </div>
          </div>
          <div className="bg-rv-bg rounded-xl p-3 col-span-2">
            <div className="text-rv-text-muted text-xs mb-1">预计续航</div>
            <div className="text-rv-text font-mono font-semibold">{getEstimatedTime()}</div>
          </div>
        </div>
      </div>

      {/* Power Sources */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* Solar */}
        <div className={`bg-rv-bg rounded-xl p-3 flex items-center gap-3 ${power.solarPower > 0 ? 'border border-rv-warning/50' : ''}`}>
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${power.solarPower > 0 ? 'bg-rv-warning/20 text-rv-warning' : 'bg-rv-surface text-rv-text-muted'}`}>
            <Sun size={20} className={power.isCharging ? 'animate-pulse' : ''} />
          </div>
          <div>
            <div className="text-rv-text-muted text-xs">太阳能</div>
            <div className="text-rv-text font-mono font-semibold">
              {power.solarPower > 0 ? `${power.solarPower}W / ${power.solarAmps}A` : '未接入'}
            </div>
          </div>
        </div>

        {/* Mains */}
        <div className={`bg-rv-bg rounded-xl p-3 flex items-center gap-3 ${power.mainsConnected ? 'border border-rv-success/50' : ''}`}>
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${power.mainsConnected ? 'bg-rv-success/20 text-rv-success' : 'bg-rv-surface text-rv-text-muted'}`}>
            <Plug size={20} />
          </div>
          <div>
            <div className="text-rv-text-muted text-xs">市电</div>
            <div className="text-rv-text font-mono font-semibold">
              {power.mainsConnected ? '已接入' : '未接入'}
            </div>
          </div>
        </div>
      </div>

      {/* Inverter Toggle */}
      <motion.button
        onClick={toggleInverter}
        whileTap={{ scale: 0.98 }}
        className={`
          w-full flex items-center justify-between px-4 py-3 rounded-xl
          border-2 transition-all duration-200
          ${power.inverterOn
            ? 'bg-rv-primary/20 border-rv-primary'
            : 'bg-rv-bg border-rv-border'
          }
        `}
      >
        <div className="flex items-center gap-3">
          <Zap size={20} className={power.inverterOn ? 'text-rv-primary' : 'text-rv-text-muted'} />
          <span className={power.inverterOn ? 'text-rv-text' : 'text-rv-text-muted'}>逆变器</span>
        </div>
        <div className={`
          w-12 h-6 rounded-full relative transition-colors duration-200
          ${power.inverterOn ? 'bg-rv-primary' : 'bg-rv-border'}
        `}>
          <motion.div
            className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-md"
            animate={{ left: power.inverterOn ? '28px' : '4px' }}
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          />
        </div>
      </motion.button>
    </div>
  )
}
