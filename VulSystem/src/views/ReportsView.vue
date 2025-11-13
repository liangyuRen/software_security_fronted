<template>
  <div class="report-view-container">
    <!-- 合并的页面头部和搜索筛选区域 -->
    <div class="unified-header-section">
      <div class="unified-header-content">
        <!-- 标题部分 -->
        <div class="title-section">
          <el-icon color="#336FFF" size="28" class="title-icon">
            <DataLine />
          </el-icon>
          <div class="title-text">
            <h1 class="page-title">{{ $t('reports.vulnerabilityReports') }}</h1>
            <p class="page-subtitle">{{ $t('reports.searchAndFilter') }}</p>
          </div>
        </div>

        <!-- 搜索和筛选部分 -->
        <div class="search-filters-row">
          <div class="search-input-wrapper">
            <el-input
              v-model="searchQuery"
              :placeholder="$t('reports.searchVulnerability')"
              class="search-input"
              size="large"
              clearable
            >
              <template #prefix>
                <el-icon class="search-icon">
                  <Search />
                </el-icon>
              </template>
            </el-input>
          </div>

          <div class="filter-item">
            <label class="filter-label">{{ $t('projects.riskLevel') }}</label>
            <el-select
              v-model="selectedRiskLevel"
              :placeholder="$t('projects.allLevels')"
              class="filter-select"
              size="large"
              clearable
              @clear="selectedRiskLevel = ''"
            >
              <el-option
                v-for="item in riskLevelOptions"
                :key="item"
                :label="item"
                :value="item"
              >
                <div class="risk-option">
                  <el-tag
                    :type="item === 'High' ? 'danger' : item === 'Medium' ? 'warning' : 'success'"
                    size="small"
                  >
                    {{ item }}
                  </el-tag>
                </div>
              </el-option>
            </el-select>
          </div>

          <div class="filter-item">
            <label class="filter-label">{{ $t('projects.timeRange') }}</label>
            <el-date-picker
              v-model="selectedTime"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              class="filter-date"
              size="large"
              clearable
              @clear="selectedTime=''"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-section">
      <LoadingFrames v-if="isLoading" class="loading-container"/>
      <div v-else class="report-content">
        <ReportList
          :reportInfoList="reportList"
          :search-query="searchQuery"
          :current-page="currentPage"
          :total-items="totalItems"
          :total-pages="totalPages"
          :filtered-reports="filteredReports"
          :is-filtered="isFiltered"
          @update:currentPage="currentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ReportInfo } from '@/components/Danger/const';
import ReportList from '@/components/Danger/ReportList.vue';
import { ArrowRight, DataLine, Search } from '@element-plus/icons-vue'
import {ref, onMounted, watch, type Ref, computed} from 'vue';
import {
  getFilteredVulnerabilityReport,
  getVulnerabilityReportList,
  getVulnerabilityReportSearch,
  type VulnerabilityReportListResponse, type VulnerabilityReportSearchResponse
} from "@/components/Danger/apis.ts";
import LoadingFrames from "@/components/LoadingFrames.vue";
import {dayjs} from "element-plus";

const searchQuery = ref('')
const selectedRiskLevel = ref('')
const riskLevelOptions = ['Low', 'Medium', 'High']
const selectedTime = ref([])

const reportList = ref<ReportInfo[]>([]);
const currentPage = ref(1);
const totalPages = ref(0);
const totalItems = ref(0);

// loading-frames
const isLoading = ref(true);

// report list
function currentChange(page: number) {
  currentPage.value = page;
  getReports(page);
}

async function getReports(currentPage: number) {
  isLoading.value = true;
  const pageSize = 10;
  reportList.value = [];
  await getVulnerabilityReportList(currentPage, pageSize).then((res) => {
    const data:VulnerabilityReportListResponse = res;
    totalPages.value = data.obj.pages;
    totalItems.value = data.obj.total;
    for(let i=0; i<data.obj.records.length; i++) {
        const report = data.obj.records[i];
        reportList.value.push({
          reportName: report.vulnerabilityName,
          reportDesc: report.description,
          reportId: report.cveId,
          time: report.disclosureTime,
          riskLevel: report.riskLevel,
          ref: report.referenceLink
        });
    }
    console.log(reportList.value);
  });
  isLoading.value = false;
}

// is in filter mode
const isFiltered = computed(() => {
  return (selectedRiskLevel.value ?? '') !== '' || ((selectedTime.value[0] ?? '') !== '' && (selectedTime.value[1] ?? '') !== '') || (searchQuery.value ?? '') !== '';
});

// search
const filteredReports = ref([])

function debounce<T extends (...args: never[]) => Promise<void> | void>(
  fn: T,
  delay: number,
  isLoadingRef: Ref<boolean>
): T {
  let timeoutId: ReturnType<typeof setTimeout>;
  return function (this: never, ...args: never[]) {
    clearTimeout(timeoutId);
    isLoadingRef.value = true;
    timeoutId = setTimeout(async () => {
      try {
        await fn.apply(this, args); // 等待异步操作完成
      } finally {
        isLoadingRef.value = false; // 无论如何都更新状态
      }
    }, delay);
  } as T;
}

