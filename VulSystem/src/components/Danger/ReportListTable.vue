<script setup lang="ts">

import {getSourceIcon, getSourceName} from "@/utils/parseSource.ts";
import HighlightSearch from "@/components/text/HighlightSearch.vue";
import type {ReportInfo} from "@/components/Danger/const.ts";
import { ref } from "vue";

const props = defineProps<{
  paginatedList: ReportInfo[],
  searchQuery: string
}>()

// 详情对话框相关
const descriptionDialogVisible = ref(false);
const selectedReport = ref<ReportInfo | null>(null);

const showDescription = (report: ReportInfo) => {
  selectedReport.value = report;
  descriptionDialogVisible.value = true;
};

</script>

<template>
  <div>
    <table class="danger-card-table" v-if="paginatedList.length > 0">
      <thead>
      <tr>
        <th class="id">漏洞 ID</th>
        <th class="name">漏洞名称与详情</th>
        <th class="time">披露时间</th>
        <th class="level">风险等级</th>
        <th class="ref">报告来源</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="item in props.paginatedList" :key="item.reportId">
        <td class="id">
          <HighlightSearch
            :text="item.reportId"
            :highlight="props.searchQuery"
          />
        </td>
        <td class="name">
          <div class="name-container">
            <HighlightSearch
              :text="item.reportName"
              :highlight="props.searchQuery"
            />
            <div class="details-icon" @click="showDescription(item)">
              <span>详情</span>
            </div>
          </div>
        </td>
        <td class="time">{{ item.time }}</td>
        <td class="level">
          <el-tag type="success" v-if="item.riskLevel==='Low'">{{item.riskLevel}}</el-tag>
          <el-tag type="warning" v-else-if="item.riskLevel==='Medium'">{{item.riskLevel}}</el-tag>
          <el-tag type="danger" v-else-if="item.riskLevel==='High'">{{item.riskLevel}}</el-tag>
        </td>
        <td class="ref">
          <a :href="item.ref" target="_blank" class="ref-item-container">
            <div class="ref-item">
              <img :src="getSourceIcon(item.ref)" alt="source" />
              <span>{{getSourceName(item.ref)}}</span>
            </div>
          </a>
        </td>
      </tr>
      </tbody>
    </table>
    <div v-else>
      <el-empty description="暂无数据" :image-size="120"/>
    </div>

    <!-- 漏洞详情对话框 -->
    <el-dialog
      v-model="descriptionDialogVisible"
      title="漏洞详情描述"
      width="70%"
      class="description-dialog"
    >
      <div v-if="selectedReport" class="description-content">
        <div class="detail-section">
          <div class="detail-label">漏洞 ID</div>
          <div class="detail-value">{{ selectedReport.reportId }}</div>
        </div>

        <div class="detail-section">
          <div class="detail-label">漏洞名称</div>
          <div class="detail-value">{{ selectedReport.reportName }}</div>
        </div>

        <div class="detail-section">
          <div class="detail-label">风险等级</div>
          <div class="detail-value">
            <el-tag
              :type="selectedReport.riskLevel === 'Low' ? 'success' : selectedReport.riskLevel === 'Medium' ? 'warning' : 'danger'"
            >
              {{ selectedReport.riskLevel }}
            </el-tag>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-label">披露时间</div>
          <div class="detail-value">{{ selectedReport.time }}</div>
        </div>

        <div class="detail-section">
          <div class="detail-label">报告来源</div>
          <div class="detail-value">
            <a :href="selectedReport.ref" target="_blank" class="source-link">
              <img :src="getSourceIcon(selectedReport.ref)" alt="source" class="source-icon" />
              {{ getSourceName(selectedReport.ref) }}
            </a>
          </div>
        </div>

        <div class="detail-section description-section">
          <div class="detail-label">漏洞描述</div>
          <div class="detail-value description-text">
            {{ selectedReport.reportDesc }}
          </div>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="descriptionDialogVisible = false">
            关闭
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.danger-card-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: #ffffff;
}

