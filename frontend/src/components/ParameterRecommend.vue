<!-- 智能参数推荐 - 横向紧凑版 -->
<template>
  <div class="param-recommend">
    <div class="recommend-header">
      <div class="header-left">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
        <span class="title">AI 智能推荐</span>
      </div>
      <el-button size="mini" type="primary" plain @click="refreshRecommendations" :loading="loading">
        <i class="el-icon-refresh"></i> 刷新
      </el-button>
    </div>

    <div v-if="loading" class="loading-state">
      <i class="el-icon-loading"></i>
      <span>分析中...</span>
    </div>

    <div v-else-if="recommendations" class="recommend-body">
      <!-- 左侧：四个参数 -->
      <div class="params-section">
        <div class="param-row">
          <div class="param-info">
            <span class="param-name">GDP增长率</span>
            <span class="param-val">{{ formatPercent(recommendations.gdp_growth_rate) }}</span>
          </div>
          <el-slider
            v-model="recommendations.gdp_growth_rate"
            :min="0" :max="0.15" :step="0.005"
            :format-tooltip="formatPercent"
            :show-input="false"
            size="small"
          />
          <div class="param-hint">{{ recommendations.gdp_reason }}</div>
        </div>

        <div class="param-row">
          <div class="param-info">
            <span class="param-name">效率提升率</span>
            <span class="param-val">{{ formatPercent(recommendations.efficiency_improvement_rate) }}</span>
          </div>
          <el-slider
            v-model="recommendations.efficiency_improvement_rate"
            :min="0" :max="0.10" :step="0.005"
            :format-tooltip="formatPercent"
            :show-input="false"
            size="small"
          />
          <div class="param-hint">{{ recommendations.efficiency_reason }}</div>
        </div>

        <div class="param-row">
          <div class="param-info">
            <span class="param-name">可再生能源提升</span>
            <span class="param-val">{{ formatPercent(recommendations.renewable_increase_rate) }}</span>
          </div>
          <el-slider
            v-model="recommendations.renewable_increase_rate"
            :min="0" :max="0.05" :step="0.002"
            :format-tooltip="formatPercent"
            :show-input="false"
            size="small"
          />
        </div>

        <div class="param-row">
          <div class="param-info">
            <span class="param-name">煤炭占比下降</span>
            <span class="param-val">{{ formatPercent(recommendations.coal_decrease_rate) }}</span>
          </div>
          <el-slider
            v-model="recommendations.coal_decrease_rate"
            :min="0" :max="0.05" :step="0.002"
            :format-tooltip="formatPercent"
            :show-input="false"
            size="small"
          />
        </div>

        <el-button type="primary" size="mini" @click="applyRecommendations" class="apply-btn">
          <i class="el-icon-check"></i> 应用推荐
        </el-button>
      </div>

      <!-- 右侧：敏感度图表 -->
      <div class="chart-section">
        <div class="chart-title">参数敏感度分析</div>
        <div ref="sensitivityChart" class="chart-area"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { recommendApi } from '@/utils/api'
import { formatPercent } from '@/utils/helpers'
import * as echarts from 'echarts'

