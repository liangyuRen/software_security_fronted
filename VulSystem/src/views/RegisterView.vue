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
  if (strength.value === 'weak') return 'red'
  if (strength.value === 'medium') return 'orange'
  return 'green'
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
    password: passwd.value,
  }
  api.register(info)
    .then(res => {
      console.log(res);
      router.push('/')
    })
    .catch(err => {
      ElMessage.error(err)
    })
}

const handleJumpToLogin = () => {
  router.push('/login')
}

</script>

<style scoped>
.register {
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

    .warning{
      color: red;
      font-size: 12px;
      margin-left: 4px;
      font-weight: bold;
    }

    .strength-indicator{
      display: flex;
      width: 100%;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
      padding-left: 4px;
      padding-right: 4px;

      .strength{
        height: 4px;
        background-color: #409eff;
        border-radius: 2px;
      }

      .strength-text{
        font-size: 12px;
        font-weight: bold;
      }
    }
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

    &.disabled{
      background-color: #ccc;
      cursor: not-allowed;
    }
  }

  .confirm-text{
    margin-left: 4px;
    font-weight: bold;
  }
}
</style>
