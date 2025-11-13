<template>
  <el-breadcrumb :separator-icon="ArrowRight" class="bread">
    <el-breadcrumb-item :to="{ path: '/' }">
      <el-icon color="#336FFF" size="14">
        <DocumentCopy />
      </el-icon>
      <span class="bread-item">{{ $t('menu.projectManagement') }}</span>
    </el-breadcrumb-item>
    <el-breadcrumb-item :to="{ path: '/projects/info' }">{{ $t('menu.projectInfo') }}</el-breadcrumb-item>
    <el-breadcrumb-item v-if="projectInfo && projectInfo.projectName">{{ projectInfo.projectName }}</el-breadcrumb-item>
  </el-breadcrumb>
  <div class="data-infos">
    <!-- <v-chart ref="mychart1" class="chart"></v-chart> -->
    <DataCard :title="$t('projectsDetail.vulnerabilityDistribution')" width="auto">
      <template #main>
        <WChart width="100%" height="200px" :option="option" ref="mychart"></WChart>
      </template>
    </DataCard>
    <DataCard :title="$t('projectsDetail.projectBasicInfo')">
      <template #main>
        <el-descriptions title="" :column="2" border style="margin-top: 15px;" v-if="projectInfo">
          <el-descriptions-item :label="$t('projectsDetail.repositoryName')" :span="2">{{ projectInfo.projectName }}</el-descriptions-item>
          <el-descriptions-item :label="$t('projectsDetail.repositoryDescription')" :span="2">{{ projectInfo.projectDescription }}</el-descriptions-item>
          <el-descriptions-item :label="$t('projectsDetail.createTime')">{{ timeFormatter(projectInfo.createTime) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('projectsDetail.latestScanTime')">{{ timeFormatter(projectInfo.lastScanTime) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('projectsDetail.detectionThreshold')">
            {{ projectInfo.riskThreshold ?? 0.45 }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('projectsDetail.projectLanguage')">
            {{ projectInfo.language ?? 'java' }}
          </el-descriptions-item>
        </el-descriptions>
      </template>
    </DataCard>
  </div>
  <DataCard :title="$t('projectsDetail.componentAnalysis')" width="auto">
    <template #right>
      <div style="display: flex; align-items: center; gap: 15px;">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button value="tree">
            <el-icon><Files /></el-icon>
            {{ $t('projectsDetail.treeView') }}
          </el-radio-button>
          <el-radio-button value="list">
            <el-icon><List /></el-icon>
            {{ $t('projectsDetail.listView') }}
          </el-radio-button>
        </el-radio-group>
        <!-- <el-input style="width: 240px;margin-right: 20px;" placeholder="请输入组件名称">
          <template #suffix>
            <el-icon>
              <Search />
            </el-icon>
          </template>
        </el-input> -->
        <SbomForm :project-name="projectInfo?.projectName || ''" :project-id="projectInfo?.id || 1" />
      </div>
    </template>
    <template #main>
      <div v-if="isTreeLoading" style="display: flex; justify-content: center; align-items: center; height: 200px;">
        <LoadingFrames size="large"></LoadingFrames>
      </div>
      <template v-else>
        <!-- Tree View -->
        <div v-if="viewMode === 'tree'" class="tree-container">
          <!-- <el-tree :data="treeData" node-key="id" default-expand-all :props="{ class: 'custom-node' }" /> -->
          <el-tree :data="treeData" node-key="id" default-expand-all :props="{ class: 'custom-node' }">
            <template #default="{ node, data }">
              <span v-if="!node.isLeaf" style="display: flex; align-items: center;">
                <el-icon v-if="node.expanded" style="margin: 0 6px 0 0px;" size="16">
                  <Folder />
                </el-icon>
                <!-- <el-icon v-else style="margin: 0 6px 0 0px;" size="16">
                  <Folder />
                </el-icon> -->
                <el-icon v-else style="margin: 0 6px 0 0px;" size="16">
                  <Files />
                </el-icon>
                {{ node.label }}
              </span>

              <span v-else style="display: flex; align-items: center;">
                <el-icon style="margin: 0 6px 0 0px;" size="16">
                  <Document />
                </el-icon>
                {{ node.label }}
              </span>
            </template>

          </el-tree>
        </div>

        <!-- List View -->
        <div v-else class="list-container">
          <el-table :data="flattenedListData" stripe style="width: 100%">
            <el-table-column prop="name" :label="$t('projectsDetail.componentName')" min-width="200">
              <template #default="{ row }">
                <div style="display: flex; align-items: center;">
                  <el-icon style="margin: 0 8px 0 0px;" size="16">
                    <Document />
                  </el-icon>
                  {{ row.name }}
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="version" :label="$t('projectsDetail.version')" width="120" />
            <el-table-column prop="vendor" :label="$t('projectsDetail.supplier')" width="150" />
            <el-table-column prop="language" :label="$t('projectsDetail.language')" width="100" />
            <el-table-column prop="level" :label="$t('projectsDetail.level')" width="80" />
          </el-table>
        </div>
      </template>

    </template>
  </DataCard>
  <DataCard :title="$t('projectsDetail.issueList')" width="auto">
    <template #main>
      <template v-if="dangerList.length > 0">
        <DangerCard v-for="danger in dangerList" :key="danger.id" :info="danger" @refresh="getProjectDetail" />
      </template>
      <template v-else>
        <el-empty :description="$t('common.noIssuesDetected')"></el-empty>
      </template>
    </template>
  </DataCard>
</template>

<script setup lang="ts">
import { ArrowRight, DocumentCopy, Document, Folder, Files, List } from '@element-plus/icons-vue'
import WChart from '@/components/chart/index.vue'
import DataCard from '@/components/DataCard.vue';
import SbomForm from '@/components/ProjectsDetail/SbomForm.vue';
import { type ProjectInfoDetail } from '@/components/Project/const';
import { onMounted, ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { DangerInfo } from '@/components/Danger/const';
import { api } from './service';
import DangerCard from '@/components/ProjectsDetail/DangerCard.vue';
import { getSbomFile } from '@/components/ProjectsDetail/service';
import type { SbomItem, SbomResponse } from '@/components/ProjectsDetail/const';
import { ElMessage } from 'element-plus';
const { t } = useI18n()

const props = defineProps<{
  projectId: number | string
}>();

// Computed properties for chart labels
const riskLabels = computed(() => [
  t('projects.high').charAt(0), // 高 -> H, High -> H
  t('projects.medium').charAt(0), // 中 -> M, Medium -> M
  t('projects.low').charAt(0) // 低 -> L, Low -> L
])

// 确保projectId是number类型
const projectId = computed(() => Number(props.projectId))
const timeFormatter = (dateString: string) => {
  // 将字符串转换为 Date 对象
  const date = new Date(dateString);

  // 获取年份、月份和日期
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0'); // 月份是0-11，+1后格式化为2位数
  const day = String(date.getDate()).padStart(2, '0'); // 获取日期并格式化为2位数

  // 将结果拼接为 "year-month-date" 格式
  const formattedDate = `${year}-${month}-${day}`;

  console.log(formattedDate); // 输出: "2025-02-13"
  return formattedDate
}
const projectInfo = ref<ProjectInfoDetail>();
const dangerList = ref<DangerInfo[]>([])
const mychart = ref()
const option = ref({
  xAxis: {
    type: 'category',
    data: riskLabels.value,
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [
        {
          value: projectInfo.value?.highRiskNum ?? 0,
          label: {
            position: 'top',
            show: true
          },
          itemStyle: {
            borderRadius: 5,
            color: '#ec4899'
          },
        },
        {
          value: projectInfo.value?.midRiskNum ?? 0,
          label: {
            position: 'top',
            show: true
          },
          itemStyle: {
            borderRadius: 5,
            color: '#8b5cf6'
          }
        },
        {
          value: projectInfo.value?.lowRiskNum ?? 0,
          label: {
            show: true,
            position: 'top',

          },
          itemStyle: {
            borderRadius: 5,
            color: '#10b981'
          }
        },
      ],
      type: 'bar',
      barWidth: 25
    }
  ]
});

const getProjectDetail = () => {
  api.getProjectDetail(projectId.value)
    .then(res => {
      projectInfo.value = res.data.obj
      const newOptionSeries = [{
        data: [
          {
            value: projectInfo.value?.highRiskNum ?? 0,
            label: {
              position: 'top',
              show: true
            },
            itemStyle: {
              borderRadius: 5,
              color: '#ec4899'
            },
          },
          {
            value: projectInfo.value?.midRiskNum ?? 0,
            label: {
              position: 'top',
              show: true
            },
            itemStyle: {
              borderRadius: 5,
              color: '#8b5cf6'
            }
          },
          {
            value: projectInfo.value?.lowRiskNum ?? 0,
            label: {
              show: true,
              position: 'top',

            },
            itemStyle: {
              borderRadius: 5,
              color: '#10b981'
            }
          },
        ],
        type: 'bar',
        barWidth: 25
      }]

      option.value = {
        ...option.value,
        xAxis: {
          type: 'category',
          data: riskLabels.value,
        },
        series: newOptionSeries,
      };
      // if (mychart.value) {
      //   mychart.value.setData(option.value)
      // }
      console.log(option.value)

    })
}

// 转换函数
const convertSbomToTree = (sbomItems: SbomItem[]): Tree[] => {
  return sbomItems
  //.filter(item => item.name) // 只过滤掉 name 为空的项
    .map(item => {
      // 创建 Tree 对象
      let label_name: string = 'default'
      if (item.vendor && item.name) {
        label_name = item.vendor + ':' + item.name
      }
      if (!item.vendor && item.name) {
        label_name = item.name
      }
      if (!item.name && item.paths) {
        label_name = item.paths[0]
      }

      const treeItem: Tree = {
        id: item.id,
        label: label_name,
        children: item.children ? convertSbomToTree(item.children) : undefined // 如果有 children，则递归转换
      };
      return treeItem;
    });
};

interface Tree {
  id: string
  label?: string
  children?: Tree[]
}

const treeData = ref<Tree[]>()
const isTreeLoading = ref<boolean>(false)
const viewMode = ref<'tree' | 'list'>('tree')
const sbomData = ref<SbomItem[]>([])

// Flatten SBOM data for list view
interface FlatListItem {
  name: string
  version: string
  vendor: string
  language: string
  level: number
}

const flattenedListData = computed<FlatListItem[]>(() => {
  if (!sbomData.value.length) return []

  const result: FlatListItem[] = []

  const flatten = (items: SbomItem[], level: number = 0) => {
    items.forEach(item => {
      if (item.name && item.version) {
        result.push({
          name: item.vendor ? `${item.vendor}:${item.name}` : item.name,
          version: item.version || 'N/A',
          vendor: item.vendor || 'N/A',
          language: item.language || 'N/A',
          level: level
        })
      }

      if (item.children && item.children.length > 0) {
        flatten(item.children, level + 1)
      }
    })
  }

  flatten(sbomData.value)
  return result
})
onMounted(() => {
  getProjectDetail()

  isTreeLoading.value = true
  getSbomFile(projectId.value, '.json', 'sbom')
    .then(res => {
      // 创建一个FileReader来读取Blob
      const reader = new FileReader();

      reader.onload = (event) => {
        try {
          // 读取结果为文本
          const text = event.target?.result;
          if (text) {
            // 解析为JSON对象
            const sbomRes: SbomResponse = JSON.parse(text as string);
            const sbomItem: SbomItem[] = sbomRes.children ?? [];

            // 处理sbomItem对象，例如打印或访问其中的属性
            console.log(sbomItem);
            sbomData.value = sbomItem
            treeData.value = convertSbomToTree(sbomItem)
            // 访问特定属性，例如：sbomItem.someProperty
            // alert(sbomItem.someProperty); // 具体属性根据实际需求来获取
            isTreeLoading.value = false
          }


        } catch (jsonError) {
          console.error('解析JSON失败:', jsonError)
        }
      };

      // 开始读取Blob对象
      reader.readAsText(res.data); // 读取Blob为文本字符串
    })
    .catch(err => {
      console.log('获取sbom结构出错', err)
      ElMessage.error(t('common.error'))
    })
    .finally(() => isTreeLoading.value = false)
  api.getVulList(projectId.value)
    .then(res => {
      dangerList.value = res.data.obj
    })
})





</script>

<style>
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

.tree-container {
  margin: 15px;
  width: 60%;

  .custom-node {

    .el-icon svg {
      color: #336fff
    }
  }

  .custom-node>.el-tree-node__content {
    font-size: 16px;
    padding: 10px 0;
    margin: 3px 0;
    border-bottom: 1px solid #e4e4e4c2;
  }

}

.list-container {
  margin: 15px;

  .el-table {
    font-size: 14px;

    .el-table__row {
      &:hover {
        background-color: #f5f7fa;
      }
    }

    .el-icon svg {
      color: #336fff;
    }
  }
}
</style>
