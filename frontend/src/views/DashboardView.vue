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
        <div class="stat-title">综合成绩
          <el-tag type="success" size="small" style="margin-left: 10px">
            排名: {{ rank }}
          </el-tag>
        </div>
        <div class="stat-value">{{ scores.comprehensive }}</div>
        <el-progress :percentage="scores.comprehensive" :show-text="false" class="stat-progress" />
        <div class="tips-container" v-if="tips.length > 0">
          <el-tooltip :content="tips[currentTipIndex]" placement="bottom">
            <el-icon><InfoFilled /></el-icon>
            <span style="margin-left: 5px">小贴士</span>
          </el-tooltip>
        </div>
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
  
  <!-- 数据分析提示卡片 -->
  <div class="analysis-cards">
    <el-card class="analysis-card">
      <h3>学习习惯分析</h3>
      <p v-if="scores.comprehensive > 80">你的学习习惯很好，继续保持！</p>
      <div v-else-if="scores.comprehensive > 60">
        <p>你的学习习惯良好，但仍有提升空间：</p>
        <ul>
          <li v-if="!loading && behaviorChartOptions.value?.series?.[0]?.data?.[0]?.value < 5">建议增加课程讨论参与度，目前发帖{{behaviorChartOptions.value.series[0].data[0].value}}次</li>
          <li v-if="!loading && heatmapOptions.value?.series?.[0]?.data?.filter(d => d[2] > 5).length < 3">视频学习时段分布不均匀，建议合理安排学习时间</li>
          <li v-if="!loading && homeworkChartOptions.value?.series?.[0]?.data?.some(score => score < 60)">部分作业成绩不理想，建议加强相关知识点复习</li>
        </ul>
      </div>
      <div v-else>
        <p>需要改进学习习惯：</p>
        <ul>
          <li>综合成绩较低，建议制定系统学习计划</li>
        </ul>
      </div>
    </el-card>
    
    <el-card class="analysis-card">
      <h3>成绩趋势分析</h3>
      <div v-if="rankPercentage <= 0.1">
        <p>你的成绩排名前10%(第{{rank}}名)，表现非常优秀！</p>
        <ul>
          <li>综合成绩：{{scores.comprehensive}}分</li>
          <li>考试成绩：{{scores.exam}}分</li>
          <li>继续保持当前学习状态，争取更高分数</li>
        </ul>
      </div>
      <div v-else-if="rankPercentage <= 0.3">
        <p>你的成绩排名前10-30%(第{{rank}}名)，表现良好</p>
        <ul>
          <li>综合成绩：{{scores.comprehensive}}分</li>
          <li v-if="scores.exam < scores.comprehensive">考试成绩({{scores.exam}}分)低于综合成绩，建议加强考试技巧</li>
          <li>分析错题本，针对性提高薄弱环节</li>
        </ul>
      </div>
      <div v-else-if="rankPercentage <= 0.6">
        <p>你的成绩排名30-60%(第{{rank}}名)，还有较大提升空间</p>
        <ul>
          <li>综合成绩：{{scores.comprehensive}}分</li>
          <li v-if="scores.exam < 70">考试成绩({{scores.exam}}分)不理想，建议多做模拟题</li>
          <li>制定每周学习计划，保持规律学习</li>
        </ul>
      </div>
      <div v-else-if="rankPercentage <= 0.9">
        <p>你的成绩排名60-90%(第{{rank}}名)，需要重点关注</p>
        <ul>
          <li>综合成绩：{{scores.comprehensive}}分</li>
          <li v-if="scores.exam < 60">考试成绩({{scores.exam}}分)较差，建议系统复习</li>
          <li>参加学习小组，向优秀同学请教方法</li>
        </ul>
      </div>
      <div v-else>
        <p>你的成绩排名后10%(第{{rank}}名)，急需改进</p>
        <ul>
          <li>综合成绩：{{scores.comprehensive}}分</li>
          <li v-if="scores.exam < 50">考试成绩({{scores.exam}}分)非常不理想</li>
          <li>联系老师或助教，获取个性化辅导</li>
          <li>每天保证至少3小时专注学习时间</li>
        </ul>
      </div>
    </el-card>
    
    <el-card class="analysis-card">
      <h3>提升建议</h3>
      <p v-if="scores.exam < 60">考试成绩不理想，建议多做模拟题。</p>
      <div v-else-if="scores.exam < 80">
        <p>考试成绩良好({{scores.exam}}分)</p>
        <ul>
          <li>建议分析错题，针对性提高</li>
          <li v-if="!loading && homeworkChartOptions.value?.series?.[0]?.data?.filter(score => score < 70).length > 0">有{{homeworkChartOptions.value.series[0].data.filter(score => score < 70).length}}次作业成绩低于70分</li>
          <li v-if="!loading && behaviorChartOptions.value?.series?.[0]?.data?.[2]?.value < 5">获赞数较少({{behaviorChartOptions.value.series[0].data[2].value}}次)，建议提高讨论质量</li>
        </ul>
      </div>
      <p v-else>考试成绩优秀，继续保持！</p>
    </el-card>
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
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import api from '@/services/api';
import BaseChart from '@/components/charts/BaseChart.vue';
import * as echarts from 'echarts';

const router = useRouter();
const loading = ref(true);
const route = useRoute();
const userInfo = ref({ id: '', name: '' });
const scores = ref({
  comprehensive: 0,
  course_points: 0,
  exam: 0
});
const rank = ref(0);
const tips = ref([
  '保持良好的学习习惯有助于提高成绩',
  '定期复习可以巩固知识点',
  '积极参与讨论有助于理解课程内容'
]);
const currentTipIndex = ref(0);

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
    const studentId = route.query.id || '';
    console.log('[DashboardView] 开始加载用户数据');
    const { data } = await api.getUserData({ id: studentId });
    console.log('[DashboardView] 用户数据加载完成:', data);
    
    userInfo.value = data.user;
    scores.value = data.scores;
    rank.value = data.rank || 0;
    currentTipIndex.value = Math.floor(Math.random() * tips.value.length);

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
  padding: 1rem;
  min-height: 23vh;
  background: white;
  border-radius: 12px;

  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding: 1.3rem;
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
      
      .tips-container {
        margin-top: 10px;
        font-size: 0.8rem;
        color: #909399;
        cursor: pointer;
        &:hover {
          color: #409EFF;
        }
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
.analysis-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
  padding: 0;

  .analysis-card {
    padding: 1.5rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    text-align: left;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }

    h3 {
      color: #303133;
      font-size: 1.1rem;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid #ebeef5;
    }

    p {
      color: #606266;
      font-size: 0.95rem;
      line-height: 1.6;
      margin-bottom: 1rem;
    }

    ul {
      padding-left: 1.5rem;
      margin: 0.5rem 0 1rem;

      li {
        color: #606266;
        font-size: 0.9rem;
        line-height: 1.8;
        margin-bottom: 0.3rem;
      }
    }
  }
}

#footer {
  padding: 0 0 30px 0;
  color: #677184;
  font-size: 14px;
  text-align: center;
  background: white;
  bottom: 0ch;
  opacity: 0.8;
}
</style>