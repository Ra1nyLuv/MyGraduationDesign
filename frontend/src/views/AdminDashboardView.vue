<template>
  <div class="admin-dashboard">
    <div style="display: flex; justify-content: space-between; align-items: center">
      <h1>管理员数据看板</h1>
      <div class="header-actions">
        <el-button type="success" @click="trainMLModels" :loading="mlManagement.modelTraining.loading">
          <el-icon><Setting /></el-icon>
          训练ML模型
        </el-button>
        <el-button type="primary" @click="goToDataImport">
          <el-icon><Upload /></el-icon>
          从文件导入数据
        </el-button>
      </div>
    </div>
    
    <!-- 导航标签页 -->
    <el-tabs v-model="activeTab" type="border-card" style="margin: 20px 0;" @tab-change="handleTabChange">
      <!-- 数据概览 -->
      <el-tab-pane label="数据概览" name="overview">
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
      </el-tab-pane>
      
      <!-- ML分析 -->
      <el-tab-pane label="智能分析" name="ml-analysis">
        <div class="ml-analysis-panel">
          <div class="panel-header">
            <h2>🤖 机器学习分析管理</h2>
            <el-button type="primary" @click="refreshMLAnalysis" :loading="mlManagement.loading">
              <el-icon><Refresh /></el-icon>
              刷新分析
            </el-button>
          </div>
          
          <!-- 聚类分析结果 -->
          <el-card v-if="mlManagement.clusterAnalysis" class="analysis-result-card">
            <template #header>
              <div class="card-header">
                <span>📊 学习行为聚类分析</span>
                <el-tag type="info">总学生数: {{ mlManagement.clusterAnalysis.total_students }}</el-tag>
              </div>
            </template>
            
            <div class="cluster-distribution">
              <div v-for="(cluster, clusterId) in mlManagement.clusterAnalysis.cluster_distribution" 
                   :key="clusterId" 
                   class="cluster-item">
                <div class="cluster-header">
                  <el-tag :color="getClusterTypeColor(clusterId)" effect="dark" size="large">
                    {{ cluster.name }}
                  </el-tag>
                  <span class="cluster-stats">
                    {{ cluster.count }}人 ({{ cluster.percentage.toFixed(1) }}%)
                  </span>
                </div>
                
                <div class="cluster-progress">
                  <el-progress :percentage="cluster.percentage" :stroke-width="20" :show-text="false" />
                </div>
                
                <div v-if="cluster.users.length > 0" class="cluster-users">
                  <el-collapse>
                    <el-collapse-item :title="`查看 ${cluster.users.length} 名学生详情`">
                      <div class="user-tags">
                        <el-tag v-for="userId in cluster.users.slice(0, 10)" 
                                :key="userId" 
                                class="user-tag"
                                @click="handleView({id: userId})">
                          {{ userId }}
                        </el-tag>
                        <el-tag v-if="cluster.users.length > 10" type="info">
                          +{{ cluster.users.length - 10 }}更多...
                        </el-tag>
                      </div>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </div>
            </div>
          </el-card>
          
          <!-- 异常检测结果 -->
          <el-card v-if="mlManagement.anomalyDetection" class="analysis-result-card">
            <template #header>
              <div class="card-header">
                <span>⚠️ 异常行为检测</span>
                <el-tag :type="mlManagement.anomalyDetection.anomaly_rate > 20 ? 'danger' : mlManagement.anomalyDetection.anomaly_rate > 10 ? 'warning' : 'success'">
                  异常率: {{ mlManagement.anomalyDetection.anomaly_rate.toFixed(1) }}%
                </el-tag>
              </div>
            </template>
            
            <div class="anomaly-summary">
              <div class="summary-stats">
                <div class="stat-item">
                  <span class="label">总检测人数：</span>
                  <span class="value">{{ mlManagement.anomalyDetection.total_users }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">异常人数：</span>
                  <span class="value anomaly-count">{{ mlManagement.anomalyDetection.anomaly_count }}</span>
                </div>
              </div>
              
              <div v-if="mlManagement.anomalyDetection.anomalies.length > 0" class="anomaly-list">
                <h4>异常学生列表：</h4>
                <div class="anomaly-students">
                  <el-card v-for="anomaly in mlManagement.anomalyDetection.anomalies.slice(0, 5)" 
                           :key="anomaly.user_id" 
                           class="anomaly-student-card"
                           @click="handleView({id: anomaly.user_id})">
                    <div class="student-info">
                      <div class="student-basic">
                        <strong>{{ anomaly.user_name }}</strong>
                        <el-tag size="small" type="info">{{ anomaly.user_id }}</el-tag>
                      </div>
                      
                      <div class="risk-info">
                        <el-tag :type="anomaly.anomaly_info.details?.risk_level === 'high' ? 'danger' : 
                                      anomaly.anomaly_info.details?.risk_level === 'medium' ? 'warning' : 'info'" 
                                size="small">
                          {{ anomaly.anomaly_info.details?.risk_level === 'high' ? '高风险' :
                              anomaly.anomaly_info.details?.risk_level === 'medium' ? '中风险' : '低风险' }}
                        </el-tag>
                        <span class="anomaly-score">
                          异常分数: {{ anomaly.anomaly_info.anomaly_score.toFixed(2) }}
                        </span>
                      </div>
                      
                      <div v-if="anomaly.anomaly_info.details?.primary_concerns" class="concerns">
                        <el-tag v-for="concern in anomaly.anomaly_info.details.primary_concerns.slice(0, 2)" 
                                :key="concern" 
                                size="small" 
                                type="warning" 
                                class="concern-tag">
                          {{ concern.length > 20 ? concern.substring(0, 20) + '...' : concern }}
                        </el-tag>
                      </div>
                    </div>
                  </el-card>
                  
                  <div v-if="mlManagement.anomalyDetection.anomalies.length > 5" class="more-anomalies">
                    <el-alert title="还有更多异常学生需要关注" 
                              :description="`总共 ${mlManagement.anomalyDetection.anomalies.length} 名学生检测到异常行为`" 
                              type="warning" 
                              show-icon />
                  </div>
                </div>
              </div>
            </div>
          </el-card>
          
          <!-- 加载状态 -->
          <el-card v-if="mlManagement.loading" class="loading-card">
            <el-skeleton :loading="true" animated :rows="5" />
          </el-card>
          
          <!-- 无数据状态 -->
          <el-empty v-if="!mlManagement.loading && !mlManagement.clusterAnalysis && !mlManagement.anomalyDetection" 
                    description="暂无ML分析数据">
            <el-button type="primary" @click="loadMLAnalysis">开始分析</el-button>
          </el-empty>
        </div>
      </el-tab-pane>
      
      <!-- 模型训练 -->
      <el-tab-pane label="模型训练" name="model-training">
        <div class="model-training-panel">
          <div class="panel-header">
            <h2>⚙️ 机器学习模型训练</h2>
          </div>
          
          <el-card class="training-card">
            <div class="training-info">
              <el-alert title="模型训练说明" 
                        description="训练机器学习模型需要使用当前所有学生数据，请确保数据充足且质量良好。训练过程可能需褁1-2分钟。" 
                        type="info" 
                        show-icon 
                        style="margin-bottom: 20px;" />
              
              <div class="training-actions">
                <el-button type="primary" 
                           size="large" 
                           @click="trainMLModels" 
                           :loading="mlManagement.modelTraining.loading">
                  <el-icon><Setting /></el-icon>
                  {{ mlManagement.modelTraining.loading ? '正在训练...' : '开始训练模型' }}
                </el-button>
              </div>
            </div>
            
            <!-- 训练结果展示 -->
            <div v-if="mlManagement.modelTraining.results" class="training-results">
              <el-divider>训练结果</el-divider>
              
              <div class="training-summary">
                <div class="summary-item">
                  <span class="label">训练样本数：</span>
                  <span class="value">{{ mlManagement.modelTraining.results.total_samples }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">训练时间：</span>
                  <span class="value">{{ new Date(mlManagement.modelTraining.results.training_time).toLocaleString() }}</span>
                </div>
              </div>
              
              <div class="model-results">
                <el-row :gutter="20">
                  <el-col v-for="(result, modelName) in mlManagement.modelTraining.results.training_results" 
                          :key="modelName" 
                          :span="8">
                    <el-card class="model-result-card">
                      <div class="model-info">
                        <h4>{{ getModelDisplayName(modelName) }}</h4>
                        <el-tag :type="result.success ? 'success' : 'danger'">
                          {{ result.success ? '训练成功' : '训练失败' }}
                        </el-tag>
                      </div>
                      <p class="model-message">{{ result.message }}</p>
                    </el-card>
                  </el-col>
                </el-row>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <div class="student-table-container">
      <el-card>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
          <h3>学生数据管理</h3>
          <el-input v-model="searchQuery" placeholder="输入学号或姓名搜索" style="width: 300px" clearable
            @input="updateFilteredStudents" @clear="handleSearchClear" />
        </div>
        <el-table :data="filteredStudentList" border style="width: 100%" @sort-change="handleSortChange"
          :default-sort="{ prop: 'name', order: 'ascending' }">
          <el-table-column prop="id" label="学号" width="180" />
          <el-table-column prop="name" label="姓名" width="180" />
          <el-table-column prop="phone_number" label="电话号码" width="180">
            <template #default="{ row }">
              {{ row.phone_number || '未填写' }}
            </template>
          </el-table-column>
          <el-table-column prop="comprehensive_score" label="综合成绩" />
          <el-table-column prop="exam_score" label="考试成绩" />
          <el-table-column label="状态" width="180">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handleView(row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="table-actions" style="margin-top: 20px">
        </div>
        <el-pagination :current-page="currentPage" :page-size="pageSize" :total="totalStudents"
          @current-change="handleCurrentChange" layout="prev, pager, next"
          style="margin-top: 20px; justify-content: center" />
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
import { ElMessage, ElMessageBox } from 'element-plus';
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
const filteredStudentList = ref([]);
const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const totalStudents = ref(0);
const sortProp = ref('name');
const sortOrder = ref('ascending');

// 机器学习管理功能
const mlManagement = ref({
  loading: false,
  clusterAnalysis: null,
  anomalyDetection: null,
  modelTraining: {
    loading: false,
    results: null
  }
});

const activeTab = ref('overview'); // overview, ml-analysis, model-training


const router = useRouter();
const goToDataImport = () => {
  router.push({ name: 'DataImport' });
};

const handleView = (row) => {
  router.push({ name: 'Dashboard', query: { id: row.id } });
};

const handleSortChange = ({ prop, order }) => {
  sortProp.value = prop;
  sortOrder.value = order;
  updateFilteredStudents();
};

const handleCurrentChange = (page) => {
  currentPage.value = page;
  updateFilteredStudents();
};

const handleSearchClear = () => {
  searchQuery.value = '';
  updateFilteredStudents();
};

const updateFilteredStudents = () => {
  let filtered = [...studentList.value];
  
  // 搜索功能
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(student => 
      student.id.toString().includes(query) || 
      student.name.toLowerCase().includes(query)
    );
  }
  
  // 排序功能
  filtered.sort((a, b) => {
    if (sortOrder.value === 'ascending') {
      return a[sortProp.value] > b[sortProp.value] ? 1 : -1;
    } else {
      return a[sortProp.value] < b[sortProp.value] ? 1 : -1;
    }
  });
  
  // 分页功能
  totalStudents.value = filtered.length;
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  filteredStudentList.value = filtered.slice(start, end);
};

// ML管理功能方法
const loadMLAnalysis = async () => {
  if (mlManagement.value.loading) return;
  
  mlManagement.value.loading = true;
  
  try {
    console.log('[管理员] 开始加载ML分析数据');
    
    const [clusterRes, anomalyRes] = await Promise.allSettled([
      api.getClusterAnalysis(),
      api.getAnomalyDetection()
    ]);
    
    if (clusterRes.status === 'fulfilled' && clusterRes.value.data.success) {
      mlManagement.value.clusterAnalysis = clusterRes.value.data.analysis;
      console.log('[管理员] 聚类分析数据加载成功');
    } else {
      console.warn('[管理员] 聚类分析失败:', clusterRes.reason);
    }
    
    if (anomalyRes.status === 'fulfilled' && anomalyRes.value.data.success) {
      mlManagement.value.anomalyDetection = anomalyRes.value.data.results;
      console.log('[管理员] 异常检测数据加载成功');
    } else {
      console.warn('[管理员] 异常检测失败:', anomalyRes.reason);
    }
    
  } catch (error) {
    console.error('[管理员] ML分析加载失败:', error);
    ElMessage.error('ML分析加载失败');
  } finally {
    mlManagement.value.loading = false;
  }
};

const trainMLModels = async () => {
  if (mlManagement.value.modelTraining.loading) return;
  
  await ElMessageBox.confirm(
    '训练机器学习模型需要一定时间，是否继续？',
    '确认训练',
    {
      confirmButtonText: '开始训练',
      cancelButtonText: '取消',
      type: 'warning'
    }
  );
  
  mlManagement.value.modelTraining.loading = true;
  
  try {
    console.log('[管理员] 开始训练ML模型');
    const response = await api.trainMLModels();
    
    if (response.data.status === 'success') {
      mlManagement.value.modelTraining.results = response.data.data;
      ElMessage.success('模型训练完成！');
      console.log('[管理员] 模型训练成功:', response.data.data);
    } else {
      throw new Error(response.data.error || '训练失败');
    }
    
  } catch (error) {
    console.error('[管理员] 模型训练失败:', error);
    ElMessage.error(`模型训练失败: ${error.response?.data?.error || error.message}`);
  } finally {
    mlManagement.value.modelTraining.loading = false;
  }
};

const refreshMLAnalysis = () => {
  loadMLAnalysis();
};

const getClusterTypeColor = (clusterId) => {
  const colors = ['#67c23a', '#409eff', '#e6a23c', '#f56c6c'];
  return colors[clusterId] || '#909399';
};

const getRiskLevelColor = (level) => {
  const colorMap = {
    'high': '#f56c6c',
    'medium': '#e6a23c', 
    'low': '#67c23a'
  };
  return colorMap[level] || '#909399';
};

const getModelDisplayName = (modelName) => {
  const nameMap = {
    'grade_prediction': '成绩预测模型',
    'clustering': '行为聚类模型',
    'anomaly_detection': '异常检测模型'
  };
  return nameMap[modelName] || modelName;
};

// 监听标签切换
const handleTabChange = (tabName) => {
  if (tabName === 'ml-analysis' && !mlManagement.value.clusterAnalysis && !mlManagement.value.anomalyDetection) {
    loadMLAnalysis();
  }
};

// 在获取数据后调用更新函数
onMounted(async () => {
  try {
    const res = await api.getAdminStats();
    // console.log('[AdminDashboardView] 原始学生数据:', JSON.parse(JSON.stringify(res.data.data.students)));
studentList.value = res.data.data.students;
// console.log('[AdminDashboardView] 过滤后学生数据:', JSON.parse(JSON.stringify(studentList.value)));
    updateFilteredStudents();
  } catch (error) {
    console.error('获取数据失败:', error);
  }
});


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
    const startTime = Date.now();
    console.log('[AdminDashboardView] 开始请求管理员数据API', {
      timestamp: new Date().toISOString(),
      request: 'getAdminStats',
      params: {}
    });
    
    const res = await api.getAdminStats();
    const endTime = Date.now();
    
    console.log('[AdminDashboardView] API响应数据:', {
      timestamp: new Date().toISOString(),
      duration: `${endTime - startTime}ms`,
      status: res.status,
      statusText: res.statusText,
      data: JSON.parse(JSON.stringify(res.data)),
      request: {
        method: res.config.method,
        url: res.config.url,
        headers: res.config.headers
      }
    }
  );
    
    if (!res.data || !res.data.data) {
      console.warn('[AdminDashboardView] API返回数据为空');
      ElMessage.warning('获取数据失败，请稍后重试');
      return;
    }
    
    if (!res.data.data.students) {
      console.warn('[AdminDashboardView] 学生数据为空');
      studentList.value = [];
      ElMessage.warning('暂无学生数据');
    } else {
      // console.log('[AdminDashboardView] 原始学生数据:', JSON.parse(JSON.stringify(res.data.data.students)));
studentList.value = res.data.data.students;
// console.log('[AdminDashboardView] 过滤后学生数据:', JSON.parse(JSON.stringify(studentList.value)));
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
    
    // console.log('[AdminDashboardView] 数据赋值完成:', {
    //   userCount: userCount.value,
    //   activeUsers: activeUsers.value,
    //   avgScore: avgScore.value
    // });
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

.student-table-container {
  margin-top: 30px;
}

.table-actions {
  margin-top: 20px;
}

#footer {
  padding: 0 0 30px 0;
  color: #677184;
  font-size: 14px;
  text-align: center;
  background: #f5f7fa;
  bottom: 0ch;
  opacity: 0.8;
  background: white;
}

/* ML管理功能样式 */
.header-actions {
  display: flex;
  gap: 10px;
}

.ml-analysis-panel, .model-training-panel {
  padding: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.analysis-result-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.cluster-distribution {
  display: grid;
  gap: 15px;
}

.cluster-item {
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
}

.cluster-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.cluster-stats {
  font-weight: 600;
  color: #606266;
}

.cluster-progress {
  margin: 10px 0;
}

.cluster-users {
  margin-top: 10px;
}

.user-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.user-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.user-tag:hover {
  transform: scale(1.1);
}

.anomaly-summary {
  padding: 15px;
}

.summary-stats {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-item .label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-item .value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.anomaly-count {
  color: #f56c6c !important;
}

.anomaly-list h4 {
  margin-bottom: 15px;
  color: #303133;
}

.anomaly-students {
  display: grid;
  gap: 10px;
}

.anomaly-student-card {
  cursor: pointer;
  transition: all 0.3s;
  border-left: 4px solid #e6a23c;
}

.anomaly-student-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.student-info {
  padding: 10px;
}

.student-basic {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.risk-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.anomaly-score {
  font-size: 12px;
  color: #909399;
}

.concerns {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.concern-tag {
  margin: 2px;
}

.more-anomalies {
  margin-top: 15px;
}

.loading-card {
  padding: 30px;
}

.training-card {
  margin-top: 20px;
}

.training-info {
  text-align: center;
  padding: 20px;
}

.training-actions {
  margin-top: 20px;
}

.training-results {
  margin-top: 20px;
}

.training-summary {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
}

.summary-item .label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.summary-item .value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.model-results {
  margin-top: 20px;
}

.model-result-card {
  text-align: center;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.model-info {
  margin-bottom: 10px;
}

.model-info h4 {
  margin-bottom: 8px;
  color: #303133;
}

.model-message {
  font-size: 14px;
  color: #606266;
  margin: 0;
}
</style>
