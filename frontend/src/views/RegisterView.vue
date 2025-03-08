<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <h2>用户注册</h2>
      <el-form :model="form" :rules="rules" ref="registerForm" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input type="password" v-model="form.password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading">注册</el-button>
        </el-form-item>
      </el-form>
      <p class="login-link">
        已有账号？<el-link type="primary" @click="goToLogin">立即登录</el-link>
      </p>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/services/api';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const router = useRouter();
const form = ref({ username: '', password: '' });
const loading = ref(false);
const registerForm = ref(null);

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
};

const handleRegister = async () => {
  try {
    await registerForm.value.validate();
    loading.value = true;
    const res = await api.registerUser({
      username: form.value.username,
      password: form.value.password
    });
    if (res.status === 201) {
      ElMessage.success('注册成功，请登录');
      router.push({ path: '/login', query: { newUser: form.value.username } });
    }
  } catch (error) {
    ElMessage.error('注册失败：' + error.response?.data.error || '未知错误');
  } finally {
    loading.value = false;
  }
};

const goToLogin = () => {
  router.push({ path: '/login', query: { newUser: form.value.username } });
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

.login-link {
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: #606266;
}
</style>
