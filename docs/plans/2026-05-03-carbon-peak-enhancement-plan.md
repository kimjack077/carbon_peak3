# 碳达峰预测系统增强实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 完善碳达峰预测系统的功能、美化界面（科技未来风）、改进用户体验、提升代码质量。

**Architecture:** 前端采用 Vue 2 + Element UI + ECharts + Three.js，通过组件化拆分实现功能模块化；后端 Flask 提供 RESTful API，新增导出和数据校验端点。界面使用玻璃态设计、霓虹光效、3D粒子背景实现科技未来风格。

**Tech Stack:** Vue 2, Element UI, ECharts, Three.js, Flask, NumPy, Matplotlib, xlsx-js-style, jspdf

---

## Phase 1: 基础架构与主题升级

### Task 1: 创建主题样式文件

**Files:**
- Create: `frontend/src/assets/styles/theme.css`
- Create: `frontend/src/assets/styles/animations.css`
- Create: `frontend/src/assets/styles/glassmorphism.css`

**Step 1: 创建主题样式文件**

```css
/* frontend/src/assets/styles/theme.css */
:root {
  /* 科技未来风色彩系统 */
  --cp-bg-deep: #0a0f1a;
  --cp-bg-surface: rgba(15, 23, 42, 0.85);
  --cp-primary: #0f766e;
  --cp-primary-glow: rgba(15, 118, 110, 0.4);
  --cp-neon-blue: #3b82f6;
  --cp-neon-purple: #8b5cf6;
  --cp-neon-orange: #f59e0b;
  --cp-glass-bg: rgba(255, 255, 255, 0.08);
  --cp-glass-border: rgba(255, 255, 255, 0.15);
  --cp-text: #e2e8f0;
  --cp-text-muted: #94a3b8;
  --cp-shadow-glow: 0 0 30px rgba(15, 118, 110, 0.3);
}
```

**Step 2: 创建动画样式文件**

```css
/* frontend/src/assets/styles/animations.css */
@keyframes neon-pulse {
  0%, 100% { box-shadow: 0 0 5px var(--cp-primary-glow), 0 0 10px var(--cp-primary-glow); }
  50% { box-shadow: 0 0 10px var(--cp-primary-glow), 0 0 20px var(--cp-primary-glow), 0 0 30px var(--cp-primary-glow); }
}

@keyframes glow-border {
  0%, 100% { border-color: var(--cp-glass-border); }
  50% { border-color: var(--cp-primary); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.neon-glow {
  animation: neon-pulse 2s ease-in-out infinite;
}

.glow-border-active {
  animation: glow-border 1.5s ease-in-out infinite;
}
```

**Step 3: 创建玻璃态样式文件**

```css
/* frontend/src/assets/styles/glassmorphism.css */
.glass-card {
  background: var(--cp-glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--cp-glass-border);
  border-radius: 16px;
  box-shadow: var(--cp-shadow-glow);
  transition: all 0.3s ease;
}

.glass-card:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: var(--cp-primary);
  transform: translateY(-4px);
  box-shadow: 0 0 40px var(--cp-primary-glow);
}

.glass-header {
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.3), rgba(139, 92, 246, 0.2));
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--cp-glass-border);
}
```

**Step 4: 提交基础样式文件**

```bash
git add frontend/src/assets/styles/
git commit -m "feat(styles): add sci-fi theme styles with glassmorphism and neon effects"
```

---

### Task 2: 创建 API 封装模块

**Files:**
- Create: `frontend/src/utils/api.js`
- Create: `frontend/src/utils/helpers.js`

**Step 1: 创建 API 封装模块**

```javascript
// frontend/src/utils/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// 请求拦截器
api.interceptors.request.use(config => {
  return config
}, error => Promise.reject(error))

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.error || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

// API 方法
export const dataApi = {
  uploadCustom: (formData) => api.post('/upload/custom', formData),
  validate: (data) => api.post('/data/validate', data),
  loadExample: () => api.post('/upload/example'),
  getTrends: () => api.get('/data/trends')
}

export const scenarioApi = {
  list: () => api.get('/scenarios'),
  create: (data) => api.post('/scenarios', data),
  delete: (name) => api.delete(`/scenarios/${encodeURIComponent(name)}`),
  copy: (data) => api.post('/scenarios/copy', data),
  compare: (names) => api.post('/scenarios/compare', { scenarios: names })
}

export const predictApi = {
  run: (scenarios, years = 36) => api.post('/predict', { scenarios, forecast_years: years }),
  status: () => api.post('/predict/status'),
  results: (name) => api.get(`/results/${name}`),
  chartData: () => api.get('/chart-data')
}

export const exportApi = {
  excel: (name) => api.get(`/export/excel/${name}`, { responseType: 'blob' }),
  pdf: (name) => api.get(`/export/pdf/${name}`, { responseType: 'blob' }),
  csv: (name) => `/api/results/${name}/download`
}

export const recommendApi = {
  parameters: () => api.get('/recommend/parameters')
}

export default api
```

**Step 2: 创建辅助函数模块**

```javascript
// frontend/src/utils/helpers.js
export const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '-'
  return Number(value).toLocaleString('zh-CN', { maximumFractionDigits: decimals })
}

export const formatPercent = (value, decimals = 1) => {
  if (value === null || value === undefined) return '-'
  return `${(Number(value) * 100).toFixed(decimals)}%`
}

export const debounce = (fn, delay = 300) => {
  let timer = null
  return function(...args) {
    clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

export const downloadBlob = (blob, filename) => {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))
```

