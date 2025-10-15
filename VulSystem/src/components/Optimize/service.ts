import axios from '@/utils/request'
import type { CompanyStrategy, StrategyRequest } from './const'
export const changeStrategy = (data: CompanyStrategy) => {
  const companyId =1
  //const companyId = +(localStorage.getItem('companyId') ?? 1)
  const requestData: StrategyRequest = {
    companyId,
    similarityThreshold: data.similarityThreshold,
    detect_strategy: data.detectStrategy,
    maxDetectNums: data.maxDetectNums,
  }
  return axios.post('/company/updateStrategy', requestData)
}

export const getStrategy = () => {
  const companyId =1
  //const companyId = localStorage.getItem('companyId') || 1
  return axios.get('/company/getStrategy', {
    params: {
      companyId,
    },
  })
}
