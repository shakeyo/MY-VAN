import { create } from 'zustand'

// Types
export interface SwitchState {
  id: string
  name: string
  icon: string
  isOn: boolean
}

export interface SceneMode {
  id: string
  name: string
  icon: string
  isActive: boolean
}

export interface PowerData {
  batteryPercent: number
  voltage: number
  current: number
  solarPower: number
  solarAmps: number
  isCharging: boolean
  mainsConnected: boolean
  inverterOn: boolean
}

export interface WaterData {
  freshWater: number
  greyWater: number
  blackWater: number
}

export interface SystemStatus {
  indoorTemp: number
  outdoorTemp: number
  bluetoothConnected: boolean
  wifiConnected: boolean
  wifiSignal: number
  time: string
  date: string
}

interface SystemState {
  // Switches
  switches: SwitchState[]
  toggleSwitch: (id: string) => void
  setSwitches: (switches: Partial<SwitchState>[]) => void

  // Scene Modes
  scenes: SceneMode[]
  activateScene: (id: string) => void

  // Power
  power: PowerData
  setPower: (power: Partial<PowerData>) => void
  toggleInverter: () => void

  // Water
  water: WaterData
  setWater: (water: Partial<WaterData>) => void

  // System Status
  status: SystemStatus
  setSystemStatus: (status: Partial<SystemStatus>) => void

  // Active Page
  activePage: string
  setActivePage: (page: string) => void

  // Simulation
  startSimulation: () => void
  stopSimulation: () => void
}

let simulationInterval: NodeJS.Timeout | null = null

// Initial Data
const initialSwitches: SwitchState[] = [
  { id: 'pump', name: '水泵', icon: 'waves', isOn: true },
  { id: 'heater', name: '热水器', icon: 'flame', isOn: false },
  { id: 'induction', name: '电磁炉', icon: 'chefHat', isOn: false },
  { id: 'inverter', name: '逆变器', icon: 'zap', isOn: true },
  { id: 'downlights', name: '筒灯', icon: 'sun', isOn: true },
  { id: 'ambient', name: '氛围灯', icon: 'sparkles', isOn: true },
  { id: 'extLight', name: '外照灯', icon: 'lamp', isOn: false },
  { id: 'extSpot', name: '外射灯', icon: 'spotlight', isOn: false },
]

const initialScenes: SceneMode[] = [
  { id: 'parking', name: '驻车模式', icon: 'parking', isActive: true },
  { id: 'leaving', name: '离车模式', icon: 'logOut', isActive: false },
  { id: 'cinema', name: '观影模式', icon: 'tv', isActive: false },
  { id: 'rest', name: '休息模式', icon: 'moon', isActive: false },
]

const initialPower: PowerData = {
  batteryPercent: 89,
  voltage: 13.4,
  current: 5.2,
  solarPower: 600,
  solarAmps: 30,
  isCharging: true,
  mainsConnected: false,
  inverterOn: true,
}

const initialWater: WaterData = {
  freshWater: 90,
  greyWater: 56,
  blackWater: 86,
}

const initialStatus: SystemStatus = {
  indoorTemp: 24,
  outdoorTemp: 32,
  bluetoothConnected: true,
  wifiConnected: true,
  wifiSignal: 85,
  time: '',
  date: '',
}

// Scene configurations - only store id and isOn for partial updates
type PartialSwitch = { id: string; isOn: boolean }
const sceneConfigs: Record<string, PartialSwitch[]> = {
  parking: [
    { id: 'ambient', isOn: true },
    { id: 'inverter', isOn: true },
    { id: 'pump', isOn: true },
    { id: 'downlights', isOn: false },
    { id: 'heater', isOn: false },
    { id: 'induction', isOn: false },
    { id: 'extLight', isOn: false },
    { id: 'extSpot', isOn: false },
  ],
  leaving: [
    { id: 'pump', isOn: false },
    { id: 'inverter', isOn: false },
    { id: 'downlights', isOn: false },
    { id: 'ambient', isOn: false },
    { id: 'heater', isOn: false },
    { id: 'induction', isOn: false },
    { id: 'extLight', isOn: false },
    { id: 'extSpot', isOn: false },
  ],
  cinema: [
    { id: 'ambient', isOn: true },
    { id: 'downlights', isOn: false },
    { id: 'extLight', isOn: false },
    { id: 'extSpot', isOn: false },
  ],
  rest: [
    { id: 'downlights', isOn: false },
    { id: 'ambient', isOn: false },
    { id: 'extLight', isOn: false },
    { id: 'extSpot', isOn: false },
    { id: 'pump', isOn: true },
    { id: 'inverter', isOn: true },
  ],
}

