<template>
  <el-breadcrumb :separator-icon="ArrowRight" class="bread">
    <el-breadcrumb-item :to="{ path: '/' }">
      <el-icon color="#336FFF" size="14">
        <DocumentCopy />
      </el-icon>
      <span class="bread-item">项目管理</span>
    </el-breadcrumb-item>
    <el-breadcrumb-item>项目信息</el-breadcrumb-item>
  </el-breadcrumb>

  <div class="data-infos">
    <!-- <v-chart ref="mychart1" class="chart"></v-chart> -->
    <DataCard title="项目风险等级分布" width="auto">
      <template #main>
        <WChart width="100%" height="160px" :option="option"></WChart>
      </template>
    </DataCard>
    <DataCard title="项目统计">
      <template #main>
        <div class="static">
          <el-statistic :value="projectStatistic?.projectNum" :value-style="{ fontSize: '36px', color: '#336fff' }">
            <template #title>
              <div style="display: inline-flex; align-items: center">
                <el-icon style="margin-right: 4px" :size="14">
                  <Tickets />
                </el-icon>
                已上传
              </div>
            </template>
          </el-statistic>
          <el-statistic :value="projectStatistic?.vulnerabilityNum"
            :value-style="{ fontSize: '36px', color: '#336fff' }">
            <template #title>
              <div style="display: inline-flex; align-items: center">
                <el-icon style="margin-right: 4px" :size="14">
                  <Reading />
                </el-icon>
                发现漏洞数
              </div>
            </template>
          </el-statistic>
        </div>
      </template>
    </DataCard>
  </div>

  <DataCard title="项目仓库" width="auto">
    <template #right>
      <el-input style="width: 240px;margin-right: 20px;" placeholder="请输入仓库名" v-model="searchValue">
        <template #suffix>
          <el-icon>
            <Search />
          </el-icon>
        </template>
      </el-input>
      <el-button type="primary" color="#336fff" @click="addFormVisible = true;">新建项目</el-button>
    </template>
    <template #main>
      <div v-if="isLoading" style="display: flex; justify-content: center; align-items: center; height: 200px;">
        <LoadingFrames size="large"></LoadingFrames>
      </div>
      <div v-else-if="filteredProjects.length > 0">
        <PInfo v-for="info in filteredProjects" :key="info.id" :project="info" @delete="handleDeleteProject"
          @edit="handleEditProject" @edit-file="handleEditProject"/>
      </div>
      <div v-else>
        <el-empty description="暂无项目"></el-empty>
      </div>
    </template>
  </DataCard>

  <ProjectForm type="add" :visible="addFormVisible" @cancel="() => addFormVisible = false" @confirm="handleAddProject"
    @close="() => addFormVisible = false" />


</template>

<script setup lang="ts">
import { ArrowRight, Tickets, Reading, Search, DocumentCopy } from '@element-plus/icons-vue'
import DataCard from '@/components/DataCard.vue';
import WChart from '@/components/chart/index.vue'
import PInfo from '@/components/Project/PInfo.vue';
import { type ProjectInfo } from '@/components/Project/const';
import {onMounted, ref, watch} from 'vue';
import ProjectForm from '@/components/Project/ProjectForm.vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  createProject, deleteProject,
  getProjectList,
  type ProjectCreateResponse,
  type ProjectListResponse, updateProject
} from "@/components/Project/apis.ts";
import LoadingFrames from "@/components/LoadingFrames.vue";
import { getCompanyStatic, type StatisticsInfo } from '@/components/Statistic/const';

const option = ref({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      // type: 'shadow' // Use shadow pointer
    }
  },
  legend: {
    orient: 'horizontal', // 水平放置
    bottom: '5%', // 放在图表底部
    left: '5%', // 放在中间
    itemGap: 30, // 图例项之间的间距
  },
  grid: {
    left: '3%',
    right: '3%',
    top: '10%', // 可以适当调整顶端留白
    bottom: '20%', // 留出底部空间给图例
    containLabel: false,
    gap: '5%',
  },
  xAxis: {
    type: 'value',
    show: false, // Hide the x-axis
    position: 'bottom',
    // max: 1.2,
    // min: 1,
  },
  yAxis: {
    type: 'category',
    data: ['项目等级风险'],
    show: false // Hide the y-axis
  },
  series: [
    {
      name: '高风险',
      type: 'bar',
      stack: 'total',
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: [5],
      itemStyle: {
        borderRadius: 5,
        // color: '#EE6666' // 设置颜色
        color: '#9045ff'
      },
      barMaxWidth: 45, // 设置柱子的最大宽度，可以控制柱子的整体高度
      // barMinHeight: 50, // 设置柱子的最小高度
      // z: 5
    },
    {
      name: '低风险',
      type: 'bar',
      stack: 'total',
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: [1],
      itemStyle: {
        borderRadius: 5, // Add rounded corners
        // color: '#fac858'
        color: '#e3ebff',
      },
      // barMinHeight: 50, // 设置柱子的最小高度
      // barMaxHeitht: 50,
      // z: 3
    },
    {
      name: '暂无风险',
      type: 'bar',
      stack: 'total',
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: [2],
      itemStyle: {
        borderRadius: 5, // Add rounded corners
        // color: '#91cc75'
        color: '#336fff',
      },
      barCategoryGap: '30%', // 设置柱状图之间的间隔
      // barMinHeight: 50,// 设置柱子的最小高度
      // barMaxHeitht: 50,
      // z: 1,
    },

  ]
});

