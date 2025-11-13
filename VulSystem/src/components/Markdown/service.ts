import axios from '@/utils/request'

export const acceptVul = (vulnerabilityid: number, ifaccept: 1 | 2) => {
  return axios.get('/vulnerability/accept', {
    params: {
      // vulnerabilityid,
      vulnerabilityid,
      ifaccept,
    },
  })
}

export const getSuggestion = (name: string, desc: string, model: string, code?: string) => {
  return axios.post(
    '/llm/repair/suggestion',
    {
      vulnerability_name: name,
      vulnerability_desc: desc,
      related_code: code,
      model:model,
    },
    {
     // baseURL: '/crawler',
      baseURL: 'http://localhost:5000',
      timeout: 30000000, // 5分钟超时时间，专门为LLM请求设置
    },
  )
}
