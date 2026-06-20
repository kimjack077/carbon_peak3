<template>
  <div class="prediction-results">
    <!-- 顶部指标卡片 -->
    <div class="metrics-bar" v-if="metricCardsData.length > 0">
      <div class="metric-item" v-for="(metric, idx) in metricCardsData" :key="idx">
        <div class="metric-icon">
          <svg v-if="idx === 0" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          <svg v-else-if="idx === 1" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          <svg v-else-if="idx === 2" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div class="metric-info">
          <div class="metric-value">{{ metric.value }}</div>
          <div class="metric-label">{{ metric.label }}</div>
        </div>
      </div>
    </div>

    <!-- 主图表：碳排放达峰预测 -->
    <div class="chart-section main-chart">
      <div class="section-header">
        <div class="section-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          <span>碳排放达峰预测</span>
        </div>
        <div class="peak-tags" v-if="peakSummaries.length > 0">
          <span
            v-for="summary in peakSummaries"
            :key="summary.name"
            :class="['peak-badge', summary.type]"
          >
            {{ summary.name }}: {{ summary.year }}年达峰
          </span>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <span>正在加载预测数据...</span>
      </div>
      <div v-else-if="error" class="error-state">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <p>{{ error }}</p>
        <el-button type="primary" size="small" @click="runAutoPrediction">重新运行预测</el-button>
      </div>
      <div v-else class="chart-wrapper">
        <div id="carbon-peak-chart" class="echarts-container"></div>
      </div>
    </div>

    <!-- 次级图表 -->
    <div class="chart-row">
      <div class="chart-section">
        <div class="section-header">
          <div class="section-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            <span>GDP预测</span>
          </div>
        </div>
        <div class="chart-wrapper">
          <div id="gdp-chart" class="echarts-container small"></div>
        </div>
      </div>

      <div class="chart-section">
        <div class="section-header">
          <div class="section-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            <span>能源消费结构</span>
          </div>
          <div class="chart-toggle">
            <button
              :class="['toggle-btn', { active: energyChartType === 'stack' }]"
              @click="energyChartType = 'stack'"
            >堆叠柱状图</button>
            <button
              :class="['toggle-btn', { active: energyChartType === 'line' }]"
              @click="energyChartType = 'line'"
            >趋势图</button>
          </div>
        </div>
        <div class="chart-wrapper">
          <div id="energy-chart" class="echarts-container small"></div>
        </div>
      </div>
    </div>

    <!-- 数据详情 -->
    <div class="chart-section data-section">
      <div class="section-header">
        <div class="section-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          <span>预测数据详情</span>
        </div>
        <el-select v-model="selectedScenario" placeholder="选择情景" size="small" @change="loadScenarioResults" class="scenario-select">
          <el-option v-for="scenario in scenarios" :key="scenario" :label="scenario" :value="scenario"></el-option>
        </el-select>
      </div>

      <el-table v-if="scenarioResults.length > 0" :data="scenarioResults" style="width: 100%" height="360" border stripe>
        <el-table-column prop="year" label="年份" width="80" fixed="left" align="center"></el-table-column>
        <el-table-column prop="data_type" label="类型" width="80" align="center">
          <template slot-scope="scope">
            <el-tag :type="scope.row.data_type === 'historical' ? 'info' : 'success'" size="mini">
              {{ scope.row.data_type === 'historical' ? '历史' : '预测' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="gdp" label="GDP(万元)" min-width="140" align="right">
          <template slot-scope="scope">{{ formatNumber(scope.row.gdp) }}</template>
        </el-table-column>
        <el-table-column prop="energy_consumption" label="能源消费(万吨标煤)" min-width="150" align="right">
          <template slot-scope="scope">{{ formatNumber(scope.row.energy_consumption) }}</template>
        </el-table-column>
        <el-table-column prop="co2_emission" label="CO₂排放(万吨)" min-width="130" align="right">
          <template slot-scope="scope">{{ formatNumber(scope.row.co2_emission) }}</template>
        </el-table-column>
      </el-table>
      <div v-else class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <p>暂无预测数据，请先运行预测</p>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="actions-bar">
      <el-button type="primary" icon="el-icon-download" @click="downloadResults">下载预测结果</el-button>
      <el-button type="success" icon="el-icon-picture" @click="saveCharts">导出图表</el-button>
      <el-button icon="el-icon-back" @click="goToScenarios">返回情景设置</el-button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'
import { themeStore } from '@/store/themeStore'

const COLORS = {
  coal: '#6B7280',
  renewable: '#10B981',
  other: '#F59E0B'
}

function hasArray(data, key) {
  return data && Array.isArray(data[key]) && data[key].length > 0
}

export default {
  name: 'PredictionResults',
  props: {
    isActive: {
      type: Boolean,
      default: false
    }
  },
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

      const firstPeak = this.peakSummaries[0]
      if (firstPeak) {
        metrics.push({
          label: '预测达峰年份',
          value: firstPeak.year + '年'
        })
      }

      const firstScenario = this.chartData[scenarioKeys[0]]
      const peakEmissionRaw = (firstScenario && firstScenario.peak && (firstScenario.peak.emission || firstScenario.peak.value)) || 0
      if (firstScenario && firstScenario.peak && peakEmissionRaw > 0) {
        metrics.push({
          label: '排放峰值',
          value: Math.round(peakEmissionRaw).toLocaleString() + '万吨'
        })
      }

      if (firstScenario && firstScenario.emissions && peakEmissionRaw > 0) {
        const peakEmission = peakEmissionRaw
        const lastEmission = firstScenario.emissions[firstScenario.emissions.length - 1] || 0
        const reduction = ((peakEmission - lastEmission) / peakEmission * 100).toFixed(1)
        metrics.push({
          label: '减排幅度',
          value: reduction + '%'
        })
      }

      metrics.push({
        label: '预测情景',
        value: scenarioKeys.length + '个'
      })

      return metrics
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      chartData: {},
      carbonPeakChart: null,
      gdpChart: null,
      energyChart: null,
      scenarios: [],
      selectedScenario: '',
      scenarioResults: [],
      energyChartType: 'stack',
      peakSummaries: []
    }
  },
  watch: {
    energyChartType() {
      this.initEnergyChart()
    },
    isActive(active) {
      if (active) {
        this.checkPredictionStatus()
        this.$nextTick(() => {
          setTimeout(() => this.handleResize(), 300)
        })
      }
    },
    isDark() {
      this.$nextTick(() => {
        setTimeout(() => {
          this.initCarbonPeakChart()
          this.initGdpChart()
          this.initEnergyChart()
        }, 300)
      })
    }
  },
  created() {
    this.checkPredictionStatus()
  },
  mounted() {
    window.addEventListener('resize', this.handleResize)
    if (this.isActive) {
      setTimeout(() => this.handleResize(), 120)
    }
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    ;[this.carbonPeakChart, this.gdpChart, this.energyChart].forEach(c => {
      if (c) c.dispose()
    })
  },
  methods: {
    normalizeYear(value) {
      const num = Number(value)
      return Number.isFinite(num) ? num : null
    },
    collectYearLabels(keys, includeHistorical = true) {
      const years = new Set()
      keys.forEach(name => {
        const item = this.chartData[name]
        if (!item) return
        if (includeHistorical && Array.isArray(item.historical_years)) {
          item.historical_years.forEach(y => {
            const year = this.normalizeYear(y)
            if (year !== null) years.add(year)
          })
        }
        if (Array.isArray(item.years)) {
          item.years.forEach(y => {
            const year = this.normalizeYear(y)
            if (year !== null) years.add(year)
          })
        }
      })
      return Array.from(years).sort((a, b) => a - b)
    },
    buildAlignedSeries(labels, years, values) {
      const valueMap = new Map()
      ;(years || []).forEach((year, index) => {
        const key = this.normalizeYear(year)
        if (key !== null) {
          const val = values && values[index] !== undefined ? Number(values[index]) : null
          valueMap.set(key, Number.isFinite(val) ? val : null)
        }
      })
      return labels.map(label => (valueMap.has(label) ? valueMap.get(label) : null))
    },
    checkPredictionStatus() {
      this.loading = true
      this.error = null
      axios.post('/api/predict/status')
        .then(response => {
          this.scenarios = response.data.scenarios || []
          if (this.scenarios.length === 0) {
            this.runAutoPrediction()
            return
          }
          this.selectedScenario = this.scenarios[0]
          this.loadScenarioResults()
          this.loadChartData()
        })
        .catch(() => {
          this.runAutoPrediction()
        })
    },
    loadChartData() {
      axios.get('/api/chart-data')
        .then(response => {
          if (!response.data || response.data.error) {
            this.error = (response.data && response.data.error) || '图表数据为空'
            this.loading = false
            return
          }

          this.chartData = response.data
          this.loading = false
          this.calculatePeakSummaries()

          this.$nextTick(() => {
            this.initCarbonPeakChart()
            this.initGdpChart()
            this.initEnergyChart()
          })
        })
        .catch(() => {
          this.error = '加载图表数据失败'
          this.loading = false
        })
    },
    calculatePeakSummaries() {
      this.peakSummaries = []
      const types = ['success', 'primary', 'warning', 'danger', 'info']
      Object.keys(this.chartData).forEach((name, index) => {
        const item = this.chartData[name]
        if (item && item.peak) {
          this.peakSummaries.push({
            name,
            year: item.peak.year,
            type: types[index % types.length]
          })
        }
      })
    },
    initCarbonPeakChart() {
      const dom = document.getElementById('carbon-peak-chart')
      if (!dom) return

      if (this.carbonPeakChart) this.carbonPeakChart.dispose()
      this.carbonPeakChart = echarts.init(dom)

      const scenarioKeys = Object.keys(this.chartData)
      const yearLabels = this.collectYearLabels(scenarioKeys, true)
      const series = []
      const firstScenario = scenarioKeys[0]
      const firstData = firstScenario ? this.chartData[firstScenario] : null

      if (firstData && hasArray(firstData, 'historical_years') && hasArray(firstData, 'historical_emissions')) {
        series.push({
          name: '历史数据',
          type: 'line',
          data: this.buildAlignedSeries(yearLabels, firstData.historical_years, firstData.historical_emissions),
          lineStyle: { width: 2, type: 'dashed', color: this.historicalColor },
          symbolSize: 5,
          connectNulls: false
        })
      }

      scenarioKeys.forEach((name, index) => {
        const item = this.chartData[name]
        if (!item || !hasArray(item, 'years') || !hasArray(item, 'emissions')) return
        series.push({
          name,
          type: 'line',
          smooth: true,
          data: this.buildAlignedSeries(yearLabels, item.years, item.emissions),
          lineStyle: { width: 3, color: this.chartColors[index % this.chartColors.length] },
          symbolSize: 5,
          connectNulls: false
        })
      })

      const textColor = this.isDark ? '#e6edf3' : '#475569'
      const lineColor = this.isDark ? '#30363d' : '#E2E8F0'

      this.carbonPeakChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          backgroundColor: this.isDark ? '#1c2128' : '#fff',
          borderColor: this.isDark ? '#30363d' : '#E2E8F0',
          textStyle: { color: textColor }
        },
        legend: {
          type: 'scroll',
          top: 10,
          textStyle: { color: textColor }
        },
        grid: { left: '8%', right: '4%', top: '15%', bottom: '12%', containLabel: true },
        xAxis: {
          type: 'category',
          name: '年份',
          data: yearLabels,
          boundaryGap: false,
          axisLabel: { rotate: 35, color: textColor },
          axisLine: { lineStyle: { color: lineColor } }
        },
        yAxis: {
          type: 'value',
          name: '碳排放量(万吨CO₂)',
          axisLabel: { color: textColor },
          splitLine: { lineStyle: { color: lineColor } }
        },
        animationDuration: 2000,
        animationEasing: 'cubicOut',
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut',
        series
      })
    },
    initGdpChart() {
      const dom = document.getElementById('gdp-chart')
      if (!dom) return

      if (this.gdpChart) this.gdpChart.dispose()
      this.gdpChart = echarts.init(dom)

      const scenarioKeys = Object.keys(this.chartData)
      const yearLabels = this.collectYearLabels(scenarioKeys, true)
      const series = []
      const firstScenario = scenarioKeys[0]
      const firstData = firstScenario ? this.chartData[firstScenario] : null

      if (firstData && hasArray(firstData, 'historical_years') && hasArray(firstData, 'historical_gdp')) {
        series.push({
          name: '历史数据',
          type: 'line',
          data: this.buildAlignedSeries(yearLabels, firstData.historical_years, firstData.historical_gdp),
          lineStyle: { width: 2, type: 'dashed', color: this.historicalColor },
          symbolSize: 5,
          connectNulls: false
        })
      }

      scenarioKeys.forEach((name, index) => {
        const item = this.chartData[name]
        if (!item || !hasArray(item, 'years') || !hasArray(item, 'gdp')) return
        series.push({
          name,
          type: 'line',
          smooth: true,
          data: this.buildAlignedSeries(yearLabels, item.years, item.gdp),
          lineStyle: { width: 3, color: this.chartColors[index % this.chartColors.length] },
          symbolSize: 5,
          connectNulls: false
        })
      })

      const textColor = this.isDark ? '#e6edf3' : '#475569'
      const lineColor = this.isDark ? '#30363d' : '#E2E8F0'

      this.gdpChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          backgroundColor: this.isDark ? '#1c2128' : '#fff',
          borderColor: this.isDark ? '#30363d' : '#E2E8F0',
          textStyle: { color: textColor }
        },
        legend: {
          type: 'scroll',
          top: 10,
          textStyle: { color: textColor }
        },
        grid: { left: '10%', right: '4%', top: '15%', bottom: '12%', containLabel: true },
        xAxis: {
          type: 'category',
          name: '年份',
          data: yearLabels,
          boundaryGap: false,
          axisLabel: { rotate: 35, color: textColor },
          axisLine: { lineStyle: { color: lineColor } }
        },
        yAxis: {
          type: 'value',
          name: 'GDP(万元)',
          axisLabel: { color: textColor },
          splitLine: { lineStyle: { color: lineColor } }
        },
        animationDuration: 2000,
        animationEasing: 'cubicOut',
        series
      })
    },
    initEnergyChart() {
      const dom = document.getElementById('energy-chart')
      if (!dom) return

      if (this.energyChart) this.energyChart.dispose()
      this.energyChart = echarts.init(dom)

      if (this.energyChartType === 'stack') {
        this.initEnergyStackChart()
      } else {
        this.initEnergyLineChart()
      }
    },
    initEnergyStackChart() {
      const firstScenario = Object.keys(this.chartData)[0]
      if (!firstScenario) return

      const data = this.chartData[firstScenario] || {}
      const years = data.years || []
      const historicalYears = data.historical_years || []
      const allYears = historicalYears.concat(years).filter((v, i, a) => a.indexOf(v) === i).sort((a, b) => a - b)

      const historicalEnergy = data.historical_energy || []
      const mix = data.energy_mix || {}
      const renewableData = mix.renewable || []
      const coalData = mix.coal || []
      const otherData = mix.other_fossil || []

      const series = [
        {
          name: '煤炭',
          type: 'bar',
          stack: 'total',
          data: allYears.map(year => {
            const histIdx = historicalYears.indexOf(year)
            if (histIdx >= 0) return (historicalEnergy[histIdx] || 0) * 0.75
            const foreIdx = years.indexOf(year)
            return foreIdx >= 0 ? (coalData[foreIdx] || 0) : 0
          }),
          itemStyle: { color: COLORS.coal }
        },
        {
          name: '其他化石能源',
          type: 'bar',
          stack: 'total',
          data: allYears.map(year => {
            const histIdx = historicalYears.indexOf(year)
            if (histIdx >= 0) return (historicalEnergy[histIdx] || 0) * 0.20
            const foreIdx = years.indexOf(year)
            return foreIdx >= 0 ? (otherData[foreIdx] || 0) : 0
          }),
          itemStyle: { color: COLORS.other }
        },
        {
          name: '可再生能源',
          type: 'bar',
          stack: 'total',
          data: allYears.map(year => {
            const histIdx = historicalYears.indexOf(year)
            if (histIdx >= 0) return (historicalEnergy[histIdx] || 0) * 0.05
            const foreIdx = years.indexOf(year)
            return foreIdx >= 0 ? (renewableData[foreIdx] || 0) : 0
          }),
          itemStyle: { color: COLORS.renewable }
        }
      ]

      const textColor = this.isDark ? '#e6edf3' : '#475569'
      const lineColor = this.isDark ? '#30363d' : '#E2E8F0'

      this.energyChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          backgroundColor: this.isDark ? '#1c2128' : '#fff',
          borderColor: this.isDark ? '#30363d' : '#E2E8F0',
          textStyle: { color: textColor }
        },
        legend: {
          bottom: 0,
          textStyle: { color: textColor }
        },
        grid: { left: '10%', right: '6%', top: '10%', bottom: '15%', containLabel: true },
        xAxis: {
          type: 'category',
          data: allYears,
          axisLabel: { rotate: 45, color: textColor },
          axisLine: { lineStyle: { color: lineColor } }
        },
        yAxis: {
          type: 'value',
          name: '能源消费(万吨标煤)',
          axisLabel: { color: textColor },
          splitLine: { lineStyle: { color: lineColor } }
        },
        animationDuration: 2000,
        animationEasing: 'cubicOut',
        series
      })
    },
    initEnergyLineChart() {
      const scenarioKeys = Object.keys(this.chartData)
      const yearLabels = this.collectYearLabels(scenarioKeys, true)
      const series = []
      const firstScenario = scenarioKeys[0]
      const firstData = firstScenario ? this.chartData[firstScenario] : null

      if (firstData && hasArray(firstData, 'historical_years') && hasArray(firstData, 'historical_energy')) {
        series.push({
          name: '历史数据',
          type: 'line',
          data: this.buildAlignedSeries(yearLabels, firstData.historical_years, firstData.historical_energy),
          lineStyle: { width: 2, type: 'dashed', color: this.historicalColor },
          symbolSize: 5,
          connectNulls: false
        })
      }

      scenarioKeys.forEach((name, index) => {
        const item = this.chartData[name]
        if (!item || !hasArray(item, 'years')) return
        const mix = item.energy_mix || {}
        const totals = mix.total || []
        series.push({
          name,
          type: 'line',
          smooth: true,
          data: this.buildAlignedSeries(yearLabels, item.years, totals),
          lineStyle: { width: 3, color: this.chartColors[index % this.chartColors.length] },
          symbolSize: 5,
          connectNulls: false
        })
      })

      const textColor = this.isDark ? '#e6edf3' : '#475569'
      const lineColor = this.isDark ? '#30363d' : '#E2E8F0'

      this.energyChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          backgroundColor: this.isDark ? '#1c2128' : '#fff',
          borderColor: this.isDark ? '#30363d' : '#E2E8F0',
          textStyle: { color: textColor }
        },
        legend: {
          type: 'scroll',
          top: 10,
          textStyle: { color: textColor }
        },
        grid: { left: '10%', right: '4%', top: '15%', bottom: '12%', containLabel: true },
        xAxis: {
          type: 'category',
          name: '年份',
          data: yearLabels,
          boundaryGap: false,
          axisLabel: { rotate: 35, color: textColor },
          axisLine: { lineStyle: { color: lineColor } }
        },
        yAxis: {
          type: 'value',
          name: '能源消费(万吨标煤)',
          axisLabel: { color: textColor },
          splitLine: { lineStyle: { color: lineColor } }
        },
        animationDuration: 2000,
        animationEasing: 'cubicOut',
        series
      })
    },
    runAutoPrediction() {
      this.loading = true
      this.error = null

      axios.get('/api/scenarios')
        .then(response => {
          const scenarios = Object.keys(response.data || {})
          if (scenarios.length === 0) {
            this.loading = false
            this.error = '没有可用的预测情景，请先创建情景'
            return
          }

          axios.post('/api/predict', { scenarios, forecast_years: 36 })
            .then(() => {
              this.$message.success('预测完成')
              this.checkPredictionStatus()
            })
            .catch(() => {
              this.loading = false
              this.error = '预测失败'
            })
        })
        .catch(() => {
          this.loading = false
          this.error = '获取情景失败'
        })
    },
    loadScenarioResults() {
      if (!this.selectedScenario) return
      axios.get(`/api/results/${this.selectedScenario}`)
        .then(response => {
          this.scenarioResults = response.data || []
        })
        .catch(() => {
          this.scenarioResults = []
        })
    },
    downloadResults() {
      if (!this.selectedScenario) {
        this.$message.warning('请先选择一个情景')
        return
      }
      const link = document.createElement('a')
      link.href = `/api/results/${this.selectedScenario}/download`
      link.download = `${this.selectedScenario}_预测结果.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    saveCharts() {
      if (!this.carbonPeakChart) return
      const url = this.carbonPeakChart.getDataURL({ type: 'png', pixelRatio: 2, backgroundColor: '#fff' })
      const link = document.createElement('a')
      link.download = '碳排放达峰预测.png'
      link.href = url
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    handleResize() {
      [this.carbonPeakChart, this.gdpChart, this.energyChart].forEach(c => {
        if (c) c.resize()
      })
    },
    goToScenarios() {
      this.$parent.$parent.activeTab = 'scenarios'
    },
    formatNumber(value) {
      if (value === null || value === undefined || Number.isNaN(Number(value))) return '-'
      return Number(value).toLocaleString('zh-CN', { maximumFractionDigits: 2 })
    }
  }
}
</script>

<style scoped>
.prediction-results {
  margin-bottom: 20px;
}

/* 顶部指标栏 */
.metrics-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--cp-bg-card, #fff);
  border: 1px solid var(--cp-border-primary, #E2E8F0);
  border-radius: var(--radius-md, 10px);
  transition: all 0.2s ease;
}

.metric-item:hover {
  box-shadow: var(--cp-shadow-md);
  border-color: var(--cp-border-secondary, #CBD5E1);
}

.metric-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--cp-primary-lightest, #DBEAFE);
  border-radius: var(--radius-md, 10px);
  color: var(--cp-primary, #1E40AF);
}

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--cp-text-primary, #0F172A);
  line-height: 1.2;
  font-family: var(--font-heading);
}

.metric-label {
  font-size: 12px;
  color: var(--cp-text-muted, #94A3B8);
  margin-top: 2px;
}

/* 图表区块 */
.chart-section {
  background: var(--cp-bg-card, #fff);
  border: 1px solid var(--cp-border-primary, #E2E8F0);
  border-radius: var(--radius-lg, 16px);
  overflow: hidden;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: var(--cp-bg-secondary, #F1F5F9);
  border-bottom: 1px solid var(--cp-border-primary, #E2E8F0);
  flex-wrap: wrap;
  gap: 10px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--cp-text-primary, #0F172A);
  font-family: var(--font-heading);
}

.section-title svg {
  color: var(--cp-primary, #1E40AF);
}

.chart-wrapper {
  padding: 16px;
}

.echarts-container {
  width: 100% !important;
  height: 400px !important;
}

.echarts-container.small {
  height: 320px !important;
}

/* 双图表行 */
.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-row .chart-section {
  margin-bottom: 0;
}

/* 达峰标签 */
.peak-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.peak-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 500;
  border-radius: var(--radius-full, 9999px);
  background: var(--cp-success-light, #D1FAE5);
  color: var(--cp-success, #059669);
  border: 1px solid var(--cp-success-light, #D1FAE5);
}

.peak-badge.primary {
  background: var(--cp-info-light, #DBEAFE);
  color: var(--cp-info, #2563EB);
  border-color: var(--cp-info-light, #DBEAFE);
}

.peak-badge.warning {
  background: var(--cp-warning-light, #FEF3C7);
  color: var(--cp-warning, #D97706);
  border-color: var(--cp-warning-light, #FEF3C7);
}

/* 图表切换 */
.chart-toggle {
  display: flex;
  gap: 4px;
  background: var(--cp-bg-tertiary, #E2E8F0);
  border-radius: var(--radius-sm, 6px);
  padding: 3px;
}

.toggle-btn {
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 500;
  border: none;
  background: transparent;
  color: var(--cp-text-secondary, #475569);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--font-body);
}

.toggle-btn.active {
  background: var(--cp-bg-card, #fff);
  color: var(--cp-primary, #1E40AF);
  box-shadow: var(--cp-shadow-xs);
}

.toggle-btn:hover:not(.active) {
  color: var(--cp-text-primary, #0F172A);
}

/* 场景选择器 */
.scenario-select {
  min-width: 180px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--cp-text-muted, #94A3B8);
  font-size: 14px;
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--cp-text-muted, #94A3B8);
  gap: 12px;
}

.error-state svg {
  color: var(--cp-warning, #D97706);
}

.error-state p {
  font-size: 14px;
  margin: 0;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--cp-text-muted, #94A3B8);
  gap: 12px;
}

.empty-state svg {
  opacity: 0.5;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

/* 操作栏 */
.actions-bar {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 20px 0 10px;
}

/* 响应式 */
@media (max-width: 992px) {
  .metrics-bar {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-row {
    grid-template-columns: 1fr;
  }

  .echarts-container {
    height: 320px !important;
  }

  .echarts-container.small {
    height: 280px !important;
  }
}

@media (max-width: 576px) {
  .metrics-bar {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions-bar {
    flex-direction: column;
  }

  .actions-bar .el-button {
    width: 100%;
  }
}
</style>