**Step 3: 提交 API 和辅助模块**

```bash
git add frontend/src/utils/
git commit -m "feat(utils): add API wrapper and helper functions"
```

---

### Task 3: 创建玻璃态卡片组件

**Files:**
- Create: `frontend/src/components/GlassmorphicCard.vue`

**Step 1: 创建玻璃态卡片组件**

```vue
<!-- frontend/src/components/GlassmorphicCard.vue -->
<template>
  <div class="glassmorphic-card" :class="{ 'glow-active': glowOnHover }">
    <div v-if="$slots.header" class="glass-card-header">
      <slot name="header"></slot>
    </div>
    <div class="glass-card-body">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="glass-card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GlassmorphicCard',
  props: {
    glowOnHover: { type: Boolean, default: true }
  }
}
</script>

<style scoped>
.glassmorphic-card {
  background: var(--cp-glass-bg, rgba(255, 255, 255, 0.08));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--cp-glass-border, rgba(255, 255, 255, 0.15));
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(15, 118, 110, 0.15);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.glassmorphic-card.glow-active:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: var(--cp-primary, #0f766e);
  transform: translateY(-6px);
  box-shadow: 0 0 40px rgba(15, 118, 110, 0.4), 0 20px 60px rgba(0, 0, 0, 0.3);
}

.glass-card-header {
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.25), rgba(139, 92, 246, 0.15));
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px 20px;
}

.glass-card-body {
  padding: 20px;
}

.glass-card-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px 20px;
  background: rgba(0, 0, 0, 0.2);
}
</style>
```

**Step 2: 提交玻璃态卡片组件**

```bash
git add frontend/src/components/GlassmorphicCard.vue
git commit -m "feat(components): add GlassmorphicCard component"
```

---

### Task 4: 创建帮助提示组件

**Files:**
- Create: `frontend/src/components/HelpTooltip.vue`

**Step 1: 创建帮助提示组件**

```vue
<!-- frontend/src/components/HelpTooltip.vue -->
<template>
  <el-tooltip
    :content="content"
    :placement="placement"
    effect="dark"
    :popper-class="popperClass"
  >
    <span class="help-icon">
      <i class="el-icon-question"></i>
    </span>
  </el-tooltip>
</template>

<script>
export default {
  name: 'HelpTooltip',
  props: {
    content: { type: String, required: true },
    placement: { type: String, default: 'top' },
    popperClass: { type: String, default: 'sci-fi-tooltip' }
  }
}
</script>

<style scoped>
.help-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.2);
  color: var(--cp-neon-blue, #3b82f6);
  cursor: help;
  transition: all 0.3s ease;
}

.help-icon:hover {
  background: rgba(59, 130, 246, 0.4);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}
</style>
```

**Step 2: 提交帮助提示组件**

```bash
git add frontend/src/components/HelpTooltip.vue
git commit -m "feat(components): add HelpTooltip component"
```

---

## Phase 2: 界面美化实施

### Task 5: 升级 App.vue 主布局

**Files:**
- Modify: `frontend/src/App.vue`

**Step 1: 导入新样式和 Three.js 背景**

在 `<style>` 部分顶部添加：
```css
@import url('./assets/styles/theme.css');
@import url('./assets/styles/animations.css');
@import url('./assets/styles/glassmorphism.css');
```

**Step 2: 更新根变量和背景**

替换现有 CSS 变量和背景样式，实现科技未来风：
```css
:root {
  --cp-bg-deep: #0a0f1a;
  --cp-bg-surface: rgba(15, 23, 42, 0.85);
  --cp-primary: #0f766e;
  --cp-primary-glow: rgba(15, 118, 110, 0.4);
  --cp-neon-blue: #3b82f6;
  --cp-neon-purple: #8b5cf6;
  --cp-neon-orange: #f59e0b;
}

#app {
  background: linear-gradient(135deg, #0a0f1a 0%, #1a1f3a 50%, #0f1a2a 100%);
}
```

**Step 3: 更新头部样式**

将 `.app-header` 改为玻璃态霓虹风格：
```css
.app-header {
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.4), rgba(139, 92, 246, 0.3));
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 30px rgba(15, 118, 110, 0.3);
}
```

**Step 4: 提交 App.vue 更新**

```bash
git add frontend/src/App.vue
git commit -m "feat(ui): upgrade App.vue to sci-fi theme with glassmorphism"
```

---

### Task 6: 创建 Three.js 粒子背景

**Files:**
- Create: `frontend/src/components/ParticleBackground.vue`

**Step 1: 创建粒子背景组件**

