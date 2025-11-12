import './assets/main.css'
import 'element-plus/theme-chalk/src/message-box.scss'
import 'element-plus/theme-chalk/src/message.scss'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import * as echarts from 'echarts'

const app = createApp(App)
// 全局挂载 echarts
app.config.globalProperties.$echarts = echarts

app.use(router)

app.mount('#app')
