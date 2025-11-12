import axios from 'axios'

const errorHandle = (status: number, info: string) => {
  switch (status) {
    case 400:
      console.log('语义有误')
      break
    case 401:
      console.log('服务器认证失败')
      break
    case 403:
      console.log('服务器拒绝访问')
      break
    case 404:
      console.log('地址错误')
      break
    case 500:
      console.log('服务器遇到意外')
      break
    case 502:
      console.log('服务器无响应')
      break
    default:
      console.log(info)
      break
  }
}

// 1.创建网络请求对象
const instance = axios.create({
  // 这里放网络请求的公共配置
  timeout: 500000,
  baseURL: '/api', // 通过Nginx代理转发到后端
//baseURL: 'http://localhost:8081',
})

// 拦截器----发送数据之前
instance.interceptors.request.use(
  (config) => {
    // 拦截器成功函数

    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token
    }

    // 对于POST请求，将数据转换为FormData（因为后端使用@RequestParams）
    if (config.method == 'post' && config.data && !(config.data instanceof FormData)) {
      try {
        const formData = new FormData()

        // 处理普通对象和FormData
        if (config.data instanceof FormData) {
          // 已经是FormData，无需转换
          return config
        }

        // 将config.data中的每一个键值对添加到formData
        Object.keys(config.data).forEach((key) => {
          if (config.data[key] !== null && config.data[key] !== undefined) {
            formData.append(key, config.data[key])
          }
        })

        config.data = formData
        // 不要手动设置Content-Type，让axios自动处理
        delete config.headers['Content-Type']
      } catch (err) {
        console.error('FormData转换失败:', err)
        return Promise.reject(err)
      }
    }

    // config:包含着网络请求的所有信息
    return config
  },
  (error) => {
    // 拦截器失败函数
    console.log('请求发送失败:', error)
    // 返回错误信息
    return Promise.reject(error)
  },
)

// 拦截器----获取数据之前
instance.interceptors.response.use(
  (response) => {
    console.log(`响应response status: ${response.status}`, response.data)
    // 拦截器成功函数
    // 返回response.data而不是response，这样才能返回后端返回的RespBean对象
    if (response.status == 200) {
      return Promise.resolve(response.data)
    } else {
      // 非200状态码视为错误
      console.error('响应状态码非200:', response.status, response.data)
      return Promise.reject(response.data || response)
    }
  },
  (error) => {
    // 拦截器失败函数
    console.error('响应拦截器错误:', error)
    const { response } = error
    if (response) {
      console.error('HTTP错误状态码:', response.status)
      errorHandle(response.status, response.statusText)
      // 尝试返回response.data，如果没有则返回整个response对象
      return Promise.reject(response.data || response)
    } else {
      console.log('网络错误或请求超时:', error.message)
      return Promise.reject({ code: -1, message: '网络错误或请求超时', obj: error.message })
    }
  },
)

//2.导出网络请求对象
export default instance
