<template>
  <div class="login">
    <div class="card">
      <h2>库灵之眼系统</h2>
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
  </div>
</template>
<script lang="ts" setup>
import router from '@/router'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from './service'

import {ArrowRightBold, Lock, User} from '@element-plus/icons-vue';

const username = ref('')
const passwd = ref('')
const handleLogin = () => {
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
