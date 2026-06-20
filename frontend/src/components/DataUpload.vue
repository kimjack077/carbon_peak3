<template>
  <div class="data-upload">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="status-indicator" :class="{ active: dataLoaded }">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          <span>{{ dataLoaded ? '数据已加载' : '未加载数据' }}</span>
        </div>
      </div>
      <div class="toolbar-right">
        <data-import @data-imported="handleDataImported"></data-import>
        <el-divider direction="vertical"></el-divider>
        <el-button size="small" icon="el-icon-refresh" @click.prevent="useExampleData" :loading="loading">
          重新加载示例
        </el-button>
      </div>
    </div>

    <!-- 数据概览卡片 -->
    <div v-if="dataInfo" class="overview-cards">
      <div class="overview-card">
        <div class="card-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
        </div>
        <div class="card-content">
          <div class="card-value">{{ dataInfo.years[0] }} - {{ dataInfo.years[1] }}</div>
          <div class="card-label">年份范围</div>
        </div>
      </div>
      <div class="overview-card">
        <div class="card-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <div class="card-content">
          <div class="card-value">{{ dataInfo.sectors.length }}个</div>
          <div class="card-label">部门数量</div>
        </div>
      </div>
      <div class="overview-card">
        <div class="card-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
          </svg>
        </div>
        <div class="card-content">
          <div class="card-value">{{ dataInfo.rows }}条</div>
          <div class="card-label">数据记录</div>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div v-if="tableData.length > 0" class="data-table-section">
      <div class="table-header">
        <span class="table-title">数据预览</span>
        <span class="table-hint">显示前10条记录</span>
      </div>
      <el-table :data="tableData.slice(0, 10)" border stripe size="small" style="width: 100%">
        <el-table-column prop="year" label="年份" width="80" align="center"></el-table-column>
        <el-table-column prop="gdp" label="GDP(万元)" min-width="120" align="right">
          <template slot-scope="scope">{{ formatNumber(scope.row.gdp) }}</template>
        </el-table-column>
        <el-table-column prop="energy_consumption" label="能源消费(万吨标煤)" min-width="140" align="right">
          <template slot-scope="scope">{{ formatNumber(scope.row.energy_consumption) }}</template>
        </el-table-column>
        <el-table-column prop="co2_emission" label="CO₂排放(万吨)" min-width="130" align="right">
          <template slot-scope="scope">{{ formatNumber(scope.row.co2_emission) }}</template>
        </el-table-column>
        <el-table-column prop="renewable_ratio" label="可再生能源占比" min-width="120" align="right">
          <template slot-scope="scope">{{ (scope.row.renewable_ratio * 100).toFixed(1) }}%</template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && !dataInfo" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="12" y1="18" x2="12" y2="12"/>
        <line x1="9" y1="15" x2="15" y2="15"/>
      </svg>
      <p>暂无数据，请导入数据或加载示例数据</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import DataImport from './DataImport.vue'

export default {
  name: 'DataUpload',
  components: { DataImport },
  data() {
    return {
      loading: false,
      dataLoaded: false,
      dataInfo: null,
      tableData: []
    }
  },
  created() {
    this.loadCurrentData()
  },
  methods: {
    handleDataImported(result) {
      // 导入成功后，直接使用返回的数据更新界面
      if (result && result.data) {
        this.dataInfo = {
          years: result.years || [0, 0],
          sectors: result.sectors || [],
          rows: result.rows || 0
        }
        this.tableData = result.data || []
        this.dataLoaded = true
        this.$emit('data-loaded', true)
        this.$message.success('数据已导入，共 ' + (result.rows || 0) + ' 条记录')
      } else {
        // 如果没有返回数据，重新加载当前数据
        this.loadCurrentData()
      }
    },
    loadCurrentData() {
      this.loading = true
      axios.get('/api/data/current')
        .then(response => {
          if (response.data && response.data.rows > 0) {
            this.dataInfo = {
              years: response.data.years || [0, 0],
              sectors: response.data.sectors || [],
              rows: response.data.rows || 0
            }
            this.tableData = response.data.data || []
            this.dataLoaded = true
            this.$emit('data-loaded', true)
          } else {
            this.useExampleData()
          }
        })
        .catch(() => {
          this.useExampleData()
        })
        .finally(() => {
          this.loading = false
        })
    },
    useExampleData() {
      this.loading = true
      axios.post('/api/upload/example')
        .then(response => {
          this.dataInfo = {
            years: response.data.years,
            sectors: response.data.sectors,
            rows: response.data.rows
          }
          this.tableData = response.data.data || []
          this.dataLoaded = true
          this.$emit('data-loaded', true)
        })
        .catch(() => {
          this.$message.error('加载示例数据失败')
        })
        .finally(() => {
          this.loading = false
        })
    },
    formatNumber(value) {
      if (value === null || value === undefined) return '-'
      return Number(value).toLocaleString('zh-CN', { maximumFractionDigits: 2 })
    }
  }
}
</script>

<style scoped>
.data-upload {
  max-width: 1000px;
}

/* 工具栏 */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--cp-bg-secondary, #F1F5F9);
  border-radius: var(--radius-md, 10px);
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 10px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--cp-text-muted, #94A3B8);
}

.status-indicator.active {
  color: var(--cp-success, #059669);
}

.status-indicator svg {
  color: inherit;
}

/* 概览卡片 */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.overview-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: var(--cp-bg-card, #fff);
  border: 1px solid var(--cp-border-primary, #E2E8F0);
  border-radius: var(--radius-md, 10px);
  transition: all 0.2s ease;
}

.overview-card:hover {
  box-shadow: var(--cp-shadow-sm);
  border-color: var(--cp-border-secondary, #CBD5E1);
}

.card-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--cp-primary-lightest, #DBEAFE);
  border-radius: var(--radius-sm, 6px);
  color: var(--cp-primary, #1E40AF);
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--cp-text-primary, #0F172A);
  line-height: 1.2;
  font-family: var(--font-heading);
}

.card-label {
  font-size: 11px;
  color: var(--cp-text-muted, #94A3B8);
  margin-top: 2px;
}

/* 数据表格 */
.data-table-section {
  background: var(--cp-bg-card, #fff);
  border: 1px solid var(--cp-border-primary, #E2E8F0);
  border-radius: var(--radius-md, 10px);
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: var(--cp-bg-secondary, #F1F5F9);
  border-bottom: 1px solid var(--cp-border-primary, #E2E8F0);
}

.table-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--cp-text-primary, #0F172A);
}

.table-hint {
  font-size: 11px;
  color: var(--cp-text-muted, #94A3B8);
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

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar-right {
    width: 100%;
    justify-content: flex-start;
  }

  .overview-cards {
    grid-template-columns: 1fr;
  }
}
</style>
