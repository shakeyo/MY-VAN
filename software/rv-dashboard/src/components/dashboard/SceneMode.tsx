import { motion } from 'framer-motion'
import { Car, LogOut, Tv, Moon } from 'lucide-react'
import { useSystemStore } from '../../store/useSystemStore'
import type { SceneMode } from '../../store/useSystemStore'

const iconMap: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  parking: Car,
  logOut: LogOut,
  tv: Tv,
  moon: Moon,
}

function SceneCard({ scene, onActivate }: { scene: SceneMode; onActivate: () => void }) {
  const Icon = iconMap[scene.icon] || Car

  return (
    <motion.button
      onClick={onActivate}
      whileTap={{ scale: 0.98 }}
      className={`
        relative flex items-center gap-3 px-5 py-4 rounded-2xl
        border-2 transition-all duration-200 overflow-hidden
        ${scene.isActive
          ? 'bg-gradient-to-r from-rv-primary/20 to-transparent border-rv-primary'
          : 'bg-rv-surface border-rv-border hover:border-rv-text-muted'
        }
      `}
    >
      {scene.isActive && (
        <motion.div
          layoutId="activeScene"
          className="absolute inset-0 bg-rv-primary/10"
          initial={false}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        />
      )}
      <div
        className={`
          w-10 h-10 rounded-lg flex items-center justify-center
          transition-all duration-200 z-10
          ${scene.isActive
            ? 'bg-rv-primary text-white'
            : 'bg-rv-bg text-rv-text-muted'
          }
        `}
      >
        <Icon size={20} />
      </div>
      <span className={`text-sm font-medium z-10 ${scene.isActive ? 'text-rv-text' : 'text-rv-text-muted'}`}>
        {scene.name}
      </span>
    </motion.button>
  )
}

export function SceneMode() {
  const { scenes, activateScene } = useSystemStore()

  return (
    <div className="space-y-4">
      <h3 className="text-rv-text font-semibold text-lg">情景模式</h3>
      <div className="grid grid-cols-2 gap-3">
        {scenes.map((scene) => (
          <SceneCard
            key={scene.id}
            scene={scene}
            onActivate={() => activateScene(scene.id)}
          />
        ))}
      </div>
    </div>
  )
}
