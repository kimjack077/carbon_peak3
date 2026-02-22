<template>
  <div class="data-upload">
    <el-card class="upload-card">
      <div slot="header" class="upload-head">
        <h2>数据来源</h2>
        <span class="upload-head-tip">自动加载示例数据，可直接开始预测</span>
      </div>
      <div class="upload-content">
        <p class="intro-copy">系统已自动加载示例数据，您可以直接进行预测。</p>
        
        <div v-if="uploadStatus" :class="['upload-status', uploadStatus.type]">
          <i :class="uploadStatus.icon"></i> {{ uploadStatus.message }}
        </div>
        
        <div v-if="dataInfo" class="data-info">
          <h3>数据概览</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="item-label">年份范围</span>
              <strong>{{ dataInfo.years.join(' - ') }}</strong>
            </div>
            <div class="info-item">
              <span class="item-label">部门</span>
              <strong>{{ dataInfo.sectors.join('、') }}</strong>
            </div>
            <div class="info-item">
              <span class="item-label">数据条数</span>
              <strong>{{ dataInfo.rows }}</strong>
            </div>
          </div>
          
          <el-button type="primary" @click="useExampleData" class="reload-btn">重新加载示例数据</el-button>
          
          <!-- 原始数据表格 -->
          <div v-if="tableData.length > 0" class="data-table">
            <h3>原始数据</h3>
            <el-table :data="tableData" border stripe style="width: 100%">
              <el-table-column prop="year" label="年份" width="100" align="center"></el-table-column>
              <el-table-column prop="gdp" label="生产总值（万元）" align="right">
                <template slot-scope="scope">
                  {{ formatNumber(scope.row.gdp) }}
                </template>
              </el-table-column>
              <el-table-column prop="energy_consumption" label="能源消费（万吨标煤）" align="right">
                <template slot-scope="scope">
                  {{ formatNumber(scope.row.energy_consumption) }}
                </template>
              </el-table-column>
              <el-table-column prop="co2_emission" label="CO₂排放（万吨）" align="right">
                <template slot-scope="scope">
                  {{ formatNumber(scope.row.co2_emission) }}
                </template>
              </el-table-column>
              <el-table-column prop="renewable_ratio" label="可再生能源占比" align="right">
                <template slot-scope="scope">
                  {{ (scope.row.renewable_ratio * 100).toFixed(1) }}%
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DataUpload',
  data() {
    return {
      uploadStatus: null,
      dataInfo: null,
      tableData: []
    }
  },
  created() {
    // 组件创建时自动加载示例数据
    this.useExampleData();
  },
  methods: {
    useExampleData() {
      this.uploadStatus = {
        type: 'loading',
        icon: 'el-icon-loading',
        message: '正在加载示例数据...'
      }
      
      axios.post('/api/upload/example')
        .then(response => {
          this.dataInfo = {
            years: response.data.years,
            sectors: response.data.sectors,
            rows: response.data.rows
          }
          this.tableData = response.data.data || []
          this.uploadStatus = {
            type: 'success',
            icon: 'el-icon-success',
            message: '已加载示例数据!'
          }
          this.$emit('data-loaded', true)
        })
        .catch(() => {
          this.uploadStatus = {
            type: 'error',
            icon: 'el-icon-error',
            message: '加载示例数据失败!'
          }
        })
    },
    formatNumber(value) {
      if (value === null || value === undefined) return '-'
      return value.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
    }
  }
}
</script>

<style scoped>
.data-upload {
  max-width: 980px;
  margin: 0 auto;
}

.upload-card {
  margin-bottom: 20px;
  border-radius: 16px;
}

.upload-content {
  text-align: left;
}

.upload-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.upload-head h2 {
  margin: 0;
  color: #134e4a;
  font-size: 20px;
  font-weight: 800;
}

.upload-head-tip {
  font-size: 12px;
  color: #5f7f74;
}

.intro-copy {
  color: #304c42;
  margin-bottom: 14px;
  line-height: 1.7;
}

pre {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  margin: 15px 0;
  text-align: left;
  overflow-x: auto;
}

.upload-status {
  margin-top: 16px;
  padding: 12px 14px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.upload-status.success {
  background-color: rgba(16, 185, 129, 0.12);
  color: #047857;
  border: 1px solid rgba(16, 185, 129, 0.22);
}

.upload-status.error {
  background-color: rgba(239, 68, 68, 0.1);
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.22);
}

.upload-status.loading {
  background-color: rgba(37, 99, 235, 0.09);
  color: #1d4ed8;
  border: 1px solid rgba(37, 99, 235, 0.18);
}

.data-info {
  margin-top: 24px;
  padding: 18px;
  background: linear-gradient(180deg, rgba(20, 184, 166, 0.08), rgba(255, 255, 255, 0.9));
  border-radius: 12px;
  text-align: left;
  border: 1px solid rgba(19, 78, 74, 0.12);
}

.data-info h3 {
  margin: 0 0 14px;
  color: #134e4a;
  font-size: 16px;
  font-weight: 800;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.info-item {
  background: #ffffff;
  border: 1px solid rgba(19, 78, 74, 0.12);
  border-radius: 10px;
  padding: 10px 12px;
  min-height: 74px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.item-label {
  color: #5f7f74;
  font-size: 12px;
}

.info-item strong {
  color: #0f3f3b;
  line-height: 1.4;
}

.reload-btn {
  margin-bottom: 20px;
}

.data-table {
  margin-top: 20px;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 12px;
  border: 1px solid rgba(19, 78, 74, 0.12);
}

.data-table h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #134e4a;
  font-size: 16px;
  font-weight: 800;
}

::v-deep .el-table th {
  background: rgba(20, 184, 166, 0.09);
  color: #134e4a;
  font-weight: 700;
}

@media (max-width: 992px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .upload-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .data-table {
    padding: 12px;
  }
}
</style>
