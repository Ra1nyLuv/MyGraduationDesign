# 部署指南

## 📋 部署概述

本文档详细说明数据可视化分析系统的生产环境部署流程，包括服务器配置、应用部署和监控设置。

### 系统架构

```
[用户] → [Nginx] → [前端静态文件]
                 → [后端Flask应用] → [MySQL数据库]
```

---

## 🖥️ 服务器要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 50GB SSD
- **操作系统**: Ubuntu 20.04 LTS / CentOS 8

### 推荐配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 100GB SSD
- **操作系统**: Ubuntu 22.04 LTS

### 软件要求
- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- Nginx 1.18+
- PM2 (进程管理器)

---

## 🚀 部署流程

### 1. 服务器准备

#### 1.1 更新系统

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

#### 1.2 安装基础软件

```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv nodejs npm mysql-server nginx git

# CentOS/RHEL
sudo yum install -y python3 python3-pip nodejs npm mysql-server nginx git
```

#### 1.3 配置防火墙

```bash
# 开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 3306  # MySQL (仅内网)
sudo ufw enable
```

### 2. 数据库配置

#### 2.1 MySQL配置

```bash
# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation
```

#### 2.2 创建数据库和用户

```sql
-- 登录MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE project_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建应用用户
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON project_db.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 2.3 优化MySQL配置

编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`：

```ini
[mysqld]
# 性能优化
innodb_buffer_pool_size = 2G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT

# 连接设置
max_connections = 200
wait_timeout = 300

# 字符集
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

重启MySQL：
```bash
sudo systemctl restart mysql
```

### 3. 应用部署

#### 3.1 创建应用用户

```bash
sudo useradd -m -s /bin/bash app
sudo su - app
```

#### 3.2 部署代码

```bash
# 克隆代码
git clone ssh://git@ssh.github.com:443/Ra1nyLuv/Data_Visualization_Project_Practice.git
cd Data_Visualization_Project_Practice

# 创建生产环境配置
cp .env.example .env.production
```

#### 3.3 编辑生产环境配置

编辑 `.env.production`：

```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_USER=app_user
MYSQL_PASSWORD=strong_password_here
MYSQL_DB=project_db

# Flask配置
FLASK_DEBUG=False
FLASK_ENV=production

# JWT配置 (使用强密钥)
JWT_SECRET_KEY=your-production-super-secret-jwt-key-with-256-bits-minimum

# 安全配置
SECRET_KEY=another-production-secret-key-for-sessions
```

#### 3.4 后端部署

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装生产环境依赖
pip install gunicorn

# 数据库迁移
export FLASK_APP=app.py
flask db upgrade

# 数据导入
cd database_import
python users_importer.py
python synthesis_grades_importer.py
# ... 其他导入脚本
cd ..
```

#### 3.5 前端构建

```bash
cd ../frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 构建结果在 dist/ 目录
```

### 4. 进程管理配置

#### 4.1 安装PM2

```bash
sudo npm install -g pm2
```

#### 4.2 创建PM2配置文件

创建 `ecosystem.config.js`：

```javascript
module.exports = {
  apps: [{
    name: 'data-viz-backend',
    cwd: '/home/app/Data_Visualization_Project_Practice/backend',
    script: 'gunicorn',
    args: '--bind 127.0.0.1:5000 --workers 4 --timeout 120 app:app',
    interpreter: '/home/app/Data_Visualization_Project_Practice/backend/venv/bin/python',
    env: {
      FLASK_ENV: 'production',
      PYTHONPATH: '/home/app/Data_Visualization_Project_Practice/backend'
    },
    error_file: '/var/log/pm2/data-viz-backend-error.log',
    out_file: '/var/log/pm2/data-viz-backend-out.log',
    log_file: '/var/log/pm2/data-viz-backend.log',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G'
  }]
}
```

#### 4.3 启动应用

```bash
# 创建日志目录
sudo mkdir -p /var/log/pm2
sudo chown app:app /var/log/pm2

# 启动应用
pm2 start ecosystem.config.js

# 保存PM2配置
pm2 save

# 设置开机自启
pm2 startup
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u app --hp /home/app
```

### 5. Nginx配置

#### 5.1 创建Nginx配置文件

创建 `/etc/nginx/sites-available/data-visualization`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /home/app/Data_Visualization_Project_Practice/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # 缓存设置
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 日志配置
    access_log /var/log/nginx/data-viz-access.log;
    error_log /var/log/nginx/data-viz-error.log;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

