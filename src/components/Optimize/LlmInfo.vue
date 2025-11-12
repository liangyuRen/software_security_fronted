<script setup lang="ts">
import type { LlmInfoType } from './const';

withDefaults(
  defineProps<{
    info: LlmInfoType
    isChosen: boolean
    isVip: boolean
  }>(),
  {
    isChosen: false,// 默认未被选择
    isVip: false
  }
);

const emit = defineEmits(['update:name'])


</script>

<template>
  <div class="llm-card">
    <div class="header">
      <h4>{{ info.llmName }}</h4>
      <div class="right">
        <div v-if="info.infoTag" class="tag" :style="{ backgroundColor: '#E4FBE5', color: '#3EC01E' }">{{ info.infoTag
        }}
        </div>
        <div v-if="info.needVip" class="tag vip-tag">会员专享</div>
        <el-tag v-if="isChosen" type="primary">已选择</el-tag>
      </div>

    </div>
    <div class="text">{{ info.desc }}</div>
    <div class="footer">
      <div class="data-info">
        <!-- <div class="data-block">
          <div class="pointer" :style="{ backgroundColor: '#87AE6C' }"></div>
          <div class="data">准确率: {{ info.accuracy }}</div>
        </div> -->
        <!-- <div class="data-block">
          <div class="pointer" :style="{ backgroundColor: '#F9C55E' }"></div>
          <div class="data">误报率: {{ info.falseRate }}</div>
        </div> -->
      </div>
      <el-button class="llm-button" v-if="!info.needVip || (info.needVip && isVip)" type="primary"
        @click="emit('update:name', info.llmName)">
        选用该模型
      </el-button>
      <div class="no-vip" v-if="info.needVip && !isVip">非会员无法使用</div>
    </div>
  </div>

</template>

<style scoped>
.llm-card {
  cursor: pointer;
  padding: 16px 20px;
  padding-bottom: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  min-height: 180px;
}

.llm-card:hover {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-color: #667eea;
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.2);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f1f5f9;
}

.llm-card:hover .header {
  border-bottom-color: #e2e8f0;
}

.header h4 {
  font-weight: 700;
  font-size: 16px;
  color: #1a202c;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header .right {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.text {
  height: 68px;
  width: 100%;
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 3;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  margin-bottom: 12px;
}

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 40px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.llm-card:hover .footer {
  border-top-color: #e2e8f0;
}

.data-info {
  display: flex;
  gap: 12px;
}

.data-block {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pointer {
  height: 10px;
  width: 10px;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.data {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}

.llm-button {
  display: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.llm-card:hover .llm-button {
  display: inline-flex;
}

.llm-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.no-vip {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  padding: 6px 12px;
  background: #f1f5f9;
  border-radius: 6px;
}

.tag {
  padding: 4px 12px;
  height: auto;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  line-height: 1.4;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.tag:hover {
  transform: scale(1.05);
}

.vip-tag {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(251, 191, 36, 0.4);
}

/* 添加动画效果 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.llm-card {
  animation: slideIn 0.5s ease-out;
  animation-fill-mode: both;
}
</style>
