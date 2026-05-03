<template>
  <div id="app">
    <div class="ambient-bg" aria-hidden="true">
      <span class="orb orb-a"></span>
      <span class="orb orb-b"></span>
      <span class="grid-pattern"></span>
    </div>
    <el-container class="app-shell">
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
            <div>
              <h1>碳达峰预测系统</h1>
              <p class="subtitle">多情景建模与路径对比分析</p>
            </div>
          </div>
          <div class="header-info">
            <el-tag size="small" effect="dark">LEAP / Kaya / STIRPAT</el-tag>
          </div>
        </div>
      </el-header>
      <el-main class="app-main">
        <section class="tab-shell">
          <el-tabs v-model="activeTab" type="card" class="app-tabs">
          <el-tab-pane label="数据来源" name="upload">
            <data-upload @data-loaded="handleDataLoaded"></data-upload>
          </el-tab-pane>
          <el-tab-pane label="情景设置" name="scenarios" :disabled="!dataLoaded">
            <scenario-manager @prediction-completed="handlePredictionCompleted"></scenario-manager>
          </el-tab-pane>
          <el-tab-pane label="预测结果" name="results" :disabled="!dataLoaded">
            <prediction-results
              ref="predictionResults"
              :key="resultsKey"
              :is-active="activeTab === 'results'"
            ></prediction-results>
          </el-tab-pane>
          </el-tabs>
        </section>
      </el-main>
      <el-footer class="app-footer">
        <p>Carbon Peak Prediction System - 基于 LEAP、Kaya、STIRPAT 模型</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import DataUpload from './components/DataUpload.vue'
import ScenarioManager from './components/ScenarioManager.vue'
import PredictionResults from './components/PredictionResults.vue'

export default {
  name: 'App',
  components: {
    DataUpload,
    ScenarioManager,
    PredictionResults
  },
  data() {
    return {
      activeTab: 'upload',
      dataLoaded: false,
      resultsKey: 0
    }
  },
  methods: {
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
@import url('./assets/styles/theme.css');
@import url('./assets/styles/animations.css');
@import url('./assets/styles/glassmorphism.css');
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Noto+Sans+SC:wght@400;500;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --cp-bg-deep: #0a0f1a;
  --cp-bg-surface: rgba(15, 23, 42, 0.85);
  --cp-bg: #0a0f1a;
  --cp-surface: rgba(15, 23, 42, 0.85);
  --cp-surface-strong: rgba(15, 23, 42, 0.95);
  --cp-text: #e2e8f0;
  --cp-text-muted: #94a3b8;
  --cp-primary: #0f766e;
  --cp-primary-deep: #14b8a6;
  --cp-primary-glow: rgba(15, 118, 110, 0.4);
  --cp-accent: #f59e0b;
  --cp-neon-blue: #3b82f6;
  --cp-neon-purple: #8b5cf6;
  --cp-glass-bg: rgba(255, 255, 255, 0.08);
  --cp-glass-border: rgba(255, 255, 255, 0.15);
  --cp-border: rgba(255, 255, 255, 0.15);
  --cp-shadow-lg: 0 20px 45px rgba(15, 118, 110, 0.2);
  --cp-shadow-sm: 0 8px 18px rgba(15, 118, 110, 0.15);
  --cp-shadow-glow: 0 0 30px rgba(15, 118, 110, 0.3);
  --cp-radius-lg: 20px;
  --cp-radius-md: 14px;
}

#app {
  font-family: 'Manrope', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--cp-text);
  background: linear-gradient(135deg, #0a0f1a 0%, #1a1f3a 50%, #0f1a2a 100%);
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.ambient-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(2px);
}

.orb-a {
  width: 420px;
  height: 420px;
  background: radial-gradient(circle at 30% 30%, rgba(15, 118, 110, 0.3), rgba(139, 92, 246, 0.15), transparent);
  top: -120px;
  left: -80px;
  animation: float-slow 11s ease-in-out infinite;
}

.orb-b {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle at 65% 40%, rgba(59, 130, 246, 0.25), rgba(15, 118, 110, 0.15), transparent);
  right: -150px;
  bottom: -150px;
  animation: float-slow 13s ease-in-out infinite reverse;
}

.grid-pattern {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(15, 118, 110, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(15, 118, 110, 0.08) 1px, transparent 1px);
  background-size: 36px 36px;
  mask-image: radial-gradient(circle at 50% 50%, rgba(0, 0, 0, 0.6), transparent 75%);
}

