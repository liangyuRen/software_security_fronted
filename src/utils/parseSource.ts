// 导入图标文件
import avdIcon from '@/assets/sourceIcon/avd.ico'
import nvdIcon from '@/assets/sourceIcon/nvd.ico'
import githubIcon from '@/assets/sourceIcon/github.png'

export function getSourceName(source: string) {
  // source is an url string, e.g. "https://avd.aliyun.com/avd/detail/12345"
  // return "阿里云"
  if (source.includes("avd.aliyun.com")) {
    return "阿里云"
  }
  if (source.includes("nvd.nist.gov")){
    return "NVD"
  }
  if (source.includes("github.com")){
    return "Github"
  }
}

export function getSourceIcon(source: string) {
  if (source.includes("avd.aliyun.com")) {
    return avdIcon
  }
  if (source.includes("nvd.nist.gov")){
    return nvdIcon
  }
  if (source.includes("github.com")){
    return githubIcon
  }
}
