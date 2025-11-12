<script setup lang="ts">
import { ref, defineEmits} from 'vue'

interface Tab {
  id: string
  name: string
}

const emit = defineEmits(['select']);

const tabs: Tab[] = [
  { id: 'java', name: '目前系统支持JavaScript,PHP,Ruby,Golang,Rust,Erlang,Python，Java' },
 // { id: 'cpp', name: 'C/C++' },
]

const selectedTab = ref<string>('java')

const handleSelect = (tabId: string): void => {
  emit('select', tabId)
  console.log(tabId)
  selectedTab.value = tabId
}
</script>

<template>
  <div class="language-selector">
    <div class="tabs-container">
      <div
        v-for="tab in tabs"
        :key="tab.id"
        class="tab"
        :class="{ 'selected': selectedTab === tab.id }"
        @click="handleSelect(tab.id)"
      >
        {{ tab.name }}
        <div v-if="selectedTab === tab.id" class="background "></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.language-selector {
  width: 100%;
  max-width: 1500px;
}

.label {
  color: #333;
  margin-bottom: 8px;
  font-size: 14px;
}

.tabs-container {
  display: flex;
  background-color: transparent;
  border: #dcdfe6 1px solid;
  border-radius: 8px;
  padding: 8px 8px;
  position: relative;
}

.tab {
  flex: 1;
  height: 60px;
  padding: 0 32px;
  border: none;
  background: none;
  font-size: 16px;
  font-weight: 600;
  color: #f4f5f6;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
  border-radius: 6px;
  outline: none;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab:hover {
  color: #edeef0;
}

.tab.selected {
  color: #0e0e0e;
  font-weight: 700;
}

.background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(42, 42, 42, 0.1);
  border-radius: 6px;
  z-index: 0;
  transition: all 0.3s ease;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
