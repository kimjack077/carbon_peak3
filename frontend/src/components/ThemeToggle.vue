<!-- 主题切换按钮 -->
<template>
  <button
    class="theme-toggle"
    @click="toggle"
    :aria-label="label"
    :title="label"
  >
    <transition name="icon-fade" mode="out-in">
      <svg v-if="isDark" key="sun" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="5"/>
        <line x1="12" y1="1" x2="12" y2="3"/>
        <line x1="12" y1="21" x2="12" y2="23"/>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
        <line x1="1" y1="12" x2="3" y2="12"/>
        <line x1="21" y1="12" x2="23" y2="12"/>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
      </svg>
      <svg v-else key="moon" class="icon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
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
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.theme-toggle:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.theme-toggle:active {
  transform: scale(0.95);
}

.icon {
  width: 16px;
  height: 16px;
}

.icon-fade-enter-active,
.icon-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.icon-fade-enter,
.icon-fade-leave-to {
  opacity: 0;
  transform: rotate(90deg) scale(0.8);
}
</style>
