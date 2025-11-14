<script setup lang="ts">
import type { ReportInfo } from './const';
import {computed} from 'vue';
import ReportListTable from "@/components/Danger/ReportListTable.vue";

const props = defineProps<{
  reportInfoList: ReportInfo[]
  filteredReports: ReportInfo[]
  currentPage: number
  totalPages: number
  totalItems: number
  searchQuery?: string
  isFiltered: boolean
}>()


const displayedPages = computed(() => {
  const pages = []
  const maxDisplayPages = 5

  let start = Math.max(1, props.currentPage - 2)
  const end = Math.min(props.totalPages, start + maxDisplayPages - 1)
  if (end - start + 1 < maxDisplayPages) {
    start = Math.max(1, end - maxDisplayPages + 1)
  }
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

// reset current page when list changes

</script>

<template>
  <div class="danger-card">
    <ReportListTable v-if="!props.isFiltered" :paginated-list="props.reportInfoList" :search-query="props.searchQuery ?? ''" />
    <ReportListTable v-else :paginated-list="filteredReports" :search-query="props.searchQuery ?? ''" />
  </div>
  <div class="card-footer" v-if="!props.isFiltered">
    <div class="pagination">
      <span class="page-info">
        <span>{{ props.currentPage }} / {{ props.totalPages }} 页</span><span>，共 {{ props.totalItems }} 条</span>
      </span>

      <button
        class="controller page-btn"
        :disabled="props.currentPage === 1"
        @click="$emit('update:currentPage', 1)"
        v-if="props.currentPage > 3"
      >
        首页
      </button>

      <button
        class="controller page-btn"
        :disabled="props.currentPage === 1"
        @click="$emit('update:currentPage', props.currentPage - 1)"
      >
        上一页
      </button>

      <button
        v-for="page in displayedPages"
        :key="page"
        class="page-btn"
        :class="{ active: props.currentPage === page }"
        @click="$emit('update:currentPage', page)"
      >
        {{ page }}
      </button>

      <button
        class="controller page-btn"
        :disabled="props.currentPage === props.totalPages"
        @click="$emit('update:currentPage', props.currentPage + 1)"
      >
        下一页
      </button>

      <button
        class="controller page-btn"
        :disabled="props.currentPage === props.totalPages"
        @click="$emit('update:currentPage', props.totalPages)"
        v-if="props.currentPage < props.totalPages - 2"
      >
        尾页
      </button>
    </div>
  </div>
</template>

<style scoped>
.danger-card {
  flex: 1;
  background-color: #ffffff;
  margin: 0;
  border: none;
  border-radius: 0;
  overflow: hidden;
}

.card-header {
  width: 100%;
  border-bottom: 1px solid #ccc;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 5px 10px;

  .card-title {
    font-size: 18px;
    /* margin-bottom: 10px; */
  }

  .right {
    display: flex;
    align-items: center;
  }
}


.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 24px;
  padding: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 0;
  border-top: 1px solid #e2e8f0;
}

.page-btn {
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  color: #475569;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  min-width: 40px;
}

.controller {
  color: #667eea;
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
}

.controller:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46a0 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.page-btn:hover:not(:disabled) {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.25);
}

.page-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border-color: #667eea;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.page-btn:disabled {
  cursor: not-allowed;
  color: #94a3b8;
  background: #f1f5f9;
  border-color: #e2e8f0;
  transform: none;
  box-shadow: none;
}

.page-info {
  margin-right: 20px;
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.page-info span {
  color: #64748b;
  font-weight: 500;
}

.page-info span:last-child {
  margin-left: 12px;
  color: #667eea;
  font-weight: 600;
}
</style>