export default {
  name: 'ParameterRecommend',
  data() {
    return {
      loading: false,
      recommendations: null,
      chart: null
    }
  },
  watch: {
    recommendations: {
      handler() {
        this.updateChart()
      },
      deep: true
    }
  },
  mounted() {
    this.loadRecommendations()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.chart) {
      this.chart.dispose()
      this.chart = null
    }
  },
  methods: {
    formatPercent,
    handleResize() {
      if (this.chart) {
        this.chart.resize()
      }
    },
    updateChart() {
      if (!this.chart || !this.recommendations) return
      this.chart.setOption({
        series: [{
          data: [{
            value: [
              this.recommendations.gdp_growth_rate || 0.05,
              this.recommendations.efficiency_improvement_rate || 0.03,
              this.recommendations.renewable_increase_rate || 0.01,
              this.recommendations.coal_decrease_rate || 0.02
            ]
          }]
        }]
      })
    },
    async loadRecommendations() {
      this.loading = true
      try {
        const data = await recommendApi.parameters()
        this.recommendations = data
        this.$nextTick(() => {
          setTimeout(() => this.initChart(), 100)
        })
      } catch (err) {
        console.error('获取推荐失败:', err)
      } finally {
        this.loading = false
      }
    },
    initChart() {
      const dom = this.$refs.sensitivityChart
      if (!dom || !this.recommendations) return

      if (this.chart) {
        this.chart.dispose()
      }

      this.chart = echarts.init(dom)

      const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
      const textColor = isDark ? '#e6edf3' : '#475569'
      const lineColor = isDark ? '#30363d' : '#E2E8F0'

      this.chart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'item',
          backgroundColor: isDark ? '#1c2128' : '#fff',
          borderColor: isDark ? '#30363d' : '#E2E8F0',
          textStyle: { color: textColor, fontSize: 11 },
          formatter: function(params) {
            const names = ['GDP增长率', '效率提升', '可再生提升', '煤炭下降']
            const vals = params.value
            return names.map((n, i) => `${n}: <b>${(vals[i] * 100).toFixed(1)}%</b>`).join('<br/>')
          }
        },
        radar: {
          indicator: [
            { name: 'GDP增长率', max: 0.15 },
            { name: '效率提升', max: 0.10 },
            { name: '可再生提升', max: 0.05 },
            { name: '煤炭下降', max: 0.05 }
          ],
          shape: 'polygon',
          splitNumber: 3,
          center: ['50%', '50%'],
          radius: '72%',
          axisName: {
            color: textColor,
            fontSize: 12
          },
          splitLine: {
            lineStyle: { color: lineColor }
          },
          splitArea: { show: false },
          axisLine: {
            lineStyle: { color: lineColor }
          }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [
              this.recommendations.gdp_growth_rate || 0.05,
              this.recommendations.efficiency_improvement_rate || 0.03,
              this.recommendations.renewable_increase_rate || 0.01,
              this.recommendations.coal_decrease_rate || 0.02
            ],
            name: '推荐参数',
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { color: '#2b6cb0', width: 2.5 },
            areaStyle: { color: 'rgba(43, 108, 176, 0.3)' },
            itemStyle: { color: '#2b6cb0', borderWidth: 2 }
          }]
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
.param-recommend {
  background: var(--cp-bg-card, #fff);
  border: 1px solid var(--cp-border-primary, #E2E8F0);
  border-radius: var(--radius-md, 10px);
  overflow: hidden;
}

.recommend-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  background: var(--cp-bg-secondary, #F1F5F9);
  border-bottom: 1px solid var(--cp-border-primary, #E2E8F0);
}

.recommend-header .header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--cp-primary, #1E40AF);
}

.recommend-header .title {
  font-size: 13px;
  font-weight: 600;
  color: var(--cp-text-primary, #0F172A);
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  color: var(--cp-text-muted, #94A3B8);
  font-size: 13px;
}

/* 横向布局 */
.recommend-body {
  display: flex;
  gap: 0;
  padding: 10px 14px;
  min-height: 240px;
}

/* 左侧参数区 - 50% */
.params-section {
  width: 50%;
  padding-right: 14px;
  border-right: 1px solid var(--cp-border-primary, #E2E8F0);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.param-row {
  margin-bottom: 6px;
}

.param-row:last-of-type {
  margin-bottom: 8px;
}

.param-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2px;
}

.param-name {
  font-size: 12px;
  color: var(--cp-text-secondary, #475569);
  font-weight: 500;
}

.param-val {
  font-size: 13px;
  font-weight: 700;
  color: var(--cp-primary, #1E40AF);
  font-family: var(--font-mono, monospace);
}

.param-row :deep(.el-slider) {
  margin: 0;
}

.param-row :deep(.el-slider__runway) {
  height: 4px;
}

.param-row :deep(.el-slider__bar) {
  height: 4px;
}

.param-row :deep(.el-slider__button) {
  width: 12px;
  height: 12px;
  border-width: 2px;
}

.param-hint {
  font-size: 10px;
  color: var(--cp-text-muted, #94A3B8);
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.apply-btn {
  width: 100%;
  margin-top: 2px;
}

/* 右侧图表区 - 50% */
.chart-section {
  width: 50%;
  padding-left: 14px;
  display: flex;
  flex-direction: column;
}

.chart-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--cp-text-secondary, #475569);
  margin-bottom: 8px;
}

.chart-area {
  flex: 1;
  width: 100%;
  min-height: 200px;
}

@media (max-width: 768px) {
  .recommend-body {
    flex-direction: column;
  }

  .params-section {
    width: 100%;
    padding-right: 0;
    border-right: none;
    border-bottom: 1px solid var(--cp-border-primary, #E2E8F0);
    padding-bottom: 12px;
  }

  .chart-section {
    width: 100%;
    padding-left: 0;
    padding-top: 12px;
  }
}
</style>
