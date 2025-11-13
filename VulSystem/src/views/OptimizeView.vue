<template>
  <div class="optimize-view-container">
    <!-- 统一的页面头部区域 -->
    <div class="unified-header-section">
      <div class="unified-header-content">
        <!-- 标题部分 -->
        <div class="title-section">
          <el-icon color="#336FFF" size="28" class="title-icon">
            <Setting />
          </el-icon>
          <div class="title-text">
            <h1 class="page-title">{{ $t('optimize.applicationOptimization') }}</h1>
            <p class="page-subtitle">{{ $t('optimize.optimizeAndImprove') }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 参数设置区域 -->
    <div class="content-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon">
            <Tools />
          </el-icon>
          {{ $t('optimize.parameterConfiguration') }}
        </h2>
      </div>
      <div class="section-content">
        <DataSetting
          :threshold-name="stratage?.detectStrategy.endsWith('whiteList') ? $t('optimize.falsePositiveThreshold') : $t('optimize.similarityThreshold')"
          :threshold="stratage?.similarityThreshold ?? 0.5"
          :K="stratage?.maxDetectNums ?? 1"
          @update:threshold="updateThreshold"
          @update:K="updateK"
        />
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="content-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon">
            <Filter />
          </el-icon>
          {{ $t('optimize.modelFilter') }}
        </h2>
      </div>
      <div class="section-content">
        <div class="filter-container">
          <div class="filter-line">
            <div class="filter-label">{{ $t('optimize.modelType') }}</div>
            <ul class="filter-list">
              <li
                v-for="item in modelFilterList"
                :key="item.value"
                @click="choosenFilter.model = item.value"
                :class="{ 'chosen': item.value === choosenFilter.model }"
                class="filter-item"
              >
                {{ item.label }}
              </li>
            </ul>
          </div>
          <div class="filter-line">
            <div class="filter-label">{{ $t('optimize.optimizer') }}</div>
            <ul class="filter-list">
              <li
                v-for="item in optimizeFilterList"
                :key="item.value"
                @click="choosenFilter.optimize = item.value"
                :class="{ 'chosen': item.value === choosenFilter.optimize }"
                class="filter-item"
              >
                {{ item.label }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 模型列表区域 -->
    <div class="content-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon">
            <DataAnalysis />
          </el-icon>
          检测模型
        </h2>
        <div class="model-info">
          <span class="model-count">共 {{ filteredList.length }} 个模型</span>
          <el-tooltip
            class="box-item"
            effect="dark"
            content="提高阈值能提升检测准确率, 但有可能减少预测结果"
            placement="bottom"
          >
            <el-icon class="info-icon">
              <InfoFilled />
            </el-icon>
          </el-tooltip>
        </div>
      </div>
      <div class="section-content">
        <div class="llm-list">
          <LlmInfo
            v-for="llm in filteredList"
            :key="llm.llmName"
            :is-vip="stratage?.isMember == 1"
            :is-chosen="llm.llmName == stratage?.detectStrategy"
            :info="llm"
            @update:name="updateStratageName"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Setting, InfoFilled, Tools, Filter, DataAnalysis } from '@element-plus/icons-vue'
import { computed, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import DataSetting from '@/components/Optimize/DataSetting.vue';
import LlmInfo from '@/components/Optimize/LlmInfo.vue';
import { ModelType, OptimizeType, type CompanyStrategy, type LlmInfoType } from '@/components/Optimize/const';
import { ElMessage } from 'element-plus';
import { changeStrategy, getStrategy } from '@/components/Optimize/service';

const { t } = useI18n()
// import TestTree from '@/components/TestTree.vue';
// const chosenLlmName = ref<string>('VulLibMiner')
const choosenFilter = ref<{ model: 'all' | ModelType, optimize: 'all' | OptimizeType }>({
  model: 'all',
  optimize: 'all'
})
const modelFilterList: Array<{ value: 'all' | ModelType, label: string, }> = [
  {
    value: 'all',
    label: '全部'
  }, {
    value: ModelType.PreTrain,
    label: '预训练模型',
  }, {
    value: ModelType.LLM,
    label: '大语言模型',
  }
]
const optimizeFilterList: Array<{ value: 'all' | OptimizeType, label: string }> = [
  {
    value: 'all',
    label: '全部'
  }, {
    value: OptimizeType.Similarity,
    label: '相似度算法优化器',
  }, {
    value: OptimizeType.WhiteList,
    label: '白名单优化器',
  }, {
    value: OptimizeType.None,
    label: '无'
  }
]

const llmList = ref<LlmInfoType[]>([
  {
    llmName: 'PreTrainModel',
    desc: '利用TF-IDF打分算法结合基于BERT-FNN的PreTrainModel方法进行检测，能够高效识别常见漏洞。',
    accuracy: 0.75,
    falseRate: 0.03,
    modelType: ModelType.PreTrain,
    optimizeType: OptimizeType.None,
  },
  {
    llmName: 'LLM',
    desc: '在PreTrainModel的识别基础上，使用大语言模型（LLM）进行漏洞检测，具有强大的漏洞检测能力。',
    accuracy: 0.85,
    falseRate: 0.01,
    modelType: ModelType.LLM,
    optimizeType: OptimizeType.None,
  },
  {
    llmName: 'LLM-lev',
    desc: '在LLM基础上结合Levenshtein距离相似度匹配算法，与您的企业白名单进行匹配，提升准确率。',
    accuracy: 0.90,
    falseRate: 0.015,
    modelType: ModelType.LLM,
    optimizeType: OptimizeType.Similarity,
  },
  {
    llmName: 'PreTrainModel-lev',
    desc: '在PreTrainModel基础上结合Levenshtein距离相似度匹配算法，与您的企业白名单进行匹配，提升准确率。',
    accuracy: 0.82,
    falseRate: 0.025,
    modelType: ModelType.PreTrain,
    optimizeType: OptimizeType.Similarity,
  },
  {
    llmName: 'LLM-cos',
    desc: '在LLM基础上结合余弦相似度匹配算法，与您的企业白名单进行匹配，提升准确率。',
    accuracy: 0.88,
    falseRate: 0.018,
    infoTag: '误报率较低',
    modelType: ModelType.LLM,
    optimizeType: OptimizeType.Similarity,
  },
  {
    llmName: 'PreTrainModel-cos',
    desc: '在PreTrainModel基础上结合余弦相似度匹配算法，与您的企业白名单进行匹配，提升准确率。',
    accuracy: 0.80,
    falseRate: 0.02,
    infoTag: '误报率较低',
    modelType: ModelType.PreTrain,
    optimizeType: OptimizeType.Similarity,
  },
  {
    llmName: 'LLM-lcs',
    desc: '在LLM基础上结合最长公共子序列（LCS）算法，与您的企业白名单进行匹配，提升准确率。',
    accuracy: 0.87,
    falseRate: 0.017,
    modelType: ModelType.LLM,
    optimizeType: OptimizeType.Similarity,
  },
  {
    llmName: 'PreTrainModel-lcs',
    desc: '在PreTrainModel基础上结合最长公共子序列（LCS）算法，与您的企业白名单进行匹配，提升准确率。',
    accuracy: 0.79,
    falseRate: 0.022,
    modelType: ModelType.PreTrain,
    optimizeType: OptimizeType.Similarity,
  },
  {
    llmName: 'LLM-VulDet',
    desc: '使用大语言模型（LLM）进行漏洞检测，能够检测出具体的版本信息。',
    accuracy: 0.79,
    falseRate: 0.022,
    infoTag: '版本检测',
    needVip: true,
    modelType: ModelType.LLM,
    optimizeType: OptimizeType.None,
  },
  {
    llmName: 'LLM-whiteList',
    desc: '在LLM检测的流程中，定制化添加您的企业白名单，确保高准确率。通过阈值过滤的方式降低误报率。',
    accuracy: 0.92,
    falseRate: 0.01,
    infoTag: '准确率较高',
    needVip: true,
    modelType: ModelType.LLM,
    optimizeType: OptimizeType.WhiteList,
  },
  {
    llmName: 'PreTrainModel-whiteList',
    desc: '在PreTrainModel检测的流程中，定制化添加您的企业白名单，确保高准确率。通过阈值过滤的方式降低误报率。',
    accuracy: 0.83,
    falseRate: 0.02,
    infoTag: '准确率较高',
    needVip: true,
    modelType: ModelType.PreTrain,
    optimizeType: OptimizeType.WhiteList,
  }
])
// 定义响应式变量
// const threshold = ref<number>(0.5);
// const K = ref<number>(3);

const filteredList = computed(() => {
  const resList = llmList.value
    .filter(({ modelType }) => {
      if (choosenFilter.value.model == 'all') {
        return true;
      } else {
        return choosenFilter.value.model == modelType
      }
    })
    .filter(({ optimizeType }) => {
      const { optimize } = choosenFilter.value;
      if (optimize == 'all') {
        return true;
      } else {
        return optimize == optimizeType
      }
    })

  const index = resList.findIndex(item => item.llmName === stratage.value?.detectStrategy);
  if (index !== -1) {
    const [itemToMove] = resList.splice(index, 1); // 删除原数组中的该项
    resList.unshift(itemToMove); // 将删除的项插入数组最前面
  }
  return resList;
})
const stratage = ref<CompanyStrategy>({
  similarityThreshold: 0.7,
  maxDetectNums: 3,
  detectStrategy: "LLM",
  isMember: 1,
})
onMounted(() => {
  getStrategy()
    .then(res => {
      stratage.value = res.data.obj
    })
})
// 更新阈值的处理函数
const updateThreshold = (value: number) => {
  if (stratage.value) {
    stratage.value.similarityThreshold = value
    changeStratage()
  }

};

// 更新 K 值的处理函数
const updateK = (value: number) => {
  if (stratage.value) {
    stratage.value.maxDetectNums = value
    changeStratage()
  }
};
// 监听 detectStrategy 的变化
watch(
  () => stratage.value?.detectStrategy,
  (newValue) => {
    console.log('change')
    // 将对应策略放到最前面
    const index = llmList.value.findIndex(item => item.llmName === newValue);
    if (index !== -1) {
      const [itemToMove] = llmList.value.splice(index, 1); // 删除原数组中的该项
      llmList.value.unshift(itemToMove); // 将删除的项插入数组最前面
    }
  },
  { immediate: true } // 立即执行一次，确保初始状态正确
);

const updateStratageName = (value: string) => {
  if (stratage.value) {
    stratage.value.detectStrategy = value
    // 将对应策略放到最前面
    // const index = llmList.findIndex(item => item.llmName === value);
    // if (index !== -1) {
    //   const [itemToMove] = llmList.splice(index, 1); // 删除原数组中的该项
    //   llmList.unshift(itemToMove); // 将删除的项插入数组最前面
    // }
    changeStratage()
  }
}

const changeStratage = () => {
  if (stratage.value) {
    changeStrategy(stratage.value)
      .then(() => ElMessage.success(t('common.configUpdated')))
  }
}

</script>

<style scoped>
.optimize-view-container {
  container-name: optimizeView;
  container-type: inline-size;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
}

.optimize-view-container::before {
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

.section-content {
  padding: 32px;
}

/* 筛选区域 */
.filter-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-line {
  display: flex;
  align-items: center;
  gap: 20px;
}

.filter-label {
  min-width: 100px;
  font-size: 15px;
  font-weight: 600;
  color: #475569;
}

.filter-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.filter-item {
  padding: 10px 20px;
  border: 2px solid #e2e8f0;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  color: #64748b;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.filter-item:hover {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.25);
}

.filter-item.chosen {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 模型信息 */
.model-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-count {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  padding: 8px 16px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
}

.info-icon {
  font-size: 20px;
  color: #667eea;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.info-icon:hover {
  transform: scale(1.1);
}

/* 模型列表 */
.llm-list {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

/* 响应式设计 */
@container optimizeView (max-width: 1200px) {
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

@container optimizeView (max-width: 1000px) {
  .llm-list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@container optimizeView (max-width: 931px) {
  .unified-header-section {
    margin: 12px;
    padding: 20px;
  }

  .content-section {
    margin: 0 12px 12px;
  }

  .section-content {
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

  .filter-line {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-label {
    margin-bottom: 8px;
  }
}

@container optimizeView (max-width: 700px) {
  .llm-list {
    grid-template-columns: repeat(1, 1fr);
  }
}

@container optimizeView (max-width: 640px) {
  .unified-header-section {
    margin: 8px;
    padding: 16px;
  }

  .content-section {
    margin: 0 8px 8px;
  }

  .section-content {
    padding: 16px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .model-info {
    width: 100%;
    justify-content: space-between;
  }

  .page-title {
    font-size: 20px;
  }

  .page-subtitle {
    font-size: 13px;
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

.content-section:nth-child(2) { animation-delay: 0.1s; }
.content-section:nth-child(3) { animation-delay: 0.2s; }
.content-section:nth-child(4) { animation-delay: 0.3s; }
</style>
