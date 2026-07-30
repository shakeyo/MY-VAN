import { motion } from 'framer-motion'
import { Battery, Zap, Sun, Plug, Activity } from 'lucide-react'
import { useSystemStore } from '../../store/useSystemStore'

export function PowerPage() {
  const { power } = useSystemStore()

  const batteryColor = power.batteryPercent > 50
    ? '#4ADE80'
    : power.batteryPercent > 20
      ? '#FBBF24'
      : '#EF4444'

  // Calculate power stats
  const powerStats = [
    { label: '电池电量', value: `${power.batteryPercent}%`, icon: Battery, color: batteryColor },
    { label: '当前电压', value: `${power.voltage.toFixed(1)}V`, icon: Activity, color: '#3B82F6' },
    { label: '当前电流', value: `${power.current >= 0 ? '+' : ''}${power.current.toFixed(1)}A`, icon: Zap, color: power.current >= 0 ? '#4ADE80' : '#EF4444' },
    { label: '太阳能功率', value: `${power.solarPower}W`, icon: Sun, color: '#FBBF24' },
    { label: '市电状态', value: power.mainsConnected ? '已接入' : '未接入', icon: Plug, color: power.mainsConnected ? '#4ADE80' : '#6B7280' },
  ]

  return (
    <div className="flex-1 p-6 overflow-auto">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Main Battery Display */}
        <motion.div
          className="bg-rv-surface rounded-3xl p-8 border border-rv-border"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-center mb-8">
            <div className="relative w-64 h-64">
              <svg className="w-full h-full transform -rotate-90">
                {/* Background circle */}
                <circle
                  cx="128"
                  cy="128"
                  r="112"
                  fill="none"
                  stroke="#374151"
                  strokeWidth="16"
                />
                {/* Progress circle */}
                <motion.circle
                  cx="128"
                  cy="128"
                  r="112"
                  fill="none"
                  stroke={batteryColor}
                  strokeWidth="16"
                  strokeLinecap="round"
                  strokeDasharray={`${2 * Math.PI * 112}`}
                  initial={{ strokeDashoffset: 2 * Math.PI * 112 }}
                  animate={{
                    strokeDashoffset: 2 * Math.PI * 112 * (1 - power.batteryPercent / 100),
                  }}
                  transition={{ duration: 1.5, ease: 'easeOut' }}
                  style={{
                    filter: `drop-shadow(0 0 10px ${batteryColor}40)`,
                  }}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <Battery size={48} style={{ color: batteryColor }} className="mb-2" />
                <span className="text-5xl font-bold text-rv-text font-mono">
                  {Math.round(power.batteryPercent)}
                </span>
                <span className="text-xl text-rv-text-muted">%</span>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-4">
            {powerStats.map((stat, index) => (
              <motion.div
                key={stat.label}
                className="bg-rv-bg rounded-xl p-4 text-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <stat.icon size={24} style={{ color: stat.color }} className="mx-auto mb-2" />
                <div className="text-rv-text-muted text-xs mb-1">{stat.label}</div>
                <div className="text-rv-text font-mono font-semibold text-lg">{stat.value}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Power Flow */}
        <motion.div
          className="bg-rv-surface rounded-2xl p-6 border border-rv-border"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h3 className="text-rv-text font-semibold text-lg mb-6">电量流向</h3>
          <div className="flex items-center justify-between">
            {/* Solar */}
            <div className="flex flex-col items-center">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center ${power.solarPower > 0 ? 'bg-rv-warning/20' : 'bg-rv-bg'}`}>
                <Sun size={32} className={power.solarPower > 0 ? 'text-rv-warning' : 'text-rv-text-muted'} />
              </div>
              <div className="mt-2 text-rv-text-muted text-sm">太阳能</div>
              <div className="text-rv-text font-mono">{power.solarPower}W</div>
            </div>

            {/* Arrow */}
            <div className="flex-1 flex items-center justify-center">
              <div className="h-0.5 bg-rv-border flex-1" />
              <Zap size={20} className="text-rv-primary mx-4" />
              <div className="h-0.5 bg-rv-border flex-1" />
            </div>

            {/* Battery */}
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 rounded-full flex items-center justify-center bg-rv-success/20">
                <Battery size={32} className="text-rv-success" />
              </div>
              <div className="mt-2 text-rv-text-muted text-sm">电池</div>
              <div className="text-rv-text font-mono">{power.batteryPercent}%</div>
            </div>

            {/* Arrow */}
            <div className="flex-1 flex items-center justify-center">
              <div className="h-0.5 bg-rv-border flex-1" />
              <Zap size={20} className="text-rv-primary mx-4" />
              <div className="h-0.5 bg-rv-border flex-1" />
            </div>

            {/* Load */}
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 rounded-full flex items-center justify-center bg-rv-primary/20">
                <Plug size={32} className="text-rv-primary" />
              </div>
              <div className="mt-2 text-rv-text-muted text-sm">负载</div>
              <div className="text-rv-text font-mono">{Math.abs(power.current * power.voltage).toFixed(0)}W</div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
