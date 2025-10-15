<template>
  <div class="register">
    <div class="card">
      <h2>库灵之眼系统</h2>

      <div class="input-container">
        <div class="input-title">用户名</div>
        <el-input v-model="username" placeholder="请输入您的用户名" clearable>
          <template #prefix>
            <el-icon><User /></el-icon>
          </template>
        </el-input>
      </div>

      <div class="input-container">
        <div class="input-title">邮箱</div>
        <el-input v-model="email" placeholder="请输入您常用的邮箱" clearable>
          <template #prefix>
            <el-icon><User /></el-icon>
          </template>
        </el-input>
        <div class="warning" v-if="!checkEmail">邮箱格式不正确</div>
      </div>

      <div class="input-container">
        <div class="input-title">密码</div>
        <el-input v-model="passwd" show-password placeholder="请输入密码" clearable>
          <template #prefix>
            <el-icon><Lock /></el-icon>
          </template>
        </el-input>
        <div class="strength-indicator">
          <div class="strength" :style="{width: strengthWidth, backgroundColor: strengthColor}"></div>
          <span class="strength-text">{{strengthText}}</span>
        </div>
      </div>

      <div class="input-container">
        <div class="input-title">确认您的密码</div>
        <el-input v-model="confirmPasswd" show-password placeholder="请再次输入密码" clearable>
          <template #prefix>
            <el-icon><Lock /></el-icon>
          </template>
        </el-input>
        <div class="warning" v-if="confirmPasswd!== '' && passwd !== confirmPasswd">两次密码不一致</div>
      </div>

      <div class="confirm-button" @click="handleRegister" :class="{disabled: !checkRegisterAvailable}">
        <el-icon><Promotion /></el-icon>
        <span class="confirm-text">注册</span>
      </div>

      <div class="other-container" @click="handleJumpToLogin">
        已经有账户？<span class="link">去登录</span>
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup>
import router from '@/router'
import {computed, ref} from 'vue'
import { ElMessage } from 'element-plus'
import { api } from './service'
import {Lock, Promotion, User} from "@element-plus/icons-vue";
const username = ref('')
const email = ref('')
const passwd = ref('')
const confirmPasswd = ref('')

const checkEmail = computed(() => {
  if (!email.value) return true
  return /^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/.test(email.value)
})

const strength = computed(() => {
  if (!passwd.value) return ''

  const len6 = passwd.value.length >= 6
  const len10 = passwd.value.length >= 10
  const hasUpper = passwd.value.match(/[A-Z]/)
  const hasSpecial = passwd.value.match(/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+/)
  const hasNumber = passwd.value.match(/[0-9]/)
  const hasLower = passwd.value.match(/[a-z]/)

  if(!len6 || !hasUpper || !hasNumber || !hasLower) return 'weak'

  if(len10 && hasSpecial) return 'strong'

  return 'medium'
})

const strengthText = computed(() => {
  if (strength.value === '') return ''
  if (strength.value === 'weak') return '密码较弱，请重新选择'
  if (strength.value === 'medium') return '密码强度中等'
  return '密码较强'
})

const strengthColor = computed(() => {
  if (strength.value === '') return ''
  if (strength.value === 'weak') return '#dc2626'
  if (strength.value === 'medium') return '#667eea'
  return '#10b981'
})

const strengthWidth = computed(() => {
  if (strength.value === '') return ''
  if (strength.value === 'weak') return '25%'
  if (strength.value === 'medium') return '50%'
  return '75%'
})

const checkRegisterAvailable = computed(() => {
  return username.value.length !== 0 && email.value.length !==0 && checkEmail.value && passwd.value.length != 0 && passwd.value === confirmPasswd.value && strength.value !== 'weak'
})

const handleRegister = () => {
  const info = {
    username: username.value,
    email: email.value,
    password: passwd.value,
    phone: ''
  }
  api.register(info)
    .then(res => {
      console.log(res);
      ElMessage.success('注册成功！')
      router.push('/login')
    })
    .catch(err => {
      console.error('注册失败:', err)
      ElMessage.error(err?.data?.message || '注册失败，请稍后重试')
    })
}

const handleJumpToLogin = () => {
  router.push('/login')
}

</script>

<style scoped>
.register {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.register::before {
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
  margin: 12px 0;
  display: flex;
  align-items: start;
  flex-direction: column;
}

.input-container .warning {
  color: #dc2626;
  font-size: 12px;
  margin-left: 4px;
  margin-top: 6px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.input-container .warning::before {
  content: '⚠';
  color: #dc2626;
}

.input-container .strength-indicator {
  display: flex;
  width: 100%;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding-left: 4px;
  padding-right: 4px;
  margin-top: 8px;
  gap: 12px;
}

.input-container .strength-indicator .strength {
  height: 5px;
  background-color: #667eea;
  border-radius: 3px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
}

.input-container .strength-indicator .strength-text {
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  color: #64748b;
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
  margin-top: 16px;
  color: #64748b;
  cursor: pointer;
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

.confirm-button {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 12px;
  height: 48px;
  cursor: pointer;
  margin: 28px 0 12px;
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

.confirm-button.disabled {
  background: linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%);
  cursor: not-allowed;
  box-shadow: none;
  opacity: 0.6;
}

.confirm-button.disabled:hover {
  transform: none;
  box-shadow: none;
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
