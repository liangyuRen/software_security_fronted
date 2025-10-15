<template>
  <el-breadcrumb :separator-icon="ArrowRight" class="bread">
    <el-breadcrumb-item :to="{ path: '/' }">
      <el-icon color="#336FFF" size="14">
        <DocumentCopy />
      </el-icon>
      <span class="bread-item">项目管理</span>
    </el-breadcrumb-item>
    <el-breadcrumb-item :to="{ path: '/projects/info' }">项目信息</el-breadcrumb-item>
    <el-breadcrumb-item v-if="projectInfo && projectInfo.projectName">{{ projectInfo.projectName }}</el-breadcrumb-item>
  </el-breadcrumb>
  <div class="data-infos">
    <!-- <v-chart ref="mychart1" class="chart"></v-chart> -->
    <DataCard title="漏洞分布" width="auto">
      <template #main>
        <WChart width="100%" height="200px" :option="option" ref="mychart"></WChart>
      </template>
    </DataCard>
    <DataCard title="项目基础信息">
      <template #main>
        <el-descriptions title="" :column="2" border style="margin-top: 15px;" v-if="projectInfo">
          <el-descriptions-item label="仓库名" :span="2">{{ projectInfo.projectName }}</el-descriptions-item>
          <el-descriptions-item label="仓库描述" :span="2">{{ projectInfo.projectDescription }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ timeFormatter(projectInfo.createTime) }}</el-descriptions-item>
          <el-descriptions-item label="最新扫描时间">{{ timeFormatter(projectInfo.lastScanTime) }}</el-descriptions-item>
          <el-descriptions-item label="检测标准阈值">
            {{ projectInfo.riskThreshold ?? 0.45 }}
          </el-descriptions-item>
          <el-descriptions-item label="项目语言">
            {{ projectInfo.language ?? 'java' }}
          </el-descriptions-item>
        </el-descriptions>
      </template>
    </DataCard>
  </div>
  <DataCard title="组件分析" width="auto">
    <template #right>
      <!-- <el-input style="width: 240px;margin-right: 20px;" placeholder="请输入组件名称">
        <template #suffix>
          <el-icon>
            <Search />
          </el-icon>
        </template>
  </el-input> -->
      <SbomForm :project-name="projectInfo?.projectName || ''" :project-id="projectInfo?.id || 1" />
    </template>
    <template #main>
      <div v-if="isTreeLoading" style="display: flex; justify-content: center; align-items: center; height: 200px;">
        <LoadingFrames size="large"></LoadingFrames>
      </div>
      <template v-else>
        <div class="tree-container">
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
      </template>

    </template>
  </DataCard>
  <DataCard title="问题列表" width="auto">
    <template #main>
      <template v-if="dangerList.length > 0">
        <DangerCard v-for="danger in dangerList" :key="danger.id" :info="danger" @refresh="getProjectDetail" />
      </template>
      <template v-else>
        <el-empty description="该项目暂未检测到问题"></el-empty>
      </template>
    </template>
  </DataCard>
</template>

<script setup lang="ts">
import { ArrowRight, DocumentCopy, Document, Folder, Files } from '@element-plus/icons-vue'
import WChart from '@/components/chart/index.vue'
import DataCard from '@/components/DataCard.vue';
import SbomForm from '@/components/ProjectsDetail/SbomForm.vue';
import { type ProjectInfoDetail } from '@/components/Project/const';
import { onMounted, ref } from 'vue';
import type { DangerInfo } from '@/components/Danger/const';
import { api } from './service';
import DangerCard from '@/components/ProjectsDetail/DangerCard.vue';
import { getSbomFile } from '@/components/ProjectsDetail/service';
import type { SbomItem, SbomResponse } from '@/components/ProjectsDetail/const';
import { ElMessage } from 'element-plus';
const props = defineProps<{
  projectId: number
}>();
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
    data: ['高', '中', '低'],
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
  api.getProjectDetail(props.projectId)
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
    .filter(item => item.vendor && item.name) // 过滤掉 label 和 name 为空的项
    .map(item => {
      // 创建 Tree 对象
      // 创建 Tree 对象
      let label_name: string = 'undefined'
      if (item.vendor && item.name) {
        label_name = item.vendor + ':' + item.name
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
onMounted(() => {
  getProjectDetail()

  isTreeLoading.value = true
  getSbomFile(props.projectId, '.json', 'sbom')
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
      ElMessage.error('获取sbom结构失败')
    })
    .finally(() => isTreeLoading.value = false)
  api.getVulList(props.projectId)
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
</style>
