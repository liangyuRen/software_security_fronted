<template>
  <el-breadcrumb :separator-icon="ArrowRight" class="bread">
    <el-breadcrumb-item :to="{ path: '/users' }">
      <el-icon color="#336FFF" size="14">
        <Discount />
      </el-icon>
      <span class="bread-item">用户中心</span>
    </el-breadcrumb-item>
  </el-breadcrumb>
  <DataCard title="个人信息" width="auto">
    <template #main>
      <div class="user-name">
        <div class="user-icon">
          <el-icon>
            <User />
            <!-- <UserFilled /> -->
          </el-icon>
        </div>
        <h4>{{ userInfo.userName || '用户名' }}</h4>
      </div>
      <div class="user-infos">
        <div class="info">
          <div class="label">
            职位
          </div>
          <div class="text">
            {{ userInfo.role || '暂无职位信息' }}
          </div>
        </div>
        <div class="info">
          <div class="label">
            手机号
          </div>
          <div class="text">
            {{ userInfo.phone || '暂无手机号' }}
          </div>
        </div>
        <div class="info">
          <div class="label">
            办公邮箱
          </div>
          <div class="text">
            {{ userInfo.email || '暂无邮箱' }}
          </div>
        </div>
        <div class="info">
          <div class="label">
            是否是会员
          </div>
          <div class="tag" :style="{ backgroundColor: userInfo.isVip ? '#FFF5EB' : '#F0F0F0', color: userInfo.isVip ? '#FE8B00' : '#999' }">
            {{ userInfo.isVip ? 'VIP' : '普通用户' }}
          </div>
        </div>
        <div class="info">
          <div class="label">
            所属团队
          </div>
          <div class="text">
            {{ userInfo.team || '暂无团队信息' }}
          </div>
        </div>
      </div>
    </template>
  </DataCard>


</template>

<script setup lang="ts">
import { ArrowRight, Discount, User } from '@element-plus/icons-vue'
import DataCard from '@/components/DataCard.vue';
import { onMounted, reactive, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { api } from './service';

// 用户信息数据结构
interface UserInfo {
  userName?: string;
  role?: string;
  phone?: string;
  email?: string;
  isVip?: boolean;
  team?: string;
  [key: string]: any;
}

const userInfo = reactive<UserInfo>({});

// 获取用户信息
const getUserInfo = () => {
  api.getUserInfo()
    .then(res => {
      console.log('用户信息响应:', res);
      if (res.data.code === 200) {
        // 将后端返回的用户数据合并到 userInfo 对象中
        Object.assign(userInfo, res.data.obj);
      } else {
        ElMessage.error(res.data.obj || '获取用户信息失败');
      }
    })
    .catch(err => {
      console.error('获取用户信息失败:', err);
      ElMessage.error('获取用户信息失败');
    });
};

onMounted(() => {
  getUserInfo();
})



</script>

<style scoped>
.bread {
  margin: 15px;
  margin-bottom: 30px;

  .el-breadcrumb__item {
    height: 18px;
  }

  .bread-item {
    color: #336FFF;
    /* font-size: 16px; */
    margin-left: 10px;
    font-weight: bold;
  }
}



.user-name {
  display: flex;
  align-items: center;
  margin: 20px 10px;

  .user-icon {
    /* color: #336fff; */
    color: #fff;
    /* border: 1px solid #8b8c8d; */
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 15px;
    background-color: #336fff;
  }

  h4 {
    /* font-weight: bold; */
    margin-left: 10px;
    /* font-size: 24px; */
  }
}

.user-infos {
  display: flex;
  justify-content: space-between;
  margin: 20px 10px;
  margin-right: 20px;

  .info {
    display: flex;
    flex-direction: column;

    .label {
      color: #666;
      font-size: 12px;
    }

    .text {
      font-size: 14px;
    }

    .tag {
      padding: 4px 15px;
      /* height: 20px; */
      border-radius: 10px;
      font-size: 12px;
      /* line-height: 20px; */
      cursor: pointer;
      margin-right: 10px;
      font-weight: bold;

    }
  }
}
</style>
