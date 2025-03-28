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
  if (!chartEl.value) return;
  console.log('[BaseChart] 开始初始化图表');

  try {
    chartInstance = echarts.init(chartEl.value);
    console.log('[BaseChart] ECharts实例创建成功');
    chartInstance.setOption(props.options);
    console.log('[BaseChart] 图表配置已应用:', props.options);
    
    // 响应式容器尺寸变化
    observer = new ResizeObserver(() => {
      console.log('[BaseChart] 检测到容器尺寸变化，重新调整图表');
      chartInstance?.resize();
    });
    observer.observe(chartEl.value);
    console.log('[BaseChart] 已添加容器尺寸监听器');
  } catch (error) {
    console.error('[BaseChart] 图表初始化失败:', error);
  }
};

const disposeChart = () => {
  if (chartInstance) {
    console.log('[BaseChart] 开始销毁图表实例');
    observer?.unobserve(chartEl.value);
    chartInstance.dispose();
    chartInstance = null;
    console.log('[BaseChart] 图表实例已销毁');
  }
};

watch(() => props.options, (newVal) => {
  if (chartInstance) {
    console.log('[BaseChart] 检测到图表配置更新:', newVal);
    chartInstance.setOption(newVal);
  }
}, { deep: true });

onMounted(initChart);
onUnmounted(disposeChart);
</script>

<style scoped>
.base-chart {
  position: relative;
  transition: all 0.3s ease;
}
</style>