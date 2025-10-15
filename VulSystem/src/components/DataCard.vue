<script setup lang="ts">
defineProps<{
  title: string
  height?: string
  width?: string
  classname?: string
}>()
</script>

<template>
  <div class="data-card" :class="classname">
    <div class="card-header">
      <h2 class="card-title">{{ title }}</h2>
      <div class="right">
        <slot name="right"></slot>
      </div>
    </div>
    <div :style="{ height, width }">
      <slot name="main"></slot>
    </div>
  </div>
</template>

<style scoped>
.data-card {
  flex: 1;
  padding: 20px;
  border-radius: 12px;
  background-color: #ffffff;
  margin: 15px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.data-card:hover {
  border-color: #667eea;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
}

.card-header {
  width: 100%;
  border-bottom: 2px solid #f1f5f9;
  padding: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  margin-bottom: 12px;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a202c;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.right {
  display: flex;
  align-items: center;
}
</style>
