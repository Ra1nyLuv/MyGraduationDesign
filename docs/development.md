# 开发环境配置指南

## 📋 环境要求

### 必需软件

| 软件    | 版本要求 | 说明         |
| ------- | -------- | ------------ |
| Node.js | v18+     | 前端开发环境 |
| Python  | 3.9+     | 后端开发环境 |
| MySQL   | 8.0+     | 数据库服务   |
| Git     | 最新版   | 版本控制     |

### 推荐软件

| 软件               | 说明           |
| ------------------ | -------------- |
| Visual Studio Code | 推荐的IDE      |
| Postman            | API接口测试    |
| MySQL Workbench    | 数据库管理工具 |
| Git Bash (Windows) | Git命令行工具  |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone ssh://git@ssh.github.com:443/Ra1nyLuv/Data_Visualization_Project_Practice.git
cd Data_Visualization_Project_Practice
```

### 2. 环境变量配置

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=project_db

# JWT配置 (请使用强密钥)
JWT_SECRET_KEY=your-super-secret-jwt-key-with-256-bits-minimum

# Flask配置
FLASK_DEBUG=True
FLASK_ENV=development
```

**⚠️ 安全提示**: 
- JWT密钥至少256位
- 数据库密码应包含特殊字符
- 生产环境设置 `FLASK_DEBUG=False`

### 3. 数据库配置

#### 3.1 创建数据库

```sql
CREATE DATABASE project_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 3.2 创建管理员账户

由于安全考虑，需要手动创建管理员账户：

1. 先在前端注册一个账户（如 `admin`）
2. 在数据库中修改角色：

```sql
UPDATE users SET role = 'admin' WHERE id = 'admin';
```

### 4. 后端环境配置

#### 4.1 创建Python虚拟环境

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 4.2 安装Python依赖

```bash
pip install -r requirements.txt
```

#### 4.3 数据库迁移

```bash
flask db upgrade
```

#### 4.4 数据导入

将Excel数据文件放置在 `data/` 目录下，然后运行导入脚本：

```bash
cd database_import
python users_importer.py
python synthesis_grades_importer.py
python homework_statistic_importer.py
python exam_statistic_importer.py
python discussion_importer.py
python video_watching_importer.py
```

### 5. 前端环境配置

```bash
cd frontend
npm install
```

### 6. 启动服务

#### 6.1 启动后端服务

```bash
cd backend
python app.py
```

后端服务将在 `http://localhost:5000` 启动

#### 6.2 启动前端服务

```bash
cd frontend
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

---

## 🔧 开发工具配置

### VS Code 推荐插件

```json
{
  "recommendations": [
    "ms-python.python",
    "Vue.volar",
    "esbenp.prettier-vscode",
    "ms-python.flake8",
    "bradlc.vscode-tailwindcss"
  ]
}
```

### VS Code 设置

创建 `.vscode/settings.json`：

```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[vue]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

---

## 📁 项目结构说明

```
Data_Visualization_Project_Practice/
├── backend/                    # 后端代码
│   ├── app/                   # 应用主目录 (待重构)
│   │   ├── models/           # 数据模型
│   │   ├── routes/           # 路由控制器
│   │   ├── services/         # 业务逻辑
│   │   └── utils/            # 工具函数
│   ├── ml_services/          # 机器学习服务
│   ├── database_import/      # 数据导入脚本
│   ├── migrations/           # 数据库迁移
│   ├── tests/               # 测试代码
│   ├── config/              # 配置文件
│   └── app.py               # 主应用文件 (待拆分)
├── frontend/                 # 前端代码
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   ├── components/      # 通用组件
│   │   ├── services/        # API服务
│   │   ├── router/          # 路由配置
│   │   └── assets/          # 静态资源
│   ├── public/              # 公共资源
│   └── package.json         # 前端依赖
├── docs/                    # 项目文档
├── data/                    # 数据文件
└── README.md               # 项目说明
```

---

## 🧪 测试环境

### 后端测试

```bash
cd backend
pytest tests/
```

### 前端测试

```bash
cd frontend
npm run test
```

### API测试

推荐使用Postman或直接运行测试脚本：

