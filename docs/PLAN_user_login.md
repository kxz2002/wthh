# 用户登录功能开发规划

## Phase 1: Discovery - 理解需求

### 当前项目状态

这是一个**家庭圈用户识别系统**的 Web 可视化应用，基于 Flask 框架。

**现有功能：**
- `/` - 首页展示
- `/api/statistics` - 统计数据
- `/api/family_circles` - 家庭圈列表（分页）
- `/api/user/<user_id>` - 用户详情
- `/api/search` - 用户搜索
- `/api/relationship` - 用户关系查询
- `/api/model_metrics` - 模型评估指标
- `/api/circle_graph/<circle_id>` - 家庭圈知识图谱

**现有技术栈：**
- Flask
- Pandas, NumPy, Scikit-learn
- 机器学习模型（家庭圈识别）

### 用户登录需求

实现用户登录功能，支持：
- 用户注册
- 用户登录/登出
- 权限控制（管理员 vs 普通用户）

---

## Phase 2: Codebase Exploration - 现有代码分析

### 已有的兼容点

1. **Flask 应用结构**：可以直接集成 Flask-Login
2. **现有路由**：受保护的路由需要添加登录验证
3. **模板系统**：已有的 `templates/index.html` 可以扩展登录页面

### 需要新增/修改的文件

| 操作 | 文件 | 说明 |
|------|------|------|
| 新增 | `core/user.py` | 用户模型 |
| 新增 | `apps/auth.py` | 认证蓝图 |
| 修改 | `apps/app.py` | 集成认证 |
| 新增 | `templates/login.html` | 登录页面 |
| 新增 | `templates/register.html` | 注册页面 |
| 新增 | `templates/dashboard.html` | 用户仪表板 |

---

## Phase 3: Clarifying Questions - 澄清问题

### 需要确认的问题

1. **用户数据存储**
   - 使用 SQLite（简单）还是 MySQL/PostgreSQL？
   - 是否需要连接到现有的用户数据？

2. **认证方式**
   - 仅需要用户名/密码？
   - 是否需要 OAuth（微信、GitHub 等）？

3. **权限角色**
   - 管理员可以做什么？
   - 普通用户可以做什么？

4. **Session 存储**
   - 服务器端 Session（默认）？
   - Redis Session？

---

## Phase 4: Architecture Design - 架构设计

### 推荐方案

**方案：Minimal Changes（推荐）**

使用 Flask-Login + SQLite，实现最简用户认证系统：

```
核心组件：
- User Model: 用户数据模型
- Auth Blueprint: 认证路由（/auth/login, /auth/register, /auth/logout）
- Login Required: 装饰器保护需要登录的路由
```

**优点：**
- 最小改动
- 与现有代码兼容
- 易于维护

---

## Phase 5: Implementation - 实现（待用户确认后开始）

### 实现步骤

1. 安装依赖：`flask-login flask-sqlalchemy werkzeug`
2. 创建用户模型
3. 创建认证蓝图
4. 修改 app.py 集成认证
5. 添加登录/注册/登出页面
6. 保护现有 API 路由
7. 添加用户权限控制

---

## Phase 6: Quality Review - 质量审查

实现完成后需要检查：
- 密码安全性（哈希存储）
- Session 安全
- XSS 防护
- 登录后重定向

---

## Phase 7: Summary - 总结

**待完成：**
- 用户注册/登录/登出
- 受保护的路由
- 用户权限控制
