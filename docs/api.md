# API 接口文档

## 概述

本文档描述了数据可视化分析系统的所有API接口。所有API遵循RESTful规范，使用JSON格式进行数据交换。

### 基础信息

- **基础URL**: `http://localhost:5000/api`
- **认证方式**: JWT Bearer Token
- **内容类型**: `application/json`
- **字符编码**: `UTF-8`

### 响应格式规范

所有API响应都遵循统一格式：

```json
{
  "success": true,              // 请求是否成功
  "message": "操作成功",        // 响应消息
  "data": {},                   // 响应数据
  "error": null                 // 错误信息（仅在失败时存在）
}
```

### 错误处理

- `200` - 请求成功
- `400` - 请求参数错误
- `401` - 认证失败/token无效
- `403` - 权限不足
- `404` - 资源不存在
- `500` - 服务器内部错误

---

## 1. 认证接口

### 1.1 用户登录

**接口地址**: `POST /api/login`

**请求参数**:
```json
{
  "id": "学号/工号",
  "password": "密码"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "id": "2021001",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "role": "user"
  }
}
```

### 1.2 用户注册

**接口地址**: `POST /api/register`

**请求参数**:
```json
{
  "id": "学号/工号",
  "name": "姓名",
  "password": "密码",
  "phone_number": "手机号码"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "用户注册成功",
  "data": {
    "user_id": "2021001"
  }
}
```

---

## 2. 用户数据接口

### 2.1 获取用户数据

**接口地址**: `GET /api/my-data`

**认证**: 需要JWT Token

