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
      if (!dom || !this.recommendations || !this.recommendations.sensitivity) return

      this.sensitivityChart = echarts.init(dom)
      this.sensitivityChart.setOption({
        tooltip: { trigger: 'axis' },
        radar: {
          indicator: [
            { name: 'GDP增长率', max: 0.15 },
            { name: '效率提升', max: 0.10 },
            { name: '可再生提升', max: 0.05 },
            { name: '煤炭下降', max: 0.05 }
          ],
          axisName: { color: '#94a3b8' }
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
.loading-state {
  text-align: center;
  padding: 20px;
  color: #94a3b8;
}
</style>