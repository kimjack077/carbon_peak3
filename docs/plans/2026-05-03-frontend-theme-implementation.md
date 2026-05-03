# Frontend Theme System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现双主题设计系统（浅色专业风默认 + 深色科技风）并增强图表数据故事感

**Architecture:** CSS 变量驱动的主题切换系统，通过 `data-theme` 属性控制，Vue reactive store 管理状态，localStorage 持久化用户偏好

**Tech Stack:** Vue 2 + Element UI + ECharts + CSS Variables

---

## Task 1: 创建设计变量基础文件

**Files:**
- Create: `frontend/src/assets/styles/design-tokens.css`

**Step 1: 创建共享设计变量文件**

```css
/* frontend/src/assets/styles/design-tokens.css */
/* 共享设计变量 - 间距、圆角、字体、动画时长等 */

:root {
  /* 圆角系统 */
  --cp-radius-sm: 8px;
  --cp-radius-md: 12px;
  --cp-radius-lg: 16px;
  --cp-radius-xl: 20px;

  /* 间距系统 (8dp rhythm) */
  --cp-spacing-xs: 4px;
  --cp-spacing-sm: 8px;
  --cp-spacing-md: 16px;
  --cp-spacing-lg: 24px;
  --cp-spacing-xl: 32px;

  /* 字体系统 */
  --cp-font-xs: 12px;
  --cp-font-sm: 14px;
  --cp-font-md: 16px;
  --cp-font-lg: 18px;
  --cp-font-xl: 24px;
  --cp-line-height: 1.5;

  /* 动画时长 */
  --cp-transition-fast: 150ms ease-out;
  --cp-transition-normal: 200ms ease-out;
  --cp-transition-slow: 300ms ease-out;

  /* 触摸目标 */
  --cp-touch-target: 44px;
}
```

**Step 2: Commit**

```bash
git add frontend/src/assets/styles/design-tokens.css
git commit -m "feat: add design tokens CSS file"
```

---

## Task 2: 创建浅色主题样式文件

**Files:**
- Create: `frontend/src/assets/styles/theme-light.css`

**Step 1: 创建浅色主题变量**

```css
/* frontend/src/assets/styles/theme-light.css */
/* 浅色专业风主题 - 清新简约 */

[data-theme="light"] {
  /* 背景色 */
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
  --cp-bg-active: rgba(15, 118, 110, 0.12);

  /* 文字色 */
  --cp-text-primary: #134e4a;
  --cp-text-secondary: #5f7f74;
  --cp-text-muted: #6b7280;
  --cp-text-inverse: #ffffff;
  --cp-text-link: #0f766e;

  /* 强调色 */
  --cp-accent-primary: #0f766e;
  --cp-accent-secondary: #14b8a6;
  --cp-accent-gradient: linear-gradient(135deg, #0f766e, #14b8a6);
  --cp-accent-light: rgba(15, 118, 110, 0.1);
  --cp-accent-danger: #ef4444;
  --cp-accent-success: #10b981;
  --cp-accent-warning: #f59e0b;

  /* 边框色 */
  --cp-border-primary: rgba(15, 118, 110, 0.12);
  --cp-border-secondary: rgba(15, 118, 110, 0.24);
  --cp-border-focus: rgba(15, 118, 110, 0.4);
  --cp-border-light: rgba(15, 118, 110, 0.06);

  /* 阴影 */
  --cp-shadow-sm: 0 2px 8px rgba(15, 118, 110, 0.06);
  --cp-shadow-md: 0 4px 12px rgba(15, 118, 110, 0.08);
  --cp-shadow-lg: 0 8px 24px rgba(15, 118, 110, 0.12);
  --cp-shadow-glow: 0 0 0 3px rgba(15, 118, 110, 0.15);

  /* 图表配色 */
  --cp-chart-historical: #64748b;
  --cp-chart-gridline: rgba(15, 118, 110, 0.1);
  --cp-chart-scenario-1: #0f766e;
  --cp-chart-scenario-2: #3b82f6;
  --cp-chart-scenario-3: #f59e0b;
  --cp-chart-scenario-4: #ef4444;
  --cp-chart-scenario-5: #8b5cf6;
  --cp-chart-scenario-6: #10b981;

  /* Header 渐变边框 */
  --cp-header-border: linear-gradient(90deg, #0f766e, #14b8a6);
}

/* 浅色主题全局样式 */
[data-theme="light"] body,
[data-theme="light"] #app {
  background: var(--cp-bg-secondary);
  color: var(--cp-text-primary);
}

/* 浅色主题禁用背景动画 */
[data-theme="light"] .ambient-bg,
[data-theme="light"] .particle-background {
  display: none !important;
}
```

