import { Home, ToggleLeft, Droplets, Battery, Settings } from 'lucide-react'
import { useSystemStore } from '../../store/useSystemStore'

const navItems = [
  { id: 'home', name: '首页', icon: Home },
  { id: 'switches', name: '开关', icon: ToggleLeft },
  { id: 'water', name: '水路', icon: Droplets },
  { id: 'power', name: '电池', icon: Battery },
  { id: 'settings', name: '设置', icon: Settings },
]

export function BottomNav() {
  const { activePage, setActivePage } = useSystemStore()

  return (
    <nav className="h-[80px] bg-rv-surface/90 backdrop-blur-md border-t border-rv-border flex items-center justify-around px-4">
      {navItems.map((item) => {
        const Icon = item.icon
        const isActive = activePage === item.id

        return (
          <button
            key={item.id}
            onClick={() => setActivePage(item.id)}
            className={`
              flex flex-col items-center justify-center gap-1.5 px-6 py-2 rounded-xl
              transition-all duration-200 min-w-[80px]
              ${isActive
                ? 'bg-rv-primary/20 text-rv-primary'
                : 'text-rv-text-muted hover:text-rv-text hover:bg-rv-surface'
              }
            `}
          >
            <Icon
              size={24}
              className={isActive ? 'text-rv-primary' : ''}
            />
            <span className={`text-xs font-medium ${isActive ? 'text-rv-primary' : ''}`}>
              {item.name}
            </span>
            {isActive && (
              <div className="absolute bottom-0 w-8 h-0.5 bg-rv-primary rounded-full" />
            )}
          </button>
        )
      })}
    </nav>
  )
}
