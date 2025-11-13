import instance from '@/utils/request.ts'
import { AxiosError, type AxiosResponse } from 'axios'

export interface VulnerabilityReportListResponse {
  code: number
  message: string
  obj: Obj

  // [property: string]: never;
}

export interface Obj {
  countId: null
  current: number
  maxLimit: null
  optimizeCountSql: boolean
  orders: string[]
  pages: number
  records: Record[]
  searchCount: boolean
  size: number
  total: number

  // [property: string]: never;
}

export interface Record {
  affectsWhitelist: number
  disclosureTime: string
  id: number
  referenceLink: string
  riskLevel: string
  vulnerabilityName: string
  cveId: string
  isDelete: number
  description: string
  // [property: string]: never;
}

export interface VulnerabilityReportSearchResponse {
  code: number
  message: string
  obj: Record[]
}

export const getVulnerabilityReportList = (page: number, size: number): Promise<VulnerabilityReportListResponse> => {
  return new Promise((resolve, reject) => {
    instance
      .get(`/vulnerabilityReport/list?page=${page}&size=${size}`)
      .then((res: AxiosResponse<VulnerabilityReportListResponse>) => {
        console.log('=== API Raw Response ===');
        console.log('Status:', res.status);
        console.log('Data:', JSON.stringify(res.data, null, 2));
        console.log('========================');
        resolve(res.data)
      })
      .catch((err: AxiosError) => {
        console.error('API Error:', err)
        reject(err)
      })
  })
}

export const getVulnerabilityReportSearch = (keyword: string) => {
  return new Promise((resolve, reject) => {
    instance
      .get(`/vulnerabilityReport/search?keyword=${keyword}`)
      .then((res: AxiosResponse<VulnerabilityReportSearchResponse>) => {
        resolve(res.data)
      })
      .catch((err: AxiosError) => {
        console.error(err)
        reject(err)
      })
  })
}

export const getFilteredVulnerabilityReport = (
  riskLevel?: string,
  startDate?: string,
  endDate?: string,
) => {
  const params = new URLSearchParams()

  if (riskLevel) params.append('riskLevel', riskLevel)
  if (startDate) params.append('startDate', startDate)
  if (endDate) params.append('endDate', endDate)

  const url = `/vulnerabilityReport/filter?${params.toString()}`
  return new Promise((resolve, reject) => {
    instance
      .get(url)
      .then((res: AxiosResponse<VulnerabilityReportSearchResponse>) => {
        resolve(res.data)
      })
      .catch((err: AxiosError) => {
        console.error(err)
        reject(err)
      })
  })
}
