
import instance from '@/utils/request.ts'
import axios from '@/utils/request'
import { type AxiosResponse } from 'axios'
import type { ProjectInfo } from './const'

export interface ProjectCreateResponse {
  code: number
  message: string
  obj: never
}

export const createProject = (project: FormData): Promise<ProjectCreateResponse> => {
  return instance
    .post(`/project/create`, project)
    .then((res: AxiosResponse<ProjectCreateResponse>) => res.data)
}

export const updateProject = (project: FormData): Promise<ProjectCreateResponse> => {
  return instance
    .post(`/project/update`, project)
    .then((res: AxiosResponse<ProjectCreateResponse>) => res.data)
}

export const deleteProject = (project: FormData): Promise<ProjectCreateResponse> => {
  return instance
    .post(`/project/delete`, project)
    .then((res: AxiosResponse<ProjectCreateResponse>) => res.data)
}

export interface ProjectListResponse {
  code: number
  message: string
  obj: Obj[]
}

export interface Obj {
  id: number
  description: string
  name: string
  risk_level: string
  risk_threshold?: string
}

export const getProjectList = (
  page: number,
  size: number,
  companyId: number
): Promise<ProjectListResponse> => {
  return instance
    .get(`/project/list?page=${page}&size=${size}&companyId=${companyId}`)
    .then((res: AxiosResponse<ProjectListResponse>) => res.data)
}

export const getVulProjectList = async () => {
  const companyId = +(localStorage.getItem('companyId') ?? 1)
  const res = await axios.get(`/project/list?page=${1}&size=${20}&companyId=${companyId}`)
  const projectInfos: Obj[] = res.data.obj
  const filteredProjects = projectInfos.filter(
    (project) => project.risk_level && project.risk_level !== '暂无风险',
  )
  const riskOrder: { [key_1: string]: number } = { 高风险: 1, 中风险: 2, 低风险: 3 }
  const sortedProjects = filteredProjects.sort((a, b) => {
    const aRisk = a.risk_level ? riskOrder[a.risk_level] || Infinity : Infinity
    const bRisk = b.risk_level ? riskOrder[b.risk_level] || Infinity : Infinity
    return aRisk - bRisk
  })
  const transformedProjects: ProjectInfo[] = sortedProjects.map((project_1) => ({
    description: project_1.description || '',
    id: project_1.id ? +project_1.id : 0,
    name: project_1.name || '',
    risk_level: project_1.risk_level || '',
    risk_threshold: project_1.risk_threshold ? parseInt(project_1.risk_threshold, 10) : 0,
    companyId: companyId + '',
    language: 'java',
    filePath: null,
  }))
  return transformedProjects
}
