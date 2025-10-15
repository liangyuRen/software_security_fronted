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
  border-radius: 5px;
  background-color: #c80a0a;
  margin: 15px;
}

.card-header {
  width: 100%;
  border-bottom: 1px solid rgba(30, 177, 60, 0.49);
  padding: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;

  .card-title {
    font-size: 18px;
    /* margin-bottom: 10px; */
  }

  .right {
    display: flex;
    align-items: center;
  }
}
</style>
