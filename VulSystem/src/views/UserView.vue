<template>
  <div class="user-view-container">
    <!-- 统一的页面头部区域 -->
    <div class="unified-header-section">
      <div class="unified-header-content">
        <!-- 标题部分 -->
        <div class="title-section">
          <el-icon color="#336FFF" size="28" class="title-icon">
            <UserFilled />
          </el-icon>
          <div class="title-text">
            <h1 class="page-title">用户中心</h1>
            <p class="page-subtitle">管理您的个人信息和账户设置</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户信息卡片 - 表格风格 -->
    <div class="content-section">
      <div class="user-content">
        <table class="user-info-table">
          <thead>
            <tr>
              <th class="user-col">用户信息</th>
              <th class="role-col">职位</th>
              <th class="contact-col">联系方式</th>
              <th class="team-col">所属团队</th>
              <th class="status-col">会员状态</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="user-col">
                <div class="user-info-cell">
                  <div class="avatar-icon">
                    <el-icon :size="36">
                      <User />
                    </el-icon>
                  </div>
                  <div class="user-details">
                    <div class="user-name">{{ userInfo.userName || '用户名' }}</div>
                    <div class="user-id">ID: {{ userInfo.id || '-' }}</div>
                  </div>
                </div>
              </td>
              <td class="role-col">
                <div class="info-cell">
                  <el-icon class="cell-icon position-icon" :size="20">
                    <Briefcase />
                  </el-icon>
                  <span>{{ userInfo.role || '暂无职位信息' }}</span>
                </div>
              </td>
              <td class="contact-col">
                <div class="contact-info">
                  <div class="contact-item">
                    <el-icon class="cell-icon phone-icon" :size="16">
                      <Phone />
                    </el-icon>
                    <span>{{ userInfo.phone || '暂无手机号' }}</span>
                  </div>
                  <div class="contact-item">
                    <el-icon class="cell-icon email-icon" :size="16">
                      <Message />
                    </el-icon>
                    <span>{{ userInfo.email || '暂无邮箱' }}</span>
                  </div>
                </div>
              </td>
              <td class="team-col">
                <div class="info-cell">
                  <el-icon class="cell-icon team-icon" :size="20">
                    <OfficeBuilding />
                  </el-icon>
                  <span>{{ userInfo.team || '暂无团队信息' }}</span>
                </div>
              </td>
              <td class="status-col">
                <div class="user-badge" :class="{ 'vip-badge': userInfo.isVip }">
                  <el-icon :size="16">
                    <StarFilled v-if="userInfo.isVip" />
                    <Star v-else />
                  </el-icon>
                  <span>{{ userInfo.isVip ? 'VIP会员' : '普通用户' }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, UserFilled, Star, StarFilled, Briefcase, Phone, Message, OfficeBuilding } from '@element-plus/icons-vue'
import { onMounted, reactive } from 'vue';
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
.user-view-container {
  container-name: userView;
  container-type: inline-size;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
}

.user-view-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 0;
}

/* 统一的页面头部区域 */
.unified-header-section {
  position: relative;
  z-index: 1;
  margin: 24px 32px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.3);
  overflow: hidden;
}

.unified-header-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%);
  background-size: 200% 100%;
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.unified-header-content {
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
}

.title-section {
  display: flex;
  align-items: center;
}

.title-icon {
  margin-right: 20px;
  filter: drop-shadow(0 4px 8px rgba(51, 111, 255, 0.4));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-3px); }
}

.title-text {
  flex: 1;
}

.page-title {
  font-size: 32px;
  font-weight: 800;
  color: #1a202c;
  margin: 0 0 8px 0;
  letter-spacing: -0.8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 16px;
  color: #64748b;
  margin: 0;
  font-weight: 400;
  opacity: 0.9;
}

/* 内容区域 */
.content-section {
  position: relative;
  z-index: 1;
  margin: 0 32px 32px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
}

