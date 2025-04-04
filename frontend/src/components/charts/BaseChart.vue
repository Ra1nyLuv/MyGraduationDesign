<template>
  <div class="base-chart">
    <el-skeleton :loading="loading" animated>
      <template #template>
        <el-skeleton-item variant="image" style="width: 100%; height: 400px" />
      </template>
      <div ref="chartEl" :style="{ height: height, width: width }" />
    </el-skeleton>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
    options: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  height: {
    type: String,
    default: '400px'
  },
  width: {
    type: String,
    default: '100%' 
  }
});

const chartEl = ref(null);
let chartInstance = null;
let observer = null;

const initChart = () => {
  if (!chartEl.value) {
    // console.warn('[BaseChart] 图表容器未准备好');
    setTimeout(initChart, 100);
    return;
  }
  
  // 确保容器已渲染且具有尺寸
  if (chartEl.value.offsetWidth === 0 || chartEl.value.offsetHeight === 0) {
    // console.warn('[BaseChart] 图表容器尺寸为0，延迟初始化');
    setTimeout(initChart, 100);
    return;
  }

  // 如果已有实例且正在加载数据，则直接返回
  if (chartInstance && props.loading) {
    // console.log('[BaseChart] 数据仍在加载中，跳过重复初始化');
    return;
  }

  // console.log('[BaseChart] 开始初始化图表');
  
  // 确保先销毁已有实例
  if (chartInstance) {
    disposeChart();
  }

  try {
    // 确保options有数据
    if (Object.keys(props.options).length > 0) {
      // 等待loading状态变为false
      if (props.loading) {
        // console.log('[BaseChart] 数据仍在加载中，延迟初始化');
        setTimeout(initChart, 100);
        return;
      }
      
      // 确保没有重复创建实例
      if (!chartInstance) {
        chartInstance = echarts.init(chartEl.value);
        // console.log('[BaseChart] ECharts实例创建成功');
      }
      
      // 设置图表配置
      chartInstance.setOption({
        ...props.options,
        notMerge: true
      }, true);
      // console.log('[BaseChart] 图表配置已应用:', props.options);
      
      // 响应式容器尺寸变化
      if (!observer) {
        observer = new ResizeObserver(() => {
          // console.log('[BaseChart] 检测到容器尺寸变化，重新调整图表');
          chartInstance?.resize();
        });
        observer.observe(chartEl.value);
        // console.log('[BaseChart] 已添加容器尺寸监听器');
      }
    } else {
      // console.warn('[BaseChart] 图表数据未准备好,延迟初始化');
      setTimeout(initChart, 100);
    }
  } catch (error) {
    // console.error('[BaseChart] 图表初始化失败:', error);
    // 初始化失败时清理资源
    disposeChart();
  }
};

const disposeChart = () => {
  if (chartInstance) {
    // console.log('[BaseChart] 开始销毁图表实例');
    if (observer && chartEl.value) {
      observer.unobserve(chartEl.value);
    }
    chartInstance.dispose();
    chartInstance = null;
    // console.log('[BaseChart] 图表实例已销毁');
  }
};

watch(() => props.loading, (newVal) => {
  // console.log('[BaseChart] 检测到loading状态变化:', newVal);
  if (!newVal && Object.keys(props.options).length > 0) {
    disposeChart();
    initChart();
  }
}, { immediate: true });

watch(() => props.options, (newVal) => {
  // console.log('[BaseChart] 检测到图表配置更新:', newVal);
  if (!props.loading && Object.keys(props.options).length > 0) {
    disposeChart();
    initChart();
  } else if (Object.keys(props.options).length === 0) {
    // console.log('[BaseChart] 图表数据为空，等待数据加载');
    setTimeout(() => initChart(), 100);
  }
}, { deep: true, immediate: true });

onMounted(initChart);
onUnmounted(disposeChart);
</script>

<style scoped>
.base-chart {
  position: relative;
  transition: all 0.3s ease;
}
</style>