**查询参数**:
- `id` (可选): 学生ID，仅管理员可查看其他用户数据

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "2021001",
      "name": "张三"
    },
    "scores": {
      "comprehensive": 85.5,
      "course_points": 88.0,
      "exam": 82.0,
      "homework": [85, 87, 83, 90, 88, 85, 89, 91]
    },
    "behavior": {
      "posted": 5,
      "replied": 12,
      "upvotes": 3
    },
    "progress": {
      "rumination_ratios": [1.2, 1.5, 0.8, 2.1, 1.3, 0.9, 1.7]
    },
    "rank": 15,
    "total_students": 80
  }
}
```

### 2.2 获取管理员统计数据

**接口地址**: `GET /api/admin-stats`

**认证**: 需要管理员权限

**响应示例**:
```json
{
  "success": true,
  "data": {
    "userCount": 80,
    "activeUsers": 72,
    "avgComprehensiveScore": 82.5,
    "maxComprehensiveScore": 95.0,
    "minComprehensiveScore": 45.5,
    "avgExamScore": 78.3,
    "maxExamScore": 98.0,
    "minExamScore": 32.0,
    "scoreDistribution": {
      "60以下": 5,
      "60-70": 12,
      "70-80": 25,
      "80-90": 30,
      "90以上": 8
    },
    "students": [
      {
        "id": "2021001",
        "name": "张三",
        "comprehensive_score": 85.5,
        "exam_score": 82.0,
        "phone_number": "138****5678"
      }
    ]
  }
}
```

---

## 3. 机器学习接口

### 3.1 模型训练

**接口地址**: `POST /api/ml/train-models`

**认证**: 需要管理员权限

**响应示例**:
```json
{
  "success": true,
  "message": "模型训练完成，成功训练 3/3 个模型",
  "data": {
    "total_samples": 80,
    "training_time": "2025-01-02T15:30:00Z",
    "training_results": {
      "grade_prediction": {
        "success": true,
        "message": "成绩预测模型训练成功"
      },
      "clustering": {
        "success": true,
        "message": "聚类模型训练成功"
      },
      "anomaly_detection": {
        "success": true,
        "message": "异常检测模型训练成功"
      }
    }
  }
}
```

### 3.2 聚类分析

**接口地址**: `GET /api/ml/cluster-analysis`

**认证**: 可选JWT Token

**响应示例**:
```json
{
  "success": true,
  "data": {
    "analysis": {
      "total_users": 80,
      "cluster_distribution": {
        "0": {
          "name": "高效学习型",
          "count": 25,
          "users": ["2021001", "2021002"],
          "percentage": 31.25,
          "characteristics": [
            "作业成绩优秀",
            "作业完成率高",
            "讨论非常活跃"
          ]
        },
        "1": {
          "name": "稳定学习型",
          "count": 30,
          "users": ["2021003", "2021004"],
          "percentage": 37.5,
          "characteristics": [
            "作业成绩良好",
            "作业完成率中等",
            "讨论较为活跃"
          ]
        }
      }
    }
  }
}
```

### 3.3 异常检测

**接口地址**: `GET /api/ml/anomaly-detection`

**认证**: 可选JWT Token

**响应示例**:
```json
{
  "success": true,
  "data": {
    "results": {
      "total_users": 80,
      "anomaly_count": 8,
      "normal_count": 72,
      "anomaly_rate": 10.0,
      "anomalies": [
        {
          "user_id": "2021050",
          "anomaly_score": -0.65,
          "severity": "high",
          "anomaly_types": [
            "low_engagement",
            "irregular_pattern"
          ]
        }
      ],
      "summary": "🚨 发现 3 个高风险学生 | ⚠️ 发现 5 个中等风险学生"
    }
  }
}
```

---

## 4. 数据导入接口

### 4.1 文件上传导入

**接口地址**: `POST /api/import-data`

**认证**: 需要管理员权限

**请求方式**: `multipart/form-data`

**请求参数**:
- `file`: Excel文件

**响应示例**:
```json
{
  "success": true,
  "message": "数据导入成功",
  "data": {
    "imported_records": 80,
    "import_time": "2025-01-02T15:30:00Z"
  }
}
```

---

## 5. 异常类型说明

### 异常行为类型定义

| 类型         | 英文标识                | 中文描述                   | 严重程度判断                 |
| ------------ | ----------------------- | -------------------------- | ---------------------------- |
| 学习参与度低 | `low_engagement`        | 作业完成率低，讨论参与少   | engagement_score < -1        |
| 学习规律异常 | `irregular_pattern`     | 学习行为不规律，成绩波动大 | homework_consistency < -1    |
| 学习表现不佳 | `poor_performance`      | 学术成绩显著低于平均水平   | academic_performance < -1.5  |
| 学习困难较大 | `excessive_struggle`    | 重复观看视频过多，理解困难 | video_rumination_ratio > 1.5 |
| 行为不一致   | `inconsistent_behavior` | 参与度与成绩不匹配         | 复合条件判断                 |

### 严重程度级别

- **high**: 异常分数 < -0.5
- **medium**: -0.5 ≤ 异常分数 < -0.2  
- **low**: 异常分数 ≥ -0.2

---

## 6. 使用示例

### JavaScript (前端)

```javascript
// 登录示例
const login = async (credentials) => {
  try {
    const response = await axios.post('/api/login', credentials);
    if (response.data.success) {
      // 保存token
      localStorage.setItem('access_token', response.data.data.token);
      return response.data.data;
    }
  } catch (error) {
    console.error('登录失败:', error.response.data.error);
  }
};

// 获取用户数据示例
const getUserData = async (studentId = '') => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.get('/api/my-data', {
      params: { id: studentId },
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data.data;
  } catch (error) {
    console.error('获取数据失败:', error.response.data.error);
  }
};
```

### Python (后端测试)

```python
import requests

# 测试登录
def test_login():
    response = requests.post('http://localhost:5000/api/login', json={
        'id': '2021001',
        'password': '1234'
    })
    return response.json()

# 测试聚类分析
def test_cluster_analysis():
    response = requests.get('http://localhost:5000/api/ml/cluster-analysis')
    return response.json()
```

---

## 7. 注意事项

### 安全性
- 所有敏感操作需要有效的JWT Token
- 管理员权限验证通过用户ID前缀 `admin` 判断
- 密码使用Bcrypt加密存储

### 性能建议
- 机器学习接口响应时间较长，建议设置合适的超时时间
- 大数据量查询时使用分页机制
- 生产环境建议启用缓存机制

### 错误处理
- 前端应实现统一的错误处理机制
- 网络错误时提供友好的用户提示
- 建议实现请求重试机制

### CORS配置
- 开发环境允许 `http://localhost:5173` 跨域访问
- 生产环境需要配置正确的域名白名单