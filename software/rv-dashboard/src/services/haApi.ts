// HA API Service for RV Dashboard

const HA_CONFIG = {
  url: '',
  token: '',
}

// Set HA Configuration
export function setHAConfig(url: string, token: string) {
  HA_CONFIG.url = url.replace(/\/$/, '') // Remove trailing slash
  HA_CONFIG.token = token
}

// Get current config
export function getHAConfig() {
  return { url: HA_CONFIG.url, token: HA_CONFIG.token }
}

// Check if configured
export function isHAConfigured() {
  return !!HA_CONFIG.url && !!HA_CONFIG.token
}

// API Headers
function getHeaders() {
  return {
    'Authorization': `Bearer ${HA_CONFIG.token}`,
    'Content-Type': 'application/json',
  }
}

// Generic API request
async function haRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  if (!HA_CONFIG.url || !HA_CONFIG.token) {
    throw new Error('HA not configured')
  }

  const response = await fetch(`${HA_CONFIG.url}/api${endpoint}`, {
    ...options,
    headers: {
      ...getHeaders(),
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`HA API Error: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

// ==================== States API ====================

// Get all states
export async function getStates() {
  return haRequest<HAState[]>('/states')
}

// Get single entity state
export async function getState(entityId: string) {
  return haRequest<HAState>(`/states/${entityId}`)
}

// Call service
export async function callService(
  domain: string,
  service: string,
  data?: Record<string, unknown>
) {
  return haRequest(`/services/${domain}/${service}`, {
    method: 'POST',
    body: JSON.stringify(data || {}),
  })
}

// ==================== Entity Helpers ====================

// Get entities by domain
export function filterEntitiesByDomain(states: HAState[], domain: string): HAState[] {
  return states.filter(state => state.entity_id.startsWith(domain))
}

// Get binary sensor state
export function getBinarySensorState(states: HAState[], entityId: string): boolean {
  const state = states.find(s => s.entity_id === entityId)
  return state?.state === 'on'
}

// Get sensor value
export function getSensorValue(states: HAState[], entityId: string): string | number {
  const state = states.find(s => s.entity_id === entityId)
  if (!state) return 0

  const val = state.state
  return isNaN(Number(val)) ? val : Number(val)
}

// Get entity attributes
export function getEntityAttributes<T extends Record<string, unknown>>(
  states: HAState[],
  entityId: string
): T | null {
  const state = states.find(s => s.entity_id === entityId)
  return (state?.attributes || null) as T | null
}

// ==================== Types ====================

export interface HAState {
  entity_id: string
  state: string
  attributes: Record<string, unknown>
  last_changed: string
  last_updated: string
  context: {
    id: string
    parent_id?: string
    user_id?: string
  }
}

export interface HAEntity {
  entity_id: string
  name?: string
  icon?: string
  device_class?: string
  unit_of_measurement?: string
}

// ==================== RV Specific Mappers ====================

export interface RVSystemData {
  // Power
  batteryPercent: number
  batteryVoltage: number
  solarPower: number
  inverterState: boolean
  mainsConnected: boolean

  // Water
  freshWater: number
  greyWater: number
  blackWater: number

  // Switches
  switches: Record<string, boolean>

  // Climate
  indoorTemp: number
  outdoorTemp: number

  // Time
  time: string
  date: string
}

// Map HA states to RV system data
export function mapHAStatesToRVData(states: HAState[]): Partial<RVSystemData> {
  const data: Partial<RVSystemData> = {}

  // Power - modify these entity IDs to match your HA setup
  const batteryEntity = states.find(s =>
    s.entity_id.includes('battery') && s.entity_id.includes('percent')
  )
  if (batteryEntity) {
    data.batteryPercent = parseFloat(batteryEntity.state) || 0
  }

  const solarEntity = states.find(s =>
    s.entity_id.includes('solar') && s.entity_id.includes('power')
  )
  if (solarEntity) {
    data.solarPower = parseFloat(solarEntity.state) || 0
  }

  const inverterEntity = states.find(s =>
    s.entity_id.includes('inverter') || s.entity_id.includes('逆变器')
  )
  if (inverterEntity) {
    data.inverterState = inverterEntity.state === 'on'
  }

  // Water tanks - modify entity IDs
  const freshWaterEntity = states.find(s =>
    s.entity_id.includes('water') && s.entity_id.includes('fresh') || s.entity_id.includes('清水')
  )
  if (freshWaterEntity) {
    data.freshWater = parseFloat(freshWaterEntity.state) || 0
  }

  const greyWaterEntity = states.find(s =>
    s.entity_id.includes('water') && s.entity_id.includes('grey') || s.entity_id.includes('灰水')
  )
  if (greyWaterEntity) {
    data.greyWater = parseFloat(greyWaterEntity.state) || 0
  }

  const blackWaterEntity = states.find(s =>
    s.entity_id.includes('water') && s.entity_id.includes('black') || s.entity_id.includes('黑水')
  )
  if (blackWaterEntity) {
    data.blackWater = parseFloat(blackWaterEntity.state) || 0
  }

  // Temperature
  const indoorTempEntity = states.find(s =>
    s.entity_id.includes('temperature') && s.entity_id.includes('indoor') || s.entity_id.includes('室内')
  )
  if (indoorTempEntity) {
    data.indoorTemp = parseFloat(indoorTempEntity.state) || 0
  }

  const outdoorTempEntity = states.find(s =>
    s.entity_id.includes('temperature') && s.entity_id.includes('outdoor') || s.entity_id.includes('室外')
  )
  if (outdoorTempEntity) {
    data.outdoorTemp = parseFloat(outdoorTempEntity.state) || 0
  }

  // Get all switch/light entities
  const switches: Record<string, boolean> = {}
  const switchEntities = states.filter(s =>
    s.entity_id.startsWith('switch.') ||
    s.entity_id.startsWith('light.') ||
    s.entity_id.startsWith('binary_sensor.')
  )
  switchEntities.forEach(entity => {
    switches[entity.entity_id] = entity.state === 'on'
  })
  data.switches = switches

  // Time
  data.time = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  data.date = new Date().toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })

  return data
}
