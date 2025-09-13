<template>
  <div class="dashboard-container">
    <!-- 顶部导航栏 -->
    <div class="navbar">
      <el-page-header @back="goBack" content="学生用户画像" class="page-header" />
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
      <el-card class="chart-card behavior-analysis-card">
        <div slot="header" class="chart-header">
          <span>学习行为分析</span>
          <div class="header-actions">
            <el-tooltip content="讨论/回帖/获赞数据" placement="top">
              <i class="el-icon-info chart-tooltip" />
            </el-tooltip>
            <el-button-group class="chart-type-switcher">
              <el-button 
                :type="behaviorChartType === 'pie' ? 'primary' : ''"
                size="small"
                @click="switchBehaviorChart('pie')">
                饼图
              </el-button>
              <el-button 
                :type="behaviorChartType === 'radar' ? 'primary' : ''"
                size="small"
                @click="switchBehaviorChart('radar')">
                雷达图
              </el-button>
            </el-button-group>
          </div>
        </div>
        
        <!-- 数据概览卡片 -->
        <div class="behavior-overview">
          <div class="behavior-stat" v-for="(item, index) in behaviorStats" :key="index">
            <div class="stat-icon" :style="{ backgroundColor: item.color }">
              <i :class="item.icon"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-label">{{ item.label }}</div>
              <div class="stat-trend" :class="item.trend.type">
                <i :class="item.trend.icon"></i>
                {{ item.trend.text }}
              </div>
            </div>
          </div>
        </div>
        
        <BaseChart :options="currentBehaviorOptions" :loading="loading" class="responsive-chart" />
        
        <!-- 学习行为评估 -->
        <div class="behavior-assessment">
          <div class="assessment-header">
            <h4>学习行为评估</h4>
            <el-tag :type="behaviorLevel.type" size="small">{{ behaviorLevel.label }}</el-tag>
          </div>
          <div class="assessment-content">
            <el-progress
              :percentage="behaviorScore"
              :stroke-width="20"
              :show-text="false"
              :color="behaviorLevel.color"
              class="behavior-progress"
            />
            <div class="assessment-details">
              <span class="score-text">行为活跃度：{{ behaviorScore }}分</span>
              <p class="assessment-desc">{{ behaviorLevel.description }}</p>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 视频学习热力图 -->
      <el-card class="chart-card">
        <div slot="header" class="chart-header">
          <span>视频学习时段分布</span>
          <el-tooltip content="不同时间段学习活跃度" placement="top">
            <i class="el-icon-info chart-tooltip" />
          </el-tooltip>
        </div>
        <BaseChart :options="studydistributeOptions" :loading="loading" class="responsive-chart" />
      </el-card>
    </div>
  </div>
  
  <!-- 数据分析提示卡片 -->
  <div class="analysis-cards">
    <el-card class="analysis-card">
      <h3>学风与学业分析</h3>
      <p v-if="scores.comprehensive > 80">你的学习习惯很好，继续保持！</p>
      <div v-else-if="scores.comprehensive > 60">
        <p>你的学习习惯良好，但仍有提升空间：</p>
        <ul>
          <li v-if="!loading && behaviorChartOptions.value?.series?.[0]?.data?.[0]?.value < 5">建议增加课程讨论参与度，目前发帖{{behaviorChartOptions.value.series[0].data[0].value}}次</li>
          <li v-if="!loading && studydistributeOptions.value?.series?.[0]?.data?.filter(d => d[2] > 5).length < 3">视频学习时段分布不均匀，建议合理安排学习时间</li>
          <li v-if="!loading && homeworkChartOptions.value?.series?.[0]?.data?.some(score => score < 60)">部分作业成绩不理想，建议加强相关知识点复习</li>
        </ul>
      </div>
      <div v-else>
        <p>需要改进学习习惯：</p>
        <ul>
          <li>综合成绩较低，建议制定系统学习计划</li>
        </ul>
      </div>
      <div>
        <ul>
          <li v-if="!loading && scores.missing_homework_count === 0">无作业缺交情况，表现良好请继续保持</li>
          <li v-else-if="!loading && scores.eligible_for_exam">您已缺交{{scores.missing_homework_count}}次作业，若再有{{4 - scores.missing_homework_count}}次作业未交，将失去期末考试资格</li>
          <li v-else-if="!loading && !scores.eligible_for_exam">您已缺交{{scores.missing_homework_count}}次作业，失去期末考试资格</li>
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
      <div class="copyright">Copyright &copy; 2025. <br>莆田学院 计算机与大数据学院 数据225 <br> 陈俊霖 <br> All rights reserved.</div>
      <div class="credits"></div>
    </div>
  </footer>

