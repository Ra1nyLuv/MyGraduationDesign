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

  try {
    chartInstance = echarts.init(chartEl.value);
    chartInstance.setOption(props.options);
    
    // 响应式容器尺寸变化
    observer = new ResizeObserver(() => {
      chartInstance?.resize();
    });
    observer.observe(chartEl.value);
  } catch (error) {
    console.error('图表初始化失败:', error);
  }
};

const disposeChart = () => {
  if (chartInstance) {
    observer?.unobserve(chartEl.value);
    chartInstance.dispose();
    chartInstance = null;
  }
};

watch(() => props.options, (newVal) => {
  if (chartInstance) {
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