import axios from '@/utils/request'

export const getSbomFile = (projectId: number, format: string, outFileName: string) => {
  return axios.get('/project/sbom', {
    params: {
      projectId,
      format,
      outFileName,
    },
    responseType: 'blob', // 设置响应类型为blob
  })
}