**Step 2: Commit**

```bash
git add frontend/src/assets/styles/theme-light.css
git commit -m "feat: add light theme CSS variables"
```

---

## Task 3: 创建深色主题样式文件

**Files:**
- Create: `frontend/src/assets/styles/theme-dark.css`

**Step 1: 创建深色主题变量**

```css
/* frontend/src/assets/styles/theme-dark.css */
/* 深色科技风主题 - 玻璃态 */

[data-theme="dark"] {
  /* 背景色 */
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
  --cp-bg-active: rgba(255, 255, 255, 0.15);

  /* 文字色 */
  --cp-text-primary: #e2e8f0;
  --cp-text-secondary: #94a3b8;
  --cp-text-muted: #64748b;
  --cp-text-inverse: #0a0f1a;
  --cp-text-link: #14b8a6;

  /* 强调色 */
  --cp-accent-primary: #14b8a6;
  --cp-accent-secondary: #0f766e;
  --cp-accent-gradient: linear-gradient(135deg, #0f766e, #14b8a6);
  --cp-accent-light: rgba(14, 184, 166, 0.15);
  --cp-accent-danger: #f87171;
  --cp-accent-success: #34d399;
  --cp-accent-warning: #fbbf24;

  /* 边框色 */
  --cp-border-primary: rgba(255, 255, 255, 0.15);
  --cp-border-secondary: rgba(255, 255, 255, 0.25);
  --cp-border-focus: rgba(14, 184, 166, 0.5);
  --cp-border-light: rgba(255, 255, 255, 0.08);

  /* 阴影 */
  --cp-shadow-sm: 0 4px 12px rgba(15, 118, 110, 0.15);
  --cp-shadow-md: 0 8px 18px rgba(15, 118, 110, 0.2);
  --cp-shadow-lg: 0 20px 45px rgba(15, 118, 110, 0.25);
  --cp-shadow-glow: 0 0 30px rgba(15, 118, 110, 0.3);

  /* 图表配色 */
  --cp-chart-historical: #94a3b8;
  --cp-chart-gridline: rgba(255, 255, 255, 0.1);
  --cp-chart-scenario-1: #14b8a6;
  --cp-chart-scenario-2: #60a5fa;
  --cp-chart-scenario-3: #fbbf24;
  --cp-chart-scenario-4: #f87171;
  --cp-chart-scenario-5: #a78bfa;
  --cp-chart-scenario-6: #34d399;
}

/* 深色主题全局样式 - 保持现有风格 */
[data-theme="dark"] #app {
  background: linear-gradient(135deg, #0a0f1a 0%, #1a1f3a 50%, #0f1a2a 100%);
  color: var(--cp-text-primary);
}

/* 深色主题启用背景动画 */
[data-theme="dark"] .ambient-bg {
  display: block;
}
```

**Step 2: Commit**

```bash
git add frontend/src/assets/styles/theme-dark.css
git commit -m "feat: add dark theme CSS variables"
```

---

## Task 4: 创建组件基础样式覆盖文件

**Files:**
- Create: `frontend/src/assets/styles/components-base.css`

**Step 1: 创建 Element UI 组件样式覆盖**

