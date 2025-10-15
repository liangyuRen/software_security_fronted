<script setup lang="ts">
import { ref, defineEmits} from 'vue'

interface Tab {
  id: string
  name: string
}

const emit = defineEmits(['select']);

const tabs: Tab[] = [
  { id: 'java', name: 'Java' },
  { id: 'cpp', name: 'C/C++' },
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
  max-width: 600px;
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
  padding: 4px 4px;
  position: relative;
}

.tab {
  flex: 1;
  height: 30px;
  padding: 0 24px;
  border: none;
  background: none;
  font-size: 14px;
  font-weight: 600;
  color: #57606a;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
  border-radius: 6px;
  outline: none;
  text-align: center;
}

.tab:hover {
  color: #24292f;
}

.tab.selected {
  color: #24292f;
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
