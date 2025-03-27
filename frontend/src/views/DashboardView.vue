<template>
  <div class="dashboard-container">
    <div class="header-container">
      <el-page-header @back="goBack" title="返回" content="数据看板" />
      <el-space :size="20">
        <el-text type="info">学号：{{ userInfo.id }}</el-text>
        <el-text>{{ userInfo.name }}</el-text>
      </el-space>
      <el-button 
        type="danger" 
        @click="handleLogout"
        class="logout-btn"
      >
        退出登录
      </el-button>
    </div> 
    
    <!-- 图表容器 -->
    <div class="chart-container">
      <el-skeleton :loading="loading" animated :count="3">
        <template #template>
          <div class="chart-skeleton">
            <el-skeleton-item variant="image" style="width: 100%; height: 400px" />
          </div>
        </template>
        
        <BaseChart 
          :options="scoreChartOption" 
          :loading="loading"
          class="chart-item"
        />
        <BaseChart 
          :options="behaviorChartOption" 
          :loading="loading"
          class="chart-item"
        />
        <BaseChart 
          :options="progressChartOption"
          :loading="loading"
          class="chart-item"
        />
      </el-skeleton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import api from '@/services/api';
import { nextTick } from 'vue';
import BaseChart from '@/components/charts/BaseChart.vue';

const loading = ref(true);
const router = useRouter();

const goBack = () => {
  history.back();
};

const handleLogout = async () => {
  try {
    localStorage.removeItem('access_token');
    router.push('/login');
    ElMessage.success('已退出登录');
  } catch (error) {
    ElMessage.error('登出失败');
  }
};

const scoreChart = ref(null);
const behaviorChart = ref(null);
const progressChart = ref(null);

onMounted(async () => {
  await fetchData();
  loading.value = false;
});

const fetchData = async () => {
  try {
    loading.value = true;
    const [gradesRes, homeworkRes, discussionRes] = await Promise.all([
      api.getUserData(),
      api.getChartData()
    ]);

    console.log('原始成绩接口数据:', gradesRes.data);
    console.log('原始作业接口数据:', homeworkRes.data);
    console.log('原始讨论接口数据:', discussionRes.data);

    // 处理综合成绩数据
    const processGrades = gradesRes.data.map(item => ({
      course: item.course_name,
      points: item.course_points,
      score: item.comprehensive_score
    }));

    // 处理作业统计
    const homeworkStats = homeworkRes.data.reduce((acc, curr) => {
      acc.labels.push(curr.week);
      acc.scores.push(curr.average_score);
      return acc;
    }, { labels: [], scores: [] });

    // 处理讨论数据
    const heatmapData = discussionRes.data.map(item => {
    // 转换时间段为预设分类  
    const timeMap = {
      'morning': '早晨',
      'forenoon': '上午',
      'noon': '中午',
      'afternoon': '下午',
      'dusk': '傍晚',
      'night': '晚上'
    };
    
    return [
      item.weekday,
      timeMap[item.time_slot] || item.time_slot, // 保留原始值用于错误排查
      item.interaction_count
    ];
    });

    // 更新现有图表配置
    scoreChartOption.value = { 
      ...scoreChartOption.value,
      xAxis: { data: homeworkStats.labels },
      series: [{ data: homeworkStats.scores }]
    };

    // 新增雷达图配置
    radarChartOption.value.radar.indicator = processGrades.map(item => ({
      name: item.course,
      max: 100
    }));
    radarChartOption.value.series[0].data = [{
      value: processGrades.map(item => item.score),
      name: '综合成绩'
    }];

    // 新增热力图配置
    heatmapChartOption.value.series[0].data = heatmapData;

    await nextTick();
    initCharts();
  } catch (error) {
    console.error('数据获取失败:', error);
    ElMessage.error('图表数据加载失败');
  } finally {
    loading.value = false;
  }
};



const scoreChartOption = ref({
  title: { text: '成绩分布', left: 'center' },
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: [],
    axisLabel: { rotate: 45 }
  },
  yAxis: { type: 'value', name: '人数' },
  series: [{ type: 'bar', data: [], itemStyle: { color: '#5470c6' } }]
});

const behaviorChartOption = ref({
  title: { text: '学习行为分析', left: 'center' },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: [] },
  yAxis: { type: 'value', name: '活跃次数' },
  series: [{ 
  type: 'line', 
  smooth: true, 
  data: [], 
  itemStyle: { color: '#91cc75' },
  areaStyle: { opacity: 0.3 }
}]
});

const radarChartOption = ref({
  title: { text: '多维成绩对比', left: 'center' },
  radar: {
    indicator: [
      { name: '课程积分', max: 100 },
      { name: '综合成绩', max: 100 },
      { name: '作业平均', max: 100 },
      { name: '考试成绩', max: 100 }
    ]
  },
  series: [{
    type: 'radar',
    data: [],
    areaStyle: { opacity: 0.2 }
  }]
});

const heatmapChartOption = ref({
  title: { text: '学习活跃时段', left: 'center' },
  tooltip: { position: 'top' },
  xAxis: { type: 'category', data: ['周一','周二','周三','周四','周五','周六','周日'] },
  yAxis: { type: 'category', data: ['早晨','上午','中午','下午','傍晚','晚上'] },
  visualMap: { min: 0, max: 10, calculable: true },
  series: [{
    type: 'heatmap',
    data: [],
    itemStyle: { borderRadius: [5, 5, 0, 0] }
  }]
});

const progressChartOption = ref({
  title: { text: '课程完成度', left: 'center' },
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: '65%',
    data: [],
    color: ['#fac858', '#ee6666']
  }]
});

const initCharts = () => {
  const initChart = (dom, option, chartName) => {
    try {
      if (!dom.value) throw new Error(`DOM元素未找到: ${chartName}`);
      if (!option.series.some(s => s.data && s.data.length)) 
        throw new Error(`空数据图表: ${chartName}`);
      
      const chart = echarts.init(dom.value);
      chart.setOption(option);
      window.addEventListener('resize', () => chart.resize());
    } catch (error) {
      console.error(`${chartName}初始化失败:`, error);
      ElMessage.error(`${chartName}初始化失败: ${error.message}`);
    }
  };

  // 使用更新后的响应式option对象
  initChart(scoreChart, scoreChartOption.value, '成绩分布图');
  initChart(behaviorChart, behaviorChartOption.value, '行为分析图');
  initChart(progressChart, progressChartOption.value, '进度图表');
};
</script>

<style scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--el-border-color);
  margin-bottom: 20px;
}

.logout-btn {
  margin-left: auto;
  -webkit-appearance: none;
  appearance: none;
}

.chart-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  padding: 20px;
}

.chart-item {
  height: 400px;
  background: #fff;
  -webkit-background-clip: padding-box;
  background-clip: padding-box;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  -webkit-user-select: none;
  user-select: none;
  -webkit-touch-action: manipulation;
  touch-action: manipulation;
}
</style>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios' // 改为从node_modules导入

const userInfo = ref({ id: '', name: '' })

const fetchUserInfo = async () => {
    try {
      const response = await axios.get('/my-data', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      userInfo.value = {
        id: response.data.scores?.id || 'N/A',
        name: response.data.scores?.name || '未知用户'
      }
    } catch (error) {
      ElMessage.error('获取用户信息失败')
    }
  };

  onMounted(() => {
    fetchUserInfo();
  });
</script>