```css
/* frontend/src/assets/styles/components-base.css */
/* Element UI 组件样式覆盖 - 双主题适配 */

/* ===== 卡片组件 ===== */
.el-card {
  background: var(--cp-bg-card);
  border: 1px solid var(--cp-border-primary);
  border-radius: var(--cp-radius-lg);
  box-shadow: var(--cp-shadow-md);
  transition: box-shadow var(--cp-transition-normal), transform var(--cp-transition-normal);
}

.el-card:hover {
  box-shadow: var(--cp-shadow-lg);
}

[data-theme="dark"] .el-card {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.el-card__header {
  background: var(--cp-bg-active);
  border-bottom: 1px solid var(--cp-border-light);
  padding: var(--cp-spacing-md) var(--cp-spacing-lg);
}

.el-card__body {
  background: transparent;
  padding: var(--cp-spacing-lg);
}

/* ===== 表格组件 ===== */
.el-table {
  background: transparent;
  color: var(--cp-text-primary);
}

.el-table th {
  background: var(--cp-bg-table-header);
  color: var(--cp-text-primary);
  font-weight: 700;
}

.el-table td {
  border-bottom: 1px solid var(--cp-border-light);
}

.el-table--striped .el-table__body tr.el-table__row--striped td {
  background: var(--cp-bg-table-row-stripe);
}

.el-table__body tr:hover > td {
  background: var(--cp-bg-hover);
}

.el-table--border::after,
.el-table--group::after,
.el-table::before {
  background-color: var(--cp-border-primary);
}

/* ===== 按钮组件 ===== */
.el-button {
  min-height: var(--cp-touch-target);
  border-radius: var(--cp-radius-md);
  font-weight: 600;
  transition: all var(--cp-transition-fast);
}

.el-button:active {
  transform: scale(0.97);
}

.el-button--primary,
.el-button--success {
  background: var(--cp-accent-gradient);
  border: 1px solid var(--cp-border-secondary);
  color: var(--cp-text-inverse);
}

.el-button--primary:hover,
.el-button--success:hover {
  box-shadow: var(--cp-shadow-glow);
}

.el-button--default {
  background: var(--cp-bg-card);
  border: 1px solid var(--cp-border-secondary);
  color: var(--cp-text-primary);
}

.el-button--danger {
  background: var(--cp-accent-danger);
  border: none;
  color: var(--cp-text-inverse);
}

.el-button.is-disabled,
.el-button.is-disabled:hover {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* ===== 表单组件 ===== */
.el-input__inner,
.el-textarea__inner {
  background: var(--cp-bg-input);
  border: 1px solid var(--cp-border-primary);
  border-radius: var(--cp-radius-md);
  color: var(--cp-text-primary);
  transition: border-color var(--cp-transition-normal), box-shadow var(--cp-transition-normal);
}

.el-input__inner:hover,
.el-textarea__inner:hover {
  border-color: var(--cp-border-secondary);
}

.el-input__inner:focus,
.el-textarea__inner:focus {
  border-color: var(--cp-accent-primary);
  box-shadow: var(--cp-shadow-glow);
}

.el-input__inner::placeholder {
  color: var(--cp-text-muted);
}

.el-form-item__label {
  color: var(--cp-text-primary);
  font-weight: 600;
}

/* ===== Slider 组件 ===== */
.el-slider__runway {
  height: 8px;
  border-radius: 999px;
  background: var(--cp-bg-active);
}

.el-slider__bar {
  background: var(--cp-accent-gradient);
  border-radius: 999px;
}

.el-slider__button {
  width: 18px;
  height: 18px;
  border: 2px solid var(--cp-accent-primary);
  background: var(--cp-bg-card);
}

/* ===== Tabs 组件 ===== */
.el-tabs__header {
  border-bottom: 1px solid var(--cp-border-primary);
}

.el-tabs__nav-wrap::after {
  background-color: var(--cp-border-primary);
}

.el-tabs__item {
  min-height: var(--cp-touch-target);
  color: var(--cp-text-secondary);
  font-weight: 600;
  transition: all var(--cp-transition-normal);
}

.el-tabs__item:hover {
  color: var(--cp-accent-primary);
}

.el-tabs__item.is-active {
  color: var(--cp-accent-primary);
  background: var(--cp-bg-active);
}

.el-tabs__item.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

[data-theme="dark"] .el-tabs__item.is-active {
  box-shadow: var(--cp-shadow-glow);
}

/* ===== Tag 组件 ===== */
.el-tag {
  border-radius: var(--cp-radius-sm);
  font-weight: 600;
}

.el-tag--dark {
  background: var(--cp-accent-primary);
  border-color: var(--cp-accent-primary);
}

.el-tag--success {
  background: var(--cp-accent-success);
  border-color: var(--cp-accent-success);
  color: var(--cp-text-inverse);
}

.el-tag--warning {
  background: var(--cp-accent-warning);
  border-color: var(--cp-accent-warning);
  color: var(--cp-text-inverse);
}

.el-tag--danger {
  background: var(--cp-accent-danger);
  border-color: var(--cp-accent-danger);
}

.el-tag--info {
  background: var(--cp-bg-active);
  border-color: var(--cp-border-primary);
  color: var(--cp-text-secondary);
}

/* ===== Divider 组件 ===== */
.el-divider {
  background-color: var(--cp-border-light);
}

.el-divider__text {
  color: var(--cp-accent-primary);
  font-weight: 700;
  background: var(--cp-bg-card);
}

/* ===== Loading 组件 ===== */
.el-loading-mask {
  background-color: rgba(0, 0, 0, 0.7);
}

.el-loading-spinner .path {
  stroke: var(--cp-accent-primary);
}

/* ===== Message 组件 ===== */
.el-message {
  border-radius: var(--cp-radius-md);
}

.el-message--success {
  background: var(--cp-accent-success);
}

.el-message--warning {
  background: var(--cp-accent-warning);
}

.el-message--error {
  background: var(--cp-accent-danger);
}

/* ===== Select 组件 ===== */
.el-select-dropdown {
  background: var(--cp-bg-card);
  border: 1px solid var(--cp-border-primary);
  border-radius: var(--cp-radius-md);
  box-shadow: var(--cp-shadow-lg);
}

.el-select-dropdown__item {
  color: var(--cp-text-primary);
}

.el-select-dropdown__item.hover,
.el-select-dropdown__item:hover {
  background: var(--cp-bg-hover);
}

.el-select-dropdown__item.selected {
  color: var(--cp-accent-primary);
  font-weight: 700;
}

/* ===== Radio Button 组件 ===== */
.el-radio-button__inner {
  background: var(--cp-bg-card);
  border-color: var(--cp-border-secondary);
  color: var(--cp-text-primary);
}

.el-radio-button__orig-radio:checked + .el-radio-button__inner {
  background: var(--cp-accent-primary);
  border-color: var(--cp-accent-primary);
  color: var(--cp-text-inverse);
  box-shadow: none;
}

/* ===== 焦点状态 (无障碍) ===== */
.el-button:focus-visible,
.el-input__inner:focus-visible,
.el-tabs__item:focus-visible {
  outline: 2px solid var(--cp-accent-primary);
  outline-offset: 2px;
}

/* ===== 响应式调整 ===== */
@media (max-width: 992px) {
  .el-card__header {
    padding: var(--cp-spacing-sm) var(--cp-spacing-md);
  }

  .el-card__body {
    padding: var(--cp-spacing-md);
  }
}
```

