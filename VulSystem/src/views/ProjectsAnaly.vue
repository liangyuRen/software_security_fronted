
<template>
  <el-breadcrumb :separator-icon="ArrowRight" class="bread">
    <el-breadcrumb-item :to="{ path: '/' }">
      <el-icon color="#336FFF" size="14">
        <DocumentCopy />
      </el-icon>
      <span class="bread-item">项目管理</span>
    </el-breadcrumb-item>
    <el-breadcrumb-item>项目综合分析</el-breadcrumb-item>
  </el-breadcrumb>

  <DataCard title="漏洞情况统计" width="auto">
    <template #main>
      <WChart width="100%" height="200px" :option="dangerChangeOption"></WChart>
    </template>
  </DataCard>
  <div class="data-infos">
    <!-- <v-chart ref="mychart1" class="chart"></v-chart> -->
    <DataCard title="待解决项目">
      <template #main>
        <div v-if="isLoading" style="display: flex; justify-content: center; align-items: center; height: 200px;">
          <LoadingFrames size="large"></LoadingFrames>
        </div>
        <template v-else-if="dangerProjectInfos.length > 0">
          <PInfo v-for="info in dangerProjectInfos" :key="info.id" :project="info" :canEdit="false" />
        </template>
        <template v-else>
          <el-empty description="暂无待解决项目"></el-empty>
        </template>

      </template>
    </DataCard>
    <div class="right-info">
      <DataCard title="组件统计">
        <template #main>
          <div class="static">
            <el-statistic :value="thirdLibraryNum" :value-style="{ fontSize: '36px', color: '#336fff' }">
              <template #title>
                <div style="display: inline-flex; align-items: center">
                  <el-icon style="margin-right: 4px" :size="14">
                    <Tickets />
                  </el-icon>
                  已扫描
                </div>
              </template>
            </el-statistic>
            <el-statistic :value="vulNum" :value-style="{ fontSize: '36px', color: '#336fff' }">
              <template #title>
                <div style="display: inline-flex; align-items: center">
                  <el-icon style="margin-right: 4px" :size="14">
                    <Reading />
                  </el-icon>
                  漏洞组件数
                </div>
              </template>
            </el-statistic>
          </div>
        </template>
      </DataCard>

      <DataCard title="各项编程语言占比">
        <template #main>
          <WChart width="100%" height="250px" :option="languageOption"></WChart>
        </template>
      </DataCard>
    </div>
  </div>

</template>

<script setup lang="ts">
import { ArrowRight, Tickets, Reading, DocumentCopy } from '@element-plus/icons-vue'
import WChart from '@/components/chart/index.vue'
import DataCard from '@/components/DataCard.vue';
import PInfo from '@/components/Project/PInfo.vue';
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
      const statistics: StatisticsInfo = res.data.obj
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

.data-infos {
  display: flex;

  .right-info {
    min-width: 330px;
    width: 30%;
    display: flex;
    flex-direction: column;
  }
}

.static {
  height: 150px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}
</style>
