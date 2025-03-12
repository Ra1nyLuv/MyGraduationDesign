<template>
  <div class="dashboard-container">
    <div class="header-container">
      <el-page-header @back="goBack" title="返回" content="数据看板" />
      <el-button 
        type="danger" 
        @click="handleLogout"
        class="logout-btn"
      >
        退出登录
      </el-button>
    </div> 
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus'; // 导入图标组件

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
}
</style>
