<template>
  <div class="auth-container">
    <div class="auth-wrapper">
      <el-card class="auth-card">
        <div class="system-header">
          <div class="logo-placeholder">
            <el-icon size="48" color="#409eff"><Management /></el-icon>
          </div>
          <h1 class="system-title">课程学生信息管理系统</h1>
          <p class="system-subtitle">Course Student Information Management System</p>
        </div>
        <div class="card-header">
          <h2>用户登录</h2>
          <p class="subtitle">欢迎回来，请登录您的账户</p>
        </div>
        <el-form :model="form" ref="loginForm" label-width="0px" @keyup.enter.native="handleLogin">
          <el-form-item prop="id">
            <el-input 
              v-model="form.id" 
              placeholder="请输入账号ID"
              prefix-icon="User"
              size="large"
              class="auth-input"
            >
            </el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input 
              type="password" 
              v-model="form.password" 
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              size="large"
              class="auth-input"
            >
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button 
              type="primary" 
              @click="handleLogin" 
              :loading="loading"
              size="large"
              class="auth-button"
              round
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
        <div class="auth-footer">
          <p class="register-link">
            还没有账号？<el-link type="primary" @click="goToRegister">立即注册</el-link>
          </p>
        </div>
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
import { ref } from 'vue';
import api from '@/services/api';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Management } from '@element-plus/icons-vue';

const router = useRouter();
const form = ref({ id: '', password: '' });
const loading = ref(false);

const handleLogin = async () => {
  try {
    loading.value = true;
    const res = await api.loginUser({
      id: form.value.id,
      password: form.value.password
    });
    if (res.status === 200) {
      ElMessage.success('登录成功');
      localStorage.setItem('access_token', res.data.token);
      localStorage.setItem('user_role', res.data.role);
      localStorage.setItem('user_id', res.data.id);
      if (res.data.role === 'admin') {
        router.push({ name: 'AdminDashboard' });
      } else {
        router.push({ 
          name: 'Dashboard',
          query: { id: res.data.id }
        });
      }
    }
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data.error || '登录失败，请检查用户名或密码');
    } else {
      ElMessage.error('网络错误，请重试');
    }
  } finally {
    loading.value = false;
  }
};

const goToRegister = () => {
  router.push('/register');
};
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.auth-wrapper {
  width: 100%;
  max-width: 450px;
}

.auth-card {
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border: none;
  padding: 2.5rem 2rem;
}

.system-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #ebeef5;
}

.logo-placeholder {
  margin-bottom: 1rem;
}

.system-title {
  font-size: 1.8rem;
  color: #303133;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.system-subtitle {
  color: #909399;
  font-size: 0.9rem;
  margin: 0;
  font-weight: 400;
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.card-header h2 {
  font-size: 1.5rem;
  color: #303133;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.subtitle {
  color: #909399;
  font-size: 0.95rem;
  margin: 0;
}

.auth-input {
  margin-bottom: 1.2rem;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  padding: 2px 12px;
}

:deep(.el-input__prefix) {
  font-size: 16px;
  color: #909399;
}

.auth-button {
  width: 100%;
  margin-top: 1rem;
  background: linear-gradient(135deg, #409eff 0%, #1a73e8 100%);
  border: none;
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 1px;
  padding: 18px;
}

.auth-button:hover {
  background: linear-gradient(135deg, #1a73e8 0%, #409eff 100%);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.auth-footer {
  text-align: center;
  margin-top: 1.5rem;
}

.register-link {
  font-size: 0.9rem;
  color: #606266;
  margin: 0;
}

#footer {
  padding: 20px 0 30px 0;
  color: #677184;
  font-size: 14px;
  text-align: center;
  background: transparent;
  position: relative;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 1.5rem 1rem;
  }
  
  .system-title {
    font-size: 1.5rem;
  }
  
  .card-header h2 {
    font-size: 1.3rem;
  }
}
</style>