async function searchReports(keyword: string) {
  filteredReports.value = [];
  isLoading.value = true;
  await getVulnerabilityReportSearch(keyword).then((res) => {
    const data:VulnerabilityReportSearchResponse = res;
    for(let i=0; i<data.obj.length; i++) {
        const report = data.obj[i];
      filteredReports.value.push({
          reportName: report.vulnerabilityName,
          reportDesc: report.description,
          reportId: report.cveId,
          time: report.disclosureTime,
          riskLevel: report.riskLevel,
          ref: report.referenceLink
        });
    }
    console.log(filteredReports.value);
  });
  isLoading.value = false;
}
const debouncedSearch = debounce(async (query: string) => {
  if ((query ?? '') !== '') {
    await searchReports(query);
  }
}, 500, isLoading); // 500ms debounce time


// filter
async function filterReports(riskLevel: string, startTime: string, endTime: string) {
  if(!((riskLevel ?? '') !== '' || ((startTime ?? '') !== '' && (endTime ?? '') !== ''))) {
    return;
  }
  isLoading.value = true;
  const TIME_FORMAT = 'YYYY-MM-DD';
  const formattedStartTime = startTime ? dayjs(startTime).format(TIME_FORMAT) : '';
  const formattedEndTime = endTime ? dayjs(endTime).format(TIME_FORMAT) : '';
  filteredReports.value = [];
  await getFilteredVulnerabilityReport(riskLevel, formattedStartTime, formattedEndTime).then((res) => {
    const data:VulnerabilityReportSearchResponse = res;
    console.log(data);
    for(let i=0; i<data.obj.length; i++) {
        const report = data.obj[i];
        filteredReports.value.push({
            reportName: report.vulnerabilityName,
            reportDesc: report.description,
            reportId: report.cveId,
            time: report.disclosureTime,
            riskLevel: report.riskLevel,
            ref: report.referenceLink
        });
    }
    console.log(filteredReports.value);
  });
  isLoading.value = false;
}

watch([selectedRiskLevel, selectedTime], ([riskLevel, time]) => {
  if ((riskLevel ?? '') === '' && ((time[0] ?? '') === '' && (time[1] ?? '') === '')) {
    return;
  }
  searchQuery.value = '';
  filterReports(riskLevel, time[0], time[1]);
});

watch(searchQuery, (newQuery) => {
  if ((newQuery ?? '') === '') {
    return;
  }
  selectedRiskLevel.value = '';
  selectedTime.value = '';
  debouncedSearch(newQuery);
});

onMounted(() => {
  getReports(currentPage.value);
})

</script>

<style scoped>
.report-view-container {
  container-name: reportsView;
  container-type: inline-size;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
}

.report-view-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 0;
}

/* 统一的页面头部和搜索筛选区域 */
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

.search-filters-row {
  display: flex;
  gap: 24px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.search-input-wrapper {
  flex: 1;
  min-width: 300px;
  max-width: 500px;
}

.search-input {
  width: 100%;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.search-input :deep(.el-input__wrapper:hover) {
  border-color: #667eea;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-icon {
  color: #a0aec0;
  font-size: 18px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 160px;
}

.filter-label {
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 4px;
}

.filter-select,
.filter-date {
  width: 160px;
}

.filter-select :deep(.el-input__wrapper),
.filter-date :deep(.el-input__wrapper) {
  border-radius: 10px;
  padding: 10px 14px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
}

.filter-select :deep(.el-input__wrapper:hover),
.filter-date :deep(.el-input__wrapper:hover) {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.filter-select :deep(.el-input__wrapper.is-focus),
.filter-date :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.risk-option {
  display: flex;
  align-items: center;
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

.report-content {
  padding: 0;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  padding: 40px;
}

/* 响应式设计 */
@container reportsView (max-width: 1200px) {
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

@container reportsView (max-width: 931px) {
  .unified-header-section {
    margin: 12px;
    padding: 20px;
  }

  .content-section {
    margin: 0 12px 12px;
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

  .search-filters-row {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .search-input-wrapper {
    min-width: 100%;
    max-width: 100%;
  }

  .filter-item {
    width: 100%;
  }

  .filter-select,
  .filter-date {
    width: 100%;
  }
}

@container reportsView (max-width: 640px) {
  .unified-header-section {
    margin: 8px;
    padding: 16px;
  }

  .content-section {
    margin: 0 8px 8px;
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

  .title-icon {
    size: 20px;
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
}

/* 滚动条样式 */
:deep(.el-scrollbar__bar) {
  opacity: 0.3;
  transition: opacity 0.3s;
}

:deep(.el-scrollbar__bar:hover) {
  opacity: 0.6;
}
</style>
