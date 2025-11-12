
<template>
  <div class="analysis-view-container">
    <!-- 统一的页面头部区域 -->
    <div class="unified-header-section">
      <div class="unified-header-content">
        <!-- 标题部分 -->
        <div class="title-section">
          <el-icon color="#336FFF" size="28" class="title-icon">
            <TrendCharts />
          </el-icon>
          <div class="title-text">
            <h1 class="page-title">项目综合分析</h1>
            <p class="page-subtitle">全面分析项目漏洞趋势与组件分布</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 漏洞情况统计 -->
    <div class="content-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon">
            <DataAnalysis />
          </el-icon>
          漏洞情况统计
        </h2>
      </div>
      <div class="chart-content">
        <WChart width="100%" height="280px" :option="dangerChangeOption"></WChart>
      </div>
    </div>

    <!-- 两栏布局 -->
    <div class="two-column-layout">
      <!-- 待解决项目 -->
      <div class="content-section left-column">
        <div class="section-header">
          <h2 class="section-title">
            <el-icon class="section-icon">
              <Warning />
            </el-icon>
            待解决项目
          </h2>
        </div>
        <div class="projects-content">
          <div v-if="isLoading" class="loading-container">
            <LoadingFrames size="large"></LoadingFrames>
          </div>
          <template v-else-if="dangerProjectInfos.length > 0">
            <PInfo
              v-for="info in dangerProjectInfos"
              :key="info.id"
              :project="info"
              :canEdit="false"
            />
          </template>
          <template v-else>
            <div class="empty-state">
              <el-empty description="暂无待解决项目" :image-size="100"></el-empty>
            </div>
          </template>
        </div>
      </div>

      <!-- 右侧统计 -->
      <div class="right-column">
        <!-- 组件统计 -->
        <div class="content-section stat-section">
          <div class="section-header">
            <h2 class="section-title">
              <el-icon class="section-icon">
                <Grid />
              </el-icon>
              组件统计
            </h2>
          </div>
          <div class="stats-content">
            <div class="stat-item">
              <div class="stat-icon-wrapper scanned-icon">
                <el-icon :size="24">
                  <Tickets />
                </el-icon>
              </div>
              <div class="stat-details">
                <div class="stat-label">已扫描</div>
                <div class="stat-value">{{ thirdLibraryNum }}</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon-wrapper vuln-icon">
                <el-icon :size="24">
                  <Reading />
                </el-icon>
              </div>
              <div class="stat-details">
                <div class="stat-label">漏洞组件数</div>
                <div class="stat-value">{{ vulNum }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 编程语言占比 -->
        <div class="content-section">
          <div class="section-header">
            <h2 class="section-title">
              <el-icon class="section-icon">
                <PieChart />
              </el-icon>
              编程语言占比
            </h2>
          </div>
          <div class="chart-content">
            <WChart width="100%" height="280px" :option="languageOption"></WChart>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Tickets, Reading, Warning, TrendCharts, DataAnalysis, Grid, PieChart } from '@element-plus/icons-vue'
import WChart from '@/components/chart/index.vue'
import PInfo from '@/components/Project/PInfo.vue';
import LoadingFrames from "@/components/LoadingFrames.vue";
import { type ProjectInfo } from '@/components/Project/const';
import { onMounted, ref } from 'vue';
import { getCompanyStatic, type StatisticsInfo } from '@/components/Statistic/const';
import { ElMessage } from 'element-plus';
import { getVulProjectList } from '@/components/Project/apis';
defineProps<{
  project: string
}>();

const dangerProjectInfos = ref<ProjectInfo[]>([
]);
const dangerChangeOption = ref({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['高风险', '中风险', '低风险'],
    right: '5%',
    top: '5%'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  // toolbox: {
  //   feature: {
  //     saveAsImage: {}
  //   }
  // },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '高风险',
      type: 'line',
      // stack: 'Total',
      smooth: true,
      data: [0, 0, 0, 0, 0, 0, 0],
      itemStyle: {
        color: '#f5800c',
      }
    },
    {
      name: '中风险',
      type: 'line',
      // stack: 'Total',
      smooth: true,
      data: [0, 0, 0, 0, 0, 0, 0],
      itemStyle: {
        color: '#fac858',
      }
    },
    {
      name: '低风险',
      type: 'line',
      // stack: 'Total',
      smooth: true,
      data: [0, 0, 0, 0, 0, 0, 0],
      itemStyle: {
        color: '#91cc75',
      }
    },
  ]
});

const languageOption = ref({
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical', // 垂直排列
    right: '5%', // 左侧显示
    top: 'center'
  },
  series: [
    {
      // name: 'Access From',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'], // 保持饼图居中
      avoidLabelOverlap: false,
      padAngle: 5,
      itemStyle: {
        borderRadius: 10,
      },
      label: {
        show: false, // 默认不显示标签
        position: 'center'
      },
      // label: {
      //   show: true, // 显示标签
      //   position: 'inside', // 设置标签显示在扇形区外
      //   formatter: '{d}%', // 显示名称、值和占比
      // },
      emphasis: {
        label: {
          show: true, // 鼠标悬停时显示标签
          formatter: '{b}: {d}%', // 显示名称和占比
          fontSize: '20', // 可以根据需求调整字体大小
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: 0, name: 'Java' },
        { value: 0, name: 'C++' },
        // { value: 580, name: 'Go' },
        // { value: 0, name: '其它' }
      ]
    }
  ]
});
const getVulChangeData = (level: 'high' | 'mid' | 'low', statistic: StatisticsInfo) => {
  let str = '{}'
  if (level == 'high') {
    str = statistic.highVulnerabilityNumByDay
  } else if (level == 'mid') {
    str = statistic.midVulnerabilityNumByDay
  } else if (level == 'low') {
    str = statistic.lowVulnerabilityNumByDay
  }
  const jsonStr = JSON.parse(str)
  const week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const data: number[] = []
  // eslint-disable-next-line prefer-const
  for (let day of week) {
    data.push(jsonStr[day] ?? 0)
  }
  return data
}

