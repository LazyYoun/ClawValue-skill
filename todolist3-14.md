# ClawValue 开发任务清单 - 2026-03-14

## 📋 今日任务

### ✅ 已完成
- [x] 创建 coder agent（独立空间，默认模型 glm-5）
- [x] 创建百炼搜索 skill
- [x] 安装 superdesign 技能
- [x] 修改 constants.py - 新增中文分类和 SkillSource
- [x] 修改 schemas.py - 更新 _guess_category 和 Skill 模型
- [x] 修改 collector.py - 增强 SkillScanner 多 workspace 支持
- [x] 修改 index.html - 添加加载动画和进度条
- [x] 排名进度条动画效果
- [x] Mock 数据选择器（5个等级）
- [x] 数字跳动动画效果

### 🔄 进行中

#### 1. 扫描能力增强
- [x] 读取 openclaw.json 获取 agent 配置
- [x] 扫描所有 agent 的 workspace
- [x] 测试多 workspace 合并逻辑

#### 2. 技能分类优化
- [x] 中文分类名称
- [x] 拓展匹配关键词
- [x] 增加更多分类维度（自动化、安全认证、社交媒体）
- [x] 验证分类效果
- [x] 修复 YAML 多行解析

#### 3. 页面展示改进
- [x] 加载动画（龙虾弹跳 + 文字流光）
- [x] 进度条动画
- [x] 状态文字切换（数据收集中→快好了→计算中→完成）
- [x] 排名进度条从0动画增长
- [x] Mock 数据选择器
- [ ] 优化页面整体布局（可继续优化）

#### 4. 测试验证
- [x] 接口功能验证
- [x] mock不同等级数据验证页面效果
- [x] 真实数据端到端测试

### ✅ 本轮完成总结
- 技能扫描：12个技能（10 workspace + 2 extra）
- 分类效果：7个类别正确分类
- YAML 解析：修复多行字符串支持
- Mock 数据：5个等级完整测试通过
- 动画效果：加载动画、进度条、数字跳动

---

## 🤖 定时任务要求

**项目路径：** `/Users/lazyyoun/Documents/clawValue`

**编码要求：**
1. 善用百炼搜索工具（web_search）
2. 善用页面设计工具（superdesign 技能）
3. 善用浏览器调试能力（可直接操作 Chrome）
4. **必须使用 qwen 进行编码修改**
5. 及时更新本 todolist 文件
6. 及时提交 git 本地代码库

**qwen 使用方式：**
```bash
/opt/homebrew/bin/qwen -p "你的编码任务"
```

---

## 📝 技术要点

### OpenClaw Skill 来源
1. **Workspace Skills** - `~/.openclaw/workspace/skills/` 目录（自定义）
2. **Built-in Skills** - OpenClaw 内置（bundled）
3. **Extra Skills** - 插件扩展（如 qqbot）

### Agent 配置结构
```json
{
  "agents": {
    "list": [
      { "id": "main", "workspace": "..." },
      { "id": "coder", "workspace": "..." }
    ]
  }
}
```

---

## 🎯 目标

打造一个吸引人的、有趣的 Claw 值评估工具！