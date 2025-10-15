import axios from '@/utils/request'

export const queryLLM = (query: string, model?: string) => {
  return axios.get(`/llm/query`, {
    baseURL: '/crawler',
    params: {
      query,
      model,
    },
  })
}
