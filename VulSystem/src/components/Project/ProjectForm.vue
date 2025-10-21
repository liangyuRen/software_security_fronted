<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { type ProjectInfo } from './const';
import { QuestionFilled } from "@element-plus/icons-vue";
import LanguageSelector from "@/components/Project/LanguageSelector.vue";
import { ElMessage, type FormInstance, type UploadInstance } from "element-plus";
import { UploadFilled } from '@element-plus/icons-vue'


// props and emits
const props = withDefaults(defineProps<{
  type: 'edit' | 'add' | 'file';
  classname?: string;
  visible: boolean
  project?: ProjectInfo
}>(), {
  type: 'add'
});
const emit = defineEmits(['cancel', 'confirm']);
const dialogVisible = ref(props.visible);
const newProject = reactive<ProjectInfo>(props.project ??
{
  id: 0,
  name: '',
  description: '',
  risk_level: '暂无风险',
  language: 'java',
  //依然修改companyid
  companyId: 1,
  //companyId: localStorage.getItem('companyId') ?? '',
  risk_threshold: 10,
  filePath: null
})
const formRef = ref<FormInstance>();
const currentFile = ref<File | null>(null);
const fileUploadServerBaseURL = '/api'; // 通过Nginx代理转发到后端
//const fileUploadServerBaseURL = 'http://localhost:8081';
const getTitle = computed(() => {
  switch (props.type) {
    case 'add':
      return '新建项目';
    case 'edit':
      return '编辑项目';
    case 'file':
      return '修改或上传项目文件';
    default:
      return '默认窗口';
  }
})

// form rules
const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' }
  ],
  risk_threshold: [
    { required: true, message: '请输入风险阈值', trigger: 'blur' }
  ],
  filePath: [
    { required: true, message: '请上传项目文件', trigger: 'change' }
  ],
  editFilePath: [
    { required: true, message: '请上传项目文件', trigger: 'change' }
  ]
}

// language change
function handleChangeLanguage(language: string) {
  newProject.language = language;
}

// tooltip content
function getTooltipContent(language: string): string {
  console.log("当前项目", newProject)
  switch (language) {
    case 'java':
      return "上传项目压缩包，支持 zip/7z/tar/gz/rar 等格式。<br>兼容 Windows、Linux、Mac 系统压缩的文件。<br>最大可接受的文件大小：100MB。";
    case 'cpp':
      return "上传项目压缩包，支持 zip/7z/tar/gz/rar 等格式。<br>兼容 Windows、Linux、Mac 系统压缩的文件。<br><span style='font-weight: bold'>请在压缩包根目录放置 kulin.txt，其中包含项目所有用到的库名，一个一行。</span><br>最大可接受的文件大小：100MB。";
    default:
      return "上传项目压缩包，支持 zip/7z/tar/gz/rar 等格式。<br>兼容 Windows、Linux、Mac 系统压缩的文件。<br>最大可接受的文件大小：100MB。";
  }
}

// file upload
const uploader = ref<UploadInstance>()

// 支持的压缩包文件类型（兼容Windows/Linux/Mac）
const SUPPORTED_ARCHIVE_TYPES = [
  // ZIP格式 - 各平台通用
  'application/zip',
  'application/x-zip-compressed',
  'application/x-zip',
  'application/octet-stream', // 通用二进制流，某些系统识别压缩包为此类型

  // 7Z格式
  'application/x-7z-compressed',
  'application/x-compressed',

  // TAR格式
  'application/x-tar',
  'application/tar',

  // TAR.GZ格式
  'application/gzip',
  'application/x-gzip',
  'application/x-compressed-tar',
  'application/x-tar+gzip',

  // RAR格式
  'application/vnd.rar',
  'application/x-rar-compressed',
  'application/x-rar',

  // 其他
  ''  // 空类型，某些浏览器可能返回空字符串
];

// 通过文件扩展名验证（更可靠的方式）
function isValidArchiveFile(fileName: string): boolean {
  const validExtensions = ['.zip', '.7z', '.tar', '.gz', '.tgz', '.tar.gz', '.rar'];
  const lowerFileName = fileName.toLowerCase();
  return validExtensions.some(ext => lowerFileName.endsWith(ext));
}

