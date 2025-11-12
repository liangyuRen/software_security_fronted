<script setup lang="ts">
import { onMounted, getCurrentInstance, defineExpose, ref, watch } from 'vue'

defineOptions({
  name: 'WChart'
})
// defineExpose 让父组件可调用此方法
defineExpose({
  setData
})

// 组件传参
const props = defineProps({
  width: {
    type: String, //参数类型
    default: '100%', //默认值
    required: false //是否必须传递
  },
  height: {
    type: String,
    default: '10rem',
    required: true
  },
  option: {
    type: Object,
    default: () => {
      return {}
    },
    required: true
  },
  // 初始化之前的工作，比如加载百度地图相关数据
  initBefore: {
    type: Function,
    required: false
  },
  // 初始化之后的工作，比如添加百度地址控件
  initAfter: {
    type: Function,
    required: false
  }
})

let chart: { setOption: (arg0: Record<string, any>) => void; resize: () => void }
const wchart = ref(null)

//声明周期函数，自动执行初始化
onMounted(() => {
  init()
  // 监控窗口大小，自动适应界面
  window.addEventListener('resize', resize, false)
})

//初始化函数
function init() {
  // 基于准备好的dom，初始化echarts实例
  const dom = wchart.value
  // 通过 internalInstance.appContext.config.globalProperties 获取全局属性或方法
  const internalInstance = getCurrentInstance()
  const echarts = internalInstance?.appContext.config.globalProperties.$echarts

  chart = echarts.init(dom, 'weizwz')
  // 渲染图表
  if (props.initBefore) {
    props.initBefore(chart).then((data: Record<string, any>) => {
      setData(data)
      if (props.initAfter) props.initAfter(chart)
    })
  } else {
    chart.setOption(props.option)
    if (props.initAfter) props.initAfter(chart)
  }
}

// 监视 option 的变化
watch(() => props.option, (newOption) => {
  if (chart) {
    chart.setOption(newOption)
    console.log('new Option')
    console.log(newOption)
  }
})

function resize() {
  chart.resize()
}
// 父组件可调用，设置动态数据
function setData(option: Record<string, any>) {
  chart.setOption(option)
}
</script>

<template>
  <div ref="wchart" :style="`width: ${props.width} ; height: ${props.height}`" />
</template>

<style lang="scss" scoped></style>
