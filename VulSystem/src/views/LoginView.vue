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
      console.log(res);
      if(res.data.code !== 200) {
        ElMessage.error(res.data.obj)
        return
      }
      //bug描述：后端返回的数据根本没有companyId这个参数
      localStorage.setItem('companyId', res.data.obj.companyId)
      localStorage.setItem('companyName', res.data.obj.companyName)
      localStorage.setItem('username', username.value)
      ElMessage.success('登录成功')
      // wait for 0.5 second
      setTimeout(() => {
        router.push('/')
      }, 500)
    })
    .catch(err => {
      ElMessage.error(err)
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
      if(res.data.code !== 200) {
        ElMessage.error(res.data.obj || '注册失败')
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
  background: url('../assets/bg.jpg');
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 中间偏右 */
.card {
  min-height: 40vh;
  background-color: #fff;
  border-radius: 12px;
  min-width: 350px;
  width: 24%;
  transform: translateX(60%);
  padding: 25px 30px;

  h2 {
    margin-bottom: 15px;
    font-weight: 600;
    font-size: 24px;
  }

  .input-container{
    margin: 4px 0;
    display: flex;
    align-items: start;
    flex-direction: column;
  }

  .input-title{
    font-size: 12px;
    color: #333;
    margin-left: 4px;
    font-weight: bold;
  }

  .el-input {
    height: 36px;
    margin: 4px 0;
    border-radius: 6px;
  }

  .other-container {
    font-size: 12px;

    .link{
      color: #336fff;
      cursor: pointer;
      font-weight: bold;
    }
  }

  .switch-container {
    text-align: center;
    margin-top: 15px;
    font-size: 12px;
    color: #666;

    .link {
      color: #336fff;
      cursor: pointer;
      font-weight: bold;
      margin-left: 4px;
    }
  }

  .confirm-button{
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #409eff;
    color: #fff;
    border-radius: 6px;
    height: 36px;
    cursor: pointer;
    margin: 25px 0 10px;
  }

  .confirm-text{
    margin-left: 4px;
    font-weight: bold;
  }
}
</style>
