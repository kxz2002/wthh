# API 接口文档

本文档记录了家庭圈用户识别系统提供的所有 API 接口。

## 基础信息

| 项目 | 说明 |
|------|------|
| 基础 URL | `http://localhost:5000` |
| 前端代理 | `http://localhost:5173` (开发环境) |
| 认证方式 | Session (Flask-Login) |
| 数据格式 | JSON |

---

## 认证接口 (Auth Blueprint)

### 1. 用户登录 (API)

**端点**: `POST /auth/api/login`

用户登录接口，返回用户信息。

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应** (成功):
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "created_at": "2026-03-02T12:00:00"
  }
}
```

**响应** (失败):
```json
{
  "error": "用户名或密码错误"
}
```

**状态码**:
- `200` - 登录成功
- `400` - 请求参数错误
- `401` - 用户名或密码错误

---

### 2. 用户注册 (API)

**端点**: `POST /auth/api/register`

注册新用户。

**请求体**:
```json
{
  "username": "string",
  "password": "string",
  "password_confirm": "string"
}
```

**响应** (成功):
```json
{
  "success": true,
  "user": {
    "id": 2,
    "username": "newuser",
    "role": "user",
    "created_at": "2026-03-02T12:00:00"
  }
}
```

**响应** (失败):
```json
{
  "error": "用户名已存在"
}
```

**状态码**:
- `201` - 注册成功
- `400` - 请求参数错误

---

### 3. 获取当前用户信息

**端点**: `GET /auth/api/userinfo`

获取当前登录用户的信息。

**响应** (已登录):
```json
{
  "id": 1,
  "username": "admin",
  "role": "admin",
  "created_at": "2026-03-02T12:00:00"
}
```

**响应** (未登录):
```json
{
  "error": "Not logged in"
}
```

**状态码**:
- `200` - 成功
- `401` - 未登录

---

### 4. 用户登出

**端点**: `GET /auth/logout`

退出当前登录状态。

**响应**: 重定向到登录页面

**状态码**: `302` (重定向)

---

### 5. 登录页面 (HTML)

**端点**: `GET /auth/login`

返回登录页面 HTML。

**状态码**: `200`

---

### 6. 注册页面 (HTML)

**端点**: `GET /auth/register`

返回注册页面 HTML。

**状态码**: `200`

---

## 数据接口 (Main Blueprint)

### 7. 获取统计数据

**端点**: `GET /api/statistics`

获取训练集、验证集、测试集的用户数量统计。

**响应**:
```json
{
  "train": {
    "total_users": 5000
  },
  "valid": {
    "total_users": 5000
  },
  "test": {
    "total_users": 2000
  }
}
```

**状态码**: `200`

---

### 8. 获取家庭圈列表

**端点**: `GET /api/family_circles`

分页获取家庭圈列表。

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 |
| per_page | int | 20 | 每页数量 |

**响应**:
```json
{
  "circles": [
    {
      "circle_id": 1,
      "size": 5,
      "key_person": 10001
    },
    {
      "circle_id": 2,
      "size": 3,
      "key_person": 10015
    }
  ],
  "total": 1000,
  "page": 1,
  "per_page": 20
}
```

**状态码**: `200`

---

### 9. 获取用户详情

**端点**: `GET /api/user/<user_id>`

根据用户 ID 获取用户详细信息及所属家庭圈。

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | string | 用户ID |

**响应**:
```json
{
  "user_id": "10001",
  "family_circle_id": 1,
  "is_key_person": true,
  "data": {
    "用户ID": 10001,
    "地址": "北京市朝阳区xxx",
    ...
  }
}
```

**状态码**:
- `200` - 成功
- `404` - 用户不存在

---

### 10. 搜索用户

**端点**: `GET /api/search`

根据用户 ID 进行模糊搜索。

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| q | string | 搜索关键词 |

**响应**:
```json
{
  "users": [
    {
      "user_id": "10001"
    },
    {
      "user_id": "10002"
    }
  ]
}
```

**状态码**: `200`

---

### 11. 获取模型指标

**端点**: `GET /api/model_metrics`

获取模型评估指标（如果存在）。

**响应**:
```json
{
  "accuracy": 0.95,
  "precision": 0.93,
  "recall": 0.92,
  "f1_score": 0.925
}
```

**状态码**: `200`

---

### 12. 获取家庭圈知识图谱

**端点**: `GET /api/circle_graph/<circle_id>`

获取指定家庭圈的知识图谱数据，包括节点（用户）和边（关系）。

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| circle_id | int | 家庭圈ID |

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| dataset | string | train | 数据集 (train/valid/test) |

**响应**:
```json
{
  "nodes": [
    {
      "id": "10001",
      "label": "10001 (关键人)",
      "group": "key_person",
      "title": "用户: 10001\n关键人"
    },
    {
      "id": "10002",
      "label": "10002",
      "group": "member",
      "title": "用户: 10002\n成员"
    }
  ],
  "edges": [
    {
      "from": "10001",
      "to": "10002",
      "label": "地址关联",
      "color": {"color": "#97C2FC"}
    },
    {
      "from": "10001",
      "to": "10003",
      "label": "账户关联",
      "color": {"color": "#FFB84D"}
    }
  ]
}
```

**节点字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 用户ID |
| label | string | 显示标签 |
| group | string | 分组 (key_person/member) |
| title | string | 鼠标悬停提示 |

**边字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| from | string | 起始用户ID |
| to | string | 目标用户ID |
| label | string | 关系类型 (地址关联/账户关联) |
| color | object | 边的颜色 |

**状态码**:
- `200` - 成功
- `404` - 家庭圈不存在

---

## 页面路由

### 13. 首页

**端点**: `GET /`

返回系统首页。**需要登录**。

**状态码**:
- `200` - 已登录
- `302` - 未登录，重定向到登录页

---

### 14. 仪表板

**端点**: `GET /dashboard`

返回用户仪表板。**需要登录**。

**状态码**:
- `200` - 已登录
- `302` - 未登录

---

## 前端 API 调用示例

### 使用 Vue + Axios

```javascript
import { authAPI, dataAPI } from '@/api'

// 登录
const loginRes = await authAPI.login('username', 'password')
console.log(loginRes.data.user)

// 获取统计数据
const statsRes = await dataAPI.getStatistics()
console.log(statsRes.data)

// 获取家庭圈列表
const circlesRes = await dataAPI.getFamilyCircles(1, 20)
console.log(circlesRes.data.circles)

// 搜索用户
const searchRes = await dataAPI.searchUsers('100')
console.log(searchRes.data.users)

// 登出
await authAPI.logout()
```

---

## 错误响应格式

所有 API 错误响应格式如下：

```json
{
  "error": "错误描述信息"
}
```

常见 HTTP 状态码：

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 302 | 重定向 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 注意事项

1. **认证**: 除登录、注册、统计数据外，其他接口可能需要登录
2. **CORS**: 生产环境需配置正确的 CORS 策略
3. **数据加载**: 首次调用数据接口会加载模型和数据，可能较慢
4. **数据库**: 用户数据存储在 SQLite 数据库中 (默认 `wthh.db`)