function handleFileChange(file: any) {
  if (file.size && file.size / 1024 / 1024 > 100) {
    ElMessage.error('文件大小不能超过100MB')
    return
  }

  // 优先使用文件扩展名验证，更可靠
  const isValidByExtension = isValidArchiveFile(file.name);
  const isValidByMimeType = SUPPORTED_ARCHIVE_TYPES.includes(file.raw.type);

  if (!isValidByExtension && !isValidByMimeType) {
    ElMessage.error(`文件格式不支持。当前文件类型: ${file.raw.type || '未知'}，请上传 zip/7z/tar/gz/rar 格式的压缩包文件`)
    console.warn('不支持的文件类型:', {
      fileName: file.name,
      mimeType: file.raw.type,
      size: file.size
    })
    return
  }

  currentFile.value = file.raw;
  console.log("已选择文件: ", currentFile.value)
  console.log("文件信息: ", {
    name: file.name,
    type: file.raw.type,
    size: (file.size / 1024 / 1024).toFixed(2) + 'MB'
  })
}
const removeFile = () => {
  currentFile.value = null
  if (uploader.value) {
    uploader.value.clearFiles()
  }
}
const uploadFile = () => {
  if (uploader.value) {
    uploader.value.submit()
  }
}
const handleFileUploadSuccess = (response: any) => {
  console.log('服务器的响应：', response)
  if (response.code === 200) {
    ElMessage.success('文件上传成功')
    newProject.filePath = response.obj
  } else {
    ElMessage.error('文件上传失败：' + response.message + '，' + response.obj)
    currentFile.value = null
    if (uploader.value) {
      uploader.value.clearFiles()
    }
  }
}

const handleFileUploadError = (err: any) => {
  console.error('文件上传失败：', err)
  ElMessage.error('文件上传失败：' + err)
  currentFile.value = null
  if (uploader.value) {
    uploader.value.clearFiles()
  }
}

async function handleConfirmCreate(formEl: FormInstance | undefined) {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      emit('confirm', newProject)
    }
  })
}

// watches
watch(() => props.visible, (newVal) => {
  // console.log(newVal)
  dialogVisible.value = newVal;
});
watch(() => props.project, (project) => {
  Object.assign(newProject, project);
})
</script>

