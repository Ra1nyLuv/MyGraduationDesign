<template>
  <div class="admin-dashboard">
    <h1>管理员数据看板</h1>
    <div class="stats-container">
      <el-card class="stat-card">
        <h3>用户总数</h3>
        <p class="stat-value">{{ userCount }}</p>
      </el-card>
      <el-card class="stat-card">
        <h3>活跃用户</h3>
        <p class="stat-value">{{ activeUsers }}</p>
      </el-card>
      <el-card class="stat-card">
        <h3>综合成绩</h3>
        <p class="stat-value">{{ avgScore.toFixed(2) }}</p>
        <p class="stat-range">最高: {{ maxScore.toFixed(2) }} 最低: {{ minScore.toFixed(2) }}</p>
      </el-card>
      <el-card class="stat-card">
        <h3>考试成绩</h3>
        <p class="stat-value">{{ avgExamScore.toFixed(2) }}</p>
        <p class="stat-range">最高: {{ maxExamScore.toFixed(2) }} 最低: {{ minExamScore.toFixed(2) }}</p>
      </el-card>
    </div>
    
    <div class="charts-container">
      <el-card class="chart-card">
        <h3>成绩分布</h3>
        <div class="chart-wrapper">
          <BaseChart :options="scoreDistributionOptions" />
        </div>
      </el-card>
      
      <el-card class="chart-card">
        <h3>用户活跃度</h3>
        <div class="chart-wrapper">
          <BaseChart :options="activityOptions" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import api from '@/services/api';
import BaseChart from '@/components/charts/BaseChart.vue';
import * as echarts from 'echarts';

const userCount = ref(0);
const activeUsers = ref(0);
const avgScore = ref(0);
const maxScore = ref(0);
const minScore = ref(0);
const avgExamScore = ref(0);
const maxExamScore = ref(0);
const minExamScore = ref(0);
const studentList = ref([]);

const scoreDistributionOptions = ref({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['60以下', '60-70', '70-80', '80-90', '90以上'] },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: [] }]
});

const activityOptions = ref({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: [
      { value: 0, name: '活跃用户' },
      { value: 0, name: '不活跃用户' }
    ]
  }]
});

onMounted(async () => {
  try {
    console.log('[AdminDashboardView] 开始请求管理员数据API');
    const res = await api.getAdminStats();
    console.log('[AdminDashboardView] API响应数据:', res.data);
    
    if (!res.data) {
      console.warn('[AdminDashboardView] API返回数据为空');
      return;
    }
    
    userCount.value = res.data.data.userCount;
    activeUsers.value = res.data.data.activeUsers;
    scoreDistributionOptions.value.series[0].data = Object.values(res.data.data.scoreDistribution);
    activityOptions.value.series[0].data[0].value = res.data.data.activeUsers;
    activityOptions.value.series[0].data[1].value = res.data.data.userCount - res.data.data.activeUsers;
    avgScore.value = res.data.data.avgComprehensiveScore;
    maxScore.value = res.data.data.maxComprehensiveScore;
    minScore.value = res.data.data.minComprehensiveScore;
    avgExamScore.value = res.data.data.avgExamScore;
    maxExamScore.value = res.data.data.maxExamScore;
    minExamScore.value = res.data.data.minExamScore;
    
    console.log('[AdminDashboardView] 数据赋值完成:', {
      userCount: userCount.value,
      activeUsers: activeUsers.value,
      avgScore: avgScore.value
    });
  } catch (error) {
    console.error('[AdminDashboardView] 获取管理员数据失败:', error);
    ElMessage.error('获取管理员数据失败');
  }
});
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
}

.stats-container {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-top: 10px;
}

.charts-container {
  display: flex;
  gap: 20px;
}

.chart-card {
  flex: 1;
}

.chart-wrapper {
  height: 400px;
}
</style>