# 用户登录功能开发规划

## Phase 1: Discovery - 理解需求

### 确认的需求

1. **用户数据存储**：MySQL（如未安装，可使用 Docker 部署）
2. **认证方式**：用户名 + 密码
3. **用户角色**：管理员、普通用户

---

## 架构设计 - 支持未来 Redis 扩展

### 推荐架构

```
┌─────────────────────────────────────────────────────────┐
│                      Flask App                          │
├─────────────────────────────────────────────────────────┤
│  Auth Service (认证服务层)                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Token Manager (可切换实现)                       │  │
│  │  ├── SessionTokenManager (当前实现)              │  │
│  │  └── RedisTokenManager (未来扩展)               │  │
│  └─────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  User Service (用户服务)                         │  │
│  │  └── MySQL/UserRepository                       │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 可扩展设计

| 组件 | 当前实现 | 未来扩展 |
|------|---------|---------|
| 存储 | MySQL | 可切换 PostgreSQL |
| 缓存 | Session | Redis Token |
| 认证 | Session | JWT + Redis |

---

## 实现方案

### 文件结构

```
src/
├── core/
│   ├── user.py              # 用户模型
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── base.py         # 认证基类
│   │   ├── session.py      # Session认证
│   │   └── token.py       # Token认证(预留)
│   ├── repository/
│   │   ├── __init__.py
│   │   └── user_repo.py   # 用户仓库
│   └── database.py         # 数据库配置
├── apps/
│   ├── auth.py             # 认证蓝图
│   └── app.py              # 主应用
├── templates/
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── config.py               # 配置文件
```

### 数据库设计

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 待确认

1. **MySQL 连接信息**：
   - Host: localhost?
   - Port: 3306?
   - Database: wthh?
   - Username/Password: ?

2. **Docker 安装**：需要您手动安装 Docker 或 MySQL

---

## 实现步骤

1. 创建数据库配置模块
2. 创建用户模型
3. 实现认证服务（Session 方式）
4. 创建认证蓝图
5. 更新主应用
6. 添加登录/注册页面
7. 添加权限控制中间件