<template>
  <!-- 新增项目的对话框 -->
  <el-dialog v-model="dialogVisible" :title="getTitle" width="900" center class="project-dialog">
    <el-form ref="formRef" :model="newProject" label-width="120px" style="max-width: 850px; margin: 0 auto;"
      :rules="rules" class="project-form">
      <el-form-item label="项目名称" prop="name" v-if="type == 'add' || type == 'edit'">
        <el-input v-model="newProject.name" placeholder="请输入项目名称" />
      </el-form-item>
      <el-form-item label="项目描述" v-if="type == 'add' || type == 'edit'">
        <el-input v-model="newProject.description" type="textarea" placeholder="请输入项目描述" />
      </el-form-item>
      <el-form-item label="风险阈值" prop="risk_threshold" v-if="type == 'add' || type == 'edit'">
        <el-input-number v-model="newProject.risk_threshold" :min="0" :max="20" />
        <div class="tips">
          <el-tooltip content="风险阈值是指项目中漏洞数量超过多少时，项目状态会变为风险状态。<br>当风险阈值为零时，代表高风险风险阈值。" raw-content placement="top">
            <el-icon class="question-icon">
              <QuestionFilled />
            </el-icon>
          </el-tooltip>
        </div>
      </el-form-item>
      <el-form-item label="项目语言" v-if="type == 'add'">
        <LanguageSelector @select="handleChangeLanguage" />
      </el-form-item>
      <el-form-item label="项目文件" prop="filePath" v-if="type == 'add'">
        <div class="upload-file-container">
          <el-upload ref="uploader" :auto-upload="false" :on-change="handleFileChange" :show-file-list="false"
            :multiple="false" :action="fileUploadServerBaseURL + '/project/uploadFile'"
            :on-success="handleFileUploadSuccess" :on-error="handleFileUploadError">
            <el-button type="primary">选择文件</el-button>
            <div class="tips">
              <el-tooltip :content="getTooltipContent(newProject.language)" raw-content placement="top">
                <el-icon class="question-icon">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </el-upload>
          <div v-if="currentFile" class="selected-file">
            <span>已选择文件: {{ currentFile.name }}</span>
            <el-button type="danger" size="small" @click="removeFile" class="remove-button"
              v-if="newProject.filePath == null">移除</el-button>
            <el-button type="primary" size="small" @click="uploadFile" v-if="newProject.filePath == null">上传</el-button>
            <div class="upload-success" v-if="newProject.filePath != null">上传成功！</div>
          </div>
        </div>
      </el-form-item>
      <el-form-item label="项目文件" prop="editFilePath" v-if="type == 'file'">
        <div class="upload-file-drag-container">
          <el-upload ref="uploader" :auto-upload="false" :on-change="handleFileChange" :show-file-list="false"
            :multiple="false" :action="fileUploadServerBaseURL + '/project/uploadFile'"
            :on-success="handleFileUploadSuccess" drag style="width: 100%" :on-error="handleFileUploadError">
            <el-icon class="el-icon--upload">
              <upload-filled />
            </el-icon>
            <div class="el-upload__text">
              <span>点击此处选择文件或将文件拖拽到此处上传</span>
            </div>
            <template #tip>
              <div class="el-upload__tip"
                style="display: flex; justify-content: flex-start; align-items: center; gap: 10px">
                支持扩展名：zip, 7z, tar, gz, rar（兼容各操作系统）
                <el-tooltip :content="getTooltipContent(newProject.language)" raw-content placement="top">
                  <el-icon class="question-icon">
                    <QuestionFilled />
                  </el-icon>
                </el-tooltip>
              </div>
            </template>
          </el-upload>
          <div v-if="currentFile" class="selected-file">
            <span>已选择文件: {{ currentFile.name }}</span>
            <el-button type="danger" size="small" @click="removeFile" class="remove-button"
              v-if="newProject.filePath == null">移除</el-button>
            <el-button type="primary" size="small" @click="uploadFile" v-if="newProject.filePath == null">上传</el-button>
            <div class="upload-success" v-if="newProject.filePath != null">上传成功！</div>
          </div>
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="emit('cancel')">取消</el-button>
        <el-button type="primary" @click="handleConfirmCreate(formRef)">
          {{ type == 'add' ? '确认添加' : '确认修改' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
/* 对话框样式 */
.project-dialog {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.project-dialog :deep(.el-dialog) {
  border-radius: 12px;
  overflow: hidden;
  position: relative !important;
  margin: 0 auto !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
}

.project-dialog :deep(.el-dialog__wrapper) {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}

/* 确保弹窗内容可以滚动 */
.project-dialog :deep(.el-dialog) {
  max-height: 90vh !important;
  overflow-y: auto !important;
}

/* 防止body被锁定 */
.project-dialog :deep(.el-overlay) {
  pointer-events: auto !important;
}

.project-dialog :deep(.el-dialog__header) {
  padding: 24px 24px 20px;
  border-bottom: 1px solid #ebeef5;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
  position: relative;
}

.project-dialog :deep(.el-dialog__header::after) {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 24px;
  right: 24px;
  height: 1px;
  background: linear-gradient(90deg, transparent, #e0e6ed, transparent);
}

.project-dialog :deep(.el-dialog__title) {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.project-dialog :deep(.el-dialog__body) {
  padding: 30px 24px;
  background: #ffffff;
  position: relative;
}

.project-dialog :deep(.el-dialog__body::before) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(64, 158, 255, 0.1), transparent);
}

.project-dialog :deep(.el-dialog__footer) {
  padding: 20px 24px 24px;
  border-top: 1px solid #ebeef5;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
  position: relative;
}

.project-dialog :deep(.el-dialog__footer::before) {
  content: '';
  position: absolute;
  top: -1px;
  left: 24px;
  right: 24px;
  height: 1px;
  background: linear-gradient(90deg, transparent, #e0e6ed, transparent);
}

/* 表单样式 */
.project-form {
  margin: 0 !important;
  position: relative;
}

.project-form :deep(.el-form-item) {
  margin-bottom: 32px;
  position: relative;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  padding: 4px;
  transition: all 0.3s ease;
}

.project-form :deep(.el-form-item:hover) {
  background: rgba(248, 249, 250, 0.9);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.project-form :deep(.el-form-item__label) {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 45px;
  text-shadow: 0 1px 1px rgba(255, 255, 255, 0.8);
  position: relative;
  z-index: 1;
}

.project-form :deep(.el-input__wrapper) {
  height: 45px;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: all 0.3s ease;
}

.project-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

.project-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #409eff inset;
}

.project-form :deep(.el-textarea__inner) {
  min-height: 100px;
  border-radius: 8px;
  font-size: 15px;
  padding: 12px 16px;
  resize: vertical;
}

.project-form :deep(.el-input-number) {
  width: 200px;
}

.project-form :deep(.el-input-number .el-input__wrapper) {
  height: 45px;
}

.tips {
  display: flex;
  align-items: center;
  margin-left: 10px;
  cursor: pointer;
}

.question-icon {
  color: #9da0a4;
  font-size: 20px;
  line-height: 16px;
  height: 20px;
  transition: color 0.3s ease;
}

.question-icon:hover {
  color: #409eff;
}

/* 上传区域样式 */
.upload-file-container {
  display: flex;
  flex-direction: column;
  align-items: start;
  gap: 16px;

  .el-upload {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .el-button {
    height: 42px;
    padding: 0 24px;
    font-size: 15px;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
  }

  .el-button--primary {
    background: linear-gradient(135deg, #409eff 0%, #66b3ff 100%);
    border: none;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
  }

  .el-button--primary:hover {
    background: linear-gradient(135deg, #337ecc 0%, #5aa3ff 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
  }

  .el-button--danger {
    background: linear-gradient(135deg, #f56c6c 0%, #ff8080 100%);
    border: none;
    box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
  }

  .el-button--danger:hover {
    background: linear-gradient(135deg, #e45656 0%, #ff6666 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(245, 108, 108, 0.4);
  }

  .selected-file {
    display: flex;
    align-items: center;
    padding: 16px 20px;
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    margin-top: 8px;
    width: 100%;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;

    span {
      font-size: 14px;
      font-weight: 500;
      color: #495057;
      flex: 1;
      word-break: break-all;
    }
  }

  .remove-button {
    margin-left: 12px;
  }

  .upload-success {
    color: #67c23a;
    font-weight: 600;
    margin-left: 12px;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .upload-success::before {
    content: "✓";
    display: inline-block;
    width: 18px;
    height: 18px;
    background: #67c23a;
    color: white;
    border-radius: 50%;
    text-align: center;
    line-height: 18px;
    font-size: 12px;
  }
}

.upload-file-drag-container {
  display: flex;
  flex-direction: column;
  align-items: start;
  width: 100%;
  position: relative;
  gap: 16px;

  :deep(.el-upload-dragger) {
    width: 100%;
    height: 200px;
    border: 2px dashed #d9d9d9;
    border-radius: 12px;
    background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
  }

  :deep(.el-upload-dragger:hover) {
    border-color: #409eff;
    background: linear-gradient(135deg, #f0f7ff 0%, #e6f3ff 100%);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(64, 158, 255, 0.15);
  }

  :deep(.el-upload-dragger.is-dragover) {
    border-color: #409eff;
    background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 100%);
    transform: scale(1.02);
  }

  :deep(.el-icon--upload) {
    font-size: 48px;
    color: #c0c4cc;
    transition: color 0.3s ease;
  }

  :deep(.el-upload-dragger:hover .el-icon--upload) {
    color: #409eff;
  }

  :deep(.el-upload__text) {
    font-size: 16px;
    color: #606266;
    font-weight: 500;
    line-height: 1.6;
  }

  :deep(.el-upload__tip) {
    font-size: 14px;
    color: #909399;
    margin-top: 12px;
    padding: 12px 16px;
    background: #f8f9fa;
    border-radius: 6px;
    border-left: 4px solid #409eff;
  }

  .selected-file {
    display: flex;
    align-items: center;
    padding: 16px 20px;
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    width: 100%;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;

    span {
      font-size: 14px;
      font-weight: 500;
      color: #495057;
      flex: 1;
      word-break: break-all;
    }
  }

  .remove-button {
    margin-left: 12px;
  }

  .upload-success {
    color: #67c23a;
    font-weight: 600;
    margin-left: 12px;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .upload-success::before {
    content: "✓";
    display: inline-block;
    width: 18px;
    height: 18px;
    background: #67c23a;
    color: white;
    border-radius: 50%;
    text-align: center;
    line-height: 18px;
    font-size: 12px;
  }
}

/* 底部按钮样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.dialog-footer .el-button {
  height: 42px;
  padding: 0 28px;
  font-size: 15px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.dialog-footer .el-button--primary {
  background: linear-gradient(135deg, #409eff 0%, #66b3ff 100%);
  border: none;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.dialog-footer .el-button--primary:hover {
  background: linear-gradient(135deg, #337ecc 0%, #5aa3ff 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.dialog-footer .el-button--default {
  background: #ffffff;
  border: 1px solid #dcdfe6;
  color: #606266;
}

.dialog-footer .el-button--default:hover {
  background: #f5f7fa;
  border-color: #c0c4cc;
  color: #409eff;
}
</style>