```bash
cd backend
python test_ml_apis.py
```

---

## 🐛 常见问题排查

### 1. 数据库连接失败

**错误**: `Access denied for user 'root'@'localhost'`

**解决方案**:
- 检查MySQL服务是否启动
- 验证 `.env` 文件中的数据库凭据
- 确认数据库用户权限

### 2. 前端启动失败

**错误**: `Node.js version mismatch`

**解决方案**:
```bash
# 升级Node.js到v18+
nvm install 18
nvm use 18
```

### 3. 机器学习模型训练失败

**错误**: `模型训练失败: 训练失败`

**解决方案**:
- 确保数据库中有足够的用户数据 (≥3个用户)
- 检查Windows环境变量: `OMP_NUM_THREADS=1`
- 运行诊断脚本: `python quick_diagnose.py`

### 4. CORS跨域错误

**错误**: `Access to XMLHttpRequest has been blocked by CORS policy`

**解决方案**:
- 确认前端运行在 `http://localhost:5173`
- 检查后端CORS配置
- 重启两个服务

### 5. JWT认证失败

**错误**: `Token has expired` 或 `Invalid token`

**解决方案**:
- 清除浏览器本地存储
- 重新登录获取新token
- 检查服务器时间是否正确

---

## 📊 性能监控

### 开发环境监控

```bash
# 监控后端性能
pip install flask-profiler
# 在app.py中启用profiler

# 监控前端性能
npm install --save-dev @vue/devtools
```

### 数据库性能

```sql
-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log';
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

---

## 🔄 开发工作流

### 1. 功能开发流程

1. **创建分支**: `git checkout -b feature/new-feature`
2. **开发功能**: 遵循代码规范
3. **运行测试**: 确保所有测试通过
4. **提交代码**: 使用规范的commit信息
5. **创建PR**: 代码审查后合并

### 2. 代码规范

#### Python (后端)
- 使用 Black 格式化代码
- 遵循 PEP 8 规范
- 函数和类添加文档字符串
- 使用类型注解

```python
def get_user_data(user_id: str) -> Dict[str, Any]:
    """
    获取用户数据
    
    Args:
        user_id: 用户ID
        
    Returns:
        用户数据字典
    """
    pass
```

#### JavaScript (前端)
- 使用 Prettier 格式化代码
- 遵循 ESLint 规则
- 使用 const/let 而非 var
- 函数添加JSDoc注释

```javascript
/**
 * 获取用户数据
 * @param {string} userId - 用户ID
 * @returns {Promise<Object>} 用户数据
 */
const getUserData = async (userId) => {
  // 实现代码
};
```

### 3. Git提交规范

```bash
# 功能开发
git commit -m "feat: 添加用户数据可视化功能"

# 问题修复
git commit -m "fix: 修复登录验证失败问题"

# 文档更新
git commit -m "docs: 更新API文档"

# 代码重构
git commit -m "refactor: 重构用户模型结构"
```

---

## 🚀 部署准备

### 生产环境配置

1. **环境变量**:
```bash
FLASK_DEBUG=False
FLASK_ENV=production
JWT_SECRET_KEY=production-super-secret-key
```

2. **数据库优化**:
```sql
-- 创建索引
CREATE INDEX idx_users_id ON users(id);
CREATE INDEX idx_synthesis_grades_score ON synthesis_grades(comprehensive_score);
```

3. **静态文件处理**:
```bash
cd frontend
npm run build
```

### Docker配置 (可选)

```dockerfile
# Dockerfile.backend
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

---

## 📞 支持与帮助

### 项目相关
- **项目文档**: `/docs` 目录
- **API文档**: `/docs/api.md`
- **问题报告**: GitHub Issues

### 技术支持
- **Flask文档**: https://flask.palletsprojects.com/
- **Vue.js文档**: https://vuejs.org/
- **Element Plus**: https://element-plus.org/
- **ECharts**: https://echarts.apache.org/

### 联系信息
- **项目负责人**: 陈俊霖
- **开发团队**: 莆田学院 新工科产业学院 数据225
- **技术栈**: Vue.js 3 + Flask + MySQL + scikit-learn