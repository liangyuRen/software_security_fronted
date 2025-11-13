<script setup lang="ts">
import { computed, ref } from 'vue';
import { type ProjectInfo } from './const';
import { Edit, Delete, ArrowDown, ArrowRight } from '@element-plus/icons-vue'
import ProjectForm from "@/components/Project/ProjectForm.vue";
import { useI18n } from 'vue-i18n';

const { t } = useI18n()

const props = withDefaults(
  defineProps<{
    project: ProjectInfo;
    classname?: string;
    canEdit?: boolean;
  }>(),
  {
    canEdit: true  // 默认可编辑
  }
);
const emit = defineEmits(['edit', 'delete', 'editFile']);

type Tags = {
  [key: string]: { color: string, bgc: string, text: string };
};
const statusTag = computed(() => {
  const tags: Tags = {
    ['高风险']: {
      color: '#FF5340',
      bgc: '#FFF4F1',
      // text: '高危 ' + (props.project.danger ?? 0)
      text: t('projectCard.highRisk')
    },
    ['低风险']: {
      color: '#336FFF',
      bgc: '#E5EFFF',
      // text: '分析中'
      text: t('projectCard.lowRisk')
    },
    ['中风险']: {
      color: '#8b5cf6',
      bgc: '#f3e8ff',
      text: t('projectCard.mediumRisk')
      // text: '中危 ' + (props.project.danger ?? 0)
    },
    ['暂无风险']: {
      color: '#3EC01E',
      bgc: '#E4FBE5',
      text: t('projectCard.noRisk')
    }
  }
  return tags[props.project.risk_level]
})

const isOpen = ref(false)
const handleOpen = () => isOpen.value = !isOpen.value

const editFormVisible = ref(false);

const handleEdit = (project: ProjectInfo) => {
  emit('edit', project);
  editFormVisible.value = false;
}

const editFileFormVisible = ref(false);

const handleEditFile = (project: ProjectInfo) => {
  emit('editFile', project);
  editFileFormVisible.value = false;
}

</script>

<template>
  <div class="project-card" :class="classname">
    <div class="card-header">
      <div class="left">
        <h2 class="card-title" @click="$router.push({ path: `/projects/info/${project.id}` });">{{ project.name }}
        </h2>
        <div class="text">{{ project.description }}</div>
        <!-- <el-text truncated type="info" size="small"></el-text> -->
      </div>
      <div class="right">
        <div class="tag" :style="{ backgroundColor: statusTag.bgc, color: statusTag.color }"
          @click="$router.push({ path: `/projects/info/${project.name}` });">{{ statusTag.text }}
        </div>
        <el-icon v-show="canEdit" class="project-icon" @click="editFormVisible = true">
          <Edit />
        </el-icon>
        <el-icon v-show="canEdit" class="project-icon" @click="emit('delete', project)">
          <Delete />
        </el-icon>
        <el-icon class="project-icon" @click="handleOpen">
          <ArrowDown v-if="isOpen" :style="{ color: '#336fff' }" />
          <ArrowRight v-else />
        </el-icon>
      </div>
    </div>
    <div class="detail" v-if="isOpen">
      <div class="text">{{ t('projectCard.detectionThreshold') }}{{ project.risk_threshold ?? 10 }}</div>
      <div class="text">{{ t('projectCard.projectLanguage') }}{{ project.language ?? 'java' }}</div>
      <div class="modify-project-button" @click="editFileFormVisible = true">
        {{ t('projectCard.modifyProjectFiles') }}
      </div>
    </div>
  </div>
  <ProjectForm type="edit" :visible="editFormVisible" @cancel="() => editFormVisible = false" @confirm="handleEdit"
    @close="() => editFormVisible = false" :project="project" />
  <ProjectForm type="file" :visible="editFileFormVisible" @cancel="() => editFileFormVisible = false" @confirm="handleEditFile"
               @close="() => editFileFormVisible = false" :project="project" />
</template>

<style scoped>
.project-card {
  flex: 1;
  border-radius: 5px;
  background-color: #fff;
  margin: 25px;

}

.card-header {
  width: 100%;
  padding: 5px;
  display: flex;
  justify-content: space-between;

  .left {
    flex: 1;

    .card-title {
      font-size: 16px;
      font-weight: 700;
      color: #24292f;
      /* margin-bottom: 10px; */
      cursor: pointer;
    }

    .text {
      flex: 1;
      width: 100%;
      font-size: 13px;
      color: #57606a;
      font-weight: 500;
      display: -webkit-box;
      /* 为了使用 WebKit 的剪裁 */
      -webkit-box-orient: vertical;
      /* 设置方向为垂直 */
      -webkit-line-clamp: 3;
      line-clamp: 3;
      /* 设置显示的行数 */
      overflow: hidden;
      /* 隐藏超出内容 */
      text-overflow: ellipsis;
      /* 显示省略号 */
      line-height: 1.6;
    }
  }


  .right {
    display: flex;

    .tag {
      padding: 0 10px;
      height: 20px;
      border-radius: 10px;
      font-size: 12px;
      line-height: 20px;
      cursor: pointer;
    }

    .project-icon {
      font-size: 20px;
      color: #808080;
      margin-left: 8px;
      cursor: pointer;
    }
  }
}

.detail {
  width: 100%;
  background-color: #dedfe03f;
  padding: 6px 20px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;

  .text {
    color: #24292f;
    font-size: 13px;
    font-weight: 600;
  }

  .modify-project-button{
    padding: 4px 12px;
    border-radius: 6px;
    background-color: #ffffff;
    color: #24292f;
    cursor: pointer;
    margin: 5px 0;
    font-size: 13px;
    font-weight: 600;
    border: 1.5px solid #d0d7de;
    transition: all 0.2s;
  }

  .modify-project-button:hover{
    background-color: #f6f8fa;
    border-color: #8c959f;
  }
}
</style>
