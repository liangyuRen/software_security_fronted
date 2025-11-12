// 模型分类
export enum ModelType {
  PreTrain,
  LLM,
}
// 优化器分类
export enum OptimizeType {
  Similarity,
  WhiteList,
  None,
}
export interface LlmInfoType {
  llmName: string
  desc: string
  infoTag?: string | undefined
  needVip?: boolean
  accuracy: number
  falseRate: number
  modelType: ModelType
  optimizeType: OptimizeType
}

export interface StrategyRequest {
  companyId: number
  /**
   *
   * 检测策略：共十种(LLM,TinyModel,LLM-lev;TinyModel-lev,LLM-cos;TinyModel-cos,LLM-lcs;TinyModel-lcs,LLM-whiteList;TinyModel-whiteList)
   */
  detect_strategy: string
  /**
   * 单位漏洞报告中检测出漏洞库的最大数量 1~3
   */
  maxDetectNums: number
  /**
   * 相似度阈值 0~1
   */
  similarityThreshold: number
}
export interface CompanyStrategy {
  /**
   *
   * 检测策略：共十种(LLM,TinyModel,LLM-lev;TinyModel-lev,LLM-cos;TinyModel-cos,LLM-lcs;TinyModel-lcs,LLM-whiteList;TinyModel-whiteList)
   */
  detectStrategy: string
  /**
   * 是否会员
   */
  isMember: number
  /**
   * 单位漏洞报告中检测出漏洞库的最大数量 1~3
   */
  maxDetectNums: number
  /**
   * 相似度阈值 0~1
   */
  similarityThreshold: number
  [property: string]: number | string | null
}
