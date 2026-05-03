<template>
  <div class="scenario-manager">
    <!-- 参数推荐区域 -->
    <parameter-recommend @apply="applyRecommendedParams" class="recommend-section" />

    <el-row :gutter="24">
      <el-col :xs="24" :sm="24" :md="10" :lg="10">
        <el-card class="scenario-card" shadow="hover">
          <div slot="header" class="card-header">
            <span class="card-title">创建预测情景</span>
          </div>
          <el-form ref="scenarioForm" :model="scenarioForm" label-width="130px" :rules="rules" label-position="left">
            <el-form-item label="情景名称" prop="name">
              <el-input v-model="scenarioForm.name" placeholder="例如：积极达峰情景"></el-input>
            </el-form-item>
            
            <el-form-item label="预测模型" prop="model_type">
              <el-select v-model="scenarioForm.model_type" placeholder="请选择预测模型" style="width: 100%">
                <el-option label="LEAP模型 - 能源结构分析" value="leap"></el-option>
                <el-option label="Kaya恒等式 - 因子分解" value="kaya"></el-option>
                <el-option label="STIRPAT模型 - 弹性分析" value="stirpat"></el-option>
              </el-select>
            </el-form-item>
            
            <el-divider content-position="left">核心参数</el-divider>
            
            <el-form-item label="GDP增长率" prop="gdp_growth_rate">
              <el-slider v-model="scenarioForm.gdp_growth_rate" :min="0" :max="0.15" :step="0.005" :format-tooltip="formatPercent" show-input :show-input-controls="false"></el-slider>
            </el-form-item>
            
            <el-form-item label="能源效率改善率" prop="efficiency_improvement_rate">
              <el-slider v-model="scenarioForm.efficiency_improvement_rate" :min="0" :max="0.10" :step="0.005" :format-tooltip="formatPercent" show-input :show-input-controls="false"></el-slider>
            </el-form-item>
            
            <el-divider content-position="left">能源结构参数</el-divider>
            
            <el-form-item label="可再生能源占比提升" prop="renewable_increase_rate">
              <el-slider v-model="scenarioForm.renewable_increase_rate" :min="0" :max="0.05" :step="0.002" :format-tooltip="formatPercent" show-input :show-input-controls="false"></el-slider>
            </el-form-item>
            
            <el-form-item label="煤炭占比下降率" prop="coal_decrease_rate">
              <el-slider v-model="scenarioForm.coal_decrease_rate" :min="0" :max="0.05" :step="0.002" :format-tooltip="formatPercent" show-input :show-input-controls="false"></el-slider>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="createScenario" :loading="creating">创建情景</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="24" :md="14" :lg="14">
        <el-card class="scenario-list-card" shadow="hover">
          <div slot="header" class="card-header">
            <span class="card-title">预测情景列表</span>
            <el-tag type="info" size="small">{{ scenarios.length }} 个情景</el-tag>
          </div>
          
          <el-table v-if="scenarios.length > 0" :data="scenarios" style="width: 100%" border stripe>
            <el-table-column prop="name" label="情景名称" min-width="120" fixed="left"></el-table-column>
            <el-table-column prop="model_type" label="模型" width="100">
              <template slot-scope="scope">
                <el-tag :type="getModelTagType(scope.row.model_type)" size="small">
                  {{ scope.row.model_type.toUpperCase() }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="gdp_growth_rate" label="GDP增长" width="90" align="center">
              <template slot-scope="scope">
                {{ (scope.row.gdp_growth_rate * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="efficiency_improvement_rate" label="效率提升" width="90" align="center">
              <template slot-scope="scope">
                {{ (scope.row.efficiency_improvement_rate * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="renewable_increase_rate" label="可再生提升" width="95" align="center">
              <template slot-scope="scope">
                {{ ((scope.row.renewable_increase_rate || 0) * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column label="操作" width="70" align="center">
              <template slot-scope="scope">
                <el-button size="mini" type="danger" icon="el-icon-delete" circle @click="deleteScenario(scope.$index, scope.row)"></el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div v-else class="empty-scenarios">
            <i class="el-icon-document"></i>
            <p>暂无情景，请创建预测情景</p>
          </div>
          
          <div class="run-prediction">
            <el-button type="success" size="large" :disabled="scenarios.length === 0" @click="runPrediction" :loading="predicting">
              <i class="el-icon-caret-right"></i> 运行预测
            </el-button>
            <span class="prediction-hint">预测区间：2024年 - 2060年</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'
import ParameterRecommend from './ParameterRecommend.vue'

export default {
  name: 'ScenarioManager',
  components: { ParameterRecommend },
  data() {
    return {
      scenarioForm: {
        name: '',
        model_type: 'leap',
        gdp_growth_rate: 0.05,
        efficiency_improvement_rate: 0.03,
        renewable_increase_rate: 0.01,
        coal_decrease_rate: 0.02
      },
      rules: {
        name: [
          { required: true, message: '请输入情景名称', trigger: 'blur' },
          { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ]
      },
      scenarios: [],
      creating: false,
      predicting: false
    }
  },
  created() {
    this.loadScenarios()
    this.loadTrends()
  },
  methods: {
    applyRecommendedParams(params) {
      this.scenarioForm = {
        ...this.scenarioForm,
        gdp_growth_rate: params.gdp_growth_rate,
        efficiency_improvement_rate: params.efficiency_improvement_rate,
        renewable_increase_rate: params.renewable_increase_rate,
        coal_decrease_rate: params.coal_decrease_rate
      }
    },
    loadScenarios() {
      axios.get('/api/scenarios')
        .then(response => {
          const data = response.data
          this.scenarios = Object.keys(data).map(key => ({
            name: key,
            ...data[key]
          }))
          
          if (this.scenarios.length === 0) {
            this.createDefaultScenario()
          }
        })
        .catch(error => {
          console.error('加载情景失败:', error)
          this.$message.error('加载情景失败')
          this.createDefaultScenario()
        })
    },
    loadTrends() {
      axios.get('/api/data/trends')
        .then(response => {
          if (response.data.suggested_efficiency_rate) {
            this.scenarioForm.efficiency_improvement_rate = response.data.suggested_efficiency_rate
          }
        })
        .catch(() => {})
    },
    createDefaultScenario() {
      const defaultScenario = {
        name: '基准情景',
        model_type: 'leap',
        gdp_growth_rate: 0.05,
        efficiency_improvement_rate: 0.03,
        renewable_increase_rate: 0.01,
        coal_decrease_rate: 0.02
      }
      
      axios.post('/api/scenarios', defaultScenario)
        .then(() => {
          this.$message.success('已创建默认情景')
          this.loadScenarios()
        })
        .catch(error => {
          console.error('创建默认情景失败:', error)
        })
    },
    createScenario() {
      this.$refs.scenarioForm.validate(valid => {
        if (valid) {
          this.creating = true
          axios.post('/api/scenarios', this.scenarioForm)
            .then(() => {
              this.$message.success('情景创建成功')
              this.loadScenarios()
              this.resetForm()
            })
            .catch(error => {
              console.error('创建情景失败:', error)
              this.$message.error('创建情景失败')
            })
            .finally(() => {
              this.creating = false
            })
        }
      })
    },
    deleteScenario(index, row) {
      this.$confirm(`确认删除情景 "${row.name}"?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        axios.delete(`/api/scenarios/${encodeURIComponent(row.name)}`)
          .then(() => {
            this.$message.success('删除成功')
            this.loadScenarios()
          })
          .catch(error => {
            console.error('删除情景失败:', error)
            this.$message.error('删除情景失败')
          })
      }).catch(() => {})
    },
    resetForm() {
      this.$refs.scenarioForm.resetFields()
    },
    runPrediction() {
      if (this.scenarios.length === 0) {
        this.$message.warning('请先创建至少一个预测情景')
        return
      }
      
      const selectedScenarios = this.scenarios.map(s => s.name)
      
      this.$confirm('确认运行预测? 将预测至2060年', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }).then(() => {
        this.predicting = true
        const loadingInstance = this.$loading({
          lock: true,
          text: '预测计算中...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        
        axios.post('/api/predict', {
          scenarios: selectedScenarios,
          forecast_years: 36
        })
          .then(() => {
            loadingInstance.close()
            this.$message.success('预测完成')
            this.$emit('prediction-completed')
          })
          .catch(error => {
            loadingInstance.close()
            console.error('预测失败:', error)
            this.$message.error('预测失败')
          })
          .finally(() => {
            this.predicting = false
          })
      }).catch(() => {})
    },
    formatPercent(value) {
      return (value * 100).toFixed(1) + '%'
    },
    getModelTagType(type) {
      const types = {
        'leap': 'success',
        'kaya': 'primary',
        'stirpat': 'warning'
      }
      return types[type] || 'info'
    }
  }
}
</script>

<style scoped>
.scenario-manager {
  margin-bottom: 20px;
}

.recommend-section {
  margin-bottom: 20px;
}

.scenario-card, .scenario-list-card {
  height: 100%;
  border-radius: 14px;
  border: 1px solid rgba(15, 118, 110, 0.14);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 17px;
  font-weight: 800;
  color: #124e66;
}

.el-divider {
  margin: 16px 0;
}

.el-divider__text {
  color: #0f766e;
  font-weight: 700;
}

.empty-scenarios {
  text-align: center;
  padding: 42px 0;
  color: #6b7280;
}

.empty-scenarios i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #9ca3af;
}

.run-prediction {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px dashed rgba(15, 118, 110, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.prediction-hint {
  color: #64748b;
  font-size: 12px;
}

::v-deep .el-slider__input {
  width: 80px;
}

::v-deep .el-table th {
  background-color: rgba(20, 184, 166, 0.08);
  color: #124e66;
  font-weight: 700;
}

::v-deep .el-form-item__label {
  color: #23423a;
  font-weight: 700;
}

::v-deep .el-input__inner,
::v-deep .el-textarea__inner {
  border-radius: 10px;
  border-color: rgba(15, 118, 110, 0.24);
}

::v-deep .el-input__inner:hover,
::v-deep .el-textarea__inner:hover {
  border-color: rgba(15, 118, 110, 0.48);
}

::v-deep .el-slider__runway {
  height: 8px;
  border-radius: 99px;
  background: rgba(15, 118, 110, 0.16);
}

::v-deep .el-slider__bar {
  background: linear-gradient(90deg, #0f766e, #14b8a6);
}

::v-deep .el-slider__button {
  width: 18px;
  height: 18px;
  border: 2px solid #0f766e;
}

@media (max-width: 992px) {
  .scenario-manager ::v-deep .el-col {
    margin-bottom: 14px;
  }

  .run-prediction {
    flex-direction: column;
    align-items: stretch;
  }

  .prediction-hint {
    text-align: center;
  }
}
</style>