```vue
<!-- frontend/src/components/ParticleBackground.vue -->
<template>
  <div ref="container" class="particle-container"></div>
</template>

<script>
import * as THREE from 'three'

export default {
  name: 'ParticleBackground',
  data() {
    return {
      scene: null,
      camera: null,
      renderer: null,
      particles: null,
      animationId: null
    }
  },
  mounted() {
    this.initThree()
    this.animate()
  },
  beforeDestroy() {
    if (this.animationId) cancelAnimationFrame(this.animationId)
    if (this.renderer) this.renderer.dispose()
  },
  methods: {
    initThree() {
      const container = this.$refs.container
      const width = window.innerWidth
      const height = window.innerHeight

      this.scene = new THREE.Scene()
      this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
      this.camera.position.z = 50

      this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
      this.renderer.setSize(width, height)
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
      container.appendChild(this.renderer.domElement)

      // 创建粒子系统
      const particleCount = 800
      const geometry = new THREE.BufferGeometry()
      const positions = new Float32Array(particleCount * 3)
      const colors = new Float32Array(particleCount * 3)

      for (let i = 0; i < particleCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 100
        positions[i + 1] = (Math.random() - 0.5) * 100
        positions[i + 2] = (Math.random() - 0.5) * 50

        // 颜色：青色到紫色渐变
        const t = Math.random()
        colors[i] = 0.06 + t * 0.5      // R
        colors[i + 1] = 0.46 - t * 0.1  // G
        colors[i + 2] = 0.43 + t * 0.35 // B
      }

      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

      const material = new THREE.PointsMaterial({
        size: 0.8,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
      })

      this.particles = new THREE.Points(geometry, material)
      this.scene.add(this.particles)

      window.addEventListener('resize', this.handleResize)
    },
    animate() {
      this.animationId = requestAnimationFrame(this.animate)

      if (this.particles) {
        this.particles.rotation.x += 0.0003
        this.particles.rotation.y += 0.0005
      }

      this.renderer.render(this.scene, this.camera)
    },
    handleResize() {
      const width = window.innerWidth
      const height = window.innerHeight
      this.camera.aspect = width / height
      this.camera.updateProjectionMatrix()
      this.renderer.setSize(width, height)
    }
  }
}
</script>

<style scoped>
.particle-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}
</style>
```

**Step 2: 在 App.vue 中引入粒子背景**

在 `<template>` 的 `#app` div 内添加：
```vue
<particle-background></particle-background>
```

并导入组件：
```javascript
import ParticleBackground from './components/ParticleBackground.vue'
// 在 components 中添加
components: { ..., ParticleBackground }
```

**Step 3: 安装 Three.js 依赖**

```bash
cd frontend && npm install three --save
```

**Step 4: 提交粒子背景**

```bash
git add frontend/src/components/ParticleBackground.vue frontend/src/App.vue frontend/package.json
git commit -m "feat(ui): add Three.js particle background for sci-fi effect"
```

---

## Phase 3: 功能完善实施

### Task 7: 创建数据导入组件

**Files:**
- Create: `frontend/src/components/DataImport.vue`
- Modify: `frontend/src/components/DataUpload.vue`

**Step 1: 创建数据导入组件**

```vue
<!-- frontend/src/components/DataImport.vue -->
<template>
  <glassmorphic-card>
    <template #header>
      <div class="import-header">
        <h3>数据导入</h3>
        <help-tooltip content="支持CSV格式，需包含year、gdp、energy_consumption、co2_emission列" />
      </div>
    </template>

    <el-upload
      drag
      action="#"
      :auto-upload="false"
      :on-change="handleFileChange"
      accept=".csv"
      :limit="1"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">拖拽文件到此处，或<em>点击上传</em></div>
      <template #tip>
        <div class="el-upload__tip">仅支持 CSV 格式文件</div>
      </template>
    </el-upload>

    <div v-if="validationResult" class="validation-result">
      <el-alert
        :type="validationResult.valid ? 'success' : 'error'"
        :title="validationResult.message"
        show-icon
      />
      <div v-if="validationResult.details" class="validation-details">
        <p v-for="detail in validationResult.details" :key="detail">{{ detail }}</p>
      </div>
    </div>

    <template #footer>
      <el-button type="primary" :disabled="!canUpload" @click="uploadData">
        确认导入
      </el-button>
    </template>
  </glassmorphic-card>
</template>

<script>
import { dataApi } from '@/utils/api'
import GlassmorphicCard from './GlassmorphicCard.vue'
import HelpTooltip from './HelpTooltip.vue'

export default {
  name: 'DataImport',
  components: { GlassmorphicCard, HelpTooltip },
  data() {
    return {
      file: null,
      validationResult: null
    }
  },
  computed: {
    canUpload() {
      return this.file && this.validationResult?.valid
    }
  },
  methods: {
    handleFileChange(file) {
      this.file = file.raw
      this.validateFile()
    },
    async validateFile() {
      if (!this.file) return

      const reader = new FileReader()
      reader.onload = async (e) => {
        try {
          const text = e.target.result
          const lines = text.split('\n')
          const headers = lines[0].split(',').map(h => h.trim().toLowerCase())

          const requiredCols = ['year', 'gdp', 'energy_consumption', 'co2_emission']
          const missing = requiredCols.filter(col => !headers.includes(col))

          if (missing.length > 0) {
            this.validationResult = {
              valid: false,
              message: '数据列不完整',
              details: [`缺少必需列: ${missing.join(', ')}`]
            }
          } else {
            this.validationResult = {
              valid: true,
              message: '数据格式正确',
              details: [`包含 ${lines.length - 1} 条数据记录`]
            }
          }
        } catch (err) {
          this.validationResult = { valid: false, message: '文件解析失败' }
        }
      }
      reader.readAsText(this.file)
    },
    async uploadData() {
      const formData = new FormData()
      formData.append('file', this.file)

      try {
        await dataApi.uploadCustom(formData)
        this.$message.success('数据导入成功')
        this.$emit('data-imported', true)
      } catch (err) {
        this.$message.error(err.message || '导入失败')
      }
    }
  }
}
</script>

<style scoped>
.import-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.import-header h3 {
  margin: 0;
  color: #e2e8f0;
}
.validation-result {
  margin-top: 16px;
}
.validation-details {
  margin-top: 8px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}
</style>
```

