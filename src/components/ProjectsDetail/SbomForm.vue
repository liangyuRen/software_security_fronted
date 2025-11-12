<script setup lang="ts">
import { computed, ref, VueElement, watch } from 'vue';
import { getSbomFile } from './service';

const props = withDefaults(
  defineProps<{
    // info: DangerInfo
    projectName: string
    projectId: number
  }>(),
  {
  }
);
const sbomformVisible = ref<boolean>(false);
const fileType = ref<string>('json')
const sbomType = ref<string | null>()
const fileName = ref<string>(props.projectName == '' ? 'sbom' : props.projectName + '_sbom');

// const folderPath = ref<string>('');
// const folderInput = ref<VueElement | null>();
const fileLoading = ref<boolean>(false)
const exportFile = () => {
  fileLoading.value = true;
  getSbomFile(props.projectId, type.value, fileName.value)
    .then(res => {
      // 创建一个Blob对象
      const url = window.URL.createObjectURL(new Blob([res.data]));

      // 创建一个a标签
      const link = document.createElement('a');
      link.href = url;

      // 设置下载文件名，可以根据后端生成的文件名进行动态命名
      link.setAttribute('download', fileName.value + type.value); // Specify the file name here

      // 模拟点击a标签
      document.body.appendChild(link);
      link.click();

      // 清除url对象和a标签
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    })

  sbomformVisible.value = false;
}
const type = computed(() => {
  let res = ''
  if (sbomType.value) {
    res += '.' + sbomType.value
  }
  res += '.' + fileType.value
  return res
})
// const promptFolderSelection = () => {
//   if (folderInput.value) {
//     folderInput.value.click();
//   }
// }
// const handleFolderSelect = event => {
//   let res = Array.from(event.target.files);
//   console.log(res);
// };

const sbomIntro = computed(() => {
  const intro: { [key in string]: string } = {
    cdx: 'CyCloneDX（CycloneDX）：是一种用于生成和管理软件物料清单（SBOM）的格式，特别针对云原生应用，强调自动化生成和来自多种来源的数据整合，便于供应链管理和合规性检查，适合复杂的微服务架构。',
    spdx: 'SPDX（Software Package Data Exchange）：开放标准，旨在促进软件包信息的共享与记录，支持详细的许可证、版权、版本等信息。它广泛应用于开源软件社区，促进透明性和合作。',
    swid: 'SWID（Software Identification Tag）：是一种软件标识标签格式，旨在帮助组织识别和管理其软件资产。SWID标签支持合规性检测与安全审查，通常用于企业的资产管理和合规审核。',
  }
  if (sbomType.value) {
    return intro[sbomType.value]
  }
  return '可选项，支持生成多种格式的 SBOM 清单'
})
</script>

<template>
  <el-button type="primary" color="#336fff" @click="sbomformVisible = true">导出SBOM</el-button>
  <el-dialog v-model="sbomformVisible" title="导出SBOM" width="40%">
    <div class="sbom">
      <div class="intro">SBOM 是软件材料清单，它提供了对软件供应链的可见性，包括组件的版本、许可证信息、漏洞等。SBOM 旨在帮助组织更好地管理和控制软件供应链，识别和处理潜在的漏洞、合规性问题和安全风险
      </div>
      <div class="type">
        <span class="label">生成工具</span>
        <div class="right">
          <el-radio-group v-model="sbomType">
            <el-radio value="cdx">CyCloneDX</el-radio>
            <el-radio value="spdx">SPDX</el-radio>
            <el-radio value="swid">SWID</el-radio>
          </el-radio-group>
          <div class="sbom-intro">{{ sbomIntro }}</div>
        </div>
      </div>
      <div class="type">
        <span class="label">文件格式</span>
        <el-radio-group v-model="fileType">
          <el-radio value="json">JSON</el-radio>
          <el-radio value="xml">XML</el-radio>
          <!-- <el-radio value="swid">SWID</el-radio> -->
        </el-radio-group>
      </div>
      <div class="type">
        <span class="label">文件名</span>
        <el-input v-model="fileName" style="width: 240px" placeholder="请输入文件名" />
        <span class="text">{{ type }}</span>
        <!-- <el-button type="primary" plain @click="promptFolderSelection">选择路径</el-button> -->
        <!-- <input type="file" ref="folderInput" webkitdirectory style="display: none" @change="handleFolderSelect"
          @click="resetInput" /> -->
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="sbomformVisible = false">取消</el-button>
        <el-button type="primary" @click="exportFile">
          确认导出
        </el-button>
      </div>
    </template>
  </el-dialog>


</template>

<style scoped>
.sbom {
  width: 95%;
  margin: 0 auto;

  .intro {
    color: #57606a;
    font-weight: 500;
    margin: 10px 0 30px 0;
  }

  .type {
    display: flex;
    /* align-items: center; */
    margin: 10px 0;

    .label {
      /* font-size: 12px; */
      color: #333;
      margin-right: 20px;
      width: 60px;
      height: 32px;
      line-height: 32px;
    }

    .right {
      flex: 1;
    }

    .text {
      margin-left: 10px;
      height: 32px;
      line-height: 32px;
    }
  }

  .sbom-intro {
    margin-top: 5px;
    color: #555557;
    background-color: #dedfe053;
    padding: 10px;
    font-size: 12px;
  }
}



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