const isLoading = ref<boolean>(false)

const getProjects = () => {
  isLoading.value = true;

  getVulProjectList()
    .then(res => {
      dangerProjectInfos.value = res
    }).catch((err) => {
      console.log(err);
      ElMessage.error('获取项目列表失败');
    }).finally(() => {
      isLoading.value = false;
    })


}

const thirdLibraryNum = ref<number>(0)
const vulNum = ref<number>(0)
onMounted(() => {
  getProjects()
  getCompanyStatic()
    .then(res => {
      const statistics: StatisticsInfo = res.obj
      const vulnerabilityNum = statistics.vulnerabilityNum

      // 修改三方库数据
      thirdLibraryNum.value = statistics.thirdLibraryNum
      vulNum.value = vulnerabilityNum


      // 修改语言饼状图配置
      // const otherLanguage = vulnerabilityNum - statistics.javaVulnerabilityNum - statistics.cVulnerabilityNum
      const newLanguageSeries = [{
        ...languageOption.value.series[0],
        data: [
          { value: statistics.javaVulnerabilityNum, name: 'Java' },
          { value: statistics.cVulnerabilityNum, name: 'C/C++' },
          // { value: 580, name: 'Go' },
          // { value: otherLanguage, name: '其它' }
        ]
      }]
      languageOption.value = {
        ...languageOption.value,
        series: newLanguageSeries
      }

      // 修改漏洞情况统计折现图
      const newDangerChangeSeries = [
        {
          name: '高风险',
          type: 'line',
          // stack: 'Total',
          smooth: true,
          data: getVulChangeData('high', statistics),
          itemStyle: {
            color: '#f5800c',
          }
        },
        {
          name: '中风险',
          type: 'line',
          // stack: 'Total',
          smooth: true,
          data: getVulChangeData('mid', statistics),
          itemStyle: {
            color: '#fac858',
          }
        },
        {
          name: '低风险',
          type: 'line',
          // stack: 'Total',
          smooth: true,
          data: getVulChangeData('low', statistics),
          itemStyle: {
            color: '#91cc75',
          }
        },
      ]
      dangerChangeOption.value = {
        ...dangerChangeOption.value,
        series: newDangerChangeSeries
      }
    })
})


</script>

<style scoped>
.analysis-view-container {
  container-name: analysisView;
  container-type: inline-size;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
}

.analysis-view-container::before {
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
  margin: 0 32px 24px;
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

.chart-content {
  padding: 32px;
}

/* 两栏布局 */
.two-column-layout {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  margin: 0 32px 32px;
}

.left-column {
  margin: 0;
}

.right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin: 0;
}

.right-column .content-section {
  margin: 0;
}

.projects-content {
  padding: 24px 32px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.empty-state {
  padding: 40px 0;
}

/* 统计项 */
.stat-section {
  flex-shrink: 0;
}

.stats-content {
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border-radius: 12px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-item:hover {
  transform: translateX(8px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.stat-item:hover .stat-icon-wrapper {
  transform: scale(1.1);
}

.scanned-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: #ffffff;
}

.vuln-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: #ffffff;
}

.stat-details {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

/* 响应式设计 */
@container analysisView (max-width: 1200px) {
  .two-column-layout {
    grid-template-columns: 1fr;
  }

  .right-column {
    flex-direction: row;
    gap: 24px;
  }

  .right-column .content-section {
    flex: 1;
  }

  .unified-header-section {
    margin: 16px;
    padding: 24px;
  }

  .content-section {
    margin: 0 16px 24px;
  }

  .two-column-layout {
    margin: 0 16px 16px;
  }

  .page-title {
    font-size: 28px;
  }
}

@container analysisView (max-width: 931px) {
  .unified-header-section {
    margin: 12px;
    padding: 20px;
  }

  .content-section {
    margin: 0 12px 20px;
  }

  .two-column-layout {
    margin: 0 12px 12px;
  }

  .right-column {
    flex-direction: column;
  }

  .section-header {
    padding: 20px;
  }

  .chart-content {
    padding: 20px;
  }

  .projects-content {
    padding: 20px;
  }

  .stats-content {
    padding: 20px;
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
}

@container analysisView (max-width: 640px) {
  .unified-header-section {
    margin: 8px;
    padding: 16px;
  }

  .content-section {
    margin: 0 8px 16px;
  }

  .two-column-layout {
    margin: 0 8px 8px;
  }

  .section-header {
    padding: 16px;
  }

  .chart-content {
    padding: 16px;
  }

  .projects-content {
    padding: 16px;
  }

  .stats-content {
    padding: 16px;
  }

  .page-title {
    font-size: 20px;
  }

  .page-subtitle {
    font-size: 13px;
  }

  .stat-value {
    font-size: 28px;
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
  animation-fill-mode: both;
}

.content-section:nth-of-type(2) { animation-delay: 0.1s; }
.content-section:nth-of-type(3) { animation-delay: 0.2s; }
.content-section:nth-of-type(4) { animation-delay: 0.3s; }
</style>