**Step 2: 更新 DataUpload.vue 引入导入组件**

在 DataUpload.vue 中添加导入功能区域。

**Step 3: 提交数据导入组件**

```bash
git add frontend/src/components/DataImport.vue frontend/src/components/DataUpload.vue
git commit -m "feat(data): add DataImport component with validation"
```

---

### Task 8: 创建参数推荐组件

**Files:**
- Create: `frontend/src/components/ParameterRecommend.vue`

**Step 1: 创建参数推荐组件**

```vue
<!-- frontend/src/components/ParameterRecommend.vue -->
<template>
  <glassmorphic-card class="param-recommend">
    <template #header>
      <div class="recommend-header">
        <h3>智能参数推荐</h3>
        <el-tag type="success" size="small" effect="dark">AI 推荐</el-tag>
      </div>
    </template>

    <div v-if="loading" class="loading-state">
      <i class="el-icon-loading"></i>
      <p>正在分析历史数据趋势...</p>
    </div>

    <div v-else-if="recommendations" class="recommend-content">
      <div class="recommend-item">
        <span class="param-label">推荐 GDP 增长率</span>
        <el-slider
          v-model="recommendations.gdp_growth_rate"
          :min="0" :max="0.15" :step="0.005"
          :format-tooltip="formatPercent"
          show-input
        />
        <span class="reason">{{ recommendations.gdp_reason }}</span>
      </div>

      <div class="recommend-item">
        <span class="param-label">推荐效率提升率</span>
        <el-slider
          v-model="recommendations.efficiency_improvement_rate"
          :min="0" :max="0.10" :step="0.005"
          :format-tooltip="formatPercent"
          show-input
        />
        <span class="reason">{{ recommendations.efficiency_reason }}</span>
      </div>

      <div class="sensitivity-chart">
        <h4>参数敏感度分析</h4>
        <div ref="sensitivityChart" class="chart-area"></div>
      </div>
    </div>

    <template #footer>
      <el-button type="primary" @click="applyRecommendations">
        应用推荐参数
      </el-button>
      <el-button @click="refreshRecommendations">
        重新分析
      </el-button>
    </template>
  </glassmorphic-card>
</template>

<script>
import { recommendApi } from '@/utils/api'
import { formatPercent } from '@/utils/helpers'
import GlassmorphicCard from './GlassmorphicCard.vue'
import * as echarts from 'echarts'

export default {
  name: 'ParameterRecommend',
  components: { GlassmorphicCard },
  data() {
    return {
      loading: false,
      recommendations: null,
      sensitivityChart: null
    }
  },
  mounted() {
    this.loadRecommendations()
  },
  beforeDestroy() {
    if (this.sensitivityChart) this.sensitivityChart.dispose()
  },
  methods: {
    formatPercent,
    async loadRecommendations() {
      this.loading = true
      try {
        const data = await recommendApi.parameters()
        this.recommendations = data
        this.$nextTick(() => this.initSensitivityChart())
      } catch (err) {
        this.$message.error('获取推荐失败')
      } finally {
        this.loading = false
      }
    },
    initSensitivityChart() {
      const dom = this.$refs.sensitivityChart
      if (!dom || !this.recommendations?.sensitivity) return

      this.sensitivityChart = echarts.init(dom)
      this.sensitivityChart.setOption({
        tooltip: { trigger: 'axis' },
        radar: {
          indicator: [
            { name: 'GDP增长率', max: 0.15 },
            { name: '效率提升', max: 0.10 },
            { name: '可再生提升', max: 0.05 },
            { name: '煤炭下降', max: 0.05 }
          ]
        },
        series: [{
          type: 'radar',
          data: [
            {
              value: [
                this.recommendations.gdp_growth_rate,
                this.recommendations.efficiency_improvement_rate,
                this.recommendations.renewable_increase_rate,
                this.recommendations.coal_decrease_rate
              ],
              name: '推荐参数',
              areaStyle: { color: 'rgba(15, 118, 110, 0.3)' }
            }
          ]
        }]
      })
    },
    applyRecommendations() {
      this.$emit('apply', this.recommendations)
      this.$message.success('已应用推荐参数')
    },
    refreshRecommendations() {
      this.loadRecommendations()
    }
  }
}
</script>

<style scoped>
.recommend-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.recommend-header h3 { margin: 0; color: #e2e8f0; }
.recommend-item {
  margin-bottom: 16px;
}
.param-label {
  display: block;
  color: #94a3b8;
  margin-bottom: 8px;
}
.reason {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}
.chart-area {
  height: 200px;
  margin-top: 16px;
}
</style>
```

**Step 2: 提交参数推荐组件**

```bash
git add frontend/src/components/ParameterRecommend.vue
git commit -m "feat(ai): add ParameterRecommend component with sensitivity analysis"
```

---

### Task 9: 创建情景对比组件

**Files:**
- Create: `frontend/src/components/ScenarioCompare.vue`

**Step 1: 创建情景对比组件**

