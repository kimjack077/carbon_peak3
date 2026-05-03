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