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

function SwitchTile({ sw, onToggle }: { sw: SwitchState; onToggle: () => void }) {
  const Icon = iconMap[sw.icon] || Zap

  return (
    <motion.button
      onClick={onToggle}
      whileTap={{ scale: 0.95 }}
      className={`
        relative flex flex-col items-center justify-center gap-2 p-4 rounded-2xl
        border-2 transition-all duration-200
        ${sw.isOn
          ? 'bg-rv-primary/10 border-rv-primary shadow-[0_0_15px_rgba(0,160,255,0.3)]'
          : 'bg-rv-surface border-rv-border hover:border-rv-text-muted'
        }
      `}
    >
      <div
        className={`
          w-12 h-12 rounded-xl flex items-center justify-center
          transition-all duration-200
          ${sw.isOn
            ? 'bg-rv-primary text-white'
            : 'bg-rv-bg text-rv-text-muted'
          }
        `}
      >
        <Icon size={24} />
      </div>
      <span className={`text-sm font-medium ${sw.isOn ? 'text-rv-text' : 'text-rv-text-muted'}`}>
        {sw.name}
      </span>
      {sw.isOn && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute top-2 right-2 w-2 h-2 bg-rv-primary rounded-full"
        />
      )}
    </motion.button>
  )
}

export function QuickSwitch() {
  const { switches, toggleSwitch } = useSystemStore()

  return (
    <div className="space-y-4">
      <h3 className="text-rv-text font-semibold text-lg">快捷开关</h3>
      <div className="grid grid-cols-4 gap-3">
        {switches.map((sw) => (
          <SwitchTile
            key={sw.id}
            sw={sw}
            onToggle={() => toggleSwitch(sw.id)}
          />
        ))}
      </div>
    </div>
  )
}