```vue
<!-- frontend/src/components/ScenarioCompare.vue -->
<template>
  <div class="scenario-compare">
    <glassmorphic-card>
      <template #header>
        <div class="compare-header">
          <h3>情景对比分析</h3>
          <el-checkbox-group v-model="selectedScenarios" size="small">
            <el-checkbox-button
              v-for="s in allScenarios"
              :key="s"
              :label="s"
            >{{ s }}</el-checkbox-button>
          </el-checkbox-group>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="8">
          <div ref="peakCompareChart" class="compare-chart"></div>
        </el-col>
        <el-col :span="8">
          <div ref="pathCompareChart" class="compare-chart"></div>
        </el-col>
        <el-col :span="8">
          <div ref="indicatorRadar" class="compare-chart"></div>
        </el-col>
      </el-row>

      <div v-if="comparisonReport" class="comparison-report">
        <h4>对比结论</h4>
        <p>{{ comparisonReport.summary }}</p>
        <el-table :data="comparisonReport.details" border stripe>
          <el-table-column prop="scenario" label="情景" />
          <el-table-column prop="peak_year" label="达峰年份" />
          <el-table-column prop="peak_value" label="峰值排放" />
          <el-table-column prop="reduction_rate" label="减排幅度" />
        </el-table>
      </div>
    </glassmorphic-card>
  </div>
</template>

<script>
import { scenarioApi } from '@/utils/api'
import GlassmorphicCard from './GlassmorphicCard.vue'
import * as echarts from 'echarts'

export default {
  name: 'ScenarioCompare',
  components: { GlassmorphicCard },
  data() {
    return {
      allScenarios: [],
      selectedScenarios: [],
      comparisonData: null,
      comparisonReport: null,
      peakCompareChart: null,
      pathCompareChart: null,
      indicatorRadar: null
    }
  },
  mounted() {
    this.loadScenarios()
  },
  beforeDestroy() {
    [this.peakCompareChart, this.pathCompareChart, this.indicatorRadar].forEach(c => {
      if (c) c.dispose()
    })
  },
  watch: {
    selectedScenarios(newVal) {
      if (newVal.length >= 2) {
        this.runComparison()
      }
    }
  },
  methods: {
    async loadScenarios() {
      try {
        const data = await scenarioApi.list()
        this.allScenarios = Object.keys(data)
      } catch (err) {
        this.$message.error('获取情景列表失败')
      }
    },
    async runComparison() {
      try {
        this.comparisonData = await scenarioApi.compare(this.selectedScenarios)
        this.comparisonReport = this.comparisonData.report
        this.$nextTick(() => this.initCharts())
      } catch (err) {
        this.$message.error('对比分析失败')
      }
    },
    initCharts() {
      this.initPeakCompareChart()
      this.initPathCompareChart()
      this.initIndicatorRadar()
    },
    initPeakCompareChart() {
      const dom = this.$refs.peakCompareChart
      if (!dom || !this.comparisonData) return

      this.peakCompareChart = echarts.init(dom)
      this.peakCompareChart.setOption({
        title: { text: '峰值年份对比', left: 'center', textStyle: { color: '#e2e8f0' } },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: this.selectedScenarios },
        yAxis: { type: 'value', name: '年份' },
        series: [{
          type: 'bar',
          data: this.comparisonData.peak_years,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#0f766e' },
              { offset: 1, color: '#14b8a6' }
            ])
          }
        }]
      })
    },
    initPathCompareChart() {
      const dom = this.$refs.pathCompareChart
      if (!dom || !this.comparisonData) return

      this.pathCompareChart = echarts.init(dom)
      this.pathCompareChart.setOption({
        title: { text: '减排路径对比', left: 'center', textStyle: { color: '#e2e8f0' } },
        tooltip: { trigger: 'axis' },
        legend: { top: 30, textStyle: { color: '#94a3b8' } },
        xAxis: { type: 'category', data: this.comparisonData.years },
        yAxis: { type: 'value', name: '排放量' },
        series: this.comparisonData.paths.map((path, i) => ({
          name: this.selectedScenarios[i],
          type: 'line',
          data: path,
          smooth: true,
          lineStyle: { width: 3 }
        }))
      })
    },
    initIndicatorRadar() {
      const dom = this.$refs.indicatorRadar
      if (!dom || !this.comparisonData) return

      this.indicatorRadar = echarts.init(dom)
      this.indicatorRadar.setOption({
        title: { text: '关键指标雷达', left: 'center', textStyle: { color: '#e2e8f0' } },
        tooltip: {},
        legend: { bottom: 0, textStyle: { color: '#94a3b8' } },
        radar: {
          indicator: [
            { name: '达峰速度', max: 100 },
            { name: '减排效果', max: 100 },
            { name: '经济影响', max: 100 },
            { name: '可行性', max: 100 }
          ],
          axisName: { color: '#94a3b8' }
        },
        series: [{
          type: 'radar',
          data: this.comparisonData.indicators.map((ind, i) => ({
            name: this.selectedScenarios[i],
            value: ind,
            areaStyle: { opacity: 0.3 }
          }))
        }]
      })
    }
  }
}
</script>

<style scoped>
.compare-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.compare-header h3 { margin: 0; color: #e2e8f0; }
.compare-chart {
  height: 280px;
}
.comparison-report {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
.comparison-report h4 {
  color: #e2e8f0;
  margin-bottom: 12px;
}
.comparison-report p {
  color: #94a3b8;
  margin-bottom: 16px;
}
</style>
```

**Step 2: 提交情景对比组件**

