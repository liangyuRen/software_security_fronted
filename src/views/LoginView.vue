<template>
  <div class="login">
    <div class="card">
      <h2>{{ isLogin ? '库灵之眼系统' : '用户注册' }}</h2>

      <!-- 登录表单 -->
      <div v-if="isLogin">
        <div class="input-container">
          <div class="input-title">用户名/邮箱</div>
          <el-input v-model="username" placeholder="请输入您的用户名或邮箱" clearable>
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="input-container">
          <div class="input-title">密码</div>
          <el-input v-model="passwd" show-password placeholder="请输入密码" clearable>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="confirm-button" @click="handleLogin">
          <el-icon><ArrowRightBold></ArrowRightBold></el-icon>
          <span class="confirm-text">登录</span>
        </div>
      </div>

      <!-- 注册表单 -->
      <div v-else>
        <div class="input-container">
          <div class="input-title">用户名</div>
          <el-input v-model="regUsername" placeholder="请输入用户名" clearable>
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="input-container">
          <div class="input-title">邮箱</div>
          <el-input v-model="regEmail" placeholder="请输入邮箱" clearable>
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </div>

          <div class="input-container">
          <div class="input-title">手机号码</div>
          <el-input v-model="regPhone" placeholder="请输入手机号码" clearable>
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="input-container">
          <div class="input-title">密码</div>
          <el-input v-model="regPassword" show-password placeholder="请输入密码" clearable>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="input-container">
          <div class="input-title">确认密码</div>
          <el-input v-model="regConfirmPassword" show-password placeholder="请再次输入密码" clearable>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="confirm-button" @click="handleRegister">
          <el-icon><ArrowRightBold></ArrowRightBold></el-icon>
          <span class="confirm-text">注册</span>
        </div>
      </div>

      <!-- 切换登录/注册 -->
      <div class="switch-container">
        <span v-if="isLogin">还没有账号？</span>
        <span v-else>已有账号？</span>
        <span class="link" @click="toggleMode">
          {{ isLogin ? '立即注册' : '立即登录' }}
        </span>
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup>
import router from '@/router'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from './service'

import {ArrowRightBold, Lock, User, Message} from '@element-plus/icons-vue';

const isLogin = ref(true)
const username = ref('')
const passwd = ref('')

// 注册相关数据
const regUsername = ref('')
const regEmail = ref('')
const regPhone = ref('')
const regPassword = ref('')
const regConfirmPassword = ref('')

// 切换登录/注册模式
const toggleMode = () => {
  isLogin.value = !isLogin.value
  // 清空表单
  if (isLogin.value) {
    // 切换到登录模式时清空注册表单
    regUsername.value = ''
    regEmail.value = ''
    regPhone.value = ''
    regPassword.value = ''
    regConfirmPassword.value = ''
  } else {
    // 切换到注册模式时清空登录表单
    username.value = ''
    passwd.value = ''
  }
}

