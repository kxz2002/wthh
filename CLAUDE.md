# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个"梧桐杯"智慧数据应用大赛的家庭圈用户识别系统，基于多维度数据（地址、账户、设备、通信等）识别家庭成员关系，并确定家庭关键人。

## 常用命令

```bash
# 激活 Conda 虚拟环境
conda activate wthh
# 或
source ~/anaconda3/etc/profile.d/conda.sh && conda activate wthh

# 运行主程序（模型训练和预测）
python src/apps/main.py

# 启动Web可视化界面
python src/apps/app.py
```

## 虚拟环境

- **环境名称**: wthh
- **Python 版本**: 3.10
- **Conda 路径**: ~/anaconda3
- **环境位置**: ~/anaconda3/envs/wthh

创建环境命令：
```bash
conda create -n wthh python=3.10 -y
conda activate wthh
pip install pandas numpy scikit-learn flask networkx openpyxl
```

注意：代码中的路径已改为相对于脚本位置的相对路径，数据文件应放在 `src/data/` 目录下。

## 项目架构

```
wthh/
├── src/                       # 源代码目录
│   ├── core/                  # 核心模块
│   │   ├── data_loader.py     # 数据加载
│   │   ├── feature_engineering.py
│   │   ├── feature_engineering_enhanced.py
│   │   └── family_circle_model.py
│   ├── apps/                  # 应用入口
│   │   ├── main.py            # 主程序
│   │   └── app.py             # Flask Web
│   ├── tools/                 # 工具脚本
│   │   ├── check_*.py
│   │   ├── view_results.py
│   │   └── report_generator.py
│   ├── scripts/               # 独立脚本
│   │   └── analyze_large_circle.py
│   ├── data/                  # 原始数据
│   ├── output/                # 输出结果
│   └── templates/
│       └── index.html
├── docs/                      # 技术文档
├── quickstart.txt            # 快速开始
├── README.md
├── requirements.txt
└── CLAUDE.md
```

## 核心模块说明

### 1. 数据加载 (core/data_loader.py)
- 处理Excel文件的特殊格式：第一行英文表头，第二行中文表头，第三行开始是数据
- `DataLoader.load_data()` 读取3个sheet
- `DataLoader.flatten_columns()` 将多级表头扁平化为中文列名

### 2. 特征工程 (core/feature_engineering*.py)
- 地址关联性特征
- 缴费账户关联性特征
- 终端共享特征
- 通信行为特征
- 基础信息特征

### 3. 家庭圈识别模型 (core/family_circle_model.py)
- 支持两种方法：
  - **监督学习**：使用LightGBM/XGBoost/RandomForest分类器（当有标签数据时）
  - **无监督学习**：基于图连通分量的聚类算法（当无标签数据时）
- 关系规则权重：账户关联(0.4) > 地址关联(0.3) > 设备共享(0.2) > 通信行为(0.1)
- 关键人识别：基于账户主、缴费行为、通信中心度等

### 4. Web可视化 (apps/app.py)
Flask应用，提供以下API端点：
- `/` - 主页面
- `/api/statistics` - 统计信息
- `/api/family_circles` - 家庭圈列表（分页）
- `/api/user/<user_id>` - 用户详情
- `/api/search` - 用户搜索
- `/api/relationship` - 用户关系查询
- `/api/circle_graph/<circle_id>` - 家庭圈知识图谱

## 数据格式

Excel文件包含3个sheet：
- Sheet 1: 带标签的训练数据（5000条）
- Sheet 2: 不带标签的验证数据（5000条）
- Sheet 3: 不带标签的测试数据（2000条）

输出CSV格式：
- `用户ID, family_circle_id, is_key_person`

## Git 工作流规范

### 分支管理规则

1. **master 分支保护**
   - 禁止直接在 master 分支上修改代码
   - 禁止在 master 分支上提交代码
   - 禁止将本地分支合并到本地 master 分支

2. **分支命名规范**
   - 所有新分支必须以 `openclaw/` 开头
   - 示例：`openclaw/feature-A`、`openclaw/bugfix-login`

3. **PR 合并规则**
   - 禁止自行审批通过 PR
   - PR 必须由人工审核后才能合并
   - 可以在确认开发完成后自行创建并提交 PR

### 提交规范

**提交格式：**
```
[Tag] 标题

详细描述（可选）
```

**Tag 类型：**
| Tag | 说明 | 示例 |
|-----|------|------|
| Feature | 新功能 | [Feature] Add user login |
| Bugfix | Bug修复 | [Bugfix] Fix login error |
| Doc | 文档更新 | [Doc] Update README |
| Model | 模型相关 | [Model] Add new feature |
| Refactor | 代码重构 | [Refactor] Optimize data loader |
| Style | 代码格式 | [Style] Format code |
| Test | 测试相关 | [Test] Add unit tests |
| Config | 配置变更 | [Config] Update requirements |

**示例：**
```
[Feature] Add user authentication

Implement OAuth2 login with Google and GitHub providers.
Include token refresh and session management.
```

### 开发流程

```bash
# 1. 创建新分支
git checkout -b openclaw/feature-xxx

# 2. 开发并提交
git add .
git commit -m "[Feature] Add new feature"

# 3. 推送到远程
git push -u origin openclaw/feature-xxx

# 4. 在 GitHub 上创建 PR
# 等待人工审核后合并
```