// project modification
const addFormVisible = ref(false)
const handleAddProject = (newProject: ProjectInfo) => {
  console.log(newProject);

  createProject(newProject).then((res: ProjectCreateResponse) => {
    console.log(res);
    if (res.code === 200) {
      ElMessage({
        message: '成功添加',
        type: 'success',
      })
      // 重新加载项目列表，而不是刷新整个页面
      const companyId = 1;
      getProjects(companyId);
    } else {
      ElMessage({
        message: '添加失败: ' + res.message + ' ' + res.obj,
        type: 'error',
      })
    }
  });
  addFormVisible.value = false;
}

const handleEditProject = (project: ProjectInfo) => {
  console.log(project);

  updateProject(project).then((res: ProjectCreateResponse) => {
    console.log(res);
    if (res.code === 200) {
      ElMessage({
        message: '成功更新',
        type: 'success',
      })
      // 重新加载项目列表，而不是刷新整个页面
      const companyId = 1;
      getProjects(companyId);
    } else {
      ElMessage({
        message: '更新失败: ' + res.message + ' ' + res.obj,
        type: 'error',
      })
    }
  }).catch((err) => {
    console.log(err);
    ElMessage.error('更新失败');
  });
}

const handleDeleteProject = (project: ProjectInfo) => {
  ElMessageBox.confirm('您确定要删除该项目吗?', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
  })
    .then(() => {
      console.log(project);

      deleteProject(project).then((res: ProjectCreateResponse) => {
        console.log(res);
        if (res.code === 200) {
          ElMessage({
            message: '成功删除',
            type: 'success',
          })
          // 重新加载项目列表，而不是刷新整个页面
          const companyId = 1;
          getProjects(companyId);
        } else {
          ElMessage({
            message: '删除失败: ' + res.message + ' ' + res.obj,
            type: 'error',
          })
        }
      }).catch((err) => {
        console.log(err);
        ElMessage.error('删除失败');
      });
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消删除'
      });
    })
}

// loading-frames
const isLoading = ref(true);


// project list
const projectInfos = ref<ProjectInfo[]>([]);
const searchValue = ref('')
const filteredProjects = ref<ProjectInfo[]>([]);

const filterProjects = () => {
  console.log("1projectInfos.value", projectInfos.value);
  console.log("1filtered",filteredProjects.value);
  if ((searchValue.value ?? '') === '') {
    filteredProjects.value = projectInfos.value;
    return;
  }
  filteredProjects.value = projectInfos.value.filter((project) => {
    if(project.name?.includes(searchValue.value ?? '')) {
      return true;
    }
  });
  console.log("projectInfos.value", projectInfos.value);
  console.log("filtered",filteredProjects.value);
}
watch(searchValue, filterProjects);
//本地的companyid类型为string,这里要转换
async function getProjects(companyId: number) {
  isLoading.value = true;
  const page = 1;
  const pageSize = 10;
  //改动描述：修改companyid的值以确保能加载出项目列表
  companyId=1;

  projectInfos.value = [];
  await getProjectList(page, pageSize, companyId).then((res) => {
    const data: ProjectListResponse = res;
    if (data.code !== 200) {
      ElMessage.error('获取项目列表失败');
      console.error(data);
      return;
    }
    projectInfos.value = data.obj;
  }).catch((err) => {
    console.log(err);
    ElMessage.error('获取项目列表失败');
  });

  isLoading.value = false;
}


// project statistic
const projectStatistic = ref<StatisticsInfo>()
onMounted(async () => {
  const companyId =1
  //const companyId = localStorage.getItem('companyId');
  await getProjects(companyId);
  filterProjects();
  // 获取统计信息
  getCompanyStatic()
    .then(res => {
      const statistics: StatisticsInfo = res.data.obj
      console.log('statistics:', statistics);
      projectStatistic.value = statistics
      // 项目风险等级分布
      const newOptionSeries = [
        {
          name: '高风险',
          type: 'bar',
          stack: 'total',
          label: {
            show: statistics.highRiskNum != 0
            // show: true
          },
          emphasis: {
            focus: 'series'
          },
          data: [statistics.highRiskNum],
          itemStyle: {
            borderRadius: 5,
            // color: '#EE6666' // 设置颜色
            color: '#9045ff'
          },
          barMaxWidth: 45, // 设置柱子的最大宽度，可以控制柱子的整体高度
          // barMinHeight: 50, // 设置柱子的最小高度
          barMaxHeight: 30
          // z: 3,
        },
        {
          name: '低风险',
          type: 'bar',
          stack: 'total',
          label: {
            // show: true
            show: statistics.lowRiskNum != 0
          },
          emphasis: {
            focus: 'series'
          },
          data: [statistics.lowRiskNum],
          itemStyle: {
            borderRadius: 5, // Add rounded corners
            // color: '#fac858'
            color: '#2967ff',
          },
          barMinHeight: 5, // 设置柱子的最小高度
          // z: 2,
        },
        {
          name: '暂无风险',
          type: 'bar',
          stack: 'total',
          label: {
            show: statistics.noRiskNum != 0
            // show: true
          },
          emphasis: {
            focus: 'series'
          },
          data: [statistics.noRiskNum],
          // data: 5,
          itemStyle: {
            borderRadius: 5, // Add rounded corners
            // color: '#91cc75'
            color: '#1c9a00',
          },
          barCategoryGap: '30%', // 设置柱状图之间的间隔
          barMinHeight: 50, // 设置柱子的最小高度
        },
      ]
      option.value = {
        ...option.value,
        series: newOptionSeries
      }

    })
})
</script>

<style scoped>
.bread {
  margin: 15px;

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
}

.chart {
  min-height: 200px;
}

.static {
  height: 150px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}
</style>
