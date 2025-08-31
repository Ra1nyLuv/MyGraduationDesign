import axios from 'axios';



const apiClient = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 5000,
});

// 请求拦截器（自动添加 Token）
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器（错误处理）
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default {
  // 用户相关接口
  registerUser(data) {
    return apiClient.post('/api/register', data);
  },
  loginUser(data) {
    return apiClient.post('/api/login', data);
  },
  // 数据接口
  getUserData(params) {
    return apiClient.get('/api/my-data', {
      params
    });
  },
  getChartData() {
    return apiClient.get('/api/chart-data');
  },
  getAdminStats() {
    return apiClient.get('/api/admin-stats');
  },

  // 机器学习相关接口
  // 成绩预测
  predictGrade(studentId) {
    return apiClient.post('/api/ml/predict-grade', {
      student_id: studentId
    });
  },

  // 学习行为聚类分析
  getClusterAnalysis() {
    return apiClient.get('/api/ml/cluster-analysis');
  },

  // 个性化推荐
  getPersonalizedRecommendations(studentId) {
    return apiClient.post('/api/ml/recommendations', {
      student_id: studentId
    });
  },

  // 异常行为检测
  getAnomalyDetection() {
    return apiClient.get('/api/ml/anomaly-detection');
  },

  // 训练所有ML模型
  trainMLModels() {
    return apiClient.post('/api/ml/train-models');
  },

  // 数据导入接口
  importData(formData) {
    return apiClient.post('/api/import-data', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};
