# 碳达峰预测系统前端美化设计

**日期**: 2026-05-03
**目标**: 完整重构为双主题设计系统，实现浅色专业风（默认）+ 深色科技风切换，增强图表数据故事感

## 1. 主题系统架构

### 1.1 文件结构

```
frontend/src/assets/styles/
├── design-tokens.css    # 共享设计变量（间距、圆角、字体等）
├── theme-light.css      # 浅色主题变量和样式
├── theme-dark.css       # 深色主题变量和样式
├── components-base.css  # 组件基础样式覆盖（Element UI）
├── animations.css       # 动画效果（保留现有，优化）
└── glassmorphism.css    # 玻璃态效果（仅深色主题）

frontend/src/store/
└── themeStore.js        # 主题状态管理（Vue reactive）

frontend/src/components/
├── ThemeToggle.vue      # 主题切换按钮组件
└── MetricCard.vue       # 图表关键指标卡片组件
```

### 1.2 主题切换机制

- `App.vue` 根元素添加 `data-theme="light"` 或 `data-theme="dark"`
- `themeStore.js` 管理当前主题状态（默认浅色）
- `localStorage` 持久化用户选择（key: `theme-preference`）
- CSS 变量通过 `[data-theme="light"]` / `[data-theme="dark"]` 选择器切换

### 1.3 CSS 变量命名规范

```css
/* 共享设计变量 - design-tokens.css */
:root {
  --cp-radius-sm: 8px;
  --cp-radius-md: 12px;
  --cp-radius-lg: 16px;
  --cp-radius-xl: 20px;
  --cp-spacing-xs: 4px;
  --cp-spacing-sm: 8px;
  --cp-spacing-md: 16px;
  --cp-spacing-lg: 24px;
  --cp-spacing-xl: 32px;
  --cp-font-xs: 12px;
  --cp-font-sm: 14px;
  --cp-font-md: 16px;
  --cp-font-lg: 18px;
  --cp-font-xl: 24px;
  --cp-line-height: 1.5;
  --cp-transition-fast: 150ms ease-out;
  --cp-transition-normal: 200ms ease-out;
  --cp-transition-slow: 300ms ease-out;
}

/* 浅色主题 - theme-light.css */
[data-theme="light"] {
  --cp-bg-primary: #ffffff;
  --cp-bg-secondary: #f8fafc;
  --cp-bg-tertiary: #f1f5f9;
  --cp-bg-card: #ffffff;
  --cp-bg-header: #ffffff;
  --cp-bg-footer: #f1f5f9;
  --cp-bg-input: #ffffff;
  --cp-bg-table-header: rgba(20, 184, 166, 0.06);
  --cp-bg-table-row-stripe: rgba(15, 118, 110, 0.03);
  --cp-bg-hover: rgba(15, 118, 110, 0.08);

  --cp-text-primary: #134e4a;
  --cp-text-secondary: #5f7f74;
  --cp-text-muted: #6b7280;
  --cp-text-inverse: #ffffff;

  --cp-accent-primary: #0f766e;
  --cp-accent-secondary: #14b8a6;
  --cp-accent-gradient: linear-gradient(135deg, #0f766e, #14b8a6);

  --cp-border-primary: rgba(15, 118, 110, 0.12);
  --cp-border-secondary: rgba(15, 118, 110, 0.24);
  --cp-border-focus: rgba(15, 118, 110, 0.4);

  --cp-shadow-sm: 0 2px 8px rgba(15, 118, 110, 0.06);
  --cp-shadow-md: 0 4px 12px rgba(15, 118, 110, 0.08);
  --cp-shadow-lg: 0 8px 24px rgba(15, 118, 110, 0.12);
  --cp-shadow-glow: none;

  --cp-chart-historical: #64748b;
  --cp-chart-gridline: rgba(15, 118, 110, 0.1);
}

/* 深色主题 - theme-dark.css */
[data-theme="dark"] {
  --cp-bg-primary: #0a0f1a;
  --cp-bg-secondary: rgba(15, 23, 42, 0.85);
  --cp-bg-tertiary: rgba(15, 23, 42, 0.6);
  --cp-bg-card: rgba(15, 23, 42, 0.85);
  --cp-bg-header: linear-gradient(135deg, rgba(15, 118, 110, 0.4), rgba(139, 92, 246, 0.3));
  --cp-bg-footer: linear-gradient(135deg, rgba(15, 118, 110, 0.35), rgba(139, 92, 246, 0.25));
  --cp-bg-input: rgba(15, 23, 42, 0.6);
  --cp-bg-table-header: rgba(15, 118, 110, 0.25);
  --cp-bg-table-row-stripe: rgba(255, 255, 255, 0.05);
  --cp-bg-hover: rgba(255, 255, 255, 0.1);

  --cp-text-primary: #e2e8f0;
  --cp-text-secondary: #94a3b8;
  --cp-text-muted: #64748b;
  --cp-text-inverse: #0a0f1a;

  --cp-accent-primary: #14b8a6;
  --cp-accent-secondary: #0f766e;
  --cp-accent-gradient: linear-gradient(135deg, #0f766e, #14b8a6);

  --cp-border-primary: rgba(255, 255, 255, 0.15);
  --cp-border-secondary: rgba(255, 255, 255, 0.25);
  --cp-border-focus: rgba(14, 184, 166, 0.5);

  --cp-shadow-sm: 0 4px 12px rgba(15, 118, 110, 0.15);
  --cp-shadow-md: 0 8px 18px rgba(15, 118, 110, 0.2);
  --cp-shadow-lg: 0 20px 45px rgba(15, 118, 110, 0.25);
  --cp-shadow-glow: 0 0 30px rgba(15, 118, 110, 0.3);

  --cp-chart-historical: #94a3b8;
  --cp-chart-gridline: rgba(255, 255, 255, 0.1);
}
```