.section-header {
  padding: 24px 32px;
  border-bottom: 2px solid #f1f5f9;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  color: #667eea;
  font-size: 24px;
}

.user-content {
  padding: 0;
}

/* 用户信息表格 */
.user-info-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: #ffffff;
}

.user-info-table th {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  color: #374151;
  font-weight: 700;
  font-size: 14px;
  padding: 16px;
  border-bottom: 2px solid #e2e8f0;
  line-height: 20px;
  text-align: left;
  position: sticky;
  top: 0;
  z-index: 10;
  letter-spacing: 0.025em;
}

.user-info-table th:first-child {
  border-top-left-radius: 12px;
}

.user-info-table th:last-child {
  border-top-right-radius: 12px;
}

.user-info-table td {
  padding: 24px 16px;
  border-bottom: 1px solid #f1f5f9;
  color: #374151;
  font-size: 14px;
  line-height: 20px;
  vertical-align: middle;
}

.user-info-table tbody tr {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.user-info-table tbody tr:hover {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transform: scale(1.005);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  z-index: 5;
}

.user-col {
  width: 280px;
  min-width: 240px;
}

.role-col {
  width: 200px;
  min-width: 160px;
}

.contact-col {
  width: 280px;
  min-width: 240px;
}

.team-col {
  width: 200px;
  min-width: 160px;
}

.status-col {
  width: 140px;
  min-width: 120px;
}

/* 用户信息单元格 */
.user-info-cell {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.user-info-table tbody tr:hover .avatar-icon {
  transform: scale(1.05);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-name {
  font-size: 18px;
  font-weight: 700;
  color: #1a202c;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.user-id {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  font-family: 'Consolas', monospace;
}

/* 信息单元格 */
.info-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cell-icon {
  flex-shrink: 0;
}

.position-icon {
  color: #8b5cf6;
}

.phone-icon {
  color: #06b6d4;
}

.email-icon {
  color: #ec4899;
}

.team-icon {
  color: #10b981;
}

/* 联系信息 */
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

/* 会员徽章 */
.user-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  color: #64748b;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.user-badge.vip-badge {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(251, 191, 36, 0.4);
}

/* 响应式设计 */
@container userView (max-width: 1200px) {
  .unified-header-section {
    margin: 16px;
    padding: 24px;
  }

  .content-section {
    margin: 0 16px 16px;
  }

  .page-title {
    font-size: 28px;
  }
}

@container userView (max-width: 931px) {
  .unified-header-section {
    margin: 12px;
    padding: 20px;
  }

  .content-section {
    margin: 0 12px 12px;
  }

  .user-content {
    padding: 20px;
  }

  .user-profile {
    flex-direction: column;
    text-align: center;
    padding: 24px;
  }

  .page-title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: 14px;
  }

  .title-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .title-icon {
    margin-bottom: 12px;
    margin-right: 0;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}

@container userView (max-width: 640px) {
  .unified-header-section {
    margin: 8px;
    padding: 16px;
  }

  .content-section {
    margin: 0 8px 8px;
  }

  .user-content {
    padding: 16px;
  }

  .user-profile {
    padding: 20px;
  }

  .page-title {
    font-size: 20px;
  }

  .page-subtitle {
    font-size: 13px;
  }

  .user-name {
    font-size: 24px;
  }

  .avatar-icon {
    width: 80px;
    height: 80px;
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.unified-header-section {
  animation: slideDown 0.8s ease-out;
}

.content-section {
  animation: fadeInUp 0.6s ease-out;
  animation-delay: 0.3s;
  animation-fill-mode: both;
}

.info-card {
  animation: fadeInUp 0.5s ease-out;
  animation-fill-mode: both;
}

.info-card:nth-child(1) { animation-delay: 0.1s; }
.info-card:nth-child(2) { animation-delay: 0.2s; }
.info-card:nth-child(3) { animation-delay: 0.3s; }
.info-card:nth-child(4) { animation-delay: 0.4s; }
</style>