**Step 2: Commit**

```bash
git add frontend/src/assets/styles/components-base.css
git commit -m "feat: add Element UI component style overrides"
```

---

## Task 5: 创建主题状态管理

**Files:**
- Create: `frontend/src/store/themeStore.js`

**Step 1: 创建 themeStore**

```javascript
// frontend/src/store/themeStore.js
import Vue from 'vue'

const STORE_KEY = 'theme-preference'

// 使用 Vue.observable 创建响应式对象 (Vue 2.x)
const state = Vue.observable({
  current: 'light'
})

const themeStore = {
  get current() {
    return state.current
  },

  init() {
    // 从 localStorage 恢复用户偏好
    const stored = localStorage.getItem(STORE_KEY)
    if (stored && (stored === 'light' || stored === 'dark')) {
      state.current = stored
    }
    this.apply()

    // 监听系统主题变化
    this.watchSystemTheme()
  },

  toggle() {
    state.current = state.current === 'light' ? 'dark' : 'light'
    localStorage.setItem(STORE_KEY, state.current)
    this.apply()
  },

  set(theme) {
    if (theme === 'light' || theme === 'dark') {
      state.current = theme
      localStorage.setItem(STORE_KEY, theme)
      this.apply()
    }
  },

  apply() {
    // 应用主题到 DOM
    document.documentElement.setAttribute('data-theme', state.current)

    // 更新 meta theme-color (移动端浏览器)
    const metaThemeColor = document.querySelector('meta[name="theme-color"]')
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', state.current === 'dark' ? '#0a0f1a' : '#ffffff')
    }
  },

  watchSystemTheme() {
    // 监听系统主题偏好变化
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', (e) => {
      // 如果用户没有手动设置过偏好，跟随系统
      if (!localStorage.getItem(STORE_KEY)) {
        state.current = e.matches ? 'dark' : 'light'
        this.apply()
      }
    })
  },

  // 检查是否为深色模式
  isDark() {
    return state.current === 'dark'
  }
}

export { themeStore }
```

**Step 2: Commit**

```bash
git add frontend/src/store/themeStore.js
git commit -m "feat: add theme state management store"
```

---

## Task 6: 创建主题切换按钮组件

**Files:**
- Create: `frontend/src/components/ThemeToggle.vue`

**Step 1: 创建 ThemeToggle 组件**

