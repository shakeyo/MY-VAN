import { useSystemStore } from './store/useSystemStore'
import {
  Header,
  BottomNav,
  HomePage,
  SwitchesPage,
  WaterPage,
  PowerPage,
  SettingsPage,
} from './components/dashboard'

function App() {
  const { activePage } = useSystemStore()

  const renderPage = () => {
    switch (activePage) {
      case 'home':
        return <HomePage />
      case 'switches':
        return <SwitchesPage />
      case 'water':
        return <WaterPage />
      case 'power':
        return <PowerPage />
      case 'settings':
        return <SettingsPage />
      default:
        return <HomePage />
    }
  }

  return (
    <div className="h-screen w-screen bg-rv-bg flex flex-col overflow-hidden font-sans">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {renderPage()}
      </main>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  )
}

export default App