</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
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
  exam: 0,
  missing_homework_count: 0,
  eligible_for_exam: true
}); 
const rank = ref(0);
const total_students = ref(0);
const tips = ref([
  '保持良好的学习习惯有助于提高成绩',
  '定期复习可以巩固知识点',
  '积极参与讨论有助于理解课程内容'
]);
const currentTipIndex = ref(0);

// 计算排名百分比
const rankPercentage = computed(() => {
  if (total_students.value === 0) return 0;
  return rank.value / total_students.value;
});

// 学习行为分析相关状态
const behaviorChartType = ref('pie'); // 当前图表类型
const behaviorStats = ref([]); // 行为统计数据
const behaviorScore = ref(0); // 行为活跃度评分
const behaviorLevel = ref({ // 行为级别
  type: 'info',
  label: '一般',
  color: '#909399',
  description: '学习行为活跃度待提升'
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
  tooltip: {
    trigger: 'item',
    formatter: function(params) {
      return `${params.name}<br/>
              数量: ${params.value}<br/>
              占比: ${params.percent}%<br/>
              <span style="color: ${params.color}">●</span> 活跃度指数: ${getBehaviorIndex(params.name, params.value)}`;
    }
  },
  legend: {
    bottom: 10,
    textStyle: {
      fontSize: 12,
      color: '#666'
    }
  },
  series: [{
    type: 'pie',
    radius: ['45%', '75%'],
    center: ['50%', '45%'],
    data: [
      { value: 0, name: '发帖讨论' },
      { value: 0, name: '回复讨论' },
      { value: 0, name: '获赞数' }
    ],
    label: {
      show: true,
      position: 'outside',
      formatter: function(params) {
        return `${params.name}\n${params.value}`;
      },
      fontSize: 12,
      fontWeight: 'bold'
    },
    labelLine: {
      show: true,
      length: 15,
      length2: 10,
      smooth: true
    },
    itemStyle: {
      borderRadius: 8,
      borderColor: '#fff',
      borderWidth: 3,
      shadowBlur: 10,
      shadowColor: 'rgba(0, 0, 0, 0.2)'
    },
    emphasis: {
      itemStyle: {
        shadowBlur: 20,
        shadowOffsetX: 0,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      },
      label: {
        show: true,
        fontSize: 14,
        fontWeight: 'bold'
      }
    },
    animationType: 'expansion',
    animationDuration: 1000,
    animationEasing: 'cubicOut'
  }]
});

// 雷达图配置
const behaviorRadarOptions = ref({
  tooltip: {
    trigger: 'item',
    formatter: function(params) {
      return `学习行为分析<br/>
              ${params.data.name}<br/>
              发帖讨论: ${params.data.value[0]}<br/>
              回复讨论: ${params.data.value[1]}<br/>
              获赞数: ${params.data.value[2]}`;
    }
  },
  radar: {
    indicator: [
      { name: '发帖讨论', max: 20 },
      { name: '回复讨论', max: 30 },
      { name: '获赞数', max: 25 }
    ],
    center: ['50%', '50%'],
    radius: '70%',
    axisName: {
      color: '#666',
      fontSize: 12
    },
    splitArea: {
      areaStyle: {
        color: ['rgba(250, 250, 250, 0.2)', 'rgba(200, 200, 200, 0.1)']
      }
    },
    splitLine: {
      lineStyle: {
        color: '#e6e6e6'
      }
    }
  },
  series: [{
    type: 'radar',
    data: [{
      value: [0, 0, 0],
      name: '学习行为',
      areaStyle: {
        color: new echarts.graphic.RadialGradient(0.5, 0.5, 0.5, [
          { offset: 0, color: 'rgba(102, 126, 234, 0.8)' },
          { offset: 1, color: 'rgba(102, 126, 234, 0.2)' }
        ])
      },
      lineStyle: {
        color: '#667eea',
        width: 3
      },
      itemStyle: {
        color: '#667eea',
        borderColor: '#fff',
        borderWidth: 2
      }
    }],
    animationDuration: 1500,
    animationEasing: 'cubicInOut'
  }]
});