```bash
git add frontend/src/components/ScenarioCompare.vue
git commit -m "feat(compare): add ScenarioCompare component with multi-chart comparison"
```

---

### Task 10: 创建导出工具模块

**Files:**
- Create: `frontend/src/utils/export.js`

**Step 1: 安装导出依赖**

```bash
cd frontend && npm install xlsx-js-style jspdf --save
```

**Step 2: 创建导出工具模块**

```javascript
// frontend/src/utils/export.js
import XLSX from 'xlsx-js-style'
import jsPDF from 'jspdf'
import { formatNumber } from './helpers'

export const exportToExcel = (data, scenarioName) => {
  const ws = XLSX.utils.json_to_sheet(data.map(row => ({
    '年份': row.year,
    '类型': row.data_type === 'historical' ? '历史' : '预测',
    'GDP(万元)': row.gdp,
    '能源消费(万吨标煤)': row.energy_consumption,
    'CO2排放(万吨)': row.co2_emission
  })))

  // 设置样式
  const range = XLSX.utils.decode_range(ws['!ref'])
  for (let R = range.s.r; R <= range.e.r; ++R) {
    for (let C = range.s.c; C <= range.e.c; ++C) {
      const cell = ws[XLSX.utils.encode_cell({ r: R, c: C })]
      if (!cell) continue

      cell.s = {
        fill: R === 0 ? { fgColor: { rgb: '0F766E' } } : undefined,
        font: {
          bold: R === 0,
          color: R === 0 ? { rgb: 'FFFFFF' } : { rgb: '000000' }
        },
        alignment: { horizontal: 'center', vertical: 'center' },
        border: {
          top: { style: 'thin', color: { rgb: 'CCCCCC' } },
          bottom: { style: 'thin', color: { rgb: 'CCCCCC' } },
          left: { style: 'thin', color: { rgb: 'CCCCCC' } },
          right: { style: 'thin', color: { rgb: 'CCCCCC' } }
        }
      }
    }
  }

  ws['!cols'] = [
    { wch: 8 }, { wch: 8 }, { wch: 14 }, { wch: 18 }, { wch: 14 }
  ]

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '预测数据')
  XLSX.writeFile(wb, `${scenarioName}_预测结果.xlsx`)
}

export const exportToPDF = async (chartImage, scenarioName, summary) => {
  const pdf = new jsPDF('p', 'mm', 'a4')
  const pageWidth = pdf.internal.pageSize.getWidth()

  // 标题
  pdf.setFontSize(18)
  pdf.setTextColor(15, 118, 110)
  pdf.text(`${scenarioName} - 碳达峰预测报告`, pageWidth / 2, 20, { align: 'center' })

  // 图表
  if (chartImage) {
    const imgData = chartImage
    const imgWidth = pageWidth - 20
    const imgHeight = 80
    pdf.addImage(imgData, 'PNG', 10, 35, imgWidth, imgHeight)
  }

  // 分析摘要
  pdf.setFontSize(12)
  pdf.setTextColor(50, 50, 50)
  pdf.text('分析摘要:', 10, 130)
  pdf.setFontSize(10)
  pdf.text(summary, 15, 140, { maxWidth: pageWidth - 30 })

  // 日期
  pdf.setFontSize(10)
  pdf.setTextColor(100, 100, 100)
  const date = new Date().toLocaleDateString('zh-CN')
  pdf.text(`生成日期: ${date}`, pageWidth / 2, 280, { align: 'center' })

  pdf.save(`${scenarioName}_预测报告.pdf`)
}

export const downloadBlob = (blob, filename) => {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
```

**Step 3: 提交导出工具**

```bash
git add frontend/src/utils/export.js frontend/package.json
git commit -m "feat(export): add Excel and PDF export utilities"
```

---

## Phase 4: 后端 API 增强

### Task 11: 添加后端导出 API

**Files:**
- Modify: `backend/app.py`
- Create: `backend/utils/export_utils.py`

**Step 1: 创建导出工具模块**

```python
# backend/utils/export_utils.py
import io
import pandas as pd
from datetime import datetime

def generate_excel_report(data, scenario_name):
    """生成Excel格式的预测报告"""
    df = pd.DataFrame(data)

    # 重命名列
    df = df.rename(columns={
        'year': '年份',
        'data_type': '类型',
        'gdp': 'GDP(万元)',
        'energy_consumption': '能源消费(万吨标煤)',
        'co2_emission': 'CO2排放(万吨)'
    })

    # 类型转换
    df['类型'] = df['类型'].apply(lambda x: '历史' if x == 'historical' else '预测')

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='预测数据', index=False)

        # 获取工作表并设置格式
        workbook = writer.book
        worksheet = writer.sheets['预测数据']

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#0F766E',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

    output.seek(0)
    return output.getvalue()

def generate_summary_text(results, peak_info):
    """生成分析摘要文本"""
    peak_year = peak_info.get('year', '未知')
    peak_value = peak_info.get('value', 0)

    summary = f"""
    根据预测结果分析：

    1. 碳排放预计在 {peak_year} 年达到峰值，峰值排放量约为 {peak_value:.2f} 万吨CO2。

    2. 从历史趋势来看，碳排放呈现先上升后下降的典型达峰路径特征。

    3. 建议重点关注能源结构优化和效率提升，以实现更早的达峰目标。

    报告生成时间: {datetime.now().strftime('%Y年%m月%d日')}
    """
    return summary.strip()
```

**Step 2: 在 app.py 添加导出端点**