```vue
<!-- frontend/src/components/ThemeToggle.vue -->
<template>
  <button
    class="theme-toggle"
    @click="toggle"
    :aria-label="label"
    :title="label"
  >
    <transition name="icon-fade" mode="out-in">
      <!-- 太阳图标 (深色模式时显示) -->
      <svg v-if="isDark" key="sun" class="icon icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="5" />
        <line x1="12" y1="1" x2="12" y2="3" />
        <line x1="12" y1="21" x2="12" y2="23" />
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
        <line x1="1" y1="12" x2="3" y2="12" />
        <line x1="21" y1="12" x2="23" y2="12" />
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
      </svg>
      <!-- 月亮图标 (浅色模式时显示) -->
      <svg v-else key="moon" class="icon icon-moon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
      </svg>
    </transition>
  </button>
</template>

<script>
import { themeStore } from '@/store/themeStore'

export default {
  name: 'ThemeToggle',
  computed: {
    isDark() {
      return themeStore.isDark()
    },
    label() {
      return this.isDark ? '切换到浅色模式' : '切换到深色模式'
    }
  },
  methods: {
    toggle() {
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
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--cp-transition-normal);
}

.theme-toggle:hover {
  border-color: var(--cp-accent-primary);
  box-shadow: var(--cp-shadow-md);
}

.theme-toggle:active {
  transform: scale(0.95);
}

.theme-toggle:focus-visible {
  outline: 2px solid var(--cp-accent-primary);
  outline-offset: 2px;
}

.icon {
  width: 20px;
  height: 20px;
}

.icon-sun {
  stroke-width: 2.5;
}

/* 图标切换动画 */
.icon-fade-enter-active,
.icon-fade-leave-active {
  transition: opacity 200ms ease, transform 300ms ease;
}

.icon-fade-enter {
  opacity: 0;
  transform: rotate(-90deg) scale(0.5);
}

.icon-fade-leave-to {
  opacity: 0;
  transform: rotate(90deg) scale(0.5);
}

/* 深色主题下的按钮样式 */
[data-theme="dark"] .theme-toggle {
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

[data-theme="dark"] .theme-toggle:hover {
  box-shadow: var(--cp-shadow-glow);
}
</style>
```

**Step 2: Commit**

```bash
git add frontend/src/components/ThemeToggle.vue
git commit -m "feat: add ThemeToggle component with sun/moon icons"
```

---

## Task 7: 创建指标卡片组件

**Files:**
- Create: `frontend/src/components/MetricCard.vue`

**Step 1: 创建 MetricCard 组件**

```vue
<!-- frontend/src/components/MetricCard.vue -->
<template>
  <div class="metric-cards">
    <div
      v-for="(metric, index) in metrics"
      :key="index"
      class="metric-card"
    >
      <span class="metric-label">{{ metric.label }}</span>
      <div class="metric-value-row">
        <span class="metric-value">{{ metric.value }}</span>
        <span
          v-if="metric.trend"
          class="metric-trend"
          :class="metric.trendClass"
        >
          <svg v-if="metric.trend === 'down'" viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
            <path d="M7 10l5 5 5-5H7z"/>
          </svg>
          <svg v-if="metric.trend === 'up'" viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
            <path d="M7 14l5-5 5 5H7z"/>
          </svg>
        </span>
      </div>
      <span class="metric-unit">{{ metric.unit }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MetricCard',
  props: {
    // 指标数据数组
    metrics: {
      type: Array,
      default: () => []
    }
  }
}
</script>

<style scoped>
.metric-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--cp-spacing-md);
  margin-bottom: var(--cp-spacing-lg);
}

.metric-card {
  background: var(--cp-bg-card);
  border: 1px solid var(--cp-border-primary);
  border-radius: var(--cp-radius-md);
  padding: var(--cp-spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--cp-spacing-xs);
  transition: box-shadow var(--cp-transition-normal);
}

.metric-card:hover {
  box-shadow: var(--cp-shadow-md);
}

.metric-label {
  font-size: var(--cp-font-xs);
  color: var(--cp-text-secondary);
  font-weight: 500;
}

.metric-value-row {
  display: flex;
  align-items: center;
  gap: var(--cp-spacing-xs);
}

.metric-value {
  font-size: var(--cp-font-xl);
  font-weight: 800;
  color: var(--cp-accent-primary);
  line-height: 1.2;
}

.metric-trend {
  display: flex;
  align-items: center;
}

.metric-trend.down {
  color: var(--cp-accent-success);
}

.metric-trend.up {
  color: var(--cp-accent-warning);
}

.metric-unit {
  font-size: var(--cp-font-xs);
  color: var(--cp-text-muted);
}

/* 深色主题 */
[data-theme="dark"] .metric-card {
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

[data-theme="dark"] .metric-card:hover {
  box-shadow: var(--cp-shadow-glow);
}

/* 响应式 */
@media (max-width: 992px) {
  .metric-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 576px) {
  .metric-cards {
    grid-template-columns: 1fr;
  }

  .metric-value {
    font-size: var(--cp-font-lg);
  }
}
</style>
```

**Step 2: Commit**

```bash
git add frontend/src/components/MetricCard.vue
git commit -m "feat: add MetricCard component for chart storytelling"
```

