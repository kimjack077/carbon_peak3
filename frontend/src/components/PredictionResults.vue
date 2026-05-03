<template>
  <div class="prediction-results">
    <el-row :gutter="24">
      <el-col :span="24">
        <el-card class="chart-card" shadow="hover">
          <div slot="header" class="card-header">
            <span class="card-title">碳排放达峰预测</span>
            <div class="peak-summary" v-if="peakSummaries.length > 0">
              <el-tag
                v-for="summary in peakSummaries"
                :key="summary.name"
                :type="summary.type"
                size="small"
                class="peak-tag"
              >
                {{ summary.name }}: {{ summary.year }}年达峰
              </el-tag>
            </div>
          </div>

          <div v-if="loading" class="loading-container">
            <i class="el-icon-loading"></i>
            <p>正在生成预测结果...</p>
          </div>
          <div v-else-if="error" class="error-container">
            <i class="el-icon-warning"></i>
            <p>{{ error }}</p>
            <el-button type="primary" @click="runAutoPrediction">重新运行预测</el-button>
          </div>
          <div v-else>
            <metric-card v-if="metricCardsData.length > 0" :metrics="metricCardsData"></metric-card>
            <div class="chart-container">
              <div id="carbon-peak-chart" class="echarts-container"></div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px;">
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <div slot="header" class="card-header">
            <span class="card-title">GDP预测</span>
          </div>
          <div class="chart-container">
            <div id="gdp-chart" class="echarts-container"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <div slot="header" class="card-header">
            <span class="card-title">能源消费结构</span>
            <el-radio-group v-model="energyChartType" size="small">
              <el-radio-button label="stack">堆叠柱状图</el-radio-button>
              <el-radio-button label="line">趋势图</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container">
            <div id="energy-chart" class="echarts-container"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px;">
      <el-col :span="24">
        <el-card class="data-card" shadow="hover">
          <div slot="header" class="card-header">
            <span class="card-title">预测数据详情</span>
            <el-select v-model="selectedScenario" placeholder="选择情景" size="small" @change="loadScenarioResults">
              <el-option v-for="scenario in scenarios" :key="scenario" :label="scenario" :value="scenario"></el-option>
            </el-select>
          </div>
          <el-table v-if="scenarioResults.length > 0" :data="scenarioResults" style="width: 100%" height="400" border stripe>
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
            <el-table-column prop="co2_emission" label="CO2排放(万吨)" min-width="130" align="right">
              <template slot-scope="scope">{{ formatNumber(scope.row.co2_emission) }}</template>
            </el-table-column>
          </el-table>
          <div v-else class="empty-data">
            <i class="el-icon-info"></i>
            <p>暂无预测数据，请先运行预测</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row style="margin-top: 24px;">
      <el-col :span="24" style="text-align: center;">
        <el-button type="primary" icon="el-icon-download" @click="downloadResults">下载预测结果</el-button>
        <el-button type="success" icon="el-icon-picture" @click="saveCharts">导出图表</el-button>
        <el-button icon="el-icon-back" @click="goToScenarios">返回情景设置</el-button>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'
