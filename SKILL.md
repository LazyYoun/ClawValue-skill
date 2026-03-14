---
name: clawvalue
description: "OpenClaw Claw度评估系统 - 量化你的 AI 自动化能力，生成龙虾能力估值趣味评估报告。支持15套主题、5级Mock数据、游戏化展示。"
version: 2.0.0
metadata:
  clawdbot:
    emoji: "🦞"
    requires:
      py:
        - flask
        - requests
    config:
      env:
        CLAWVALUE_PORT:
          description: 服务端口
          default: 5002
---

# 🦞 ClawValue - OpenClaw 能力估值系统

量化你在 OpenClaw 上的 AI 自动化能力，生成趣味化的"龙虾能力估值"评估报告。

## ✨ 核心特性

### 🎮 游戏化评估
- **等级系统**：Lv.1 入门小白 → Lv.5 龙虾大师
- **全球排名**：基于使用深度的百分位排名
- **成就徽章**：技能大师、自动化达人、Token燃烧者等

### 🎨 视觉设计
- **15套精美主题**：深色系、浅色系、特色系
- **现代UI风格**：玻璃态卡片、oklch颜色、流畅动画
- **响应式布局**：适配桌面和移动端

### 📊 数据可视化
- **技能分类**：9大类别（社交媒体、工具效率、自动化等）
- **能力评分**：技能、自动化、集成三维度
- **日志统计**：INFO/WARN/ERROR/工具调用

### 🧪 Mock数据
- **5个等级预设**：快速体验不同等级效果
- **真实数据切换**：一键切换真实/Mock数据

## 🚀 快速开始

### 启动服务

```bash
cd /Users/lazyyoun/Documents/clawValue
python3 scripts/server.py
```

访问：http://localhost:5002

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/` | GET | 获取完整评估数据 |
| `/api/stats` | GET | 获取统计数据 |
| `/api/generate-image` | POST | 生成龙虾海报 |

## 📈 评估维度

### 使用深度等级

| 等级 | 名称 | 特征 |
|------|------|------|
| Lv.1 | 入门小白 | 刚接触 OpenClaw，基础交互 |
| Lv.2 | 初级玩家 | 开始使用自定义技能 |
| Lv.3 | 中级开发者 | 多技能协作，自动化场景 |
| Lv.4 | 高级工程师 | 多 Agent，复杂工作流 |
| Lv.5 | 龙虾大师 | 全方位自动化，Proactive 模式 |

### 技能分类

- **社交媒体**：微信、小红书、微博等
- **工具效率**：OSS、MCP、CLI工具
- **自动化**：定时任务、心跳监控
- **搜索研究**：百炼搜索、资讯摘要
- **开发运维**：GitHub、CI/CD
- **媒体内容**：前端设计、博客管理
- **沟通协作**：消息通知、机器人
- **数据存储**：数据库、缓存
- **安全认证**：认证、加密

## 🎯 触发关键词

- "评估我的 OpenClaw 能力"
- "龙虾能力估值"
- "Claw 度评估"
- "我的龙虾值是多少"

## 📁 项目结构

```
clawvalue/
├── SKILL.md              # 技能说明
├── lib/
│   ├── constants.py      # 常量定义（分类、来源）
│   ├── schemas.py        # 数据模型
│   ├── collector.py      # 数据采集（技能扫描、日志解析）
│   └── evaluation.py     # 评估逻辑
├── scripts/
│   └── server.py         # Flask 服务
└── web/
    └── index.html        # 前端页面（单文件）
```

## 🔧 技术栈

- **后端**：Python Flask
- **前端**：原生 HTML/CSS/JS
- **样式**：oklch 颜色、CSS变量、动画
- **数据**：JSONL 日志解析、技能扫描

---

*🦞 ClawValue v2.0 - 让 AI 能力量化变得有趣！*