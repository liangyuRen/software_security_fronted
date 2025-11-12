import axios from '@/utils/request'
export interface StatisticsInfo {
  /**
   * c语言漏洞数量
   */
  cVulnerabilityNum: number
  /**
   * 高风险项目数量
   */
  highRiskNum: number
  /**
   * 高风险漏洞数量
   */
  highRiskVulnerabilityNum: number
  /**
   * 高风险库数量本周变化
   */
  highVulnerabilityNumByDay: string
  /**
   * java语言漏洞数量
   */
  javaVulnerabilityNum: number
  /**
   * 低风险项目数量
   */
  lowRiskNum: number
  /**
   * 低风险漏洞数量
   */
  lowRiskVulnerabilityNum: number
  /**
   * 低风险库数量本周变化
   */
  lowVulnerabilityNumByDay: string
  /**
   * 中风险漏洞数量
   */
  midRiskVulnerabilityNum: number
  /**
   * 中风险库数量本周变化
   */
  midVulnerabilityNumByDay: string
  /**
   * 暂无风险项目数量
   */
  noRiskNum: number
  /**
   * 已上传项目数量
   */
  projectNum: number
  /**
   * 已扫描第三方库数量
   */
  thirdLibraryNum: number
  /**
   * 总漏洞数量
   */
  vulnerabilityNum: number
}

export const getCompanyStatic = () => {

  //const companyId = localStorage.getItem('companyId') ?? 1  改动描述：companyid问题
  const companyId =1
  return axios.get('/project/statistics', {
    params: {
      companyId,
    },
  })
}