import MetricCard from './MetricCard.vue'
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
  components: {
    MetricCard
  },
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
      if (active && !this.loading && !this.error) {
        this.$nextTick(() => {
          setTimeout(() => {
            this.initCarbonPeakChart()
            this.initGdpChart()
            this.initEnergyChart()
            this.handleResize()
          }, 120)
        })
      }
    },
    isDark() {
      // 主题变化时重绘所有图表
      this.$nextTick(() => {
        setTimeout(() => {
          this.initCarbonPeakChart()
          this.initGdpChart()
          this.initEnergyChart()
        }, 300) // 等待 CSS 过渡完成
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
      Object.keys(this.chartData).forEach((name, index) => {
        const item = this.chartData[name]
        if (item && item.peak) {
          this.peakSummaries.push({
            name,
            year: item.peak.year,
            type: index === 0 ? 'success' : index === 1 ? 'primary' : 'warning'
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

      this.carbonPeakChart.setOption({
        title: { text: '碳排放达峰预测', left: 'center' },
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
        },
        legend: { type: 'scroll', top: 30 },
        grid: { left: '8%', right: '4%', top: '22%', bottom: '12%', containLabel: true },
        xAxis: { type: 'category', name: '年份', data: yearLabels, boundaryGap: false, axisLabel: { rotate: 35 } },
        yAxis: { type: 'value', name: '碳排放量(万吨CO2)' },
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

      this.gdpChart.setOption({
        title: { text: 'GDP预测', left: 'center' },
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
        },
        legend: { type: 'scroll', top: 30 },
        grid: { left: '10%', right: '4%', top: '22%', bottom: '12%', containLabel: true },
        xAxis: { type: 'category', name: '年份', data: yearLabels, boundaryGap: false, axisLabel: { rotate: 35 } },
        yAxis: { type: 'value', name: 'GDP(万元)' },
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

      this.energyChart.setOption({
        title: { text: `能源消费结构（${firstScenario}）`, left: 'center' },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          backgroundColor: this.isDark ? 'rgba(15, 23, 42, 0.9)' : '#ffffff',
          borderColor: this.isDark ? 'rgba(255, 255, 255, 0.2)' : 'rgba(15, 118, 110, 0.2)',
          borderRadius: 12,
          shadowBlur: this.isDark ? 20 : 8,
          shadowColor: this.isDark ? 'rgba(15, 118, 110, 0.3)' : 'rgba(15, 118, 110, 0.1)',
          textStyle: {
            color: this.isDark ? '#e2e8f0' : '#134e4a'
          }
        },
        legend: { bottom: 0 },
        grid: { left: '10%', right: '6%', top: '16%', bottom: '18%', containLabel: true },
        xAxis: { type: 'category', data: allYears, axisLabel: { rotate: 45 } },
        yAxis: { type: 'value', name: '能源消费(万吨标煤)' },
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

      this.energyChart.setOption({
        title: { text: '综合能源消费预测', left: 'center' },
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
        },
        legend: { type: 'scroll', top: 30 },
        grid: { left: '10%', right: '4%', top: '22%', bottom: '12%', containLabel: true },
        xAxis: { type: 'category', name: '年份', data: yearLabels, boundaryGap: false, axisLabel: { rotate: 35 } },
        yAxis: { type: 'value', name: '能源消费(万吨标煤)' },
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

.chart-card,
.data-card {
  border-radius: 14px;
  border: 1px solid rgba(15, 118, 110, 0.14);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.card-title {
  font-size: 16px;
  font-weight: 800;
  color: #124e66;
}

.peak-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chart-container {
  width: 100%;
  min-height: 300px;
}

.echarts-container {
  width: 100% !important;
  height: 450px !important;
  min-height: 400px !important;
  border-radius: 12px;
}

.loading-container,
.error-container,
.empty-data {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  color: #909399;
}

.loading-container i,
.error-container i,
.empty-data i {
  font-size: 40px;
  margin-bottom: 10px;
}

::v-deep .el-radio-button__orig-radio:checked + .el-radio-button__inner {
  background-color: #0f766e;
  border-color: #0f766e;
  box-shadow: -1px 0 0 0 #0f766e;
}

::v-deep .el-table th {
  background-color: rgba(20, 184, 166, 0.08);
  color: #124e66;
  font-weight: 700;
}

::v-deep .el-table--border::after,
::v-deep .el-table--group::after,
::v-deep .el-table::before {
  background-color: rgba(15, 118, 110, 0.2);
}

@media (max-width: 992px) {
  .prediction-results ::v-deep .el-col {
    margin-bottom: 12px;
  }

  .echarts-container {
    height: 320px !important;
    min-height: 300px !important;
  }

  .loading-container,
  .error-container,
  .empty-data {
    min-height: 220px;
  }
}
</style>
