import { motion } from 'framer-motion'
import {
  Waves,
  Flame,
  ChefHat,
  Zap,
  Sun,
  Sparkles,
  Lamp,
  Crosshair,
} from 'lucide-react'
import { useSystemStore, SwitchState } from '../../store/useSystemStore'

const iconMap: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  waves: Waves,
  flame: Flame,
  chefHat: ChefHat,
  zap: Zap,
  sun: Sun,
  sparkles: Sparkles,
  lamp: Lamp,
  spotlight: Crosshair,
}

function SwitchCard({ sw, onToggle }: { sw: SwitchState; onToggle: () => void }) {
  const Icon = iconMap[sw.icon] || Zap

  return (
    <motion.button
      onClick={onToggle}
      whileTap={{ scale: 0.95 }}
      className={`
        relative flex items-center justify-between p-5 rounded-2xl
        border-2 transition-all duration-200
        ${sw.isOn
          ? 'bg-rv-primary/10 border-rv-primary shadow-[0_0_15px_rgba(0,160,255,0.3)]'
          : 'bg-rv-surface border-rv-border hover:border-rv-text-muted'
        }
      `}
    >
      <div className="flex items-center gap-4">
        <div
          className={`
            w-14 h-14 rounded-xl flex items-center justify-center
            transition-all duration-200
            ${sw.isOn
              ? 'bg-rv-primary text-white'
              : 'bg-rv-bg text-rv-text-muted'
            }
          `}
        >
          <Icon size={28} />
        </div>
        <div className="text-left">
          <div className="text-rv-text font-semibold text-lg">{sw.name}</div>
          <div className={`text-sm ${sw.isOn ? 'text-rv-success' : 'text-rv-text-muted'}`}>
            {sw.isOn ? '运行中' : '已关闭'}
          </div>
        </div>
      </div>
      <div
        className={`
          w-16 h-8 rounded-full relative transition-colors duration-200
          ${sw.isOn ? 'bg-rv-primary' : 'bg-rv-border'}
        `}
      >
        <motion.div
          className="absolute top-1 w-6 h-6 bg-white rounded-full shadow-md"
          animate={{ left: sw.isOn ? '32px' : '4px' }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        />
      </div>
    </motion.button>
  )
}

export function SwitchesPage() {
  const { switches, toggleSwitch } = useSystemStore()

  const electricalSwitches = switches.filter(s =>
    ['inverter', 'induction'].includes(s.id)
  )
  const lightingSwitches = switches.filter(s =>
    ['downlights', 'ambient', 'extLight', 'extSpot'].includes(s.id)
  )
  const waterSwitches = switches.filter(s =>
    ['pump', 'heater'].includes(s.id)
  )

  return (
    <div className="flex-1 p-6 overflow-auto">
      <div className="space-y-8 max-w-4xl mx-auto">
        {/* Electrical */}
        <div>
          <h3 className="text-rv-text font-semibold text-lg mb-4 flex items-center gap-2">
            <Zap className="text-rv-warning" size={20} />
            电力设备
          </h3>
          <div className="space-y-3">
            {electricalSwitches.map((sw) => (
              <SwitchCard
                key={sw.id}
                sw={sw}
                onToggle={() => toggleSwitch(sw.id)}
              />
            ))}
          </div>
        </div>

        {/* Lighting */}
        <div>
          <h3 className="text-rv-text font-semibold text-lg mb-4 flex items-center gap-2">
            <Sun className="text-rv-primary" size={20} />
            照明设备
          </h3>
          <div className="space-y-3">
            {lightingSwitches.map((sw) => (
              <SwitchCard
                key={sw.id}
                sw={sw}
                onToggle={() => toggleSwitch(sw.id)}
              />
            ))}
          </div>
        </div>

        {/* Water */}
        <div>
          <h3 className="text-rv-text font-semibold text-lg mb-4 flex items-center gap-2">
            <Waves className="text-blue-400" size={20} />
            水路设备
          </h3>
          <div className="space-y-3">
            {waterSwitches.map((sw) => (
              <SwitchCard
                key={sw.id}
                sw={sw}
                onToggle={() => toggleSwitch(sw.id)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