## 2. 组件样式规范

### 2.1 卡片组件 (el-card)

**浅色主题**:
- 背景: `var(--cp-bg-card)`
- 阴影: `var(--cp-shadow-md)`
- 圆角: `var(--cp-radius-lg)` (16px)
- 边框: `1px solid var(--cp-border-primary)`
- Header 背景: `linear-gradient(135deg, rgba(15,118,110,0.08), rgba(20,184,166,0.04))`

**深色主题**:
- 背景: `var(--cp-bg-card)` + `backdrop-filter: blur(12px)`
- 阴影: `var(--cp-shadow-lg)` + `var(--cp-shadow-glow)`
- 圆角: `var(--cp-radius-xl)` (20px)
- 边框: `1px solid var(--cp-border-primary)`
- Header 背景: 现有玻璃渐变

### 2.2 表格组件 (el-table)

**浅色主题**:
- 表头背景: `var(--cp-bg-table-header)`
- 表头文字: `var(--cp-text-primary)` + font-weight 700
- 条纹行: `var(--cp-bg-table-row-stripe)`
- 边框: `var(--cp-border-primary)`
- Hover 行: `var(--cp-bg-hover)` + 微妙高亮

**深色主题**:
- 表头背景: `var(--cp-bg-table-header)`
- 条纹行: `var(--cp-bg-table-row-stripe)`
- 边框: `var(--cp-border-primary)`
- Hover 行: 霓虹发光效果

### 2.3 按钮组件

**主按钮 (primary/success)**:
- 背景: `var(--cp-accent-gradient)`
- 圆角: `var(--cp-radius-md)` (12px)
- 最小高度: 44px（满足触摸目标）
- 浅色边框: `rgba(255,255,255,0.25)`
- 深色发光: `var(--cp-shadow-glow)`
- Hover: 增强阴影/发光
- Pressed: `scale(0.97)` + `opacity: 0.9`, 150ms ease-out

**次按钮 (default)**:
- 浅色: 白底 `var(--cp-bg-card)` + 青边框 `var(--cp-border-secondary)`
- 深色: 玻璃态边框

**危险按钮 (danger)**:
- 背景: `#ef4444`（两主题统一）
- 圆角: `var(--cp-radius-md)`

### 2.4 表单组件

**输入框 (el-input)**:
- 圆角: `var(--cp-radius-md)` (12px)
- 边框: `var(--cp-border-primary)`
- 背景: `var(--cp-bg-input)`
- Hover 边框: `var(--cp-border-secondary)`
- Focus ring/glow: `var(--cp-shadow-glow)` (深色) / `box-shadow: 0 0 0 3px rgba(15,118,110,0.2)` (浅色)

**滑块 (el-slider)**:
- 轨道: 渐变 `var(--cp-accent-gradient)`
- 按钮: 18px 圆形，边框 `var(--cp-accent-primary)`
- 圆角: `999px` (完全圆角)

## 3. 图表数据故事感增强

### 3.1 关键指标卡片组件 (MetricCard.vue)

