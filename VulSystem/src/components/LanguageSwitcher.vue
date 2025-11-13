<template>
  <el-dropdown @command="handleLanguageChange" trigger="click">
    <span class="language-switcher">
      <el-icon><Setting /></el-icon>
      {{ currentLanguageLabel }}
      <el-icon class="el-icon--right"><ArrowDown /></el-icon>
    </span>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="lang in languages"
          :key="lang.value"
          :command="lang.value"
          :class="{ active: currentLocale === lang.value }"
        >
          {{ lang.label }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Setting, ArrowDown } from '@element-plus/icons-vue'

interface Language {
  value: string
  label: string
}

const languages: Language[] = [
  { value: 'zh', label: '中文' },
  { value: 'en', label: 'English' }
]

const { locale } = useI18n()

const currentLocale = computed(() => locale.value)

const currentLanguageLabel = computed(() => {
  const lang = languages.find(l => l.value === currentLocale.value)
  return lang ? lang.label : '中文'
})

function handleLanguageChange(lang: string): void {
  locale.value = lang
  localStorage.setItem('language', lang)
}
</script>

<style scoped>
.language-switcher {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  color: #fff;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.language-switcher:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.el-dropdown-menu .active {
  color: #409eff;
  font-weight: bold;
}
</style>