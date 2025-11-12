<script setup lang="ts">
import { ref } from 'vue'
import LLMHelperBody from "@/components/LLMHelper/LLMHelperBody.vue";
import {Orange} from "@element-plus/icons-vue";

const helperVisible = ref(false)
</script>

<template>
  <div class="llm-helper">
    <div class="llm-helper-button" @click="helperVisible = !helperVisible" v-show="!helperVisible">
        <el-icon size="24"><Orange /></el-icon>
    </div>
    <div class="llm-helper-body" v-show="helperVisible">
      <LLMHelperBody @closeBody="helperVisible = !helperVisible"/>
    </div>
  </div>

</template>

<style scoped>

.llm-helper-button {
  position: fixed;
  right: 0;
  bottom: 0;
  margin: 20px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #4169E1;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

.llm-helper-button .el-icon {
  color: white;
}

</style>