---

## Task 8: 修改 App.vue 引入新样式系统

**Files:**
- Modify: `frontend/src/App.vue`

**Step 1: 更新样式导入**

将现有的样式导入替换为新系统：

```vue
<!-- frontend/src/App.vue style 部分 -->
<style>
/* 导入新的主题系统 */
@import url('./assets/styles/design-tokens.css');
@import url('./assets/styles/theme-light.css');
@import url('./assets/styles/theme-dark.css');
@import url('./assets/styles/components-base.css');
@import url('./assets/styles/animations.css');
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Noto+Sans+SC:wght@400;500;700&display=swap');
```

**Step 2: 更新根元素样式**

移除现有 `:root` 硬编码变量，改用 CSS 变量引用：

```css
/* 替换现有 #app 样式 */
#app {
  font-family: 'Manrope', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--cp-text-primary);
  background: var(--cp-bg-primary);
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  transition: background 400ms ease-out, color 300ms ease-out;
}
```

**Step 3: 更新 Header 样式使用 CSS 变量**

```css
/* 替换现有 .app-header 样式 */
.app-header {
  color: var(--cp-text-primary);
  height: 78px !important;
  padding: 0 var(--cp-spacing-lg);
  display: flex;
  align-items: center;
  border-bottom: 2px solid var(--cp-header-border);
  background: var(--cp-bg-header);
  box-shadow: var(--cp-shadow-sm);
  transition: all var(--cp-transition-slow);
}

/* 深色主题保持玻璃态 */
[data-theme="dark"] .app-header {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--cp-border-primary);
  box-shadow: var(--cp-shadow-glow);
}
```

**Step 4: 更新 Footer 样式**

```css
/* 替换现有 .app-footer 样式 */
.app-footer {
  background: var(--cp-bg-footer);
  color: var(--cp-text-secondary);
  height: 48px !important;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--cp-font-xs);
  border-top: 1px solid var(--cp-border-light);
  transition: all var(--cp-transition-slow);
}

/* 深色主题保持玻璃态 */
[data-theme="dark"] .app-footer {
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
```

**Step 5: 在 template 中添加 ThemeToggle**

```vue
<!-- frontend/src/App.vue template 部分修改 -->
<el-header class="app-header">
  <div class="header-content">
    <div class="logo">
      <!-- ... 保持现有 logo 结构 -->
    </div>
    <div class="header-info">
      <el-tag size="small" effect="dark">LEAP / Kaya / STIRPAT</el-tag>
      <theme-toggle></theme-toggle>
    </div>
  </div>
</el-header>
```

**Step 6: 导入 ThemeToggle 组件**

```javascript
// frontend/src/App.vue script 部分
import ThemeToggle from './components/ThemeToggle.vue'
import { themeStore } from './store/themeStore'

export default {
  components: {
    // ... 现有组件
    ThemeToggle
  },
  created() {
    // 初始化主题
    themeStore.init()
  }
}
```

**Step 7: Commit**

```bash
git add frontend/src/App.vue
git commit -m "feat: integrate theme system into App.vue"
```

---

## Task 9: 修改 PredictionResults 添加指标卡片

**Files:**
- Modify: `frontend/src/components/PredictionResults.vue`

**Step 1: 导入 MetricCard 组件**

```javascript
// 在 script 部分 import 区域添加
import MetricCard from './MetricCard.vue'
import { themeStore } from '@/store/themeStore'

export default {
  components: {
    // ... 现有组件
    MetricCard
  },
  // ...
}
```

**Step 2: 添加计算属性生成指标数据**

```javascript
// 在 computed 区域添加
computed: {
  isDark() {
    return themeStore.isDark()
  },
  chartColors() {
    return this.isDark
      ? ['#14b8a6', '#60a5fa', '#fbbf24', '#f87171', '#a78bfa', '#34d399']
      : ['#0f766e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#10b981']
  },
  historicalColor() {
    return this.isDark ? '#94a3b8' : '#64748b'
  },
  metricCardsData() {
    if (!this.chartData || Object.keys(this.chartData).length === 0) {
      return []
    }

    const metrics = []
    const scenarioKeys = Object.keys(this.chartData)

    // 达峰年份
    const firstPeak = this.peakSummaries[0]
    if (firstPeak) {
      metrics.push({
        label: '预测达峰年份',
        value: firstPeak.year + '年',
        unit: '',
        trend: 'down',
        trendClass: 'down'
      })
    }

    // 排放峰值
    const firstScenario = this.chartData[scenarioKeys[0]]
    if (firstScenario && firstScenario.peak) {
      metrics.push({
        label: '排放峰值',
        value: Math.round(firstScenario.peak.emission).toLocaleString(),
        unit: '万吨CO₂',
        trend: null
      })
    }

    // 减排幅度 (计算从峰值到终点)
    if (firstScenario && firstScenario.emissions) {
      const peakEmission = firstScenario.peak?.emission || 0
      const lastEmission = firstScenario.emissions[firstScenario.emissions.length - 1] || 0
      const reduction = ((peakEmission - lastEmission) / peakEmission * 100).toFixed(1)
      metrics.push({
        label: '减排幅度',
        value: reduction + '%',
        unit: '预测下降',
        trend: parseFloat(reduction) > 0 ? 'down' : 'up',
        trendClass: parseFloat(reduction) > 0 ? 'down' : 'up'
      })
    }

    // 情景数量
    metrics.push({
      label: '预测情景',
      value: scenarioKeys.length + '个',
      unit: '已创建',
      trend: null
    })

    return metrics
  }
}
```