**布局**:
```
┌─────────────────────────────────────────────────────────────────┐
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │  达峰年份   │ │  排放峰值   │ │  减排幅度   │ │  情景数量   │   │
│  │   2030年    │ │   12,450   │ │    -35%    │ │     3个    │   │
│  │  ↓ 下降趋势 │ │  万吨CO₂   │ │  预测下降  │ │   已创建   │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**组件结构**:
```vue
<template>
  <div class="metric-cards">
    <div class="metric-card" v-for="metric in metrics">
      <span class="metric-label">{{ metric.label }}</span>
      <div class="metric-value-row">
        <span class="metric-value">{{ metric.value }}</span>
        <span class="metric-trend" :class="metric.trendClass">
          <svg v-if="metric.trend === 'down'">↓</svg>
          <svg v-if="metric.trend === 'up'">↑</svg>
        </span>
      </div>
      <span class="metric-unit">{{ metric.unit }}</span>
    </div>
  </div>
</template>
```

**样式**:
- 浅色: 白底 `var(--cp-bg-card)`, 青边框, 圆角 12px
- 深色: 玻璃态背景, 霓虹边框
- 数值: 24px font-weight 800, `var(--cp-accent-primary)`
- 趋势箭头: 下降绿色 `#10b981`, 上升橙色 `#f59e0b`

### 3.2 峰值标注线 (ECharts markLine)

```javascript
// 在碳排放图表中添加
markLine: {
  silent: true,
  symbol: 'none',
  lineStyle: {
    type: 'dashed',
    color: var(--cp-accent-primary), // 主题色
    width: 2
  },
  label: {
    formatter: '峰值点',
    position: 'end'
  },
  data: peakYears.map(year => ({
    xAxis: year
  }))
}
```

### 3.3 图表配色统一

```javascript
// 重新定义配色
const SCENARIO_COLORS_LIGHT = ['#0f766e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#10b981'];
const SCENARIO_COLORS_DARK = ['#14b8a6', '#60a5fa', '#fbbf24', '#f87171', '#a78bfa', '#34d399'];

// Tooltip 样式
tooltip: {
  backgroundColor: isDark ? 'rgba(15, 23, 42, 0.9)' : '#ffffff',
  borderColor: isDark ? 'rgba(255, 255, 255, 0.2)' : 'rgba(15, 118, 110, 0.2)',
  borderRadius: 12,
  shadowBlur: isDark ? 20 : 8,
  shadowColor: isDark ? 'rgba(15, 118, 110, 0.3)' : 'rgba(15, 118, 110, 0.1)'
}
```

## 4. 导航与布局

### 4.1 Header

