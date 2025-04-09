<template>
  <div class="admin-dashboard">
    <div style="display: flex; justify-content: space-between; align-items: center">
      <h1>管理员数据看板</h1>
      <el-button type="primary" @click="goToDataImport">从文件导入数据</el-button>
    </div>
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

// 在获取数据后调用更新函数
onMounted(async () => {
  try {
    const res = await api.getAdminStats();
    console.log('[AdminDashboardView] 原始学生数据:', JSON.parse(JSON.stringify(res.data.data.students)));
studentList.value = res.data.data.students;
console.log('[AdminDashboardView] 过滤后学生数据:', JSON.parse(JSON.stringify(studentList.value)));
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
    });
    
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
      console.log('[AdminDashboardView] 原始学生数据:', JSON.parse(JSON.stringify(res.data.data.students)));
studentList.value = res.data.data.students;
console.log('[AdminDashboardView] 过滤后学生数据:', JSON.parse(JSON.stringify(studentList.value)));
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
</style>
