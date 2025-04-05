<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <h2>用户登录</h2>
      <el-form :model="form" ref="loginForm" label-width="80px" @keyup.enter.native="handleLogin">
        <el-form-item label="账号" prop="id">
          <el-input v-model="form.id" placeholder="请输入账号ID"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input type="password" v-model="form.password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading">登录</el-button>
        </el-form-item>
      </el-form>
      <p class="register-link">
        还没有账号？<el-link type="primary" @click="goToRegister">立即注册</el-link>
      </p>
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
import { ref } from 'vue';
import api from '@/services/api';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

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
        router.push({ name: 'Dashboard', params: { userId: res.data.id } });
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
  background: #f8f9fa;
}

.auth-card {
  width: 420px;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.el-form-item {
  margin-bottom: 1.5rem;
}

.el-button {
  width: 100%;
  margin-top: 0.5rem;
}

.register-link {
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: #606266;
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