```python
# backend/app.py 末尾添加

from utils.export_utils import generate_excel_report, generate_summary_text

@app.route('/api/export/excel/<name>', methods=['GET'])
def export_excel(name):
    """导出Excel格式预测结果"""
    try:
        results = get_scenario_results(name)
        excel_data = generate_excel_report(results, name)

        response = make_response(excel_data)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename={name}_预测结果.xlsx'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/pdf/<name>', methods=['GET'])
def export_pdf(name):
    """导出PDF格式预测报告"""
    try:
        results = get_scenario_results(name)
        # 这里需要配合前端图表生成
        summary = generate_summary_text(results, {})

        # 简化版：返回JSON让前端生成PDF
        return jsonify({
            'summary': summary,
            'scenario': name,
            'data': results[:10]  # 前10条数据
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommend/parameters', methods=['GET'])
def recommend_parameters():
    """智能参数推荐"""
    try:
        # 基于历史数据趋势的简单推荐
        historical_data = load_current_data()

        if historical_data and len(historical_data) >= 4:
            years = [d['year'] for d in historical_data]
            gdps = [d['gdp'] for d in historical_data]
            energies = [d['energy_consumption'] for d in historical_data]

            # 计算GDP平均增长率
            gdp_growth = sum((gdps[i+1]/gdps[i] - 1) for i in range(len(gdps)-1)) / (len(gdps)-1)

            # 计算效率改善率
            intensities = [e/g for e, g in zip(energies, gdps)]
            efficiency_improve = sum((intensities[i] - intensities[i+1])/intensities[i]
                                    for i in range(len(intensities)-1)) / (len(intensities)-1)

            recommendations = {
                'gdp_growth_rate': round(gdp_growth * 0.9, 4),  # 稍保守一点
                'efficiency_improvement_rate': round(max(efficiency_improve, 0.02), 4),
                'renewable_increase_rate': 0.015,
                'coal_decrease_rate': 0.02,
                'gdp_reason': f'基于历史{len(years)}年数据趋势，建议采用略保守的增长率',
                'efficiency_reason': f'历史能效改善趋势良好，建议维持或加强',
                'sensitivity': [gdp_growth, efficiency_improve, 0.015, 0.02]
            }
        else:
            recommendations = {
                'gdp_growth_rate': 0.05,
                'efficiency_improvement_rate': 0.03,
                'renewable_increase_rate': 0.01,
                'coal_decrease_rate': 0.02,
                'gdp_reason': '数据不足，采用默认推荐值',
                'efficiency_reason': '数据不足，采用默认推荐值',
                'sensitivity': [0.05, 0.03, 0.01, 0.02]
            }

        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenarios/compare', methods=['POST'])
def compare_scenarios():
    """情景对比分析"""
    try:
        data = request.get_json()
        scenario_names = data.get('scenarios', [])

        if len(scenario_names) < 2:
            return jsonify({'error': '至少需要选择2个情景进行对比'}), 400

        comparison_data = {
            'peak_years': [],
            'paths': [],
            'indicators': [],
            'years': [],
            'report': {
                'summary': f'对比分析了 {len(scenario_names)} 个情景的碳排放路径差异',
                'details': []
            }
        }

        all_years = set()

        for name in scenario_names:
            results = get_scenario_results(name)
            if not results:
                continue

            # 找峰值年份
            emissions = [r['co2_emission'] for r in results if r['data_type'] == 'prediction']
            if emissions:
                peak_idx = emissions.index(max(emissions))
                peak_year = results[peak_idx]['year']
                peak_value = emissions[peak_idx]

                comparison_data['peak_years'].append(peak_year)
                comparison_data['paths'].append(emissions)
                comparison_data['report']['details'].append({
                    'scenario': name,
                    'peak_year': peak_year,
                    'peak_value': f'{peak_value:.2f}',
                    'reduction_rate': f'{((emissions[0] - emissions[-1])/emissions[0]*100):.1f}%'
                })

                # 关键指标评分（简化版）
                comparison_data['indicators'].append([
                    100 - peak_year + 2020,  # 达峰速度
                    80,  # 减排效果（简化）
                    70,  # 经济影响（简化）
                    75   # 可行性（简化）
                ])

            for r in results:
                all_years.add(r['year'])

        comparison_data['years'] = sorted(list(all_years))

        return jsonify(comparison_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenarios/copy', methods=['POST'])
def copy_scenario():
    """复制情景"""
    try:
        data = request.get_json()
        source_name = data.get('source')
        new_name = data.get('name')

        if not source_name or not new_name:
            return jsonify({'error': '需要提供源情景名和新情景名'}), 400

        scenarios = load_scenarios()
        if source_name not in scenarios:
            return jsonify({'error': '源情景不存在'}), 404

        scenarios[new_name] = {**scenarios[source_name]}
        save_scenarios(scenarios)

        return jsonify({'success': True, 'name': new_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Step 3: 提交后端 API 更新**

```bash
git add backend/app.py backend/utils/export_utils.py
git commit -m "feat(api): add export, recommend, and compare API endpoints"
```

---

## Phase 5: 图表工具栏与交互

### Task 12: 创建图表工具栏组件

**Files:**
- Create: `frontend/src/components/ChartToolbar.vue`

**Step 1: 创建图表工具栏组件**

```vue
<!-- frontend/src/components/ChartToolbar.vue -->
<template>
  <div class="chart-toolbar">
    <el-tooltip content="重置缩放" placement="top">
      <el-button size="mini" icon="el-icon-refresh" @click="$emit('reset')" circle />
    </el-tooltip>
    <el-tooltip content="下载图表" placement="top">
      <el-button size="mini" icon="el-icon-download" @click="$emit('download')" circle />
    </el-tooltip>
    <el-tooltip content="全屏查看" placement="top">
      <el-button size="mini" icon="el-icon-full-screen" @click="toggleFullscreen" circle />
    </el-tooltip>
    <el-tooltip content="数据表格" placement="top">
      <el-button size="mini" icon="el-icon-s-data" @click="$emit('toggle-table')" circle />
    </el-tooltip>
  </div>
