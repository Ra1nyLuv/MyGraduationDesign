<template>
  <div class="admin-dashboard">
    <el-dialog v-model="editDialogVisible" title="编辑学生信息" width="30%">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="电话号码">
          <el-input v-model="editForm.phone_number" placeholder="请输入电话号码" />
        </el-form-item>
        <el-form-item label="综合成绩">
          <el-input-number v-model="editForm.comprehensive_score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="考试成绩">
          <el-input-number v-model="editForm.exam_score" :min="0" :max="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditSubmit">确认</el-button>
        </span>
      </template>
    </el-dialog>
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
    
    <div class="student-table-container">
      <el-card>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
          <h3>学生数据管理</h3>
          <el-input
            v-model="searchQuery"
            placeholder="输入学号或姓名搜索"
            style="width: 300px"
            clearable
            @input="updateFilteredStudents"
            @clear="handleSearchClear"
          />
        </div>
        <el-table
  :data="filteredStudentList"
  border
  style="width: 100%"
  @sort-change="handleSortChange"
  :default-sort="{ prop: 'name', order: 'ascending' }"
>
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
          <!-- <el-button type="primary" @click="handleAdd">添加学生</el-button> -->
        </div>
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="totalStudents"
          @current-change="handleCurrentChange"
          layout="prev, pager, next"
          style="margin-top: 20px; justify-content: center"
        />
      </el-card>
    </div>
  </div>
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

const editDialogVisible = ref(false);
const editForm = ref({
  phone_number: '',
  comprehensive_score: 0,
  exam_score: 0
});
const currentEditRow = ref(null);

const handleEdit = (row) => {
  currentEditRow.value = row;
  editForm.value = {
    phone_number: row.phone_number || '',
    comprehensive_score: row.comprehensive_score,
    exam_score: row.exam_score
  };
  editDialogVisible.value = true;
};

const handleEditSubmit = async () => {
  try {
    await api.update({
      id: currentEditRow.value.id,
      phone_number: editForm.value.phone_number || null,
      comprehensive_score: editForm.value.comprehensive_score,
      exam_score: editForm.value.exam_score
    });
    
    ElMessage.success('修改成功');
    editDialogVisible.value = false;
    const res = await api.getAdminStats();
    studentList.value = res.data.data.students;
  } catch (error) {
    console.error('修改失败:', error);
    ElMessage.error('修改失败');
  }
};

const router = useRouter();
const handleView = (row) => {
  router.push({ name: 'Dashboard', query: { id: row.id } });
};

const handleDelete = async (row) => {
  try {
    await api.deleteStudent(row.id);
    ElMessage.success('删除成功');
    // 刷新数据
    const res = await api.getAdminStats();
    console.log('[AdminDashboardView] 原始学生数据:', JSON.parse(JSON.stringify(res.data.data.students)));
studentList.value = res.data.data.students;
console.log('[AdminDashboardView] 过滤后学生数据:', JSON.parse(JSON.stringify(studentList.value)));
    updateFilteredStudents();
  } catch (error) {
    console.error('删除失败:', error);
    ElMessage.error('删除失败');
  }
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

// const formatPhoneNumber = (row) => {
//   console.log('[AdminDashboardView] 电话号码数据:', row.phone_number);
//   return row.phone_number || '未填写';
// };

// const handleAdd = () => {
//   ElMessageBox.prompt('请输入学生ID,姓名（用逗号分隔）', '添加学生', {
//     confirmButtonText: '确认',
//     cancelButtonText: '取消'
//   }).then(async ({ value }) => {
//     const [id, name] = value.split(',');
//     if (!id || !name) {
//       ElMessage.error('输入的ID和姓名格式不正确，请重新输入');
//       return;
//     }
//     try {
//       await api.addStudent({
//         id: (id),
//         name: name.trim(' '),
//         password: '1234',
//         phone_number: '13900000000',
//         role: 'user',
//         comprehensive_score: 0,
//         exam_score: 0
//       });
//       ElMessage.success('添加成功');
//       const res = await api.getAdminStats();
//       // console.log('[AdminDashboardView] 原始学生数据:', JSON.parse(JSON.stringify(res.data.data.students)));
// studentList.value = res.data.data.students;
// // console.log('[AdminDashboardView] 过滤后学生数据:', JSON.parse(JSON.stringify(studentList.value)));
//     } catch (error) {
//       console.error('添加失败:', error);
//       ElMessage.error('添加失败');
//     }
//   }).catch(() => {
//     ElMessage.info('取消添加');
//   });
// };

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
</style>