.danger-card-table .id {
  width: 160px;
}

.danger-card-table tbody .id *{
  font-family: Consolas, monospace;
  font-weight: bold;
}

.danger-card-table .name {
  width: 500px;
}

.danger-card-table .name .name-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.danger-card-table .time {
  width: 150px;
  min-width: 140px;
}

.danger-card-table .level {
  width: 120px;
  min-width: 100px;
}

.danger-card-table .level .el-tag {
  font-weight: 600;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.danger-card-table .ref {
  width: 120px;
  min-width: 100px;
}

.danger-card-table th {
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

.danger-card-table th:first-child {
  border-top-left-radius: 12px;
}

.danger-card-table th:last-child {
  border-top-right-radius: 12px;
}

.danger-card-table td {
  padding: 16px;
  height: auto;
  border-bottom: 1px solid #f1f5f9;
  color: #374151;
  font-size: 14px;
  line-height: 20px;
  vertical-align: middle;
}

.danger-card-table tbody tr {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.danger-card-table tbody tr:hover {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transform: scale(1.01);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  z-index: 5;
}

.danger-card-table tbody tr:hover td {
  border-bottom-color: #e2e8f0;
}

.ref-item-container {
  display: flex;
  align-items: center;
}

.ref-item {
  height: 20px;
  display: inline-flex;
  align-items: center;
}

.ref-item img {
  height: 20px;
  width: 20px;
  border-radius: 6px;
  margin-right: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.ref-item:hover img {
  transform: scale(1.1);
}

.ref-item span {
  font-size: 13px;
  line-height: 20px;
  font-weight: 600;
  color: #667eea;
  transition: color 0.3s ease;
}

.ref-item:hover span {
  color: #5a67d8;
}

.details-icon {
  border: 2px solid #667eea;
  border-radius: 8px;
  min-width: 48px;
  height: 28px;
  line-height: 28px;
  display: flex;
  margin-left: 12px;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  font-weight: 600;
  font-size: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.details-icon:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.details-icon span {
  color: #ffffff;
  font-weight: 600;
  font-size: 12px;
  text-align: center;
}

/* 添加一些微妙的动画效果 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.danger-card-table tbody tr {
  animation: slideIn 0.5s ease-out;
  animation-fill-mode: both;
}

.danger-card-table tbody tr:nth-child(1) { animation-delay: 0.05s; }
.danger-card-table tbody tr:nth-child(2) { animation-delay: 0.1s; }
.danger-card-table tbody tr:nth-child(3) { animation-delay: 0.15s; }
.danger-card-table tbody tr:nth-child(4) { animation-delay: 0.2s; }
.danger-card-table tbody tr:nth-child(5) { animation-delay: 0.25s; }
.danger-card-table tbody tr:nth-child(6) { animation-delay: 0.3s; }
.danger-card-table tbody tr:nth-child(7) { animation-delay: 0.35s; }
.danger-card-table tbody tr:nth-child(8) { animation-delay: 0.4s; }
.danger-card-table tbody tr:nth-child(9) { animation-delay: 0.45s; }
.danger-card-table tbody tr:nth-child(10) { animation-delay: 0.5s; }

/* 详情对话框样式 */
.description-dialog :deep(.el-dialog) {
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.description-dialog :deep(.el-dialog__header) {
  border-bottom: 2px solid #f1f5f9;
}

.description-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 700;
  color: #1a202c;
}

.description-content {
  padding: 20px 0;
  max-height: 600px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-label {
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 14px;
  color: #2d3748;
  line-height: 1.6;
  padding: 12px;
  background-color: #f7fafc;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  word-break: break-word;
}

.description-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 2px solid #e2e8f0;
}

.description-text {
  white-space: pre-wrap;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 16px;
  line-height: 1.8;
  max-height: 400px;
  overflow-y: auto;
}

.source-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
}

.source-link:hover {
  color: #5a67d8;
}

.source-icon {
  height: 20px;
  width: 20px;
  border-radius: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>

