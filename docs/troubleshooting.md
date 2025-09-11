# 故障排除手册

## 📋 快速诊断

### 系统健康检查清单

- [ ] 前端服务运行正常 (`http://localhost:5173`)
- [ ] 后端服务运行正常 (`http://localhost:5000`)
- [ ] 数据库连接正常
- [ ] 环境变量配置正确
- [ ] 依赖包安装完整

---

## 🔧 自动诊断工具

项目提供了多个诊断脚本，帮助快速定位问题：

### Windows环境
```cmd
# 快速诊断ML功能
cd backend
python quick_diagnose.py

# 完整ML系统诊断
python diagnose_ml_training.py

# ML API测试
python test_ml_apis.py
```

### 通用诊断
```bash
# 检查ML模块状态
python check_ml_status.py

# 验证优化后的ML功能
python verify_optimized_ml.py
```

---

## 🚨 常见问题解决方案

### 1. 启动问题

#### 1.1 前端启动失败

**症状**: `npm run dev` 报错

**常见错误**:
```bash
Error: Node.js version mismatch
Error: Cannot resolve dependency
```

**解决方案**:
```bash
# 检查Node.js版本 (需要v18+)
node --version

# 如果版本不符，升级Node.js
nvm install 18
nvm use 18

# 清理并重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 如果仍有问题，尝试
npm cache clean --force
npm install
```

#### 1.2 后端启动失败

**症状**: `python app.py` 报错

**常见错误**:
```
ImportError: No module named 'flask'
MySQL connection failed
JWT_SECRET_KEY环境变量未配置
```

**解决方案**:
```bash
# 检查虚拟环境
cd backend
python --version  # 应该是3.9+

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 检查环境变量
echo $JWT_SECRET_KEY  # Linux/macOS
echo %JWT_SECRET_KEY%  # Windows

# 如果环境变量未加载，手动加载
source ../.env  # Linux/macOS
```

### 2. 数据库问题

#### 2.1 数据库连接失败

**症状**: `Access denied for user 'root'@'localhost'`

**解决方案**:
```bash
# 1. 检查MySQL服务状态
# Windows
net start mysql

# Linux/macOS
sudo systemctl status mysql

# 2. 验证数据库凭据
mysql -u root -p

# 3. 检查.env文件配置
cat .env
# 确认MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST设置正确

# 4. 重置MySQL密码（如果忘记）
sudo mysql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'new_password';
FLUSH PRIVILEGES;
```

#### 2.2 数据库不存在

**症状**: `Unknown database 'project_db'`

**解决方案**:
```sql
-- 登录MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE project_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 验证数据库创建
SHOW DATABASES;
```

#### 2.3 数据表不存在

**症状**: `Table 'project_db.users' doesn't exist`

**解决方案**:
```bash
cd backend

# 运行数据库迁移
flask db upgrade

# 如果没有迁移文件，创建迁移
flask db init
flask db migrate -m "初始化数据库"
flask db upgrade

# 导入数据
cd database_import
python users_importer.py
python synthesis_grades_importer.py
# ... 其他导入脚本
```

### 3. 机器学习问题

#### 3.1 模型训练失败

**症状**: "模型训练失败: 训练失败"

**诊断步骤**:
```bash
# 1. 运行诊断工具
python quick_diagnose.py

# 2. 检查用户数据量
python -c "
from app import app, User, db
with app.app_context():
    print('用户数量:', User.query.count())
"

# 3. 详细诊断
python diagnose_ml_training.py
```

**常见原因和解决方案**:

| 错误信息     | 原因               | 解决方案                                |
| ------------ | ------------------ | --------------------------------------- |
| 数据量不足   | 用户数量 < 3       | 导入更多用户数据                        |
| 特征提取失败 | 数据格式问题       | 检查数据完整性                          |
| 模块导入失败 | 依赖包缺失         | `pip install scikit-learn numpy pandas` |
| 内存不足     | Windows KMeans警告 | 设置 `OMP_NUM_THREADS=1`                |

#### 3.2 智能分析无内容

**症状**: 智能分析板块显示"暂无ML分析数据"

**解决步骤**:
```bash
# 1. 检查模型是否训练成功
curl http://localhost:5000/api/ml/cluster-analysis

# 2. 检查异常检测
curl http://localhost:5000/api/ml/anomaly-detection

# 3. 重新训练模型
curl -X POST http://localhost:5000/api/ml/train-models

# 4. 检查前端控制台错误
# 按F12打开开发者工具，查看Console标签页
```

#### 3.3 前端Vue渲染错误

**症状**: `Cannot read properties of undefined`

**解决方案**:
```javascript
// 检查数据结构匹配
// 错误: anomaly.anomaly_info.details?.risk_level
// 正确: anomaly.severity

// 检查API响应格式
console.log('API响应:', response.data);

// 添加数据验证
if (response.data.success && response.data.results) {
    // 处理数据
}
```

### 4. 网络和CORS问题

#### 4.1 跨域错误

**症状**: `Access to XMLHttpRequest has been blocked by CORS policy`

