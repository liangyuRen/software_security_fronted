<script setup lang="ts">
import {computed, reactive, ref, watch} from 'vue';
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
function getTooltipContent(language: string): string{
  console.log("当前项目", newProject)
  switch (language){
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
  <el-dialog v-model="dialogVisible" :title="getTitle" width="600">
    <el-form ref="formRef" :model="newProject" label-width="auto" style="max-width: 600px" :rules="rules">
      <el-form-item label="项目名称" prop="name" v-if="type == 'add' || type == 'edit'">
        <el-input v-model="newProject.name" placeholder="请输入项目名称" />
      </el-form-item>
      <el-form-item label="项目描述"  v-if="type == 'add' || type == 'edit'">
        <el-input v-model="newProject.description" type="textarea" placeholder="请输入项目描述" />
      </el-form-item>
      <el-form-item label="风险阈值" prop="risk_threshold"  v-if="type == 'add' || type == 'edit'">
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
            :on-success="handleFileUploadSuccess"
            :on-error="handleFileUploadError"
          >
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
            :on-success="handleFileUploadSuccess" drag
            style="width: 100%"
            :on-error="handleFileUploadError"
          >
            <el-icon class="el-icon--upload">
              <upload-filled />
            </el-icon>
            <div class="el-upload__text">
              <span>点击此处选择文件或将文件拖拽到此处上传</span>
            </div>
            <template #tip>
                <div class="el-upload__tip" style="display: flex; justify-content: flex-start; align-items: center; gap: 10px">
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
}

.upload-file-container {
  display: flex;
  flex-direction: column;
  align-items: start;

  span {
    font-size: 13px;
    font-weight: 500;
  }

  .selected-file {
    margin-top: 10px;
    display: flex;
    flex-direction: row;
  }

  .remove-button {
    margin-left: 10px;
  }

  .upload-success {
    color: #67c23a;
    font-weight: bold;
    margin-left: 10px;
  }
}

.upload-file-drag-container {
  display: flex;
  flex-direction: column;
  align-items: start;
  width: 100%;
  position: relative;
  margin: 0 20px;
  span {
    font-size: 13px;
    font-weight: 500;
  }

  .selected-file {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
  }

  .remove-button {
    margin-left: 10px;
  }

  .upload-success {
    color: #67c23a;
    font-weight: bold;
    margin-left: 10px;
  }
}
</style>
