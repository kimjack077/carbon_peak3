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
        xAxis: { type: 'category', data: this.selectedScenarios, axisLabel: { color: '#94a3b8' } },
        yAxis: { type: 'value', name: '年份', axisLabel: { color: '#94a3b8' } },
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
        xAxis: { type: 'category', data: this.comparisonData.years, axisLabel: { color: '#94a3b8' } },
        yAxis: { type: 'value', name: '排放量', axisLabel: { color: '#94a3b8' } },
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