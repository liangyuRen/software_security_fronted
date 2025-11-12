<script setup lang="ts">
import { ref, watch } from 'vue';
import { Edit, Delete, ArrowDown, ArrowRight } from '@element-plus/icons-vue'

const props = withDefaults(
  defineProps<{
    thresholdName: string
    threshold: number,
    K: number
  }>(),
  {
    thresholdName: '相似度阈值'  // 默认可编辑
  }
);

// 本地响应式变量
const threshold = ref(props.threshold);
const K = ref(props.K);
const emit = defineEmits(['update:threshold', 'update:K']);
// 将每个变量同步到 Vulkan
const updateThreshold = (value: number) => {
  threshold.value = value;
  emit('update:threshold', value); // Emit event to parent component
};

const updateK = (value: number) => {
  K.value = value;
  emit('update:K', value); // Emit event to parent component
};

// 监听prop变化，并更新本地值
watch(() => props.threshold, (newValue) => {
  threshold.value = newValue;
});

watch(() => props.K, (newValue) => {
  K.value = newValue;
});
</script>

<template>
  <div class="data-setting">
    <!-- Threshold 编辑部分 -->
    <EditableField :label="thresholdName" v-model="threshold" :inputType="'ElSlider'"
      :inputProps="{ min: 0, max: 1, step: 0.05, showInput: true }" @update:modelValue="updateThreshold" />

    <!-- K 值编辑部分 -->
    <EditableField :label="'单位漏洞报告中检测出漏洞库的最大数量'" v-model="K" :inputType="'ElInputNumber'"
      :inputProps="{ min: 1, max: 128 }" @update:modelValue="updateK" />
    <!-- <div class="info">
      <div class="label">{{ thresholdName }}</div>
      <template v-if="threshold.isEdit">
        <el-slider v-model="threshold.data" show-input min="0" max="1" step="0.05" />
        <div class="text">
          <span class="edit" @click="editThreshold">确认修改</span>
          <span class="cancel" @click="cancelThreshold">取消</span>
        </div>
      </template>
<template v-else>
        <div class="data">{{ threshold.data }}</div>
        <div class="text">
          <span class="edit" @click="threshold.isEdit = true">修改</span>
        </div>
      </template>
</div> -->


    <!-- <div class="info">
      <div class="label">单位漏洞报告中检测出漏洞库的最大数量</div>
      <template v-if="K.isEdit">
        <el-input-number v-model="K.data" :min="1" :max="128" />
        <div class="text">
          <span class="edit" @click="editK">确认修改</span>
          <span class="cancel" @click="cancelK">取消</span>
        </div>
      </template>
      <template v-else>
        <div class="data">{{ K.data }}</div>
        <div class="text">
          <span class="edit" @click="K.isEdit = true">修改</span>
        </div>
      </template>
    </div> -->
  </div>



</template>

<style scoped>
.data-setting {
  width: 100%;
  display: flex;
  margin: 5px 0 12px;
  padding: 5px 10px;
  /* background-color: #fff; */
  border-radius: 5px;
}
</style>
