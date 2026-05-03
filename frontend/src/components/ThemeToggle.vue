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