const studydistributeOptions = ref({
  tooltip: {
    trigger: 'item',
    formatter: function(params) {
      return `${params.name}<br>学习活跃度: ${params.value[2]}<br>${getTimeRangeDescription(params.value[0])}`;
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '15%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['6:00', '9:00', '12:00', '15:00', '18:00', '21:00', '24:00'],
    axisLabel: {
      rotate: 45,
      color: '#6c757d',
      fontWeight: 'bold'
    },
    axisLine: {
      lineStyle: {
        color: '#6c757d'
      }
    },
    splitArea: {
      show: true
    }
  },
  yAxis: {
    type: 'category',
    show: false,
    splitArea: {
      show: true
    }
  },
  visualMap: {
    min: 0,
    max: 10,
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: '0%',
    inRange: {
      color: ['#f7fbff', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b']
    }
  },
  series: [{
    name: '学习活跃度',
    type: 'heatmap',
    data: [],
    label: {
      show: false
    },
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      }
    },
    progressive: 1000,
    animation: false
  }]
});

// 计算当前显示的行为图表配置
const currentBehaviorOptions = computed(() => {
  switch (behaviorChartType.value) {
    case 'radar':
      return behaviorRadarOptions.value;
    default:
      return behaviorChartOptions.value;
  }
});

// 切换行为图表类型
const switchBehaviorChart = (type) => {
  behaviorChartType.value = type;
};

// 获取行为指数
const getBehaviorIndex = (name, value) => {
  const weights = {
    '发帖讨论': 3,
    '回复讨论': 2,
    '获赞数': 2.5
  };
  return Math.round(value * (weights[name] || 1));
};

// 计算行为活跃度评分
const calculateBehaviorScore = (behaviorData) => {
  const posted = behaviorData.posted || 0;
  const replied = behaviorData.replied || 0;
  const upvotes = behaviorData.upvotes || 0;
  
  // 加权计算：发帖(3分) + 回复(2分) + 获赞(2.5分)
  const totalScore = (posted * 3 + replied * 2 + upvotes * 2.5);
  // 按100分制计算，假设满分标准为：发帖10次，回复20次，获赖20次
  const maxScore = 10 * 3 + 20 * 2 + 20 * 2.5; // 120分
  return Math.min(Math.round((totalScore / maxScore) * 100), 100);
};

// 获取行为级别
const getBehaviorLevel = (score) => {
  if (score >= 80) {
    return {
      type: 'success',
      label: '非常活跃',
      color: '#67c23a',
      description: '学习行为非常活跃，继续保持！'
    };
  } else if (score >= 60) {
    return {
      type: 'warning',
      label: '较为活跃',
      color: '#e6a23c',
      description: '学习行为较为活跃，可以适当增加参与度'
    };
  } else if (score >= 40) {
    return {
      type: 'info',
      label: '一般活跃',
      color: '#909399',
      description: '学习行为一般，建议更多参与讨论交流'
    };
  } else {
    return {
      type: 'danger',
      label: '活跃度低',
      color: '#f56c6c',
      description: '学习行为活跃度较低，建议增加课程参与度'
    };
  }
};

// 更新行为统计数据
const updateBehaviorStats = (behaviorData) => {
  const posted = behaviorData.posted || 0;
  const replied = behaviorData.replied || 0;
  const upvotes = behaviorData.upvotes || 0;
  
  behaviorStats.value = [
    {
      value: posted,
      label: '发帖讨论',
      icon: 'el-icon-edit',
      color: '#667eea',
      trend: {
        type: posted >= 5 ? 'positive' : 'neutral',
        icon: posted >= 5 ? 'el-icon-arrow-up' : 'el-icon-minus',
        text: posted >= 5 ? '表现良好' : '可以更多'
      }
    },
    {
      value: replied,
      label: '回复讨论',
      icon: 'el-icon-chat-dot-round',
      color: '#764ba2',
      trend: {
        type: replied >= 10 ? 'positive' : 'neutral',
        icon: replied >= 10 ? 'el-icon-arrow-up' : 'el-icon-minus',
        text: replied >= 10 ? '表现良好' : '可以更多'
      }
    },
    {
      value: upvotes,
      label: '获赞数',
      icon: 'el-icon-thumb',
      color: '#f093fb',
      trend: {
        type: upvotes >= 8 ? 'positive' : 'neutral',
        icon: upvotes >= 8 ? 'el-icon-arrow-up' : 'el-icon-minus',
        text: upvotes >= 8 ? '质量较高' : '可提升质量'
      }
    }
  ];
  
  // 计算行为评分
  behaviorScore.value = calculateBehaviorScore(behaviorData);
  behaviorLevel.value = getBehaviorLevel(behaviorScore.value);
};

