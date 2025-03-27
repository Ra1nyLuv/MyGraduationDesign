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
  getUserData() {
    return apiClient.get('/api/my-data', {
  
    });
  },
  getChartData() {
    return apiClient.get('/api/data', {
  
    });
  },
};
