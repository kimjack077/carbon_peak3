<template>
  <div class="data-upload">
    <el-card class="upload-card">
      <div slot="header">
        <h2>数据来源</h2>
      </div>
      <div class="upload-content">
        <p>系统已自动加载示例数据，您可以直接进行预测。</p>
        
        <div v-if="uploadStatus" :class="['upload-status', uploadStatus.type]">
          <i :class="uploadStatus.icon"></i> {{ uploadStatus.message }}
        </div>
        
        <div v-if="dataInfo" class="data-info">
          <h3>数据概览</h3>
          <p><strong>年份范围：</strong>{{ dataInfo.years.join(' - ') }}</p>
          <p><strong>部门：</strong>{{ dataInfo.sectors.join('、') }}</p>
          <p><strong>数据条数：</strong>{{ dataInfo.rows }}</p>
          
          <el-button type="primary" @click="useExampleData" style="margin-bottom: 20px;">重新加载示例数据</el-button>
          
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
  max-width: 800px;
  margin: 0 auto;
}

.upload-card {
  margin-bottom: 20px;
}

.upload-content {
  text-align: center;
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
  margin-top: 20px;
  padding: 10px;
  border-radius: 4px;
}

.upload-status.success {
  background-color: #f0f9eb;
  color: #67c23a;
}

.upload-status.error {
  background-color: #fef0f0;
  color: #f56c6c;
}

.upload-status.loading {
  background-color: #f5f7fa;
  color: #909399;
}

.data-info {
  margin-top: 30px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  text-align: left;
}

.data-info h3 {
  margin-top: 0;
  color: #409EFF;
}

.data-table {
  margin-top: 30px;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.data-table h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}
</style>
