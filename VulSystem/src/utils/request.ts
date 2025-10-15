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
  baseURL: 'http://localhost:8081', // 服务器地址，上线后需要修改
})

// 拦截器----发送数据之前
instance.interceptors.request.use(
  (config) => {
    // 拦截器成功函数

    // 暂时不可这样做，原因：formData 中含有文件，querystring.stringify 会将文件转为字符串
    if (config.method == 'post') {
      // config.data = querystring.stringify(config.data)
      // 由于后端处理post请求是用的@RequestParams，故这里将请求体转成表单对象
      const formData = new FormData()

      // 将config.data中的每一个键值对添加到formData
      Object.keys(config.data).forEach((key) => {
        // 假设config.data[key]可能是文件，使用append添加
        formData.append(key, config.data[key])
      })

      // 将formData赋给config.data
      config.data = formData

      // 设置正确的Content-Type
      config.headers['Content-Type'] = 'multipart/form-data'
    }

    // config:包含着网络请求的所有信息
    return config
  },
  (error) => {
    // 拦截器失败函数
    console.log('请求发送失败')
    // 返回错误信息
    return Promise.reject(error)
  },
)

// 拦截器----获取数据之前
instance.interceptors.response.use(
  (response) => {
    console.log(`响应response: ${response}`)
    // 拦截器成功函数
    return response.status == 200 ? Promise.resolve(response) : Promise.reject(response)
  },
  (error) => {
    // 拦截器失败函数
    const { response } = error
    errorHandle(response.status, response.info)
  },
)

//2.导出网络请求对象
export default instance
