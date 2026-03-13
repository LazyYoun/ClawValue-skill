---
name: clawvalue
description: "OpenClaw Claw度评估系统 - 量化你的 AI 自动化能力，生成龙虾能力估Skill 趣味评估报告"
version: 1.0.0
metadata:
  clawdbot:
    emoji: "🦞"
    requires:
      py:
        - sqlite3
        - flask
        - requests
    config:
      env:
        CLAWVALUE_DATA_DIR:
          description: 数据目录
          default: ~/.openclaw/workspace/data
        CLAWVALUE_DB_PATH:
          description: SQLite 数据库路径
          default: ~/.openclaw/workspace/data/clawvalue.db
---

# OpenClaw Claw度评估系统

量化你在 OpenClaw 上的 AI 自动化能力，生成趣味化的"龙虾能力估Skill"评估报告。

## 功能特点

- 📊 **使用深度评估**：三级技术指标体系（浅度/中度/深度）
- 💰 **价值估算**：基于真实数据的价值量化
- 🦞 **趣味表达**："龙虾能力估Skill" 等级与调侃话术
- 📈 **多维图表**：使用频率、技能分布、Token 消耗等可视化
- 💾 **本地存储**：SQLite 持久化历史数据
- 🌐 **多模式访问**：API / 命令行 / Web 页面

## 快速开始

### 方式一：提示词模式（直接返回 JSON）

```bash
python3 scripts/analyzer.py --mode json
```

**输出示例：**
```json
{
  "level": "中度使用",
  "value_estimate": "3,500元",
  "skill_count": 12,
  "session_count": 156,
  "usage_days": 45,
  "lobster_skill": "🦞 龙虾能力估Skill v1.0 - 七分熟"
}
```

### 方式二：启动后端服务

```bash
python3 scripts/server.py --port 5002
```

访问：http://localhost:5002

### 方式三：直接打开 Web 页面

```bash
open web/index.html
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/stats` | GET | 获取统计数据 |
| `/api/skills` | GET | 获取技能列表 |
| `/api/sessions` | GET | 获取会话历史 |
| `/api/evaluation` | GET | 获取评估结果 |
| `/api/refresh` | POST | 刷新数据 |

## 使用深度指标

| 维度 | 浅度 | 中度 | 深度 |
|------|------|------|------|
| 基础交互 | 简单问答 | 调用技能 | 跨平台控制 |
| 技能广度 | 默认技能 | 5+ 技能 | 15+ 工作流 |
| 流程自动化 | 单步操作 | 多步串联 | ReAct 循环 |
| 系统集成 | 单 Agent | 1-2 节点 | 多 Agent 协作 |

## 价值估算标准

| 等级 | 估值范围 | 特征 |
|------|----------|------|
| 基础价值级 | 100-200元 | 默认技能，低 Token 消耗 |
| 进阶价值级 | 1,000-5,000元 | 10+ 技能，自定义开发 |
| 高阶价值级 | 10,000元+ | 15+ 技能，多 Agent，Proactive |

## 触发关键词

- "评估我的 OpenClaw 能力"
- "龙虾能力估Skill"
- "Claw 度评估"
- "量化我的 AI 自动化价值"

## 目录结构

```
clawvalue/
├── SKILL.md                 # 本文件
├── scripts/
│   ├── collector.py         # 数据采集
│   ├── analyzer.py          # 数据分析
│   └── server.py            # 后端服务
├── data/
│   └── clawvalue.db         # SQLite 数据库
├── web/
│   ├── index.html           # 前端页面
│   ├── style.css
│   └── app.js
└── lib/
    ├── parser.py            # 日志解析
    ├── models.py            # 数据模型
    └── evaluation.py        # 评估逻辑
```

## 依赖安装

```bash
pip install flask sqlite3 requests
```

---

*🦞 龙虾能力估Skill v1.0 - 量化你的 AI 自动化价值*