# ClawValue 主题系统设计规格 (SPEC)

> 创建时间: 2026-03-14
> 状态: 设计完成，待实现

---

## 1. 设计目标

- 提供 **5 套风格迥异的主题**，覆盖不同用户偏好
- 主题切换**即时生效**，无需刷新
- 主题选择**持久化**到 localStorage
- 每套主题具备**完整一致**的视觉体系

---

## 2. 主题风格定义

### 主题 1: 深海龙虾 (Deep Sea Lobster) - 默认
- **风格**: 深色科技风
- **关键词**: 赛博朋克、深邃、科技感
- **配色**:
  - 背景: `#0f0f23` → `#1a1a3e` 渐变
  - 主色: `#ff6b6b` (龙虾红)
  - 辅色: `#4facfe` (科技蓝)
  - 强调: `#feca57` (金黄)
  - 文字: `#e0e0e0` / `#888888`
- **特点**: 渐变背景、玻璃态卡片、霓虹边缘

### 主题 2: 清新田园 (Fresh Garden)
- **风格**: 明亮清新风
- **关键词**: 自然、舒适、易读
- **配色**:
  - 背景: `#f8fdf8` (浅绿白)
  - 主色: `#43e97b` (草绿)
  - 辅色: `#38f9d7` (薄荷)
  - 强调: `#f093fb` (粉紫)
  - 文字: `#2d3436` / `#636e72`
- **特点**: 大圆角、柔和阴影、自然纹理

### 主题 3: 赛博霓虹 (Cyber Neon)
- **风格**: 未来科技风
- **关键词**: 赛博朋克、霓虹、炫酷
- **配色**:
  - 背景: `#0a0a0a` (纯黑)
  - 主色: `#ff00ff` (品红霓虹)
  - 辅色: `#00ffff` (青色霓虹)
  - 强调: `#ffff00` (黄色霓虹)
  - 文字: `#ffffff` / `#888888`
- **特点**: 发光边框、扫描线效果、霓虹动画

### 主题 4: 复古打字机 (Retro Typewriter)
- **风格**: 复古文艺风
- **关键词**: 怀旧、温暖、经典
- **配色**:
  - 背景: `#f4e4c1` (旧纸张)
  - 主色: `#8b4513` (棕色)
  - 辅色: `#d2691e` (巧克力)
  - 强调: `#b8860b` (暗金)
  - 文字: `#3e2723` / `#5d4037`
- **特点**: 衬线字体、纸张纹理、打字机动画

### 主题 5: 极简水墨 (Minimal Ink)
- **风格**: 东方禅意风
- **关键词**: 简约、留白、意境
- **配色**:
  - 背景: `#fafafa` (宣纸白)
  - 主色: `#2c2c2c` (墨黑)
  - 辅色: `#666666` (灰)
  - 强调: `#c41e3a` (朱红印章)
  - 文字: `#1a1a1a` / `#666666`
- **特点**: 大量留白、细边框、墨迹纹理

---

## 3. CSS 变量体系

```css
:root {
  /* 核心颜色 */
  --bg-primary: #0f0f23;
  --bg-secondary: #1a1a3e;
  --bg-card: rgba(255, 255, 255, 0.05);
  
  --text-primary: #e0e0e0;
  --text-secondary: #888888;
  --text-muted: #555555;
  
  --accent-primary: #ff6b6b;
  --accent-secondary: #4facfe;
  --accent-highlight: #feca57;
  
  /* 功能色 */
  --color-success: #43e97b;
  --color-warning: #feca57;
  --color-error: #ff6b6b;
  --color-info: #4facfe;
  
  /* 边框和阴影 */
  --border-color: rgba(255, 255, 255, 0.1);
  --border-radius: 20px;
  --shadow-card: 0 20px 40px rgba(0, 0, 0, 0.3);
  
  /* 动画 */
  --transition-fast: 0.2s ease;
  --transition-normal: 0.3s ease;
}
```

---

## 4. 主题切换器 UI

### 位置
- 顶部导航栏右侧
- 或设置面板中

### 交互
1. 点击主题图标 → 展开主题选择面板
2. 主题卡片预览（缩略图 + 名称）
3. 点击选择 → 即时切换 + 保存到 localStorage
4. 显示切换成功 Toast

### 主题卡片设计
```
┌─────────────────┐
│   [预览色块]     │
│   主题名称       │
│   🦞 深海龙虾    │
└─────────────────┘
```

---

## 5. 实现方案

### 5.1 HTML 结构
```html
<!-- 主题切换器 -->
<div class="theme-switcher">
  <button class="theme-toggle" onclick="toggleThemePanel()">
    🎨 主题
  </button>
  <div class="theme-panel" id="theme-panel">
    <!-- 主题卡片动态生成 -->
  </div>
</div>
```

### 5.2 JavaScript 逻辑
```javascript
// 主题配置
const themes = {
  'deep-sea': { name: '深海龙虾', icon: '🦞', ... },
  'fresh-garden': { name: '清新田园', icon: '🌿', ... },
  'cyber-neon': { name: '赛博霓虹', icon: '⚡', ... },
  'retro-type': { name: '复古打字机', icon: '📜', ... },
  'minimal-ink': { name: '极简水墨', icon: '🎨', ... }
};

// 切换主题
function setTheme(themeId) {
  document.documentElement.setAttribute('data-theme', themeId);
  localStorage.setItem('clawvalue-theme', themeId);
}

// 初始化主题
function initTheme() {
  const saved = localStorage.getItem('clawvalue-theme') || 'deep-sea';
  setTheme(saved);
}
```

### 5.3 CSS 切换
```css
/* 默认主题 */
:root { ... }

/* 深海龙虾 */
[data-theme="deep-sea"] { ... }

/* 清新田园 */
[data-theme="fresh-garden"] {
  --bg-primary: #f8fdf8;
  --accent-primary: #43e97b;
  ...
}

/* 其他主题... */
```

---

## 6. 主题细节

### 深海龙虾 (当前默认)
- 保留现有样式
- 优化渐变和玻璃态效果
- 添加更多微交互

### 清新田园
- 明亮背景 + 深色文字
- 大圆角 (24px+)
- 柔和阴影 (多层级)
- 自然元素装饰 (叶子、草地纹理)

### 赛博霓虹
- 纯黑背景
- 霓虹发光边框 (box-shadow + glow)
- 扫描线动画 (CSS animation)
- 科技感字体

### 复古打字机
- 旧纸张背景 (SVG 纹理)
- 衬线字体 (Playfair Display)
- 打字机动画 (文字逐字出现)
- 印章装饰元素

### 极简水墨
- 大量留白
- 细边框 (1px)
- 简洁图标
- 禅意动画 (缓慢淡入)

---

## 7. 响应式适配

- **桌面端**: 主题面板以浮动面板形式展示
- **移动端**: 全屏主题选择页面
- **平板**: 侧边抽屉形式

---

## 8. 性能考虑

- CSS 变量切换，无需重载页面
- 主题 CSS 内联，减少网络请求
- 切换动画控制在 300ms 内

---

## 9. 后续扩展

- [ ] 用户自定义主题 (颜色选择器)
- [ ] 主题导入/导出
- [ ] 更多预设主题
- [ ] 跟随系统深色/浅色模式

---

*设计完成，准备实现*