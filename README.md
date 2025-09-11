# 课程学习数据可视化分析系统

## 📋 项目概述

本项目是一个基于Vue.js 3和Flask的教育数据可视化分析系统，专为**莆田学院新工科产业学院数据225班**开发。系统通过机器学习算法和数据可视化技术，帮助教师和学生更好地理解学习行为模式，提供个性化的学习建议和干预措施。

### 🎯 核心价值
- **学生端**: 直观了解个人学习状态，获得个性化学习建议
- **教师端**: 识别需要关注的学生，实施精准教学干预
- **管理端**: 全面掌握班级学习情况，优化教学资源配置

### ✨ 主要功能
- 📊 **学生数据可视化看板** - 成绩分布、学习行为、时段热力图
- 🏛️ **管理员数据管理界面** - 用户管理、数据导入、系统配置
- 🤖 **智能学习行为分析** - K-means聚类识别学习模式
- 🚨 **异常行为检测** - Isolation Forest检测需要关注的学生
- 📈 **成绩预测模型** - 多算法自适应预测学习效果
- 💡 **个性化学习建议** - 基于数据分析生成定制化建议

## 🏗️ 技术架构

### 前端技术栈
- **Vue.js** 3.5.13 - 渐进式JavaScript框架
- **Element Plus** 2.9.7 - Vue 3 组件库
- **ECharts** 5.6.0 - 数据可视化库
- **Vite** 6.1.0 - 快速构建工具
- **Vue Router** 4.5.0 - 路由管理
- **Axios** 1.8.4 - HTTP客户端

### 后端技术栈
- **Python Flask** - 轻量级Web框架
- **SQLAlchemy** - ORM数据库操作
- **Flask-JWT-Extended** - JWT认证
- **scikit-learn** 1.3.0 - 机器学习库
- **MySQL** 8.0+ - 关系型数据库
- **Flask-CORS** - 跨域资源共享

### 机器学习组件
- **聚类分析**: K-means算法 + 自适应参数调整
- **异常检测**: Isolation Forest + 多维度异常识别
- **成绩预测**: 多算法自适应选择 (Ridge/DecisionTree/RandomForest)
- **特征工程**: 学习一致性指标、视频投入度、综合参与度

## 🚀 快速开始

### 📋 环境要求
- **Node.js** v18+ (前端开发)
- **Python** 3.9+ (后端开发)
- **MySQL** 8.0+ (数据库)
- **Git** (版本控制)

### ⚡ 一键安装
```bash
# 克隆项目
git clone ssh://git@ssh.github.com:443/Ra1nyLuv/Data_Visualization_Project_Practice.git
cd Data_Visualization_Project_Practice

# 安装所有依赖
npm run install
```

### 🔧 环境配置

1. **复制环境变量模板**:
```bash
cp .env.example .env
```

2. **编辑环境变量** (`.env`):
```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_strong_password
MYSQL_DB=project_db

# JWT配置 (请使用强密钥)
JWT_SECRET_KEY=your-super-secret-jwt-key-with-256-bits-minimum

# Flask配置
FLASK_DEBUG=True
FLASK_ENV=development
```

### 🗄️ 数据库设置

