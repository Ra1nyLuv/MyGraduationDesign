# 课程学习数据可视化分析系统

## 项目介绍
本项目是一个基于Vue.js和Flask的PTU数据可视化课程学习数据可视化分析系统，用于展示和分析学生的学习成绩、行为数据等信息。
该项目采用前后端分离架构，前端使用Vue.js和Element Plus进行开发，后端使用Python Flask和SQLAlchemy进行开发。
## 功能特点
- 学生数据可视化看板
- 管理员数据管理界面
- 成绩分布分析
- 学习行为分析
- 视频学习时段热力图

## 技术栈
### 前端
- Vue.js 3 (v3.5.13)
- Element Plus (v2.9.7)
- ECharts (v5.6.0)
- Vite (v6.1.0)
- Vue Router (v4.5.0)
- Axios (v1.8.4)

### 后端
- Python Flask (latest)
- Flask-CORS (latest)
- Flask-SQLAlchemy (latest)
- Python-dotenv (latest)
- Flask-Bcrypt (latest)
- PyMySQL (latest)
- Flask-Migrate (latest)
- MySQL (latest)

## 安装部署
### 环境要求
- Node.js v18+
- Python 3.9+
- MySQL 8.0+

### 1.注意自行修改/.env文件配置
### 2.数据库
在/backend目录下, 运行`flask db upgrade && flask db migrate
导入从超星导出的数据可视化课程成绩数据(本项目中为`data/BigData233-234(Python).xlsx`)
导入脚本已经准备好, 路径:`backend/database_import`
运行importer脚本后, 数据插入完成
- user表导入脚本中默认设置普通用户的密码为`1234`
- 注意数据文件存放路径
#### 注意:出于安全考虑, 数据文件中无管理员用户数据, 运行导入脚本中未插入管理员账户, 需要在/register页面注册管理员账户, 并手动修改数据库users表将其role字段改为admin, 例如注册了一个id为admin的用户, 例如:
```
('admin', '管理员', 'password','13912345678', 'user');
```
请手动在数据库端修改role字段为admin, 例如:
```
update users set role = 'admin' where id = 'admin';
```

### 3.前端
1. 进入frontend目录
2. 运行 `npm install` 安装依赖
3. 配置环境变量(如有需要)
4. 运行 `npm run dev` 启动开发服务器

### 4.后端
1. 创建Python虚拟环境
2. 安装依赖 `pip install -r requirements.txt`
3. 配置数据库连接(修改.env文件)
4. 运行数据库迁移 `flask db upgrade`
5. 运行 `python app.py` 启动服务

## 常见问题
1. 前端启动失败：检查Node.js版本是否符合要求
2. 后端数据库连接失败：检查.env文件配置和MySQL服务状态
3. 跨域问题：确保前后端端口配置正确

## 项目结构
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