// 更新所有行为图表数据
const updateAllBehaviorCharts = (behaviorData) => {
  const posted = behaviorData.posted || 0;
  const replied = behaviorData.replied || 0;
  const upvotes = behaviorData.upvotes || 0;
  
  // 更新饼图
  behaviorChartOptions.value.series[0].data = [
    { value: posted, name: '发帖讨论' },
    { value: replied, name: '回复讨论' },
    { value: upvotes, name: '获赞数' }
  ];
  
  // 更新雷达图
  behaviorRadarOptions.value.series[0].data[0].value = [posted, replied, upvotes];
  
  // 更新统计数据
  updateBehaviorStats(behaviorData);
};

function getTimeRangeDescription(index) {
  const descriptions = [
    '晨间学习效率较高',
    '上午专注力最佳时段',
    '午间休息时间',
    '下午学习黄金时段',
    '傍晚复习效果较好',
    '夜间学习需注意休息'
  ];
  return descriptions[index] || '';
}

// 生成学习行为模拟数据
const generateMockBehaviorData = () => {
  const mockData = {
    posted: Math.floor(Math.random() * 8) + 2,  // 2-9次发帖
    replied: Math.floor(Math.random() * 15) + 5, // 5-19次回复
    upvotes: Math.floor(Math.random() * 12) + 3  // 3-14次获赞
  };
  console.log('[DashboardView] 生成模拟学习行为数据:', mockData);
  return mockData;
};

// 生成视频学习时段分布模拟数据
const generateMockStudyDistributionData = () => {
  const mockData = [];
  // 生成7个时段的数据 (6:00, 9:00, 12:00, 15:00, 18:00, 21:00, 24:00)
  for (let timeIndex = 0; timeIndex < 7; timeIndex++) {
    // 模拟不同时段的学习活跃度
    let baseActivity;
    switch (timeIndex) {
      case 0: // 6:00 晨间
        baseActivity = Math.random() * 3 + 1; // 1-4
        break;
      case 1: // 9:00 上午
        baseActivity = Math.random() * 5 + 4; // 4-9
        break;
      case 2: // 12:00 午间
        baseActivity = Math.random() * 2 + 1; // 1-3
        break;
      case 3: // 15:00 下午
        baseActivity = Math.random() * 4 + 3; // 3-7
        break;
      case 4: // 18:00 傍晚
        baseActivity = Math.random() * 3 + 2; // 2-5
        break;
      case 5: // 21:00 夜间
        baseActivity = Math.random() * 6 + 5; // 5-11
        break;
      case 6: // 24:00 深夜
        baseActivity = Math.random() * 2 + 0.5; // 0.5-2.5
        break;
      default:
        baseActivity = Math.random() * 3 + 1;
    }
    
    // 转换为热力图数据格式 [x, y, value]
    mockData.push([timeIndex, 0, Math.round(baseActivity * 10) / 10]);
  }
  
  console.log('[DashboardView] 生成模拟视频学习时段分布数据:', mockData);
  return mockData;
};

// 检查学习行为数据是否为空或无效
const isEmptyBehaviorData = (behavior) => {
  if (!behavior) return true;
  const totalActivity = (behavior.posted || 0) + (behavior.replied || 0) + (behavior.upvotes || 0);
  return totalActivity === 0;
};

// 检查视频学习时段分布数据是否为空或无效
const isEmptyStudyDistributionData = (distributionData) => {
  if (!distributionData || !Array.isArray(distributionData)) return true;
  if (distributionData.length === 0) return true;
  
  // 检查是否所有数值都为0或无效
  const hasValidData = distributionData.some(item => {
    return Array.isArray(item) && item.length >= 3 && (item[2] > 0);
  });
  
  return !hasValidData;
};