1. **创建数据库**:
```sql
CREATE DATABASE project_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. **运行数据库迁移**:
```bash
cd backend
flask db upgrade
```

3. **导入示例数据**:
```bash
cd database_import
python users_importer.py
python synthesis_grades_importer.py
# ... 其他导入脚本
```

### 🏃‍♂️ 启动服务

**启动后端服务**:
```bash
cd backend
python app.py
# 服务运行在 http://localhost:5000
```

**启动前端服务**:
```bash
cd frontend
npm run dev
# 服务运行在 http://localhost:5173
```

### 👤 管理员账户设置

由于安全考虑，需要手动创建管理员账户：

1. 在前端注册一个账户 (如用户ID: `admin`)
2. 在数据库中修改角色：
```sql
UPDATE users SET role = 'admin' WHERE id = 'admin';
```

## 📚 文档体系

我们提供了完整的文档体系来帮助开发者快速上手和深入了解系统：

| 文档             | 描述               | 链接                                                    |
| ---------------- | ------------------ | ------------------------------------------------------- |
| 🚀 **快速开始**   | 环境配置和安装指南 | [development.md](./docs/development.md)                 |
| 📖 **API文档**    | 完整的API接口说明  | [api.md](./docs/api.md)                                 |
| 🤖 **机器学习**   | ML算法详细说明     | [machine-learning.md](./docs/machine-learning.md)       |
| 🚀 **部署指南**   | 生产环境部署流程   | [deployment.md](./docs/deployment.md)                   |
| 🔧 **故障排除**   | 常见问题解决方案   | [troubleshooting.md](./docs/troubleshooting.md)         |
| 🏗️ **系统架构**   | 技术架构设计       | [system_architecture.md](./docs/system_architecture.md) |
| 🗄️ **数据库设计** | ER图和表结构       | [database_er_diagram.md](./docs/database_er_diagram.md) |

## 🎯 使用指南

### 👨‍🎓 学生用户
1. 使用学号登录系统
2. 查看个人学习数据仪表盘
3. 分析学习趋势和排名情况
4. 获取个性化学习建议

### 👨‍🏫 管理员用户
1. 使用管理员账户登录
2. 访问管理员数据看板
3. 进行机器学习模型训练
4. 查看智能分析结果
5. 识别需要关注的学生
6. 导入和管理学生数据

## 🤖 机器学习功能

### 学习行为聚类
- **算法**: K-means聚类
- **功能**: 识别4种学习模式 (高效型、稳定型、需要帮助型、观望型)
- **自适应**: 根据数据规模动态调整聚类数量

### 异常行为检测
- **算法**: Isolation Forest
- **功能**: 检测5种异常类型 (低参与度、学习规律异常、表现不佳、学习困难、行为不一致)
- **分级**: 高/中/低风险三级预警

### 成绩预测
- **算法**: 自适应选择 (Ridge/DecisionTree/RandomForest)
- **功能**: 预测学生学习表现，提供置信度评估
- **特色**: 特征重要性分析和个性化建议生成

## 📊 系统特色

### 🎨 数据可视化
- **ECharts集成**: 丰富的图表类型 (柱状图、饼图、热力图)
- **响应式设计**: 适配各种屏幕尺寸
- **实时更新**: 数据变化实时反映在图表中
- **交互体验**: 图表点击、悬停等交互功能

### 🔒 安全特性
- **JWT认证**: 无状态的用户认证机制
- **角色权限**: 学生/管理员分级权限控制
- **密码加密**: Bcrypt安全哈希算法
- **CORS配置**: 严格的跨域资源共享控制

### ⚡ 性能优化
- **懒加载**: Vue组件和路由懒加载
- **缓存策略**: 智能的数据缓存机制
- **异步处理**: 非阻塞的API调用
- **代码分割**: Vite自动代码分割优化

### 🔧 开发体验
- **热重载**: 开发时实时更新
- **ESLint/Prettier**: 代码质量和格式化
- **类型检查**: JavaScript类型安全
- **调试工具**: 完善的调试和诊断工具

## 🚨 常见问题

### 快速诊断
```bash
# 运行自动诊断脚本
cd backend
python quick_diagnose.py
```

### 常见问题及解决
| 问题         | 症状               | 解决方案                |
| ------------ | ------------------ | ----------------------- |
| 前端启动失败 | Node.js版本错误    | 升级到Node.js v18+      |
| 后端连接失败 | 数据库连接错误     | 检查.env配置和MySQL服务 |
| 跨域问题     | API调用被阻止      | 确认前后端端口配置      |
| ML训练失败   | 数据量不足         | 确保数据库有≥3个用户    |
| 权限错误     | 管理员功能无法访问 | 检查用户role字段        |

详细的故障排除步骤请参考 [故障排除手册](./docs/troubleshooting.md)
```
Data_Visualization_Project_Practice
├─ backend
│  ├─ app.py
│  ├─ backups
│  ├─ backup_mysql.py
│  ├─ database_import
│  │  ├─ data_analysis.py
│  │  ├─ discussion_importer.py
│  │  ├─ exam_statistic_importer.py
│  │  ├─ homework_statistic_importer.py
│  │  ├─ offline_importer.py
│  │  ├─ synthesis_grades_importer.py
│  │  ├─ users_importer.py
│  │  ├─ video_watching_importer.py
│  │  └─ __init__.py
│  ├─ migrations
│  │  ├─ alembic.ini
│  │  ├─ env.py
│  │  ├─ README
│  │  ├─ script.py.mako
│  │  ├─ versions
│  │  │  ├─ 067be5e0157f_.py
│  │  │  ├─ 4dcc26af386a_.py
│  │  │  ├─ 5a4fa81b92a6_.py
│  │  │  ├─ 804a032e670d_.py
│  │  │  ├─ 850d14a51522_添加作业统计表.py
│  │  │  ├─ b650d471895b_更新用户模型.py
│  │  │  ├─ d2c83409de8a_.py
│  │  │  └─ e0e741e6d389_.py
│  │  └─ __init__.py
│  └─ requirements.txt
├─ frontend
│  ├─ .editorconfig
│  ├─ .prettierrc.json
│  ├─ eslint.config.js
│  ├─ index.html
│  ├─ jsconfig.json
│  ├─ package.json
│  ├─ public
│  │  └─ favicon.ico
│  ├─ README.md
│  ├─ src
│  │  ├─ App.vue
│  │  ├─ assets
│  │  │  ├─ base.css
│  │  │  ├─ logo.svg
│  │  │  └─ main.css
│  │  ├─ components
│  │  │  ├─ charts
│  │  │  │  └─ BaseChart.vue
│  │  │  ├─ HelloWorld.vue
│  │  │  ├─ icons
│  │  │  │  ├─ IconCommunity.vue
│  │  │  │  ├─ IconDocumentation.vue
│  │  │  │  ├─ IconEcosystem.vue
│  │  │  │  ├─ IconSupport.vue
│  │  │  │  └─ IconTooling.vue
│  │  │  ├─ TheWelcome.vue
│  │  │  └─ WelcomeItem.vue
│  │  ├─ main.js
│  │  ├─ router
│  │  │  └─ index.js
│  │  ├─ services
│  │  │  └─ api.js
│  │  ├─ styles
│  │  │  └─ global.css
│  │  └─ views
│  │     ├─ AdminDashboardView.vue
│  │     ├─ DashboardView.vue
│  │     ├─ DataImport.vue
│  │     ├─ LoginView.vue
│  │     └─ RegisterView.vue
│  └─ vite.config.js
├─ package.json
├─ project.zip
├─ README.md
├─ scripts
└─ tests

```