**解决方案**:
```python
# 检查后端CORS配置 (app.py)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

# 确认前端运行在正确端口
# 前端: http://localhost:5173
# 后端: http://localhost:5000
```

#### 4.2 API调用失败

**症状**: 网络请求超时或失败

**解决方案**:
```javascript
// 检查API服务状态
fetch('http://localhost:5000/api/')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('API错误:', error));

// 增加超时和错误处理
axios.defaults.timeout = 10000;
axios.interceptors.response.use(
  response => response,
  error => {
    console.error('API请求失败:', error);
    return Promise.reject(error);
  }
);
```

### 5. 权限问题

#### 5.1 管理员权限不足

**症状**: "无权限执行此操作"

**解决方案**:
```sql
-- 检查用户角色
SELECT id, name, role FROM users WHERE id = 'your_admin_id';

-- 设置管理员权限
UPDATE users SET role = 'admin' WHERE id = 'your_admin_id';
```

#### 5.2 JWT Token失效

**症状**: `Token has expired` 或 `Invalid token`

**解决方案**:
```javascript
// 清除本地存储的token
localStorage.removeItem('access_token');

// 重新登录获取新token
// 或实现token自动刷新机制
```

### 6. 性能问题

#### 6.1 页面加载缓慢

**诊断步骤**:
```bash
# 1. 检查网络请求时间
# 浏览器F12 → Network标签页

# 2. 检查服务器性能
htop  # Linux/macOS
taskmgr  # Windows

# 3. 检查数据库查询
# MySQL慢查询日志
```

**优化方案**:
```javascript
// 前端优化
// 1. 启用懒加载
const DashboardView = () => import('@/views/DashboardView.vue');

// 2. 图表懒加载
const chartOptions = computed(() => {
  return visibleCharts.value.includes('homework') ? homeworkOptions : {};
});

// 3. 数据分页
const pageSize = 20;
```

```python
# 后端优化
# 1. 数据库查询优化
users = User.query.options(
    db.joinedload(User.synthesis_grades),
    db.selectinload(User.homework_statistic)
).limit(100).all()

# 2. 添加缓存
from flask_caching import Cache
cache = Cache(app)

@cache.memoize(timeout=300)
def get_user_stats():
    # 缓存5分钟
    pass
```

#### 6.2 内存占用过高

**解决方案**:
```bash
# 1. 重启服务释放内存
pm2 restart all  # 生产环境
# 或直接重启开发服务器

# 2. 检查内存泄漏
# 使用memory_profiler监控Python内存使用

# 3. 优化数据处理
# 使用生成器代替列表，及时释放大对象
```

---

## 🔍 高级诊断技巧

### 1. 日志分析

#### 后端日志
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看Flask日志
app.logger.setLevel(logging.DEBUG)
```

#### 前端日志
```javascript
// 启用Vue开发工具
Vue.config.devtools = true;

// 详细的API调用日志
axios.interceptors.request.use(request => {
  console.log('API请求:', request);
  return request;
});
```

### 2. 数据库诊断

```sql
-- 检查数据完整性
SELECT 
  TABLE_NAME,
  TABLE_ROWS,
  DATA_LENGTH,
  INDEX_LENGTH
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'project_db';

-- 分析查询性能
EXPLAIN SELECT * FROM users WHERE id = '2021001';

-- 检查锁定情况
SHOW PROCESSLIST;
```

### 3. 系统资源监控

```bash
# CPU使用率
top -p $(pgrep -f "python app.py")

# 内存使用详情
ps aux | grep python

# 磁盘I/O
iotop -p $(pgrep -f "python app.py")

# 网络连接
netstat -an | grep :5000
```

---

## 📞 获取帮助

### 1. 自助诊断流程

1. **运行诊断脚本**: `python quick_diagnose.py`
2. **检查日志文件**: 查看错误消息
3. **验证配置**: 确认环境变量和依赖
4. **测试连接**: 验证数据库和网络
5. **重启服务**: 清理可能的临时问题

### 2. 问题报告模板

当需要寻求帮助时，请提供以下信息：

```
### 问题描述
[详细描述遇到的问题]

### 环境信息
- 操作系统: 
- Python版本: 
- Node.js版本: 
- MySQL版本: 

### 错误信息
[完整的错误消息和堆栈跟踪]

### 重现步骤
1. 
2. 
3. 

### 已尝试的解决方案
[列出已经尝试过的方法]

### 相关日志
[粘贴相关的日志内容]
```

### 3. 紧急联系方式

- **技术支持**: 陈俊霖
- **开发团队**: 莆田学院 新工科产业学院 数据225
- **文档更新**: 如发现文档问题，请及时反馈

---

## 🔄 预防性维护

### 定期检查清单

#### 每日检查
- [ ] 服务运行状态
- [ ] 错误日志
- [ ] 系统资源使用

#### 每周检查
- [ ] 数据库备份
- [ ] 安全更新
- [ ] 性能指标

#### 每月检查
- [ ] 依赖包更新
- [ ] 配置文件审查
- [ ] 容量规划

通过遵循这些故障排除步骤和预防性维护措施，可以显著提高系统的稳定性和可用性。