.app-shell {
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

.el-container {
  min-height: 100vh;
}

.app-header {
  color: #f8fafc;
  height: 78px !important;
  padding: 0 28px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.4), rgba(139, 92, 246, 0.3));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 0 30px rgba(15, 118, 110, 0.3);
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo svg {
  opacity: 0.92;
}

.logo h1 {
  font-size: 22px;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: 0.4px;
}

.subtitle {
  font-size: 12px;
  opacity: 0.85;
  margin-top: 4px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.header-info .el-tag {
  min-height: 30px;
  padding: 0 12px;
  border: 1px solid rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
  letter-spacing: 0.03em;
  font-weight: 700;
}

.app-main {
  padding: 26px;
  min-height: calc(100vh - 126px);
}

.tab-shell {
  background: var(--cp-glass-bg);
  border: 1px solid var(--cp-glass-border);
  box-shadow: var(--cp-shadow-glow);
  border-radius: var(--cp-radius-lg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 14px 16px 18px;
}

.app-footer {
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.35), rgba(139, 92, 246, 0.25));
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  color: rgba(255, 255, 255, 0.86);
  height: 48px !important;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  letter-spacing: 0.02em;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}

::v-deep .app-tabs > .el-tabs__header {
  margin-bottom: 18px;
}

::v-deep .app-tabs > .el-tabs__header .el-tabs__nav-wrap::after {
  background-color: rgba(255, 255, 255, 0.15);
}

::v-deep .app-tabs > .el-tabs__header .el-tabs__item {
  min-height: 44px;
  line-height: 44px;
  padding: 0 22px;
  font-weight: 700;
  color: var(--cp-text-muted);
  transition: all 0.2s ease;
  border-radius: 11px 11px 0 0;
}

::v-deep .app-tabs > .el-tabs__header .el-tabs__item:focus,
::v-deep .app-tabs > .el-tabs__header .el-tabs__item:focus-visible {
  outline: 2px solid rgba(15, 118, 110, 0.5);
  outline-offset: -2px;
}

::v-deep .app-tabs > .el-tabs__header .el-tabs__item.is-active {
  color: var(--cp-primary-deep);
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 15px rgba(15, 118, 110, 0.3);
}

::v-deep .app-tabs > .el-tabs__header .el-tabs__item:hover {
  color: var(--cp-primary);
}

::v-deep .el-card {
  border: 1px solid var(--cp-glass-border);
  box-shadow: var(--cp-shadow-sm);
  border-radius: var(--cp-radius-md);
  overflow: hidden;
  background: var(--cp-glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

::v-deep .el-card__header {
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.25), rgba(139, 92, 246, 0.15));
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px 20px;
}

::v-deep .el-card__body {
  background: rgba(15, 23, 42, 0.6);
}

::v-deep .el-button--primary {
  background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
  border: 1px solid rgba(255, 255, 255, 0.25);
  box-shadow: 0 0 10px rgba(15, 118, 110, 0.3);
}

::v-deep .el-button--primary:hover {
  background: linear-gradient(135deg, #0d6560 0%, #0f9f8f 100%);
  box-shadow: 0 0 20px rgba(15, 118, 110, 0.5);
}

::v-deep .el-button--success {
  background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 10px rgba(15, 118, 110, 0.3);
}

::v-deep .el-button--success:hover {
  background: linear-gradient(135deg, #0d6560 0%, #0d9f90 100%);
  box-shadow: 0 0 20px rgba(15, 118, 110, 0.5);
}

::v-deep .el-button {
  min-height: 40px;
}

::v-deep .el-button:focus,
::v-deep .el-button:focus-visible,
::v-deep .el-input__inner:focus,
::v-deep .el-textarea__inner:focus,
::v-deep .el-select .el-input.is-focus .el-input__inner {
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.2);
}

@keyframes float-slow {
  0% {
    transform: translateY(0) translateX(0);
  }
  50% {
    transform: translateY(16px) translateX(8px);
  }
  100% {
    transform: translateY(0) translateX(0);
  }
}

@media (max-width: 992px) {
  .app-main {
    padding: 16px;
  }

  .app-header {
    height: auto !important;
    padding: 14px 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .logo h1 {
    font-size: 19px;
  }

  .subtitle {
    font-size: 11px;
    letter-spacing: 0.08em;
  }

  ::v-deep .app-tabs > .el-tabs__header .el-tabs__item {
    padding: 0 14px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .orb-a,
  .orb-b {
    animation: none;
  }

  * {
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
  }
}
</style>
