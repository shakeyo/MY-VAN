import { QuickSwitch } from './QuickSwitch'
import { SceneMode } from './SceneMode'
import { PowerMonitor } from './PowerMonitor'
import { WaterMonitor } from './WaterMonitor'

export function HomePage() {
  return (
    <div className="flex-1 p-6 overflow-auto">
      <div className="grid grid-cols-12 gap-6 h-full">
        {/* Left Panel - Controls */}
        <div className="col-span-4 flex flex-col gap-6">
          <QuickSwitch />
          <SceneMode />
        </div>

        {/* Right Panel - Monitoring */}
        <div className="col-span-8 flex flex-col gap-6">
          <PowerMonitor />
          <WaterMonitor />
        </div>
      </div>
    </div>
  )
}
