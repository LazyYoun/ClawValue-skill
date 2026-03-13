# OpenClaw 官方文档参考

> 本文档整理 OpenClaw 官方文档中与 ClawValue 数据采集相关的关键信息。
> 官方文档地址: https://docs.openclaw.ai/zh-CN/

---

## 📁 日志系统

### 日志存放位置

默认日志路径：
```
/tmp/openclaw/openclaw-YYYY-MM-DD.log
```

可在 `~/.openclaw/openclaw.json` 中覆盖：
```json
{
  "logging": {
    "file": "/path/to/openclaw.log"
  }
}
```

### 日志格式 (JSONL)

每行一个 JSON 对象：

```json
{
  "0": "[tools] read failed: ENOENT: no such file or directory",
  "_meta": {
    "runtime": "node",
    "runtimeVersion": "23.5.0",
    "hostname": "unknown",
    "name": "openclaw",
    "date": "2026-03-12T17:00:04.080Z",
    "logLevelId": 5,
    "logLevelName": "ERROR",
    "path": {
      "fullFilePath": "file:///opt/homebrew/lib/node_modules/openclaw/dist/logger-BDhFOulu.js:20:34",
      "fileName": "logger-BDhFOulu.js",
      "fileNameWithLine": "logger-BDhFOulu.js:20",
      "fileColumn": "34",
      "fileLine": "20",
      "filePath": "opt/homebrew/lib/node_modules/openclaw/dist/logger-BDhFOulu.js"
    }
  },
  "time": "2026-03-13T01:00:04.080+08:00"
}
```

### 日志字段说明

| 字段 | 说明 |
|------|------|
| `0` | 日志消息内容（OpenClaw 使用 "0" 作为消息键） |
| `_meta` | 元数据对象 |
| `_meta.logLevelName` | 日志级别: DEBUG/INFO/WARN/ERROR/FATAL |
| `_meta.logLevelId` | 日志级别 ID (数字) |
| `_meta.runtime` | 运行时环境 (node) |
| `_meta.runtimeVersion` | 运行时版本 |
| `_meta.date` | UTC 时间戳 |
| `time` | 本地时间戳 |

### CLI 日志跟踪

```bash
# 实时跟踪日志
openclaw logs --follow

# JSON 格式输出
openclaw logs --follow --json

# 纯文本输出
openclaw logs --follow --plain
```

### 日志配置

```json
{
  "logging": {
    "level": "info",
    "file": "/tmp/openclaw/openclaw-YYYY-MM-DD.log",
    "consoleLevel": "info",
    "consoleStyle": "pretty",
    "redactSensitive": "tools",
    "redactPatterns": ["sk-.*"]
  }
}
```

---

## 🪙 Token 使用与成本

### Token 基础

- OpenClaw 跟踪 **token** 而非字符
- 大多数 OpenAI 风格模型：英文文本约 **4 字符 = 1 token**

### 系统提示词构成

每次运行时组装：
- 工具列表 + 简短描述
- Skills 列表（仅元数据）
- 自我更新指令
- 工作区引导文件（AGENTS.md、SOUL.md、TOOLS.md 等）
- 时间（UTC + 用户时区）
- 回复标签 + 心跳行为
- 运行时元数据

### 上下文窗口包含

- 系统提示词
- 对话历史（用户 + 助手消息）
- 工具调用和工具结果
- 附件/转录（图片、音频、文件）
- 压缩摘要和修剪产物

### 查看 Token 使用量

```bash
# 聊天中命令
/status          # 状态卡片（模型、上下文、token、成本）
/usage tokens    # 每响应使用量页脚
/usage cost      # 本地成本摘要

# CLI
openclaw status --usage
```

### 成本估算配置

```json
{
  "models": {
    "providers": {
      "<provider>": {
        "models": [{
          "id": "model-id",
          "cost": {
            "input": 0.00,      // 每 1M token 美元
            "output": 0.00,
            "cacheRead": 0.00,
            "cacheWrite": 0.00
          }
        }]
      }
    }
  }
}
```

### 缓存 TTL 与心跳

- 心跳可保持缓存"热"状态
- 设置心跳间隔略小于缓存 TTL（如 55m vs 1h）
- 可降低缓存写入成本

```yaml
agents:
  defaults:
    heartbeat:
      every: "55m"
```

---

## 📊 诊断事件 (OpenTelemetry)

### 诊断事件目录

**模型使用：**
- `model.usage`: Token、成本、持续时间、上下文、提供商/模型/渠道、会话 ID

**消息流：**
- `webhook.received`: 每渠道的 webhook 入口
- `webhook.processed`: Webhook 已处理 + 持续时间
- `message.queued`: 消息入队等待处理
- `message.processed`: 结果 + 持续时间

**队列 + 会话：**
- `session.state`: 会话状态转换
- `session.stuck`: 会话卡住警告

### 启用诊断

```json
{
  "diagnostics": {
    "enabled": true
  }
}
```

### 导出到 OpenTelemetry

```json
{
  "plugins": {
    "allow": ["diagnostics-otel"]
  },
  "diagnostics": {
    "enabled": true,
    "otel": {
      "enabled": true,
      "endpoint": "http://otel-collector:4318",
      "protocol": "http/protobuf",
      "serviceName": "openclaw-gateway",
      "traces": true,
      "metrics": true,
      "logs": true
    }
  }
}
```

### 导出的指标

| 指标名称 | 类型 | 说明 |
|----------|------|------|
| `openclaw.tokens` | 计数器 | Token 使用量 |
| `openclaw.cost.usd` | 计数器 | 成本（美元） |
| `openclaw.run.duration_ms` | 直方图 | 运行持续时间 |
| `openclaw.context.tokens` | 直方图 | 上下文大小 |

---

## 🔧 配置文件

### 配置路径

```
~/.openclaw/openclaw.json
```

### 关键配置结构

```json
{
  "meta": {
    "lastTouchedVersion": "2026.3.8",
    "lastTouchedAt": "2026-03-13T13:19:16.508Z"
  },
  "auth": {
    "profiles": {
      "dashscope:default": {
        "provider": "dashscope",
        "mode": "api_key"
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "dashscope/qwen-plus"
      },
      "heartbeat": {
        "every": "55m"
      }
    }
  },
  "models": {
    "providers": {
      "dashscope": {
        "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api": "openai-completions",
        "models": [...]
      }
    }
  },
  "channels": {
    "whatsapp": {...},
    "telegram": {...}
  }
}
```

---

## 📝 参考链接

- 官方文档: https://docs.openclaw.ai/zh-CN/
- 日志文档: https://docs.openclaw.ai/zh-CN/logging
- Token 使用: https://docs.openclaw.ai/zh-CN/reference/token-use
- 系统提示词: https://docs.openclaw.ai/zh-CN/concepts/system-prompt
- 上下文: https://docs.openclaw.ai/zh-CN/concepts/context
- Gateway 配置: https://docs.openclaw.ai/zh-CN/gateway/configuration
- 文档索引: https://docs.openclaw.ai/llms.txt