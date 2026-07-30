import { motion } from 'framer-motion'
import { Droplets, Waves, Trash2 } from 'lucide-react'
import { useSystemStore } from '../../store/useSystemStore'

function WaterTank({ name, value, icon: Icon, color }: {
  name: string
  value: number
  icon: React.ComponentType<{ size?: number; className?: string }>
  color: string
}) {
  const isLow = name === '清水箱' && value < 20
  const isHigh = name !== '清水箱' && value > 80
  const statusColor = isLow ? '#EF4444' : isHigh ? '#FBBF24' : color

  return (
    <motion.div
      className="bg-rv-surface rounded-2xl p-6 border border-rv-border"
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex items-center gap-3 mb-4">
        <Icon size={24} className={color === '#3B82F6' ? 'text-blue-500' : color === '#6B7280' ? 'text-gray-500' : 'text-purple-500'} />
        <span className="text-rv-text font-semibold text-lg">{name}</span>
      </div>

      {/* Tank Visual */}
      <div className="relative h-48 bg-rv-bg rounded-xl overflow-hidden mb-4">
        {/* Water */}
        <motion.div
          className="absolute bottom-0 left-0 right-0 rounded-xl"
          style={{
            height: `${value}%`,
            background: `linear-gradient(180deg, ${color}40 0%, ${color} 100%)`,
          }}
          initial={{ height: 0 }}
          animate={{ height: `${value}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
        >
          {/* Wave Effect */}
          <svg className="absolute top-0 left-0 w-full -translate-y-1/2" viewBox="0 0 100 10" preserveAspectRatio="none">
            <motion.path
              d="M0 5 Q 25 0, 50 5 T 100 5 V 10 H 0 Z"
              fill={color}
              opacity={0.5}
              animate={{
                d: [
                  'M0 5 Q 25 0, 50 5 T 100 5 V 10 H 0 Z',
                  'M0 5 Q 25 10, 50 5 T 100 5 V 10 H 0 Z',
                  'M0 5 Q 25 0, 50 5 T 100 5 V 10 H 0 Z',
                ],
              }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            />
          </svg>
        </motion.div>

        {/* Percentage */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span
            className="text-4xl font-bold font-mono"
            style={{ color: value > 50 ? '#fff' : statusColor }}
          >
            {Math.round(value)}%
          </span>
        </div>
      </div>

      {/* Status */}
      <div className={`flex items-center justify-center gap-2 text-sm ${isLow || isHigh ? 'text-rv-danger' : 'text-rv-text-muted'}`}>
        <div className={`w-2 h-2 rounded-full ${isLow || isHigh ? 'bg-rv-danger animate-pulse' : 'bg-rv-success'}`} />
        {isLow ? '需要加水' : isHigh ? '需要清理' : '状态正常'}
      </div>
    </motion.div>
  )
}

export function WaterPage() {
  const { water } = useSystemStore()

  return (
    <div className="flex-1 p-6 overflow-auto">
      <div className="grid grid-cols-3 gap-6 h-full">
        <WaterTank name="清水箱" value={water.freshWater} icon={Waves} color="#3B82F6" />
        <WaterTank name="灰水箱" value={water.greyWater} icon={Droplets} color="#6B7280" />
        <WaterTank name="黑水箱" value={water.blackWater} icon={Trash2} color="#8B5CF6" />
      </div>
    </div>
  )
}