</template>

<script>
export default {
  name: 'ChartToolbar',
  methods: {
    toggleFullscreen() {
      const chartContainer = this.$parent.$el.querySelector('.echarts-container')
      if (!document.fullscreenElement) {
        chartContainer?.requestFullscreen()
      } else {
        document.exitFullscreen()
      }
    }
  }
}
</script>

<style scoped>
.chart-toolbar {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  z-index: 10;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.chart-toolbar:hover {
  opacity: 1;
}

.chart-toolbar .el-button {
  background: rgba(15, 118, 110, 0.2);
  border: 1px solid rgba(15, 118, 110, 0.4);
  color: #14b8a6;
}

.chart-toolbar .el-button:hover {
  background: rgba(15, 118, 110, 0.4);
  box-shadow: 0 0 10px rgba(15, 118, 110, 0.5);
}
</style>
```

**Step 2: 在 PredictionResults.vue 集成工具栏**

在图表容器添加工具栏组件。

**Step 3: 提交图表工具栏**

```bash
git add frontend/src/components/ChartToolbar.vue frontend/src/components/PredictionResults.vue
git commit -m "feat(charts): add ChartToolbar component with zoom, download, fullscreen"
```

---

### Task 13: 更新 ScenarioManager 集成推荐功能

**Files:**
- Modify: `frontend/src/components/ScenarioManager.vue`

**Step 1: 引入参数推荐组件**

```vue
<!-- 在 ScenarioManager.vue template 顶部添加 -->
<parameter-recommend @apply="applyRecommendedParams" />
```

```javascript
// 在 components 添加
import ParameterRecommend from './ParameterRecommend.vue'
components: { ..., ParameterRecommend }

// 在 methods 添加
methods: {
  applyRecommendedParams(params) {
    this.scenarioForm = {
      ...this.scenarioForm,
      gdp_growth_rate: params.gdp_growth_rate,
      efficiency_improvement_rate: params.efficiency_improvement_rate,
      renewable_increase_rate: params.renewable_increase_rate,
      coal_decrease_rate: params.coal_decrease_rate
    }
  }
}
```

**Step 2: 提交集成**

```bash
git add frontend/src/components/ScenarioManager.vue
git commit -m "feat(scenario): integrate ParameterRecommend into ScenarioManager"
```

---

## Phase 6: 新标签页集成

### Task 14: 添加情景对比标签页

**Files:**
- Modify: `frontend/src/App.vue`

**Step 1: 添加新标签页**

```vue
<!-- 在 el-tabs 中添加新 tab-pane -->
<el-tab-pane label="情景对比" name="compare" :disabled="!dataLoaded">
  <scenario-compare></scenario-compare>
</el-tab-pane>
```

```javascript
// 导入组件
import ScenarioCompare from './components/ScenarioCompare.vue'
components: { ..., ScenarioCompare }
```

**Step 2: 提交标签页集成**

```bash
git add frontend/src/App.vue
git commit -m "feat(tabs): add scenario comparison tab to main navigation"
```

---

## Phase 7: 最终集成与测试

### Task 15: 验证前端功能

**Files:**
- All frontend files

**Step 1: 运行前端开发服务器**

```bash
cd frontend && npm run serve
```

验证：
- 页面正常加载
- 科技未来风界面显示正确
- 粒子背景动画运行
- 所有标签页可切换
- 数据导入功能正常
- 参数推荐可应用
- 情景对比可运行
- 图表工具栏可用

**Step 2: 验证后端 API**

```bash
cd backend && python app.py
```

验证：
- `/api/upload/example` 正常
- `/api/recommend/parameters` 返回数据
- `/api/scenarios/compare` 正常
- `/api/export/excel` 导出正常

**Step 3: 提交最终集成**

```bash
git add -A
git commit -m "feat: complete sci-fi themed UI with all enhancements"
```

---

## 执行顺序总结

| Phase | Tasks | 内容 |
|-------|-------|------|
| 1 | 1-4 | 基础架构与主题升级 |
| 2 | 5-6 | 界面美化（App.vue + Three.js背景） |
| 3 | 7-10 | 功能完善（数据导入、参数推荐、情景对比、导出） |
| 4 | 11 | 后端 API 增强 |
| 5 | 12-13 | 图表交互集成 |
| 6 | 14 | 标签页集成 |
| 7 | 15 | 最终测试与验证 |

---

## 验收标准

1. 所有新功能正常工作
2. 科技未来风界面效果达标
3. 粒子背景流畅运行
4. 情景对比分析正确
5. 导出功能可用（CSV/Excel/PDF）
6. 参数推荐功能可用
7. 图表交互增强可用
8. 无明显性能问题
9. 响应式布局正常