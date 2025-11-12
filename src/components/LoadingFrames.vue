<template>
  <div class="loader-container">
    <div class="wave-loader">
      <div
        v-for="(item, index) in items"
        :key="index"
        class="wave-bar"
        :style="{
        animationDelay: `${- index * 0.1}s`
      }"
      ></div>
    </div>

    <div class="load-text">
      <span>加载数据中，请稍候</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const items = ref(new Array(16).fill(null));
</script>

<style scoped>
.loader-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 20px;
}
.wave-loader {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
}

.wave-bar {
  width: 6px;
  height: 20px;
  background: #336fff;
  border-radius: 3px;
  animation: wave 2s ease-in-out infinite;
  transform-origin: bottom;
}

@keyframes wave {
  0%, 100% {
    transform: scaleY(1);
    //opacity: 0.8;
  }
  25% {
    transform: scaleY(2.2);
    //opacity: 1;
  }
  50% {
    transform: scaleY(0.8);
    //opacity: 0.6;
  }
  75% {
    transform: scaleY(1.5);
    //opacity: 0.9;
  }
}

@media (prefers-reduced-motion: reduce) {
  .wave-bar {
    animation: wave 2s ease-in-out infinite;
  }
}

.load-text span {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #24292f;
  font-weight: 700;
}
</style>
