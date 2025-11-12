<script setup lang="ts">
import { ref, toRefs, watch } from 'vue';
import { InfoFilled } from '@element-plus/icons-vue'
const props = defineProps({
  label: String,
  modelValue: [Number, String],
  inputType: {
    type: String,
    default: 'el-input-number'
  },
  inputProps: {
    type: Object,
    default: () => ({})
  },
});

// 使用 defineEmits 声明可以发出的事件
const emit = defineEmits(['update:modelValue']);

// 使用 toRefs 将响应式对象属性解构成响应式引用
const isEdit = ref<boolean>(false);

// 本地响应式变量
const localValue = ref(props.modelValue); // 初始化本地值

// 监听 modelValue 的变化，以保持 localValue 同步
watch(() => props.modelValue, (newValue) => {
  localValue.value = newValue;
});

// 确认编辑时更新 modelValue
function confirmEdit() {
  // 发出事件以更新父组件的 modelValue
  emit('update:modelValue', localValue.value);
  isEdit.value = false
}

function cancelEdit() {
  isEdit.value = false
  localValue.value = props.modelValue
}

</script>

<template>
  <div class="info">
    <div class="label">{{ label }}</div>
    <template v-if="isEdit">
      <div class="input">
        <el-slider v-if="inputType == 'ElSlider'" v-model="localValue as number" v-bind="inputProps" />
        <el-input-number v-else-if="inputType == 'ElInputNumber'" v-model="localValue as number" v-bind="inputProps" />
      </div>
      <div class="text">
        <span class="edit" @click="confirmEdit">确认修改</span>
        <span class="cancel" @click="cancelEdit">取消</span>
      </div>
    </template>
    <template v-else>
      <div class="data">{{ modelValue }}</div>
      <div class="text">
        <span class="edit" @click="isEdit = true">修改</span>
      </div>
    </template>
  </div>

</template>

<style scoped>
.data-setting {
  .info {
    flex: 1;
    display: flex;
    align-items: center;

    .label {
      font-size: 14px;
      font-weight: bold;
      margin-right: 25px;
      color: #555557;
    }


    .input {
      flex: 1;
      max-width: 40%;
    }

    .el-input-number {
      max-width: 100px;
    }

    .text {
      font-size: 14px;
      cursor: pointer;

      .edit {
        color: #336FFF;
        margin: 0 10px;
      }

      .cancel {
        color: #B7B9BD;
      }
    }
  }
}
</style>
