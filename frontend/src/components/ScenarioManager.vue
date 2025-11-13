<template>
  <div class="scenario-manager">
    <el-row :gutter="20">
      <el-col :span="10">
        <el-card class="scenario-card">
          <div slot="header">
            <h2>创建预测情景</h2>
          </div>
          <el-form ref="scenarioForm" :model="scenarioForm" label-width="120px" :rules="rules">
            <el-form-item label="情景名称" prop="name">
              <el-input v-model="scenarioForm.name" placeholder="请输入情景名称"></el-input>
            </el-form-item>
            
            <el-form-item label="预测模型" prop="model_type">
              <el-select v-model="scenarioForm.model_type" placeholder="请选择预测模型">
                <el-option label="LEAP模型" value="leap"></el-option>
                <el-option label="Kaya模型" value="kaya"></el-option>
              </el-select>
              <span class="param-unit">（LEAP适合能源结构分析，Kaya适合因子分解）</span>
            </el-form-item>
            
            <el-form-item label="GDP增长率" prop="gdp_growth_rate">
              <el-input-number 
                v-model="scenarioForm.gdp_growth_rate" 
                :precision="3" 
                :step="0.005" 
                :min="0" 
                :max="0.2"
                controls-position="right">
              </el-input-number>
              <span class="param-unit">（如0.083表示8.3%/年，历史值）</span>
            </el-form-item>
            
            <el-form-item label="能源效率改善率" prop="efficiency_improvement_rate">
              <el-input-number 
                v-model="scenarioForm.efficiency_improvement_rate" 
                :precision="3" 
                :step="0.005" 
                :min="0" 
                :max="0.15"
                controls-position="right">
              </el-input-number>
              <span class="param-unit">（如0.05表示能源强度下降5%/年）</span>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="createScenario">创建情景</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :span="14">
        <el-card class="scenario-list-card">
          <div slot="header">
            <h2>预测情景列表</h2>
          </div>
          
          <el-table
            v-if="scenarios.length > 0"
            :data="scenarios"
            style="width: 100%"
            border>
            <el-table-column
              prop="name"
              label="情景名称"
              width="140">
            </el-table-column>
            <el-table-column
              prop="model_type"
              label="模型类型"
              width="100">
              <template slot-scope="scope">
                <el-tag :type="scope.row.model_type === 'leap' ? 'success' : 'primary'" size="small">
                  {{ scope.row.model_type === 'leap' ? 'LEAP' : scope.row.model_type === 'kaya' ? 'Kaya' : '未知' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              prop="gdp_growth_rate"
              label="GDP增长率"
              width="110">
              <template slot-scope="scope">
                {{ (scope.row.gdp_growth_rate * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column
              prop="efficiency_improvement_rate"
              label="能源效率改善率"
              width="140">
              <template slot-scope="scope">
                {{ (scope.row.efficiency_improvement_rate * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column
              label="操作">
              <template slot-scope="scope">
                <el-button
                  size="mini"
                  type="danger"
                  @click="deleteScenario(scope.$index, scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div v-else class="empty-scenarios">
            <i class="el-icon-loading"></i>
            <p>正在创建默认情景...</p>
          </div>
          
          <div class="run-prediction">
            <el-form :inline="true" class="prediction-form">
              <el-form-item label="预测年数">
                <el-input-number v-model="forecastYears" :min="5" :max="100" :step="5"></el-input-number>
              </el-form-item>
              <el-form-item>
                <el-button type="success" :disabled="scenarios.length === 0" @click="runPrediction">运行预测</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ScenarioManager',
  data() {
    return {
      scenarioForm: {
        name: '',
        model_type: 'leap',
        gdp_growth_rate: 0.083,
        efficiency_improvement_rate: 0.05
      },
      rules: {
        name: [
          { required: true, message: '请输入情景名称', trigger: 'blur' },
          { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ]
      },
      scenarios: [],
      forecastYears: 30
    }
  },
  created() {
    this.loadScenarios()
  },
  methods: {
    loadScenarios() {
      axios.get('/api/scenarios')
        .then(response => {
          const data = response.data
          this.scenarios = Object.keys(data).map(key => ({
            name: key,
            ...data[key]
          }))
          
          // 如果没有情景，自动创建一个默认情景
          if (this.scenarios.length === 0) {
            this.createDefaultScenario()
          }
        })
        .catch(error => {
          console.error('加载情景失败:', error)
          this.$message.error('加载情景失败')
          // 如果加载失败，也创建一个默认情景
          this.createDefaultScenario()
        })
    },
    createDefaultScenario() {
      const defaultScenario = {
        name: '历史趋势情景',
        model_type: 'leap',
        gdp_growth_rate: 0.083,
        efficiency_improvement_rate: 0.05
      }
      
      axios.post('/api/scenarios', defaultScenario)
        .then(() => {
          this.$message.success('已创建默认情景')
          this.loadScenarios()
        })
        .catch(error => {
          console.error('创建默认情景失败:', error)
          this.$message.error('创建默认情景失败')
        })
    },
    createScenario() {
      this.$refs.scenarioForm.validate(valid => {
        if (valid) {
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
        } else {
          return false
        }
      })
    },
    deleteScenario(index, row) {
      this.$confirm(`确认删除情景 "${row.name}"?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 调用API删除情景
        axios.delete(`/api/scenarios/${encodeURIComponent(row.name)}`)
          .then(() => {
            this.$message.success('删除成功')
            // 重新加载情景列表
            this.loadScenarios()
          })
          .catch(error => {
            console.error('删除情景失败:', error)
            this.$message.error('删除情景失败')
          })
      }).catch(() => {
        // 取消删除
      })
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
      
      this.$confirm('确认运行预测?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }).then(() => {
        const loadingInstance = this.$loading({
          lock: true,
          text: '预测计算中...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        
        axios.post('/api/predict', {
          scenarios: selectedScenarios,
          forecast_years: this.forecastYears
        })
          .then(() => {
            loadingInstance.close()
            this.$message.success('预测完成')
            // 发出预测完成事件，让父组件处理页面切换和刷新
            this.$emit('prediction-completed')
          })
          .catch(error => {
            loadingInstance.close()
            console.error('预测失败:', error)
            this.$message.error('预测失败')
          })
      }).catch(() => {
        // 取消预测
      })
    }
  }
}
</script>

<style scoped>
.scenario-manager {
  margin-bottom: 20px;
}

.scenario-card, .scenario-list-card {
  height: 100%;
}

.param-unit {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.empty-scenarios {
  text-align: center;
  padding: 30px 0;
  color: #909399;
}

.empty-scenarios i {
  font-size: 40px;
  margin-bottom: 10px;
}

.run-prediction {
  margin-top: 20px;
  text-align: right;
}
</style> 