// 登录处理
const handleLogin = () => {
  if (!username.value || !passwd.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  api.login(username.value, passwd.value)
    .then(res => {
      console.log('【登录响应】', res)
      console.log('【res类型】', typeof res)
      console.log('【res.code】', res?.code)
      console.log('【res.obj】', res?.obj)

      // 处理响应
      if(!res || typeof res !== 'object') {
        ElMessage.error('登录响应数据格式错误')
        return
      }

      if(res.code !== 200) {
        const errMsg = typeof res.obj === 'string' ? res.obj : res.message || '登录失败'
        ElMessage.error(errMsg)
        return
      }

      // 验证响应数据
      if (!res.obj || !res.obj.token) {
        ElMessage.error('登录响应数据缺少必要字段(token)')
        console.error('【响应数据异常】', res.obj)
        return
      }

      // 保存用户信息到localStorage
      const companyId = 1  // 写死为1
      const companyName = res.obj.companyName || 'company'
      const token = res.obj.token

      try {
        localStorage.setItem('companyId', String(companyId))
        localStorage.setItem('companyName', companyName)
        localStorage.setItem('username', username.value)
        localStorage.setItem('token', token)

        console.log('【localStorage已设置】')
        console.log('  companyId:', localStorage.getItem('companyId'))
        console.log('  token:', localStorage.getItem('token')?.substring(0, 20) + '...')

        // 验证数据是否真的被保存
        const savedCompanyId = localStorage.getItem('companyId')
        const savedToken = localStorage.getItem('token')

        if (!savedCompanyId || !savedToken) {
          ElMessage.error('登录信息保存失败，请检查浏览器存储权限')
          console.error('【localStorage保存失败】', { savedCompanyId, savedToken })
          return
        }

        ElMessage.success('登录成功')

        // 延迟跳转，确保localStorage已同步
        console.log('【准备跳转到首页】')
        setTimeout(() => {
          console.log('【执行路由跳转】')
          router.push('/').catch(err => {
            console.error('【路由跳转错误】', err)
            // 如果路由失败，尝试刷新页面
            window.location.href = '/'
          })
        }, 300)  // 减少延迟时间，因为数据保存已验证
      } catch (error) {
        console.error('【localStorage操作错误】', error)
        ElMessage.error('登录信息保存异常：' + String(error))
      }
    })
    .catch(err => {
      console.error('【登录请求错误】', err)
      const errMsg = err?.message || err?.data?.message || JSON.stringify(err)
      ElMessage.error('登录失败: ' + errMsg)
    })
}

// 注册处理
const handleRegister = () => {
  // 表单验证
  if (!regUsername.value) {
    ElMessage.warning('请输入用户名')
    return
  }

  if (!regEmail.value) {
    ElMessage.warning('请输入邮箱')
    return
  }
    if (!regPhone.value) {
    ElMessage.warning('请输入电话号码')
    return
  }

  if (!regPassword.value) {
    ElMessage.warning('请输入密码')
    return
  }

  if (regPassword.value !== regConfirmPassword.value) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  // 调用注册API
  const registerInfo = {
    username: regUsername.value,
    email: regEmail.value,
    password: regPassword.value,
    phone: regPhone.value
  }

  api.register(registerInfo)
    .then(res => {
      console.log(res);
      if(res.code !== 200) {
        ElMessage.error(res.obj || '注册失败')
        return
      }

      ElMessage.success('注册成功，请登录')
      // 切换到登录模式
      setTimeout(() => {
        isLogin.value = true
        // 清空注册表单
        regUsername.value = ''
        regEmail.value = ''
        regPassword.value = ''
        regConfirmPassword.value = ''
        regPhone.value = ''
      }, 1000)
    })
    .catch(err => {
      ElMessage.error('注册失败：' + err)
    })
}
</script>

<style scoped>
.login {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login::before {
  content: '';
  position: absolute;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: drift 20s linear infinite;
}

@keyframes drift {
  from {
    transform: translate(0, 0);
  }
  to {
    transform: translate(50px, 50px);
  }
}

/* 中间偏右 */
.card {
  position: relative;
  z-index: 1;
  min-height: 40vh;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  min-width: 380px;
  width: 26%;
  transform: translateX(50%);
  padding: 40px 36px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  transform: translateX(50%) translateY(-8px);
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.35);
}

.card h2 {
  margin-bottom: 28px;
  font-weight: 800;
  font-size: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
  letter-spacing: -0.5px;
}

.input-container {
  margin: 16px 0;
  display: flex;
  align-items: start;
  flex-direction: column;
}

.input-title {
  font-size: 13px;
  color: #475569;
  margin-left: 4px;
  margin-bottom: 8px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.card :deep(.el-input) {
  height: 44px;
  margin: 4px 0;
  border-radius: 12px;
}

.card :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.card :deep(.el-input__wrapper:hover) {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.card :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
}

.card :deep(.el-input__prefix) {
  color: #667eea;
  font-size: 18px;
}

.other-container {
  font-size: 13px;
  text-align: center;
  margin-top: 12px;
  color: #64748b;
}

.other-container .link {
  color: #667eea;
  cursor: pointer;
  font-weight: 700;
  transition: color 0.3s ease;
}

.other-container .link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.switch-container {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: #64748b;
}

.switch-container .link {
  color: #667eea;
  cursor: pointer;
  font-weight: 700;
  margin-left: 6px;
  transition: color 0.3s ease;
}

.switch-container .link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.confirm-button {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 12px;
  height: 48px;
  cursor: pointer;
  margin: 32px 0 12px;
  font-size: 15px;
  font-weight: 700;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  border: none;
}

.confirm-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(102, 126, 234, 0.5);
}

.confirm-button:active {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.confirm-text {
  margin-left: 8px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .card {
    width: 35%;
    transform: translateX(40%);
  }

  .card:hover {
    transform: translateX(40%) translateY(-8px);
  }
}

@media (max-width: 931px) {
  .card {
    width: 50%;
    transform: translateX(20%);
  }

  .card:hover {
    transform: translateX(20%) translateY(-8px);
  }
}

@media (max-width: 640px) {
  .card {
    width: 90%;
    min-width: 300px;
    transform: translateX(0);
    padding: 32px 24px;
  }

  .card:hover {
    transform: translateY(-8px);
  }

  .card h2 {
    font-size: 24px;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  animation: fadeIn 0.6s ease-out;
}
</style>