**Step 3: 在 template 中添加 MetricCard**

```vue
<!-- 在碳排放图表卡片内部，chart-container 之前添加 -->
<el-card class="chart-card" shadow="hover">
  <div slot="header" class="card-header">
    <span class="card-title">碳排放达峰预测</span>
    <!-- ... 现有的 peak-summary -->
  </div>

  <div v-if="loading" class="loading-container">...</div>
  <div v-else-if="error" class="error-container">...</div>
  <div v-else>
    <!-- 新增: 指标卡片区域 -->
    <metric-card v-if="metricCardsData.length > 0" :metrics="metricCardsData"></metric-card>
    <div class="chart-container">
      <div id="carbon-peak-chart" class="echarts-container"></div>
    </div>
  </div>
</el-card>
```

**Step 4: 更新图表配色使用主题变量**

修改 `initCarbonPeakChart` 方法：

```javascript
// 在 initCarbonPeakChart 中替换 SCENARIO_COLORS
// 将 lineStyle.color 改为使用 this.chartColors[index % this.chartColors.length]

// 历史数据线颜色改为使用 this.historicalColor
lineStyle: { width: 2, type: 'dashed', color: this.historicalColor }
```

**Step 5: 添加峰值标注线**

```javascript
// 在 carbonPeakChart setOption 中添加 markLine
this.carbonPeakChart.setOption({
  // ... 现有配置
  series,
  // 新增: 峰值标注线
  graphic: this.peakSummaries.map((summary, idx) => ({
    type: 'line',
    shape: { x1: 0, y1: 0, x2: 0, y2: 0 },
    style: {
      stroke: this.chartColors[idx % this.chartColors.length],
      lineWidth: 2,
      lineDash: [4, 4]
    },
    // 具体位置需要根据图表坐标计算
  }))
})
```

**Step 6: 更新 Tooltip 样式**

```javascript
// 在所有图表 setOption 中统一 tooltip 样式
tooltip: {
  trigger: 'axis',
  backgroundColor: this.isDark ? 'rgba(15, 23, 42, 0.9)' : '#ffffff',
  borderColor: this.isDark ? 'rgba(255, 255, 255, 0.2)' : 'rgba(15, 118, 110, 0.2)',
  borderRadius: 12,
  shadowBlur: this.isDark ? 20 : 8,
  shadowColor: this.isDark ? 'rgba(15, 118, 110, 0.3)' : 'rgba(15, 118, 110, 0.1)',
  textStyle: {
    color: this.isDark ? '#e2e8f0' : '#134e4a'
  }
}
```

**Step 7: 监听主题变化重绘图表**

```javascript
// 在 watch 区域添加
watch: {
  // ... 现有 watch
  isDark(newVal) {
    // 主题变化时重绘所有图表
    this.$nextTick(() => {
      setTimeout(() => {
        this.initCarbonPeakChart()
        this.initGdpChart()
        this.initEnergyChart()
      }, 300) // 等待 CSS 过渡完成
    })
  }
}
```

**Step 8: Commit**

```bash
git add frontend/src/components/PredictionResults.vue
git commit -m "feat: add metric cards and theme-aware chart colors"
```

---

## Task 10: 修改 DataUpload 组件适配双主题

**Files:**
- Modify: `frontend/src/components/DataUpload.vue`

**Step 1: 更新样式使用 CSS 变量**

将所有硬编码颜色替换为 CSS 变量：

