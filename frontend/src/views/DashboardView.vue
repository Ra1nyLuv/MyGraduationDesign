<template>
  <div class="dashboard-container">
    <el-page-header @back="goBack" title="返回" content="数据看板" />
    <!-- 添加导航菜单 -->
    <el-menu mode="horizontal" class="nav-menu">
      <el-menu-item index="1">数据看板</el-menu-item>
      <el-menu-item index="2" @click="handleLogout">退出登录</el-menu-item>
    </el-menu>
    <div class="stat-cards">
      <el-card v-for="(stat, index) in stats" :key="index" class="stat-card">
        <div class="stat-icon">
          <el-icon :size="30" :color="stat.color">
            <component :is="stat.icon" />
          </el-icon>
        </div>
        <div class="stat-info">
          <div class="value">{{ stat.value }}</div>
          <div class="label">{{ stat.label }}</div>
        </div>
      </el-card>
    </div>
    <el-card class="chart-card">
      <template #header>
        <span>月度访问趋势</span>
        <el-tooltip content="基于最近6个月的数据" placement="top">
          <el-icon><QuestionFilled /></el-icon>
        </el-tooltip>
      </template>
      <div ref="chart" class="chart"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';
import api from '@/services/api';
import {
  UserFilled,
  Document,
  Histogram,
  QuestionFilled,
} from '@element-plus/icons-vue'; // 导入图标组件

const chart = ref(null);
const stats = ref([
  { value: 0, label: '总用户数', icon: UserFilled, color: '#409EFF' },
  { value: 0, label: '今日访问', icon: Document, color: '#67C23A' },
  { value: 0, label: '异常次数', icon: Histogram, color: '#F56C6C' },
]);

onMounted(async () => {
  try {
    const res = await api.getChartData();
    const data = res.data;

    // 更新统计卡片
    stats.value = [
      { ...stats.value[0], value: data.totalUsers || 0 },
      { ...stats.value[1], value: data.todayVisits || 0 },
      { ...stats.value[2], value: data.errors || 0 },
    ];

    // 初始化图表
    const chartInstance = echarts.init(chart.value);
    chartInstance.setOption({
      title: { text: '月度访问量趋势' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data.labels },
      yAxis: { type: 'value' },
      series: [
        {
          name: '访问量',
          type: 'line',
          data: data.visits,
          smooth: true,
        },
      ],
    });
  } catch (error) {
    console.error('数据加载失败:', error);
  }
});

const goBack = () => {
  history.back();
};

// 添加退出登录方法
const handleLogout = async () => {
  try {
    await api.post('/logout');
    localStorage.removeItem('access_token');
    router.push('/login');
  } catch (error) {
    ElMessage.error('登出失败');
  }
};

// 完善图表数据获取
onMounted(async () => {
  try {
    const res = await api.getChartData();
    stats.value = res.data.stats;
    initChart(res.data.chartData);
  } catch (error) {
    ElMessage.error('数据加载失败');
  }
});

// 添加图表初始化方法
const initChart = (data) => {
  const chartInstance = echarts.init(chart.value);
  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: data.scoreDistribution.map(item => item.scoreRange),
      name: '分数区间'
    },
    yAxis: { type: 'value', name: '学生数量' },
    series: [{
      name: '成绩分布',
      type: 'bar',
      data: data.scoreDistribution.map(item => item.count),
      itemStyle: { color: '#409EFF' }
    }]
  });

  // 添加课程进度环形图
  const pieChart = echarts.init(document.createElement('div'));
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      name: '课程进度',
      type: 'pie',
      radius: ['40%', '70%'],
      data: data.courseProgress,
      label: { show: false },
      emphasis: { label: { show: true } }
    }]
  });
  chart.value.parentElement.appendChild(pieChart.getDom());
};
</script>

<style scoped>
.nav-menu {
  margin-bottom: 20px;
}
.dashboard-container {
  padding: 20px;
}
.stat-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}
.stat-card {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.stat-info {
  text-align: right;
  padding-right: 20px;
}
.chart-card {
  margin-top: 20px;
}
.chart {
  width: 100%;
  height: 400px;
}
</style>
