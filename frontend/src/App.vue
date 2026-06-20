<template>
  <div id="app">
    <div class="app-layout">
      <!-- Header -->
      <header class="app-header">
        <div class="header-inner">
          <div class="header-left">
            <div class="logo-mark">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
            </div>
            <div class="logo-text">
              <h1>碳达峰预测系统</h1>
              <span class="logo-sub">Carbon Peak Prediction</span>
            </div>
          </div>
          <div class="header-right">
            <div class="model-tags">
              <span class="tag">LEAP</span>
              <span class="tag">Kaya</span>
              <span class="tag">STIRPAT</span>
            </div>
            <theme-toggle></theme-toggle>
          </div>
        </div>
      </header>

      <!-- Main Content -->
      <main class="app-main">
        <div class="main-inner">
          <div class="tab-container">
            <div class="tab-bar">
              <button
                v-for="tab in tabs"
                :key="tab.name"
                :class="['tab-btn', { active: activeTab === tab.name, disabled: tab.disabled }]"
                :disabled="tab.disabled"
                @click.prevent="switchTab(tab.name)"
                type="button"
              >
                <span class="tab-icon" v-html="tab.icon"></span>
                <span class="tab-label">{{ tab.label }}</span>
              </button>
            </div>
            <div class="tab-content">
              <data-upload v-show="activeTab === 'upload'" @data-loaded="handleDataLoaded"></data-upload>
              <scenario-manager v-show="activeTab === 'scenarios'"></scenario-manager>
              <prediction-results
                v-show="activeTab === 'results'"
                ref="predictionResults"
                :key="resultsKey"
                :is-active="activeTab === 'results'"
              ></prediction-results>
              <scenario-compare v-show="activeTab === 'compare'" :is-active="activeTab === 'compare'"></scenario-compare>
            </div>
          </div>
        </div>
      </main>

      <!-- Footer -->
      <footer class="app-footer">
        <span>Carbon Peak Prediction System · 基于 LEAP、Kaya、STIRPAT 模型</span>
      </footer>
    </div>
  </div>
</template>

<script>
import DataUpload from './components/DataUpload.vue'
import ScenarioManager from './components/ScenarioManager.vue'
import PredictionResults from './components/PredictionResults.vue'
import ScenarioCompare from './components/ScenarioCompare.vue'
import ThemeToggle from './components/ThemeToggle.vue'
import { themeStore } from './store/themeStore'

export default {
  name: 'App',
  components: {
    DataUpload,
    ScenarioManager,
    PredictionResults,
    ScenarioCompare,
    ThemeToggle
  },
  data() {
    return {
      activeTab: 'upload',
      dataLoaded: false,
      resultsKey: 0
    }
  },
  computed: {
    tabs() {
      return [
        {
          name: 'upload',
          label: '数据来源',
          icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
          disabled: false
        },
        {
          name: 'scenarios',
          label: '情景设置',
          icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
          disabled: !this.dataLoaded
        },
        {
          name: 'results',
          label: '预测结果',
          icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
          disabled: !this.dataLoaded
        },
        {
          name: 'compare',
          label: '情景对比',
          icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>',
          disabled: !this.dataLoaded
        }
      ]
    }
  },
  created() {
    themeStore.init()
  },
  methods: {
    switchTab(name) {
      this.activeTab = name
    },
    handleDataLoaded(success) {
      this.dataLoaded = success
      if (success) {
        this.activeTab = 'scenarios'
      }
    },
    handlePredictionCompleted() {
      this.resultsKey += 1
      this.activeTab = 'results'
    }
  }
}
</script>

<style>
@import url('./assets/styles/design-tokens.css');
@import url('./assets/styles/theme-light.css');
@import url('./assets/styles/theme-dark.css');
@import url('./assets/styles/components-base.css');

/* ===== Global Reset ===== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  background: var(--cp-bg-primary);
  color: var(--cp-text-primary);
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: 1.5;
}

#app {
  min-height: 100vh;
  background: var(--cp-bg-primary);
  color: var(--cp-text-primary);
  transition: background-color var(--transition-slow), color var(--transition-slow);
}

/* ===== App Layout ===== */
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ===== Header ===== */
.app-header {
  height: 56px;
  background: var(--cp-bg-header);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky, 200);
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--space-6, 24px);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3, 12px);
}

.logo-mark {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-md, 10px);
  color: white;
}

.logo-text h1 {
  font-size: var(--text-base, 15px);
  font-weight: 600;
  color: white;
  line-height: 1.2;
  font-family: var(--font-heading);
}

.logo-sub {
  font-size: var(--text-xs, 11px);
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-4, 16px);
}

.model-tags {
  display: flex;
  gap: var(--space-2, 8px);
}

.model-tags .tag {
  font-size: var(--text-xs, 11px);
  color: rgba(255, 255, 255, 0.75);
  padding: 3px 8px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-sm, 6px);
  font-weight: 500;
  letter-spacing: 0.3px;
}

/* ===== Main Content ===== */
.app-main {
  flex: 1;
  padding: var(--space-6, 24px);
  background: var(--cp-bg-primary);
}

.main-inner {
  max-width: 1400px;
  margin: 0 auto;
}

/* ===== Tab Container ===== */
.tab-container {
  background: var(--cp-bg-card);
  border-radius: var(--radius-lg, 16px);
  border: 1px solid var(--cp-border-primary);
  box-shadow: var(--cp-shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
  overflow: hidden;
}

.tab-bar {
  display: flex;
  background: var(--cp-bg-secondary);
  border-bottom: 1px solid var(--cp-border-primary);
  padding: 0 var(--space-2, 8px);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2, 8px);
  padding: 0 var(--space-5, 20px);
  height: 46px;
  border: none;
  background: transparent;
  color: var(--cp-text-secondary);
  font-family: var(--font-body);
  font-size: var(--text-sm, 13px);
  font-weight: 500;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
  white-space: nowrap;
  outline: none;
}

.tab-btn:hover:not(:disabled) {
  color: var(--cp-primary);
  background: var(--cp-bg-hover);
}

.tab-btn.active {
  color: var(--cp-primary);
  font-weight: 600;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: var(--space-4, 16px);
  right: var(--space-4, 16px);
  height: 2px;
  background: var(--cp-primary);
  border-radius: 1px 1px 0 0;
}

.tab-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.tab-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
}

.tab-icon svg {
  width: 16px;
  height: 16px;
}

.tab-content {
  padding: var(--space-6, 24px);
  min-height: 60vh;
}

/* ===== Footer ===== */
.app-footer {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--cp-bg-footer);
  border-top: 1px solid var(--cp-border-primary);
  color: var(--cp-text-muted);
  font-size: var(--text-xs, 11px);
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .app-header {
    height: auto;
    padding: var(--space-3, 12px) 0;
  }

  .header-inner {
    padding: 0 var(--space-4, 16px);
    flex-wrap: wrap;
    gap: var(--space-2, 8px);
  }

  .model-tags {
    display: none;
  }

  .app-main {
    padding: var(--space-4, 16px);
  }

  .tab-bar {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .tab-btn {
    padding: 0 var(--space-3, 12px);
    font-size: var(--text-xs, 11px);
  }

  .tab-content {
    padding: var(--space-4, 16px);
  }
}
</style>