#### 5.2 启用站点

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/data-visualization /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载Nginx
sudo systemctl reload nginx
```

### 6. SSL证书配置 (推荐)

#### 6.1 使用Let's Encrypt

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 监控与维护

### 1. 应用监控

#### 1.1 PM2监控

```bash
# 查看应用状态
pm2 status

# 查看实时日志
pm2 logs

# 查看监控信息
pm2 monit

# 重启应用
pm2 restart data-viz-backend
```

#### 1.2 系统监控

安装系统监控工具：

```bash
sudo apt install htop iotop nethogs
```

#### 1.3 日志监控

创建日志轮转配置 `/etc/logrotate.d/data-visualization`：

```
/var/log/pm2/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 app app
    postrotate
        pm2 reloadLogs
    endscript
}
```

### 2. 数据库维护

#### 2.1 备份脚本

创建 `/home/app/scripts/backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/home/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
mysqldump -u app_user -p'strong_password_here' project_db > $BACKUP_FILE

# 压缩备份
gzip $BACKUP_FILE

# 删除7天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

设置定时备份：
```bash
chmod +x /home/app/scripts/backup.sh
crontab -e
# 添加: 0 2 * * * /home/app/scripts/backup.sh
```

#### 2.2 性能优化

定期优化数据库：

```sql
-- 分析表
ANALYZE TABLE users, synthesis_grades, homework_statistic;

-- 优化表
OPTIMIZE TABLE users, synthesis_grades, homework_statistic;

-- 检查索引使用情况
SHOW INDEX FROM users;
```

### 3. 安全维护

#### 3.1 系统更新

```bash
# 每周执行
sudo apt update && sudo apt upgrade -y
sudo systemctl reboot
```

#### 3.2 安全扫描

```bash
# 安装安全工具
sudo apt install fail2ban ufw

# 配置fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
# 编辑配置文件，启用SSH保护
```

#### 3.3 密钥轮换

定期更换JWT密钥和数据库密码。

---

## 🔄 更新部署

### 1. 代码更新流程

```bash
# 切换到应用用户
sudo su - app
cd Data_Visualization_Project_Practice

# 备份当前版本
git tag backup-$(date +%Y%m%d_%H%M%S)

# 获取最新代码
git pull origin main

# 更新后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 运行数据库迁移
flask db upgrade

# 重新构建前端
cd ../frontend
npm install
npm run build

# 重启应用
pm2 restart data-viz-backend

# 重载Nginx (如有静态文件更新)
sudo systemctl reload nginx
```

### 2. 滚动更新策略

对于零停机部署：

```bash
# 方案1: 蓝绿部署
# 在新端口启动新版本
pm2 start ecosystem.config.js --name data-viz-backend-new

# 更新Nginx配置指向新端口
# 停止旧版本
pm2 delete data-viz-backend

# 方案2: 使用负载均衡
# 配置多个实例，逐个更新
```

---

## 🛠️ 故障排除

### 1. 常见问题

#### 应用无法启动
```bash
# 检查PM2状态
pm2 status

# 查看错误日志
pm2 logs data-viz-backend

# 检查端口占用
sudo netstat -tlnp | grep :5000
```

#### 数据库连接失败
```bash
# 检查MySQL状态
sudo systemctl status mysql

# 测试连接
mysql -u app_user -p project_db

# 检查配置文件
cat .env.production
```

#### Nginx 502错误
```bash
# 检查Nginx错误日志
sudo tail -f /var/log/nginx/error.log

# 检查后端服务状态
curl http://127.0.0.1:5000/api/

# 重启服务
pm2 restart data-viz-backend
sudo systemctl restart nginx
```

### 2. 性能问题

#### 响应缓慢
```bash
# 检查系统资源
htop
iostat -x 1

# 检查数据库性能
mysql -u root -p -e "SHOW PROCESSLIST;"

# 分析慢查询
mysql -u root -p -e "SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;"
```

#### 内存不足
```bash
# 清理系统缓存
sudo sync && sudo sysctl vm.drop_caches=3

# 重启应用释放内存
pm2 restart data-viz-backend

# 检查内存使用
free -h
```

---

## 📞 技术支持

### 联系信息
- **项目负责人**: 陈俊霖
- **开发团队**: 莆田学院 新工科产业学院 数据225
- **邮箱**: [技术支持邮箱]

### 紧急联系
- **系统故障**: [紧急联系电话]
- **安全事件**: [安全团队联系方式]

### 文档更新
本文档最后更新: 2025-01-02
如有问题或建议，请联系开发团队。