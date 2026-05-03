<!-- frontend/src/components/MetricCard.vue -->
<template>
  <div class="metric-cards">
    <div
      v-for="(metric, index) in metrics"
      :key="index"
      class="metric-card"
    >
      <span class="metric-label">{{ metric.label }}</span>
      <div class="metric-value-row">
        <span class="metric-value">{{ metric.value }}</span>
        <span
          v-if="metric.trend"
          class="metric-trend"
          :class="metric.trendClass"
        >
          <svg v-if="metric.trend === 'down'" viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
            <path d="M7 10l5 5 5-5H7z"/>
          </svg>
          <svg v-if="metric.trend === 'up'" viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
            <path d="M7 14l5-5 5 5H7z"/>
          </svg>
        </span>
      </div>
      <span class="metric-unit">{{ metric.unit }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MetricCard',
  props: {
    // 指标数据数组
    metrics: {
      type: Array,
      default: () => []
    }
  }
}
</script>

<style scoped>
.metric-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--cp-spacing-md);
  margin-bottom: var(--cp-spacing-lg);
}

.metric-card {
  background: var(--cp-bg-card);
  border: 1px solid var(--cp-border-primary);
  border-radius: var(--cp-radius-md);
  padding: var(--cp-spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--cp-spacing-xs);
  transition: box-shadow var(--cp-transition-normal);
}

.metric-card:hover {
  box-shadow: var(--cp-shadow-md);
}

.metric-label {
  font-size: var(--cp-font-xs);
  color: var(--cp-text-secondary);
  font-weight: 500;
}

.metric-value-row {
  display: flex;
  align-items: center;
  gap: var(--cp-spacing-xs);
}

.metric-value {
  font-size: var(--cp-font-xl);
  font-weight: 800;
  color: var(--cp-accent-primary);
  line-height: 1.2;
}

.metric-trend {
  display: flex;
  align-items: center;
}

.metric-trend.down {
  color: var(--cp-accent-success);
}

.metric-trend.up {
  color: var(--cp-accent-warning);
}

.metric-unit {
  font-size: var(--cp-font-xs);
  color: var(--cp-text-muted);
}

/* 深色主题 */
[data-theme="dark"] .metric-card {
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

[data-theme="dark"] .metric-card:hover {
  box-shadow: var(--cp-shadow-glow);
}

/* 响应式 */
@media (max-width: 992px) {
  .metric-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 576px) {
  .metric-cards {
    grid-template-columns: 1fr;
  }

  .metric-value {
    font-size: var(--cp-font-lg);
  }
}
</style>