// 生命周期钩子
onMounted(async () => {
  try {
    const studentId = route.query.id || '';
    console.log('[DashboardView] 开始加载用户数据');
    const { data } = await api.getUserData({ id: studentId });
    console.log('[DashboardView] 用户数据加载完成:', data);
    console.log('[DashboardView] 总学生数:', data.total_students);
    
    userInfo.value = data.user;
    scores.value = data.scores;
    rank.value = data.rank || 0;
    total_students.value = data.total_students || 0;
    console.log('[DashboardView] totalStudents赋值后:', total_students.value);
    currentTipIndex.value = Math.floor(Math.random() * tips.value.length);

    // 更新图表数据
    console.log('[DashboardView] 开始更新图表数据');
    homeworkChartOptions.value.series[0].data = data.scores.homework;
    
    // 检查学习行为数据，如果为空则生成模拟数据
    let behaviorData = data.behavior;
    if (isEmptyBehaviorData(behaviorData)) {
      behaviorData = generateMockBehaviorData();
      console.log('[DashboardView] 使用模拟学习行为数据');
    } else {
      console.log('[DashboardView] 使用真实学习行为数据');
    }
    
    // 更新所有行为相关图表和统计
    updateAllBehaviorCharts(behaviorData);
    
    // 检查视频学习时段分布数据，如果为空则生成模拟数据
    let studyDistributionData = data.progress.rumination_ratios.map((v, i) => [i % 7, Math.floor(i / 7), v]);
    if (isEmptyStudyDistributionData(studyDistributionData)) {
      studyDistributionData = generateMockStudyDistributionData();
      console.log('[DashboardView] 使用模拟视频学习时段分布数据');
    } else {
      console.log('[DashboardView] 使用真实视频学习时段分布数据');
    }
    
    studydistributeOptions.value.series[0].data = studyDistributionData;
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
        font-size: 16px;
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
        font-size: 16px;
        border-bottom: 1px solid #ebeef5;
        

        .chart-tooltip {
          cursor: help;
          margin-left: 0.5rem;
          color: #909399;
        }
        
        .header-actions {
          display: flex;
          align-items: center;
          gap: 15px;
          border-radius: 22px;
        }
        
        .chart-type-switcher {
          .el-button {
            padding: 4px 8px;
            font-size: 11px;
            
            &.el-button--primary {
              background: #409eff;
              border-color: #409eff;
            }
          }
        }
      }
      
      // 视频学习时段分布卡片
      &:nth-child(3) {
        max-width: 500px;
        
        .responsive-chart {
          height: 280px;
        }
        
        .chart-header {
          font-size: 16px;
        }
      }
    }
    
    // 学习行为分析特殊样式
    .behavior-analysis-card {
      .behavior-overview {
        display: grid;
        grid-template-columns: repeat(3, minmax(90px, 1fr));
        gap: 15px;
        margin-bottom: 10px;
        padding: 0 10px;
        
        .behavior-stat {
          display: flex;
          align-items: center;
          padding: 15px;
          background: linear-gradient(135deg, #f8f9ff 0%, #e8edff 100%);
          border-radius: 12px;
          border: 1px solid #e1e8ff;
          transition: all 0.3s ease;
          
          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
          }
          
          .stat-icon {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            color: white;
            font-size: 16px;
          }
          
          .stat-content {
            flex: 1;
            
            .stat-value {
              font-size: 24px;
              font-weight: bold;
              color: #2c3e50;
              margin: 0;
            }
            
            .stat-label {
              font-size: 12px;
              color: #7f8c8d;
              margin: 2px 0 4px 0;
            }
            
            .stat-trend {
              font-size: 11px;
              display: flex;
              align-items: center;
              gap: 4px;
              
              &.positive {
                color: #27ae60;
              }
              
              &.neutral {
                color: #95a5a6;
              }
            }
          }
        }
      }
      
      .behavior-assessment {
        margin-top: 20px;
        padding: 20px;
        background: linear-gradient(135deg, #f8f9ff 0%, #fff 100%);
        border-radius: 12px;
        border: 1px solid #e1e8ff;
        
        .assessment-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
          
          h4 {
            margin: 0;
            color: #2c3e50;
            font-size: 16px;
          }
        }
        
        .assessment-content {
          .behavior-progress {
            margin-bottom: 15px;
          }
          
          .assessment-details {
            display: flex;
            justify-content: space-between;
            align-items: center;
            
            .score-text {
              font-weight: 600;
              color: #667eea;
              font-size: 14px;
            }
            
            .assessment-desc {
              margin: 0;
              font-size: 13px;
              color: #7f8c8d;
              font-style: italic;
            }
          }
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
  font-size: 12px;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  text-align: center;
  background: white;
  bottom: 0ch;
  opacity: 0.8;
}
</style>