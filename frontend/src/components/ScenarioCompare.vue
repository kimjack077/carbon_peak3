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
  props: {
    isActive: {
      type: Boolean,
      default: false
    }
  },
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
    isActive(active) {
      if (active) {
        this.loadScenarios()
      }
    },
    selectedScenarios(newVal, oldVal) {
      // 只在用户手动切换时触发，不在初始化时触发（避免重复调用）
      if (newVal.length >= 2 && JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
        this.runComparison()
      } else if (newVal.length < 2) {
        this.comparisonData = null
        this.comparisonReport = null
      }
    }
  },
  methods: {
    async loadScenarios() {
      try {
        const data = await scenarioApi.list()
        this.allScenarios = Object.keys(data)
        // 自动选中所有场景并运行对比
        if (this.allScenarios.length > 0) {
          this.selectedScenarios = [...this.allScenarios]
          if (this.allScenarios.length >= 2) {
            await this.runComparison()
          }
        }
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

      if (this.peakCompareChart) {
        this.peakCompareChart.dispose()
      }

      this.peakCompareChart = echarts.init(dom)

      const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
      const textColor = isDark ? '#e6edf3' : '#475569'
      const bgColor = 'transparent'

      const lineColor = isDark ? '#30363d' : '#E2E8F0'

      this.peakCompareChart.setOption({
        backgroundColor: bgColor,
        title: { text: '峰值年份对比', left: 'center', textStyle: { color: textColor, fontSize: 14 } },
        tooltip: {
          trigger: 'axis',
          backgroundColor: isDark ? '#1c2128' : '#fff',
          borderColor: isDark ? '#30363d' : '#E2E8F0',
          textStyle: { color: textColor },
          formatter: function(params) {
            return params[0].name + ': <b>' + params[0].value + '年</b>'
          }
        },
        grid: { left: '12%', right: '8%', top: '15%', bottom: '15%' },
        xAxis: {
          type: 'category',
          data: this.selectedScenarios,
          axisLabel: { color: textColor, rotate: 15, fontSize: 11 },
          axisLine: { lineStyle: { color: lineColor } }
        },
        yAxis: {
          type: 'value',
          name: '年份',
          min: 2020,
          max: 2060,
          interval: 5,
          axisLabel: { color: textColor },
          splitLine: { lineStyle: { color: lineColor } }
        },
        series: [{
          type: 'bar',
          data: this.comparisonData.peak_years,
          barMaxWidth: 50,
          label: {
            show: true,
            position: 'top',
            color: textColor,
            fontWeight: 'bold',
            fontSize: 11,
            formatter: '{c}'
          },
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#1E40AF' },
              { offset: 1, color: '#3B82F6' }
            ]),
            borderRadius: [4, 4, 0, 0]
          }
        }]
      })
    },
    initPathCompareChart() {
      const dom = this.$refs.pathCompareChart
      if (!dom || !this.comparisonData) return

      if (this.pathCompareChart) {
        this.pathCompareChart.dispose()
      }

      this.pathCompareChart = echarts.init(dom)

      const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
      const textColor = isDark ? '#e6edf3' : '#475569'

      const lineColor = isDark ? '#30363d' : '#E2E8F0'

      this.pathCompareChart.setOption({
        backgroundColor: 'transparent',
        title: { text: '减排路径对比', left: 'center', textStyle: { color: textColor, fontSize: 14 } },
        tooltip: {
          trigger: 'axis',
          backgroundColor: isDark ? '#1c2128' : '#fff',
          borderColor: isDark ? '#30363d' : '#E2E8F0',
          textStyle: { color: textColor }
        },
        legend: {
          top: 30,
          textStyle: { color: textColor }
        },
        grid: { left: '10%', right: '5%', top: '22%', bottom: '12%', containLabel: true },
        xAxis: {
          type: 'category',
          data: this.comparisonData.years,
          axisLabel: { color: textColor, rotate: 35 },
          axisLine: { lineStyle: { color: lineColor } }
        },
        yAxis: {
          type: 'value',
          name: '排放量(万吨)',
          axisLabel: { color: textColor },
          splitLine: { lineStyle: { color: lineColor } }
        },
        series: this.comparisonData.paths.map((path, i) => ({
          name: this.selectedScenarios[i],
          type: 'line',
          data: path,
          smooth: true,
          lineStyle: { width: 3 },
          symbolSize: 5
        }))
      })
    },
    initIndicatorRadar() {
      const dom = this.$refs.indicatorRadar
      if (!dom || !this.comparisonData) return

      if (this.indicatorRadar) {
        this.indicatorRadar.dispose()
      }

      this.indicatorRadar = echarts.init(dom)

      const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
      const textColor = isDark ? '#e6edf3' : '#475569'

      this.indicatorRadar.setOption({
        backgroundColor: 'transparent',
        title: { text: '关键指标雷达', left: 'center', textStyle: { color: textColor, fontSize: 14 } },
        tooltip: {},
        legend: { bottom: 0, textStyle: { color: textColor } },
        radar: {
          indicator: [
            { name: '达峰速度', max: 100 },
            { name: '减排效果', max: 100 },
            { name: '经济影响', max: 100 },
            { name: '可行性', max: 100 }
          ],
          axisName: { color: textColor }
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

.compare-header h3 {
  margin: 0;
  color: var(--cp-text-primary, #0F172A);
  font-size: 16px;
  font-weight: 600;
}

.compare-chart {
  height: 280px;
}

.comparison-report {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--cp-border-primary, #E2E8F0);
}

.comparison-report h4 {
  color: var(--cp-text-primary, #0F172A);
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
}

.comparison-report p {
  color: var(--cp-text-secondary, #475569);
  margin-bottom: 16px;
  font-size: 13px;
  line-height: 1.6;
}
</style>
