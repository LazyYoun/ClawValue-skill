# 🦞 ClawValue - OpenClaw Claw度评估系统

量化你在 OpenClaw 上的 AI 自动化能力，生成趣味化的"龙虾能力估Skill"评估报告。

## ✨ 功能特点

- 📊 **使用深度评估**：三级技术指标体系（浅度/中度/深度）
- 💰 **价值估算**：基于真实数据的价值量化
- 🦞 **趣味表达**："龙虾能力估Skill" 等级与调侃话术
- 🏆 **成就系统**：解锁特殊成就，展示你的实力
- 📈 **多维图表**：使用频率、技能分布可视化
- 💾 **本地存储**：SQLite 持久化历史数据

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python3 scripts/server.py --port 5002
```

访问：http://localhost:5002

### 命令行数据采集

```bash
python3 scripts/collector.py --output json
```

## 📡 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/` | GET | 仪表盘主数据接口 |
| `/api/stats` | GET | 获取统计数据 |
| `/api/skills` | GET | 获取技能列表 |
| `/api/sessions` | GET | 获取会话历史 |
| `/api/evaluation` | GET | 获取评估结果 |
| `/api/refresh` | POST | 刷新数据 |
| `/api/health` | GET | 健康检查 |

## 🦐 使用深度等级

| 等级 | 名称 | 描述 |
|------|------|------|
| Lv.1 | 🐣 入门小白 | 刚接触 OpenClaw，还在探索阶段 |
| Lv.2 | 🎮 初级玩家 | 开始使用基本功能 |
| Lv.3 | 💻 中级开发者 | 熟练使用各种技能 |
| Lv.4 | 🚀 高级工程师 | 自定义技能，深度集成 |
| Lv.5 | 🦞 龙虾大师 | 达到专家级别，效率爆表 |

## 🏆 成就系统

| 成就 | 条件 |
|------|------|
| 🏅 技能大师 | 自定义技能超过5个 |
| 🤖 自动化达人 | 开启心跳检测 |
| 🌐 多渠道运营 | 连接2个以上平台 |
| ⚡ 超级用户 | 日均 Token 消耗超过 50000 |

## 📁 目录结构

```
clawvalue/
├── SKILL.md                 # 技能定义
├── requirements.txt         # Python 依赖
├── scripts/
│   ├── collector.py         # 数据采集脚本
│   └── server.py            # Flask 后端服务
├── data/
│   └── clawvalue.db         # SQLite 数据库
├── web/
│   └── index.html           # 前端页面
└── lib/
    ├── parser.py            # 日志解析模块
    ├── models.py            # 数据模型
    └── evaluation.py        # 评估引擎
```

## 🔧 技术栈

- **后端**: Python 3 + Flask
- **数据库**: SQLite
- **前端**: HTML/CSS/JavaScript + Chart.js
- **数据采集**: 解析 OpenClaw 日志和配置

## 📄 License

MIT

---

*🦞 龙虾能力估Skill v1.0 - 量化你的 AI 自动化价值*