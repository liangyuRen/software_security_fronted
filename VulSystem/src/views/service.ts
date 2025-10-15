import axios from '../utils/request'

export const api = {
  login(username: string, password: string) {
    console.log(username, password)
    return axios.get('/user/login', {params: {username: username, password: password}});
  },

  register(info) {
    console.log(info)
    return axios.post('/user/register', {
      username: info.username,
      email: info.email,
      password: info.password,
      phone:info.phone
    });
  },

  getProjectDetail(projectId: number) {
    return axios.get('/project/info', {
      params: {
        projectid: projectId,
      },
    })
  },

  getVulList(projectId: number) {
    return axios.get('/project/getVulnerabilities', {
      params: {
        id: projectId,
      },
    })
  },

  getUserInfo() {
    return axios.get('/user/info', {
      params: {
        username: localStorage.getItem('username'),
      },
    });
  },
}
