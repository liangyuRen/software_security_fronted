<template>
  <div class="projects-view-container">
    <!-- 统一的页面头部区域 -->
    <div class="unified-header-section">
      <div class="unified-header-content">
        <!-- 标题部分 -->
        <div class="title-section">
          <el-icon color="#336FFF" size="28" class="title-icon">
            <DocumentCopy />
          </el-icon>
          <div class="title-text">
            <h1 class="page-title">项目管理</h1>
            <p class="page-subtitle">管理和监控您的项目安全状态</p>
          </div>
        </div>

        <!-- 统计卡片区域 -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon-wrapper risk-icon">
              <el-icon :size="24">
                <Warning />
              </el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">项目风险分布</div>
              <WChart width="100%" height="120px" :option="option"></WChart>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon-wrapper project-icon">
              <el-icon :size="24">
                <Tickets />
              </el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">已上传项目</div>
              <div class="stat-value">{{ projectStatistic?.projectNum || 0 }}</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon-wrapper vuln-icon">
              <el-icon :size="24">
                <Reading />
              </el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">发现漏洞数</div>
              <div class="stat-value">{{ projectStatistic?.vulnerabilityNum || 0 }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 项目列表区域 -->
    <div class="content-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon">
            <Folder />
          </el-icon>
          项目仓库
        </h2>
        <div class="section-actions">
          <el-input
            v-model="searchValue"
            placeholder="搜索项目名称..."
            class="search-input"
            clearable
          >
            <template #prefix>
              <el-icon class="search-icon">
                <Search />
              </el-icon>
            </template>
          </el-input>
          <el-button
            type="primary"
            class="add-project-btn"
            @click="addFormVisible = true"
          >
            <el-icon class="btn-icon">
              <Plus />
            </el-icon>
            新建项目
          </el-button>
        </div>
      </div>

      <div class="projects-content">
        <div v-if="isLoading" class="loading-container">
          <LoadingFrames size="large"></LoadingFrames>
        </div>
        <div v-else-if="filteredProjects.length > 0" class="projects-list">
          <PInfo
            v-for="info in paginatedProjects"
            :key="info.id"
            :project="info"
            @delete="handleDeleteProject"
            @edit="handleEditProject"
            @edit-file="handleEditProject"
          />
          <!-- 分页组件 -->
          <div class="pagination-wrapper" v-if="filteredProjects.length > pageSize">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :small="false"
              :disabled="isLoading"
              :background="true"
              layout="total, sizes, prev, pager, next, jumper"
              :total="filteredProjects.length"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
        <div v-else class="empty-state">
          <el-empty description="暂无项目" :image-size="120" />
        </div>
      </div>
    </div>

    <ProjectForm
      type="add"
      :visible="addFormVisible"
      @cancel="() => addFormVisible = false"
      @confirm="handleAddProject"
      @close="() => addFormVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { Tickets, Reading, Search, DocumentCopy, Warning, Folder, Plus } from '@element-plus/icons-vue'
import WChart from '@/components/chart/index.vue'
import PInfo from '@/components/Project/PInfo.vue';
import { type ProjectInfo } from '@/components/Project/const';
import {onMounted, ref, watch, computed} from 'vue';
import ProjectForm from '@/components/Project/ProjectForm.vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  createProject, deleteProject,
  getProjectList,
  type ProjectCreateResponse,
  type ProjectListResponse, updateProject,
  uploadAndAnalyzeProject,
  getProjectAnalysisStatus,
  type UploadAndAnalyzeResponse,
  type AnalysisStatusResponse
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

/**
 * 处理新项目添加
 * 使用新的统一上传API（uploadAndAnalyzeProject）
 * 上传后启动异步分析，并轮询查询进度
 */
const handleAddProject = (formDataWrapper: any) => {
  // 从表单组件接收FormData
  const formData = formDataWrapper.formData || formDataWrapper;
  const projectInfo = formDataWrapper.projectInfo || formDataWrapper;

  console.log('上传项目信息：', projectInfo);

  // 调用新的统一上传API
  uploadAndAnalyzeProject(formData).then((res: UploadAndAnalyzeResponse) => {
    console.log('上传响应：', res);
    if (res.code === 200) {
      const projectId = res.obj.projectId;
      ElMessage.success('项目上传成功，正在自动分析...');

      // 启动轮询获取分析进度
      monitorProjectAnalysis(projectId);

      // 较早关闭对话框
      addFormVisible.value = false;
    } else {
      ElMessage.error('项目上传失败: ' + res.message);
      addFormVisible.value = false;
    }
  }).catch((err) => {
    console.error('上传失败：', err);
    ElMessage.error('项目上传失败，请检查网络或文件格式');
    addFormVisible.value = false;
  });
}

/**
 * 监控项目分析进度
 * 每2秒轮询一次，直到分析完成或失败
 */
function monitorProjectAnalysis(projectId: number) {
  let pollCount = 0;
  const maxPolls = 90; // 最多轮询90次（90 * 2秒 = 180秒 = 3分钟）
  const pollInterval = 2000; // 2秒轮询一次

  const intervalId = setInterval(async () => {
    if (pollCount >= maxPolls) {
      clearInterval(intervalId);
      ElMessage.warning('分析超时，请稍后在项目详情页查看');
      return;
    }

    try {
      const response: AnalysisStatusResponse = await getProjectAnalysisStatus(projectId);

      if (response.code === 200) {
        const status = response.obj;

        console.log(`[分析进度] 项目${projectId}: ${status.status}，语言: ${status.language}`);

        // 分析完成
        if (status.status === 'completed') {
          clearInterval(intervalId);
          ElMessage.success({
            message: `✅ 分析完成\n检测语言：${status.language}\n` +
                    `组件数：${status.componentCount}\n` +
                    `漏洞数：${status.vulnerabilityCount}\n` +
                    `风险等级：${status.riskLevel}`,
            duration: 5000
          });

          // 刷新项目列表展示最新数据
          const companyId = 1;
          getProjects(companyId);
          return;
        }

        // 分析失败
        if (status.status === 'failed') {
          clearInterval(intervalId);
          ElMessage.error(`❌ 分析失败：${status.message || '未知原因'}`);

          // 仍然刷新列表，显示失败状态的项目
          const companyId = 1;
          getProjects(companyId);
          return;
        }

        // 分析中 - 仅输出日志，不弹出提示
        if (status.status === 'analyzing') {
          console.log(`[进度] 项目${projectId}分析中...`);
        }
      }
    } catch (err) {
      console.error('查询分析状态失败：', err);
      // 继续轮询，不中断
    }

    pollCount++;
  }, pollInterval);
}

const handleEditProject = (project: ProjectInfo) => {
  console.log(project);

  // Build FormData from ProjectInfo
  const formData = new FormData()
  formData.append('id', project.id.toString())
  formData.append('name', project.name)
  formData.append('description', project.description)
  formData.append('riskThreshold', project.risk_threshold.toString())
  if (project.filePath) {
    formData.append('filePath', project.filePath)
  }

  updateProject(formData).then((res: ProjectCreateResponse) => {
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

      // Build FormData from ProjectInfo
      const formData = new FormData()
      formData.append('id', project.id.toString())

      deleteProject(formData).then((res: ProjectCreateResponse) => {
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

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)
const totalProjects = ref(0)

// 计算当前页显示的项目
const paginatedProjects = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredProjects.value.slice(start, end)
})

const filterProjects = () => {
  console.log("1projectInfos.value", projectInfos.value);
  console.log("1filtered",filteredProjects.value);
  if ((searchValue.value ?? '') === '') {
    filteredProjects.value = projectInfos.value;
  } else {
    filteredProjects.value = projectInfos.value.filter((project) => {
      if(project.name?.includes(searchValue.value ?? '')) {
        return true;
      }
    });
  }
  // 搜索时重置到第一页
  currentPage.value = 1;
  console.log("projectInfos.value", projectInfos.value);
  console.log("filtered",filteredProjects.value);
}

// 分页事件处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}
watch(searchValue, filterProjects);
//本地的companyid类型为string,这里要转换
async function getProjects(companyId: number, page?: number) {
  isLoading.value = true;
  const currentPageNum = page || currentPage.value;
  const pageSizeVal = pageSize.value;
  //改动描述：修改companyid的值以确保能加载出项目列表
  companyId=1;

  if (currentPageNum === 1) {
    projectInfos.value = [];
    await getProjectList(1, 1000, companyId).then((res) => { // 获取所有数据用于计算总数
      const data: ProjectListResponse = res;
      if (data.code !== 200) {
        ElMessage.error('获取项目列表失败');
        console.error(data);
        return;
      }
      // Convert Obj[] to ProjectInfo[]
      const transformedProjects: ProjectInfo[] = data.obj.map((obj) => ({
        id: obj.id,
        description: obj.description || '',
        name: obj.name || '',
        risk_level: obj.risk_level || '暂无风险',
        risk_threshold: obj.risk_threshold ? parseInt(obj.risk_threshold, 10) : 0,
        language: 'java', // default value
        companyId: companyId,
        filePath: null,
      }));
      projectInfos.value = transformedProjects;
      totalProjects.value = transformedProjects.length;
      filteredProjects.value = transformedProjects;
    }).catch((err) => {
      console.log(err);
      ElMessage.error('获取项目列表失败');
    });
  } else {
    // 对于其他页面，我们使用已有的数据进行分页
    // 这里假设我们已经在第一次加载时获取了所有数据
  }

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
.projects-view-container {
  container-name: projectsView;
  container-type: inline-size;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
}

.projects-view-container::before {
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
  margin-bottom: 32px;
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

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 24px;
}

.stat-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  padding: 24px;
  border-radius: 16px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.risk-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #ffffff;
}

.project-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: #ffffff;
}

.vuln-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: #ffffff;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.section-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  width: 280px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
}

.search-input :deep(.el-input__wrapper:hover) {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-icon {
  color: #a0aec0;
}

.add-project-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px;
  padding: 10px 24px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.add-project-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.add-project-btn:active {
  transform: translateY(0);
}

.btn-icon {
  font-size: 18px;
}

.projects-content {
  padding: 24px 32px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.projects-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding: 16px 0;
  border-top: 1px solid #f1f5f9;
}

.pagination-wrapper :deep(.el-pagination) {
  --el-pagination-button-bg-color: #ffffff;
  --el-pagination-hover-color: #667eea;
  --el-pagination-active-color: #667eea;
  --el-pagination-bg-color: #ffffff;
  --el-pagination-border-radius: 8px;
}

.pagination-wrapper :deep(.el-pagination .el-pager li) {
  border-radius: 8px;
  margin: 0 2px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.pagination-wrapper :deep(.el-pagination .el-pager li:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
}

.pagination-wrapper :deep(.el-pagination .el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
}

.pagination-wrapper :deep(.el-pagination .btn-prev),
.pagination-wrapper :deep(.el-pagination .btn-next) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.pagination-wrapper :deep(.el-pagination .btn-prev:hover),
.pagination-wrapper :deep(.el-pagination .btn-next:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
}

.pagination-wrapper :deep(.el-pagination .el-pagination__sizes) {
  margin-right: 16px;
}

.pagination-wrapper :deep(.el-pagination .el-select .el-input__wrapper) {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.pagination-wrapper :deep(.el-pagination .el-select .el-input__wrapper:hover) {
  border-color: #667eea;
}

.pagination-wrapper :deep(.el-pagination .el-pagination__jump) {
  margin-left: 16px;
}

.pagination-wrapper :deep(.el-pagination .el-input__wrapper) {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.pagination-wrapper :deep(.el-pagination .el-input__wrapper:hover) {
  border-color: #667eea;
}

.empty-state {
  padding: 60px 0;
}

/* 响应式设计 */
@container projectsView (max-width: 1200px) {
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

@container projectsView (max-width: 931px) {
  .unified-header-section {
    margin: 12px;
    padding: 20px;
  }

  .content-section {
    margin: 0 12px 12px;
  }

  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    padding: 20px;
  }

  .section-actions {
    flex-direction: column;
    width: 100%;
  }

  .search-input {
    width: 100%;
  }

  .add-project-btn {
    width: 100%;
    justify-content: center;
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
    margin-bottom: 24px;
  }

  .title-icon {
    margin-bottom: 12px;
    margin-right: 0;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}

@container projectsView (max-width: 640px) {
  .unified-header-section {
    margin: 8px;
    padding: 16px;
  }

  .content-section {
    margin: 0 8px 8px;
  }

  .section-header {
    padding: 16px;
  }

  .projects-content {
    padding: 16px;
  }

  .page-title {
    font-size: 20px;
  }

  .page-subtitle {
    font-size: 13px;
  }

  .title-section {
    margin-bottom: 20px;
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
  animation-delay: 0.3s;
  animation-fill-mode: both;
}

.stat-card {
  animation: fadeInUp 0.5s ease-out;
  animation-fill-mode: both;
}

.stat-card:nth-child(1) { animation-delay: 0.1s; }
.stat-card:nth-child(2) { animation-delay: 0.2s; }
.stat-card:nth-child(3) { animation-delay: 0.3s; }
</style>
