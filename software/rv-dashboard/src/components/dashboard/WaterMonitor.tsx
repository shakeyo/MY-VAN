import { motion } from 'framer-motion'
import { Droplets } from 'lucide-react'
import { useSystemStore } from '../../store/useSystemStore'

interface TankBarProps {
  label: string
  value: number
  color: string
  icon: string
}

function TankBar({ label, value, color, icon }: TankBarProps) {
  const isLow = value < 10 && label === '清水箱'
  const isHigh = value > 90 && label !== '清水箱'
  const barColor = isLow ? '#EF4444' : isHigh ? '#FBBF24' : color

  return (
    <div className="flex items-center gap-4">
      <div className="w-16 text-rv-text-muted text-sm">{label}</div>
      <div className="flex-1 h-8 bg-rv-bg rounded-lg overflow-hidden relative">
        {/* Wave Effect */}
        {label === '清水箱' && value > 0 && (
          <motion.div
            className="absolute inset-0 opacity-30"
            style={{
              background: `linear-gradient(90deg, transparent 0%, ${color} 50%, transparent 100%)`,
            }}
            animate={{
              x: ['-100%', '100%'],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'linear',
            }}
          />
        )}
        <motion.div
          className="h-full rounded-lg relative overflow-hidden"
          style={{ backgroundColor: barColor }}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0" />
        </motion.div>
      </div>
      <div className="w-12 text-right">
        <span className={`font-mono font-semibold ${isLow || isHigh ? 'text-rv-danger' : 'text-rv-text'}`}>
          {value}%
        </span>
      </div>
    </div>
  )
}

export function WaterMonitor() {
  const { water } = useSystemStore()

  return (
    <div className="bg-rv-surface rounded-2xl p-5 border border-rv-border">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-rv-text font-semibold text-lg flex items-center gap-2">
          <Droplets className="text-blue-400" size={20} />
          水路监控
        </h3>
      </div>

      <div className="space-y-4">
        <TankBar
          label="清水箱"
          value={Math.round(water.freshWater)}
          color="#3B82F6"
          icon="fresh"
        />
        <TankBar
          label="灰水箱"
          value={Math.round(water.greyWater)}
          color="#6B7280"
          icon="grey"
        />
        <TankBar
          label="黑水箱"
          value={Math.round(water.blackWater)}
          color="#8B5CF6"
          icon="black"
        />
      </div>

      {/* Water Status Messages */}
      <div className="mt-4 pt-4 border-t border-rv-border">
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className={`flex items-center gap-2 ${water.freshWater < 20 ? 'text-rv-danger' : 'text-rv-text-muted'}`}>
            <div className={`w-2 h-2 rounded-full ${water.freshWater < 20 ? 'bg-rv-danger' : 'bg-rv-success'}`} />
            {water.freshWater < 20 ? '清水不足' : '供水正常'}
          </div>
          <div className={`flex items-center gap-2 ${water.greyWater > 80 ? 'text-rv-warning' : 'text-rv-text-muted'}`}>
            <div className={`w-2 h-2 rounded-full ${water.greyWater > 80 ? 'bg-rv-warning' : 'bg-rv-success'}`} />
            {water.greyWater > 80 ? '灰水箱满' : '灰水正常'}
          </div>
        </div>
      </div>
    </div>
  )
}
