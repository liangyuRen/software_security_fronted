// Types
export interface DangerInfo {
  // label: string
  // desc: string
  ref: string
  // language: string
  // risk: string
  // detectTime: string
  description: string
  id: number
  isaccept: number
  language: string
  name: string
  riskLevel: string
  time: string
}

export interface ReportInfo {
  reportName: string // 漏洞报告名
  reportDesc: string // 漏洞描述
  reportId: string // 编号
  time: string // 披露时间
  isCve: boolean
  isPoc: boolean
  riskLevel: string; // 风险等级
  ref: string //漏洞来源
}

// Constants
