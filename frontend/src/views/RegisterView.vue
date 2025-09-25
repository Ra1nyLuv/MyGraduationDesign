<template>
  <div class="auth-container">
    <div class="auth-wrapper">
      <el-card class="auth-card">
        <div class="card-header">
          <h2>用户注册</h2>
          <p class="subtitle">创建新账户以开始使用系统</p>
        </div>
        <el-form :model="form" :rules="rules" ref="registerForm" label-width="0px" @keyup.enter.native="handleRegister">
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
          <el-form-item prop="name">
            <el-input 
              v-model="form.name" 
              placeholder="请输入真实姓名"
              prefix-icon="UserFilled"
              size="large"
              class="auth-input"
            >
            </el-input>
          </el-form-item>
          <el-form-item prop="phone_number">
            <el-input 
              v-model="form.phone_number" 
              placeholder="请输入11位手机号"
              prefix-icon="Phone"
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
              @click="handleRegister" 
              :loading="loading"
              size="large"
              class="auth-button"
              round
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>
        <div class="auth-footer">
          <p class="login-link">
            已有账号？<el-link type="primary" @click="goToLogin">立即登录</el-link>
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

const router = useRouter();
const form = ref({ id: '', password: '', name: '', phone_number: '' });
const loading = ref(false);
const registerForm = ref(null);

const rules = {
  id: [{ required: true, message: '请输入账号ID', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone_number: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
};

const handleRegister = async () => {
  try {
    await registerForm.value.validate();
    loading.value = true;
    const res = await api.registerUser({
      id: form.value.id,
      name: form.value.name,
      phone_number: form.value.phone_number,
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

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.card-header h2 {
  font-size: 1.8rem;
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

.login-link {
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
  
  .card-header h2 {
    font-size: 1.5rem;
  }
}
</style>