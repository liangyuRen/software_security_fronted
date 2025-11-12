export interface SbomItem {
  vendor?: string
  name?: string
  version?: string
  language?: string
  id: string
  paths?: string[]
  children?: SbomItem[]
  [property: string]: any
}

export interface SbomResponse {
  task_info: {
    tool_version?: string
    app_name?: string
    size?: number
    start_time?: string
    end_time: '2025-03-13 20:07:46'
    cost_time: 0.0025309
    error: 'not config vuln database origin'
  }
  id: string
  children?: SbomItem[]
}