```css
/* 替换现有样式 */
.upload-card {
  margin-bottom: var(--cp-spacing-lg);
  border-radius: var(--cp-radius-lg);
}

.upload-head h2 {
  color: var(--cp-text-primary);
  font-size: var(--cp-font-lg);
  font-weight: 800;
}

.upload-head-tip {
  font-size: var(--cp-font-xs);
  color: var(--cp-text-secondary);
}

.intro-copy {
  color: var(--cp-text-secondary);
  line-height: var(--cp-line-height);
}

.upload-status.success {
  background: var(--cp-accent-light);
  color: var(--cp-accent-primary);
  border: 1px solid var(--cp-border-secondary);
}

.upload-status.error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--cp-accent-danger);
  border: 1px solid rgba(239, 68, 68, 0.22);
}

.upload-status.loading {
  background: rgba(37, 99, 235, 0.09);
  color: #1d4ed8;
  border: 1px solid rgba(37, 99, 235, 0.18);
}

.data-info {
  background: var(--cp-bg-active);
  border-radius: var(--cp-radius-md);
  border: 1px solid var(--cp-border-primary);
}

.data-info h3 {
  color: var(--cp-text-primary);
  font-size: var(--cp-font-md);
  font-weight: 800;
}

.info-item {
  background: var(--cp-bg-card);
  border: 1px solid var(--cp-border-primary);
  border-radius: var(--cp-radius-md);
}

.item-label {
  color: var(--cp-text-muted);
  font-size: var(--cp-font-xs);
}

.info-item strong {
  color: var(--cp-text-primary);
}

.data-table {
  background: var(--cp-bg-card);
  border-radius: var(--cp-radius-md);
  border: 1px solid var(--cp-border-primary);
}

.data-table h3 {
  color: var(--cp-text-primary);
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/DataUpload.vue
git commit -m "feat: update DataUpload styles to use CSS variables"
```

---

## Task 11: 修改 ScenarioManager 组件适配双主题

**Files:**
- Modify: `frontend/src/components/ScenarioManager.vue`

**Step 1: 更新样式使用 CSS 变量**

```css
/* 替换现有样式 */
.scenario-manager {
  margin-bottom: var(--cp-spacing-lg);
}

.recommend-section {
  margin-bottom: var(--cp-spacing-lg);
}

.scenario-card,
.scenario-list-card {
  border-radius: var(--cp-radius-lg);
  border: 1px solid var(--cp-border-primary);
}

.card-title {
  font-size: var(--cp-font-md);
  font-weight: 800;
  color: var(--cp-text-primary);
}

.empty-scenarios {
  color: var(--cp-text-muted);
}

.empty-scenarios i {
  color: var(--cp-text-muted);
}

.prediction-hint {
  color: var(--cp-text-muted);
  font-size: var(--cp-font-xs);
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/ScenarioManager.vue
git commit -m "feat: update ScenarioManager styles to use CSS variables"
```

---

## Task 12: 测试双主题系统

**Files:**
- None (manual testing)

**Step 1: 启动前端开发服务器**

```bash
cd frontend && npm run serve
```

**Step 2: 手动测试清单**

| 测试项 | 预期结果 |
|--------|----------|
| 默认主题 | 浅色主题，白色背景，青绿色点缀 |
| 点击切换按钮 | 平滑过渡到深色主题 |
| 深色主题 | 玻璃态卡片，霓虹发光效果，背景动画 |
| 再次切换 | 回到浅色主题 |
| 刷新页面 | 保持上次选择的主题 |
| 图表配色 | 两主题下颜色协调，对比度足够 |
| 指标卡片 | 正确显示达峰年份、峰值、趋势箭头 |
| 移动端 | 响应式布局正常 |
| `prefers-reduced-motion` | 动画禁用 |

**Step 3: 如发现问题，修复并提交**

---

## Task 13: 最终提交和文档更新

**Step 1: 运行 lint 检查**

```bash
cd frontend && npm run lint
```

**Step 2: 修复 lint 问题（如有）**

**Step 3: 提交所有更改**

```bash
git add -A
git commit -m "feat: complete dual-theme system implementation"
```

---

## 实施优先级总结

| 任务 | 优先级 | 预估时间 |
|------|--------|----------|
| Task 1-4 (样式文件) | P0 | 20分钟 |
| Task 5-6 (主题切换) | P0 | 15分钟 |
| Task 7 (指标卡片) | P1 | 10分钟 |
| Task 8 (App.vue) | P0 | 15分钟 |
| Task 9 (PredictionResults) | P1 | 20分钟 |
| Task 10-11 (组件样式) | P1 | 15分钟 |
| Task 12 (测试) | P0 | 15分钟 |
| Task 13 (收尾) | P0 | 5分钟 |

**总预估时间: 约 1.5-2 小时**