<template>
  <div class="dashboard-container">
    <!-- 顶部导航栏 -->
    <div class="navbar">
      <el-page-header @back="goBack" content="数据可视化看板" class="page-header" />
      <div class="user-info">
        <el-tag type="info" effect="dark" size="large" class="user-id">
          {{ userInfo.id }}
        </el-tag>
        <el-divider direction="vertical" />
        <span class="username">{{ userInfo.name }}</span>
      </div>
    </div>

    <!-- 统计数据面板 -->
    <div class="stat-panel">
      <div class="stat-item">
        <div class="stat-title">综合成绩</div>
        <div class="stat-value">{{ scores.comprehensive }}</div>
        <el-progress :percentage="scores.comprehensive" :show-text="false" class="stat-progress" />
      </div>
      <div class="stat-item">
        <div class="stat-title">课程积分</div>
        <div class="stat-value">{{ scores.course_points }}</div>
        <el-progress :percentage="scores.course_points" status="success" :show-text="false" class="stat-progress" />
      </div>
      <div class="stat-item">
        <div class="stat-title">考试成绩</div>
        <div class="stat-value">{{ scores.exam }}</div>
        <el-progress :percentage="scores.exam" status="warning" :show-text="false" class="stat-progress" />
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="chart-grid">
      <!-- 作业成绩分布 -->
      <el-card class="chart-card">
        <div slot="header" class="chart-header">
          <span>作业成绩分布</span>
          <el-tooltip content="各次作业得分趋势" placement="top">
            <i class="el-icon-info chart-tooltip" />
          </el-tooltip>
        </div>
        <BaseChart :options="homeworkChartOptions" :loading="loading" class="responsive-chart" />
      </el-card>

      <!-- 学习行为分析 -->
      <el-card class="chart-card">
        <div slot="header" class="chart-header">
          <span>学习行为分析</span>
          <el-tooltip content="讨论/回帖/获赞数据" placement="top">
            <i class="el-icon-info chart-tooltip" />
          </el-tooltip>
        </div>
        <BaseChart :options="behaviorChartOptions" :loading="loading" class="responsive-chart" />
      </el-card>

      <!-- 视频学习热力图 -->
      <el-card class="chart-card">
        <div slot="header" class="chart-header">
          <span>视频学习时段分布</span>
          <el-tooltip content="不同时间段学习活跃度" placement="top">
            <i class="el-icon-info chart-tooltip" />
          </el-tooltip>
        </div>
        <BaseChart :options="heatmapOptions" :loading="loading" class="responsive-chart" />
      </el-card>
    </div>
  </div>
  <footer id="footer">
    <div class="container">
      <div class="copyright">Copyright &copy; 2025. <br>莆田学院 新工科产业学院 数据225 <br> 陈俊霖 <br> All rights reserved.</div>
      <div class="credits"></div>
    </div>
  </footer>

</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import api from '@/services/api';
import BaseChart from '@/components/charts/BaseChart.vue';
import * as echarts from 'echarts';

const router = useRouter();
const loading = ref(true);
const userInfo = ref({ id: '', name: '' });
const scores = ref({
  comprehensive: 0,
  course_points: 0,
  exam: 0
});

// 图表配置
const homeworkChartOptions = ref({
  color: ['#5470C6'],
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: ['作业2', '作业3', '作业4', '作业5', '作业6', '作业7', '作业8', '作业9'],
    axisLabel: { rotate: 45 }
  },
  yAxis: { type: 'value' },
  series: [{
    name: '成绩',
    type: 'bar',
    data: [],
    barWidth: '60%',
    itemStyle: {
      borderRadius: [5, 5, 0, 0],
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: '#5470C6' },
        { offset: 1, color: '#91CC75' }
      ])
    }
  }]
});

const behaviorChartOptions = ref({
  color: ['#EE6666'],
  tooltip: { trigger: 'item' },
  legend: { bottom: 10 },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: [
      { value: 0, name: '发帖讨论' },
      { value: 0, name: '回复讨论' },
      { value: 0, name: '获赞数' }
    ],
    label: { show: false },
    itemStyle: {
      borderRadius: 8,
      borderColor: '#fff',
      borderWidth: 2
    }
  }]
});

const heatmapOptions = ref({
  tooltip: { position: 'top' },
  xAxis: {
    type: 'category',
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  },
  yAxis: {
    type: 'category',
    data: ['早晨', '上午', '中午', '下午', '傍晚', '晚上']
  },
  visualMap: {
    min: 0,
    max: 10,
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: 10
  },
  series: [{
    type: 'heatmap',
    data: [],
    itemStyle: {
      borderRadius: [5, 5, 0, 0],
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: '#FAC858' },
        { offset: 1, color: '#EE6666' }
      ])
    }
  }]
});

// 生命周期钩子
onMounted(async () => {
  try {
    console.log('[DashboardView] 开始加载用户数据');
    const { data } = await api.getUserData();
    console.log('[DashboardView] 用户数据加载完成:', data);
    
    userInfo.value = data.user;
    scores.value = data.scores;

    // 更新图表数据
    console.log('[DashboardView] 开始更新图表数据');
    homeworkChartOptions.value.series[0].data = data.scores.homework;
    behaviorChartOptions.value.series[0].data = [
      { value: data.behavior.posted, name: '发帖讨论' },
      { value: data.behavior.replied, name: '回复讨论' },
      { value: data.behavior.upvotes, name: '获赞数' }
    ];
    heatmapOptions.value.series[0].data = data.progress.rumination_ratios.map((v, i) => [i % 7, Math.floor(i / 7), v]);
    console.log('[DashboardView] 图表数据更新完成');

  } catch (error) {
    console.error('[DashboardView] 数据加载失败:', error);
    ElMessage.error('数据加载失败');
  } finally {
    loading.value = false;
    console.log('[DashboardView] 数据加载流程结束');
  }
});

// 事件处理
const goBack = () => history.back();
const handleLogout = () => {
  localStorage.removeItem('access_token');
  router.push('/login');
  ElMessage.success('已安全退出');
};
</script>

<style lang="scss">
.user-id{
  background-color: #4e6fa3e4;
}

.dashboard-container {
  padding: 2rem;
  min-height: 100vh;
  background: #f5f7fa;

  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding: 1rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }

  .stat-panel {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;

    .stat-item {
      padding: 1.5rem;
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      transition: transform 0.3s ease;

      &:hover {
        transform: translateY(-5px);
      }

      .stat-title {
        color: #606266;
        margin-bottom: 0.5rem;
      }

      .stat-value {
        font-size: 2rem;
        font-weight: 600;
        color: #303133;
        margin: 1rem 0;
      }
    }
  }

  .chart-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;

    .chart-card {
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      transition: transform 0.3s ease;

      &:hover {
        transform: translateY(-5px);
      }

      .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .chart-tooltip {
          cursor: help;
          margin-left: 0.5rem;
          color: #909399;
        }
      }
    }
  }

  .responsive-chart {
    height: 400px;
  }
}
#footer {
  padding: 0 0 30px 0;
  color: #677184;
  font-size: 14px;
  text-align: center;
  background: #f5f7fa;
  bottom: 0ch;
  opacity: 0.8;
}
</style>