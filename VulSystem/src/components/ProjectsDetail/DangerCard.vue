<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { Edit, Delete, ArrowDown, ArrowRight } from '@element-plus/icons-vue'
import type { DangerInfo } from '../Danger/const';
import AdviceCard from '../Markdown/AdviceCard.vue';
import { acceptVul } from '../Markdown/service';

const props = withDefaults(
  defineProps<{
    info: DangerInfo
  }>(),
  {
  }
);

interface Tags {
  [key: string]: {
    color: string; // 颜色
    bgc: string;   // 背景色
    text: string;  // 文本
  }
}

const statusTag = computed(() => {
  const tags: Tags = {
    ['High']: {
      color: '#FF5340',
      bgc: '#FFF4F1',
      text: '高风险'
    },
    ['Medium']: {
      color: '#8b5cf6',
      bgc: '#f3e8ff',
      text: '中风险'
    },
    ['Low']: {
      color: '#336FFF',
      bgc: '#E5EFFF',
      text: '低风险'
    },
  }
  const res = tags[props.info.riskLevel];
  if (res) {
    return res
  }
  return {
    color: '#FF5340',
    bgc: '#FFF4F1',
    text: '高风险'
  }
})
console.log('测试问题列表')
// 本地响应式变量
const localAccept = ref<boolean>(props.info.isaccept == 1); // 初始化本地值

// 监听 modelValue 的变化，以保持 localAccept 同步
watch(() => props.info.isaccept, (newValue) => {
  localAccept.value = newValue == 1;
});
const emit = defineEmits(['refresh'])
const dialogVisible = ref<boolean>(false)
const loading = ref<boolean>(false)
// 采纳漏洞
const beforeAcceptChange = () => {
  loading.value = true
  // 1:采纳 2: 不采纳
  const ifaccept = localAccept.value ? 2 : 1
  return acceptVul(props.info.id, ifaccept).finally(() => {
    loading.value = false
    emit('refresh')
  })
}
const timeFormatter = (dateString: string) => {
  // 将字符串转换为 Date 对象
  const date = new Date(dateString);

  // 获取年份、月份和日期
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0'); // 月份是0-11，+1后格式化为2位数
  const day = String(date.getDate()).padStart(2, '0'); // 获取日期并格式化为2位数

  // 将结果拼接为 "year-month-date" 格式
  const formattedDate = `${year}-${month}-${day}`;

  console.log(formattedDate); // 输出: "2025-02-13"
  return formattedDate
}
// 取消采纳
</script>

<template>
  <div class="vul-card">
    <div class="header">
      <div class="left">
        <h4>{{ info.name }}</h4>
        <div class="link"></div>
      </div>
      <el-button v-if="localAccept" type="primary" plain @click="dialogVisible = true">查看修复建议</el-button>

    </div>
    <el-text class="text" truncated type="info" line-clamp="2">{{ info.description }}</el-text>
    <div class="footer">
      <div class="data-info">
        <div class="tag" :style="{ backgroundColor: statusTag.bgc, color: statusTag.color }">{{ statusTag.text }}</div>
        <!-- <div class="tag">{{ 会员专享 }}</div> -->
        <div class="info-tag">
          语言: {{ info.language }}
        </div>
        <div class="info-tag">
          {{ timeFormatter(info.time) }}
        </div>

      </div>
      <div class="right">
        <div class="label">采纳该问题</div>
        <el-switch v-model="localAccept" :loading="loading" :before-change="beforeAcceptChange" />
      </div>
    </div>
  </div>
  <el-dialog v-model="dialogVisible" title="" width="70%">
    <!-- <span>This is a message</span> -->
    <AdviceCard :info="info" />
    <!-- <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="dialogVisible = false">
          Confirm
        </el-button>
      </div>
    </template> -->
  </el-dialog>

</template>

<style scoped>
.vul-card {
  margin: 25px 0;
  border: #E5E5E5 1px solid;
  cursor: pointer;
  padding: 10px 15px;
  padding-bottom: 0;
  /* box-shadow: rgba(99, 99, 99, 0.116) 0px 2px 8px 0px; */
  border-radius: 3px;
  height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  .header,
  .footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }



  .header {
    margin-bottom: 10px;
    height: 35px;
  }

  .left,
  .right {
    display: flex;
    align-items: center;
  }

  .text {
    flex: 1;
    width: 100%;
  }

  .footer {
    border-top: 1px solid #efefefd5;
    height: 50px;

    .data-info {
      display: flex;


      .data-block {
        display: flex;
        align-items: center;
        margin-right: 10px;
      }

      .pointer {
        height: 10px;
        width: 10px;
        border-radius: 5px;
        margin-right: 5px;
      }

      .data {
        font-size: 10px;
      }
    }


    .label {
      font-size: 12px;
      /* color: #8B8C8F; */
      margin-right: 20px;
    }

  }

}


.tag,
.info-tag {
  padding: 4px 15px;
  /* height: 20px; */
  border-radius: 14px;
  font-size: 12px;
  /* line-height: 20px; */
  cursor: pointer;
  margin-right: 10px;
  /* font-weight: bold; */
}

.info-tag {
  border: 1px solid #12112a2c;
}
</style>