**浅色主题**:
- 背景: `var(--cp-bg-header)` (#ffffff)
- 底边框: `linear-gradient(90deg, #0f766e, #14b8a6)` 渐变线 2px
- 阴影: `var(--cp-shadow-sm)`
- Logo SVG: 青绿色 `var(--cp-accent-primary)`

**深色主题**:
- 背景: `var(--cp-bg-header)` (玻璃渐变)
- 保持现有霓虹发光效果

**主题切换按钮位置**: Header 右侧，`.header-info` 区域

### 4.2 Tabs (el-tabs)

**浅色主题**:
- 类型: `type="card"` 保持
- 卡片样式: 白底, 激活态青绿底色 `rgba(15,118,110,0.1)` + 文字加粗
- 禁用态: `opacity: 0.5` + cursor: not-allowed

**深色主题**:
- 保持现有玻璃态样式
- 激活态发光效果

### 4.3 Footer

**浅色主题**:
- 背景: `var(--cp-bg-footer)` (#f1f5f9)
- 文字: `var(--cp-text-secondary)`
- 简洁无边框

**深色主题**:
- 保持现有玻璃渐变

### 4.4 响应式布局

保持现有断点:
- `max-width: 992px`: 平板适配
- 网格列数调整: `el-col` xs/sm/md/lg
- 图表高度: 浅色 400px, 深色 450px; 移动端 320px

## 5. 动画效果

### 5.1 微交互 (150-300ms)

```css
/* 按钮 pressed */
.btn-pressed {
  transform: scale(0.97);
  opacity: 0.9;
  transition: transform 150ms ease-out, opacity 150ms ease-out;
}

/* 卡片 hover */
.card-hover {
  transform: translateY(-2px);
  box-shadow: var(--cp-shadow-lg);
  transition: transform 200ms ease-out, box-shadow 200ms ease-out;
}

/* 输入框 focus */
.input-focus {
  border-color: var(--cp-border-focus);
  box-shadow: var(--cp-shadow-glow) or focus-ring;
  transition: border-color 200ms ease-out, box-shadow 200ms ease-out;
}
```

### 5.2 页面过渡 (300-400ms)

```css
/* Tab 切换 */
.tab-transition {
  animation: fade-slide 300ms ease-out;
}

/* 主题切换 */
.theme-transition {
  transition: background-color 400ms ease-out,
              color 300ms ease-out,
              border-color 300ms ease-out,
              box-shadow 400ms ease-out;
}
```

### 5.3 背景动画处理

**浅色主题**:
- 禁用 `ParticleBackground` 组件
- 禁用 `.ambient-bg` (.orb, .grid-pattern)
- 纯色背景 + 微妙渐变

**深色主题**:
- 保留所有现有背景动画
- 粒子、orb 浮动、网格图案

**无障碍**:
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 6. 主题切换器组件

### 6.1 ThemeToggle.vue

```vue
<template>
  <button
    class="theme-toggle"
    @click="toggleTheme"
    :aria-label="isDark ? '切换到浅色模式' : '切换到深色模式'"
  >
    <transition name="icon-rotate" mode="out-in">
      <svg v-if="isDark" key="sun" class="icon" viewBox="0 0 24 24">
        <!-- sun icon -->
        <circle cx="12" cy="12" r="5" fill="currentColor"/>
        <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="currentColor" stroke-width="2"/>
      </svg>
      <svg v-else key="moon" class="icon" viewBox="0 0 24 24">
        <!-- moon icon -->
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" fill="currentColor"/>
      </svg>
    </transition>
  </button>
</template>

<script>
import { themeStore } from '@/store/themeStore'

export default {
  computed: {
    isDark() { return themeStore.current === 'dark' }
  },
  methods: {
    toggleTheme() {
      themeStore.toggle()
    }
  }
}
</script>

<style scoped>
.theme-toggle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 2px solid var(--cp-border-secondary);
  background: var(--cp-bg-card);
  color: var(--cp-accent-primary);
  cursor: pointer;
  transition: all var(--cp-transition-normal);
}

.theme-toggle:hover {
  border-color: var(--cp-accent-primary);
  box-shadow: var(--cp-shadow-glow);
}

.icon {
  width: 20px;
  height: 20px;
  transition: transform 300ms ease-out;
}

.icon-rotate-enter-active,
.icon-rotate-leave-active {
  transition: transform 300ms ease-out;
}

.icon-rotate-enter {
  transform: rotate(-180deg);
}

.icon-rotate-leave-to {
  transform: rotate(180deg);
}
</style>
```

### 6.2 themeStore.js

```javascript
import { reactive, watch } from 'vue'

const STORE_KEY = 'theme-preference'

export const themeStore = reactive({
  current: 'light',

  init() {
    const stored = localStorage.getItem(STORE_KEY)
    if (stored) {
      this.current = stored
    }
    this.apply()
  },

  toggle() {
    this.current = this.current === 'light' ? 'dark' : 'light'
    localStorage.setItem(STORE_KEY, this.current)
    this.apply()
  },

  apply() {
    document.documentElement.setAttribute('data-theme', this.current)
  }
})

// 初始化时自动应用
themeStore.init()
```

## 7. 实施优先级

| 优先级 | 任务 | 预估工作量 |
|--------|------|------------|
| P0 | 创建 design-tokens.css + theme-light.css + theme-dark.css | 中 |
| P0 | 修改 App.vue 引入新样式系统 | 小 |
| P1 | 创建 ThemeToggle.vue + themeStore.js | 小 |
| P1 | 修改 Header/Footer 适配双主题 | 小 |
| P1 | 修改 el-card/el-table/el-button 样式覆盖 | 中 |
| P2 | 创建 MetricCard.vue 组件 | 中 |
| P2 | 修改 PredictionResults.vue 添加指标卡片 | 中 |
| P2 | 修改 ECharts 配置适配双主题配色 | 中 |
| P3 | 优化动画效果 | 小 |
| P3 | 测试响应式布局 + 无障碍 | 小 |

## 8. 测试验收标准

- [ ] 浅色主题：所有组件显示正常，配色协调
- [ ] 深色主题：所有组件显示正常，玻璃态效果完整
- [ ] 主题切换：平滑过渡，localStorage 持久化生效
- [ ] 图表指标卡：正确显示达峰年份、峰值、趋势箭头
- [ ] 峰值标注线：在正确位置显示
- [ ] 响应式：移动端/平板/桌面端布局正常
- [ ] 无障碍：`prefers-reduced-motion` 禁用动画，焦点状态可见
- [ ] 触摸目标：所有按钮 ≥44px