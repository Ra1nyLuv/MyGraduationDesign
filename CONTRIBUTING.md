# 贡献指南

感谢您对本项目的关注和贡献！本文档将帮助您了解如何参与项目开发。

## 📋 开发流程

### 1. 开发环境设置

请参考 [开发环境配置指南](./docs/development.md) 完成环境搭建。

### 2. 分支管理

```bash
# 主分支
main - 生产环境代码
develop - 开发环境代码

# 功能分支命名规范
feature/功能名称 - 新功能开发
bugfix/问题描述 - 问题修复
hotfix/紧急修复 - 紧急修复
docs/文档更新 - 文档相关更新
refactor/重构描述 - 代码重构
```

### 3. 提交流程

```bash
# 1. 从develop分支创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 开发和测试
# ... 进行开发

# 3. 提交代码
git add .
git commit -m "feat: 添加新功能描述"

# 4. 推送分支
git push origin feature/new-feature

# 5. 创建Pull Request
# 在GitHub上创建PR，目标分支为develop
```

## 📝 代码规范

### 1. 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```bash
<类型>(<范围>): <描述>

类型包括：
- feat: 新功能
- fix: 问题修复
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建工具或辅助工具的变动

示例：
feat(auth): 添加JWT认证功能
fix(ml): 修复聚类分析数据处理问题
docs(api): 更新API文档
refactor(backend): 重构用户模型结构
```

### 2. Python代码规范

```python
# 使用类型注解
def get_user_data(user_id: str) -> Dict[str, Any]:
    """
    获取用户数据
    
    Args:
        user_id: 用户ID
        
    Returns:
        用户数据字典
        
    Raises:
        ValueError: 当用户ID无效时
    """
    pass

# 遵循PEP 8规范
# 使用Black格式化工具
# 函数和类添加文档字符串
# 使用有意义的变量名
```

### 3. JavaScript代码规范

```javascript
/**
 * 获取用户数据
 * @param {string} userId - 用户ID
 * @returns {Promise<Object>} 用户数据
 */
const getUserData = async (userId) => {
  try {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error('获取用户数据失败:', error);
    throw error;
  }
};

// 使用 const/let，避免 var
// 使用 ES6+ 语法
// 函数添加 JSDoc 注释
// 使用 Prettier 格式化
```

### 4. Vue组件规范

```vue
<template>
  <!-- 使用语义化的HTML标签 -->
  <div class="user-dashboard">
    <h1>{{ title }}</h1>
    <!-- 组件应该有clear的层次结构 -->
  </div>
</template>

<script setup>
// 使用Composition API
// 导入语句放在顶部
import { ref, computed, onMounted } from 'vue';

// Props定义
const props = defineProps({
  userId: {
    type: String,
    required: true
  }
});

// 响应式数据
const title = ref('用户数据面板');

// 计算属性
const computedValue = computed(() => {
  // 计算逻辑
});

// 生命周期
onMounted(() => {
  // 初始化逻辑
});
</script>

<style scoped>
/* 使用scoped样式避免样式污染 */
.user-dashboard {
  padding: 20px;
}
</style>
```

## 🧪 测试要求

### 1. 后端测试

```python
# 单元测试示例
import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_user_registration(app):
    """测试用户注册功能"""
    with app.test_client() as client:
        response = client.post('/api/register', json={
            'id': 'test_user',
            'name': '测试用户',
            'password': 'test_password',
            'phone_number': '13800138000'
        })
        assert response.status_code == 201
        assert 'user_id' in response.json
```

### 2. 前端测试

```javascript
// 组件测试示例
import { mount } from '@vue/test-utils';
import UserDashboard from '@/components/UserDashboard.vue';

describe('UserDashboard', () => {
  it('应该正确渲染用户信息', () => {
    const wrapper = mount(UserDashboard, {
      props: {
        userId: 'test_user'
      }
    });
    
    expect(wrapper.find('.user-info').exists()).toBe(true);
  });
});
```

### 3. 测试运行

```bash
# 后端测试
cd backend
pytest tests/

# 前端测试
cd frontend
npm run test

# 覆盖率测试
cd backend
pytest --cov=app tests/
```

## 📚 文档规范

### 1. API文档

所有API接口都应该在 [API文档](./docs/api.md) 中有详细说明，包括：

- 接口地址和方法
- 请求参数
- 响应格式
- 错误码说明
- 使用示例

### 2. 代码注释

- Python函数使用docstring
- JavaScript函数使用JSDoc
- 复杂逻辑添加行内注释
- 配置文件添加说明注释

### 3. README更新

新功能开发完成后，应该更新相关的README文档。

## 🔍 代码审查

### 1. 自我检查清单

提交PR前请确认：

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 测试全部通过
- [ ] 更新了相关文档
- [ ] 没有引入新的安全风险
- [ ] 性能没有显著下降

### 2. PR模板

```markdown
## 变更说明
[简要描述本次变更的内容]

## 变更类型
- [ ] 新功能 (feature)
- [ ] 问题修复 (bugfix)
- [ ] 性能优化 (performance)
- [ ] 代码重构 (refactor)
- [ ] 文档更新 (docs)

## 测试
- [ ] 添加了单元测试
- [ ] 添加了集成测试
- [ ] 手动测试通过

## 影响范围
- [ ] 前端
- [ ] 后端
- [ ] 数据库
- [ ] 机器学习模块

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 更新了相关文档
- [ ] 没有破坏现有功能
```

## 🐛 问题报告

### 1. Bug报告模板

```markdown
## 问题描述
[详细描述遇到的问题]

## 重现步骤
1. 打开页面...
2. 点击按钮...
3. 查看结果...

## 预期行为
[描述期望的正确行为]

## 实际行为
[描述实际发生的行为]

## 环境信息
- 操作系统: 
- 浏览器: 
- Node.js版本: 
- Python版本: 

## 截图或日志
[如果有相关截图或错误日志，请附上]
```

### 2. 功能请求模板

```markdown
## 功能描述
[详细描述建议的新功能]

## 使用场景
[说明这个功能的使用场景和价值]

## 解决方案
[如果有具体的实现思路，请说明]

## 替代方案
[是否有其他解决方案]

## 优先级
- [ ] 高 (影响核心功能)
- [ ] 中 (改善用户体验)
- [ ] 低 (可有可无)
```

## 📞 联系方式

### 技术讨论
- **项目负责人**: 陈俊霖
- **开发团队**: 莆田学院 新工科产业学院 数据225

### 问题反馈
- **GitHub Issues**: 用于bug报告和功能请求
- **邮件联系**: [技术支持邮箱]

## 📄 许可证

本项目采用 [MIT License](./LICENSE)，欢迎大家使用和贡献。

---

感谢您的贡献！每一个PR都让项目变得更好。