export const useSystemStore = create<SystemState>((set, get) => ({
  // Switches
  switches: initialSwitches,
  toggleSwitch: (id) => {
    set((state) => ({
      switches: state.switches.map((s) =>
        s.id === id ? { ...s, isOn: !s.isOn } : s
      ),
    }))
  },
  setSwitches: (updates) => {
    set((state) => ({
      switches: state.switches.map((s) => {
        const update = updates.find((u) => u.id === s.id)
        return update ? { ...s, ...update } : s
      }),
    }))
  },

  // Scenes
  scenes: initialScenes,
  activateScene: (id) => {
    const config = sceneConfigs[id]
    if (!config) return

    set((state) => ({
      scenes: state.scenes.map((s) => ({
        ...s,
        isActive: s.id === id,
      })),
      switches: state.switches.map((s) => {
        const sceneConfig = config.find((c) => c.id === s.id)
        return sceneConfig ? { ...s, isOn: sceneConfig.isOn ?? s.isOn } : s
      }),
    }))
  },

  // Power
  power: initialPower,
  setPower: (power) => {
    set((state) => ({
      power: { ...state.power, ...power },
    }))
  },
  toggleInverter: () => {
    set((state) => ({
      power: { ...state.power, inverterOn: !state.power.inverterOn },
    }))
  },

  // Water
  water: initialWater,
  setWater: (water) => {
    set((state) => ({
      water: { ...state.water, ...water },
    }))
  },

  // Status
  status: initialStatus,
  setSystemStatus: (status) => {
    set((state) => ({
      status: { ...state.status, ...status },
    }))
  },

  // Active Page
  activePage: 'home',
  setActivePage: (page) => {
    set({ activePage: page })
  },

  // Simulation
  startSimulation: () => {
    if (simulationInterval) return

    simulationInterval = setInterval(() => {
      const state = get()
      const { power, water, status } = state

      // Update time
      const now = new Date()
      const time = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      const date = now.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })

      // Simulate power fluctuations
      let newBattery = power.batteryPercent
      let newVoltage = power.voltage + (Math.random() - 0.5) * 0.2
      let newCurrent = power.current + (Math.random() - 0.5) * 0.5
      let newSolarPower = power.solarPower + (Math.random() - 0.5) * 50
      let newSolarAmps = power.solarAmps + (Math.random() - 0.5) * 5
      let isCharging = power.isCharging

      // Battery drain/charge logic
      const inverterOn = state.switches.find(s => s.id === 'inverter')?.isOn ?? false
      if (inverterOn && !power.mainsConnected) {
        newBattery -= 0.1
      }
      if (power.solarPower > 0 && !power.mainsConnected) {
        newBattery += 0.05
      }

      // Clamp values
      newBattery = Math.max(0, Math.min(100, newBattery))
      newVoltage = Math.max(10, Math.min(15, newVoltage))
      newCurrent = Math.max(-10, Math.min(20, newCurrent))
      newSolarPower = Math.max(0, Math.min(1000, newSolarPower))
      newSolarAmps = Math.max(0, Math.min(50, newSolarAmps))
      isCharging = newSolarPower > 50 || power.mainsConnected

      // Water consumption (very slow)
      const pumpOn = state.switches.find(s => s.id === 'pump')?.isOn ?? false
      if (pumpOn) {
        // Random water usage
        if (Math.random() < 0.1) {
          set((s) => ({
            water: {
              ...s.water,
              freshWater: Math.max(0, s.water.freshWater - 0.1),
              greyWater: Math.min(100, s.water.greyWater + 0.05),
            },
          }))
        }
      }

      set({
        power: {
          ...power,
          batteryPercent: Math.round(newBattery * 10) / 10,
          voltage: Math.round(newVoltage * 10) / 10,
          current: Math.round(newCurrent * 10) / 10,
          solarPower: Math.round(newSolarPower),
          solarAmps: Math.round(newSolarAmps * 10) / 10,
          isCharging,
        },
        status: {
          ...status,
          time,
          date,
          indoorTemp: 24 + Math.round((Math.random() - 0.5) * 2),
          outdoorTemp: 32 + Math.round((Math.random() - 0.5) * 4),
        },
      })
    }, 5000)
  },

  stopSimulation: () => {
    if (simulationInterval) {
      clearInterval(simulationInterval)
      simulationInterval = null
    }
  },
}))
