<template>
  <div class="simple-predictor">
    <h1>简化版碳达峰预测系统</h1>
    
    <!-- 场景管理区 -->
    <div class="scenarios-section">
      <h2>场景设置</h2>
      
      <!-- 场景列表 -->
      <div class="scenarios-list">
        <div v-for="(scenario, index) in scenarios" :key="index" class="scenario-item">
          <span class="scenario-name">{{ scenario.name }} ({{ scenario.model_type.toUpperCase() }})</span>
          <button @click="deleteScenario(index)" class="btn-delete">删除</button>
        </div>
      </div>
      
      <!-- 新增场景表单 -->
      <div class="add-scenario-form">
        <h3>新增场景</h3>
        <div class="form-group">
          <label>场景名称:</label>
          <input v-model="newScenario.name" type="text" placeholder="例如：积极达峰场景">
        </div>
        
        <div class="form-group">
          <label>模型类型:</label>
          <select v-model="newScenario.model_type">
            <option value="leap">LEAP模型</option>
            <option value="kaya">Kaya模型</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>生产总值增长率 (%):</label>
          <input v-model.number="newScenario.gdp_growth_rate" type="number" step="0.01" min="0" max="1">
          <span class="hint">{{ (newScenario.gdp_growth_rate * 100).toFixed(1) }}%</span>
        </div>
        
        <div class="form-group">
          <label>能源效率改善率 (%):</label>
          <input v-model.number="newScenario.efficiency_improvement_rate" type="number" step="0.01" min="0" max="1">
          <span class="hint">{{ (newScenario.efficiency_improvement_rate * 100).toFixed(1) }}%</span>
        </div>
        
        <div class="form-group">
          <label>可再生能源占比提升率 (%):</label>
          <input v-model.number="newScenario.renewable_increase_rate" type="number" step="0.001" min="0" max="0.1">
          <span class="hint">{{ (newScenario.renewable_increase_rate * 100).toFixed(1) }}%/年</span>
        </div>
        
        <button @click="addScenario" class="btn-add">添加场景</button>
      </div>
      
      <!-- 预测按钮 -->
      <div class="predict-section">
        <div class="form-group">
          <label>预测年限:</label>
          <input v-model.number="forecastYears" type="number" min="5" max="50" step="5">
          <span class="hint">年</span>
        </div>
        <button @click="runPrediction" :disabled="scenarios.length === 0 || loading" class="btn-predict">
          {{ loading ? '预测中...' : '运行预测' }}
        </button>
      </div>
    </div>
    
    <!-- 图表展示区 -->
    <div v-if="predictionResults.length > 0" class="charts-section">
      <h2>预测结果</h2>
      
      <!-- 碳排放曲线图 -->
      <div class="chart-container">
        <h3>碳排放预测曲线</h3>
        <canvas ref="co2Chart"></canvas>
        <div class="peak-info">
          <div v-for="(result, index) in predictionResults" :key="index" class="peak-item">
            <strong>{{ result.name }}:</strong> 
            碳达峰年份 <span class="peak-year">{{ result.peak_year }}</span> 年, 
            峰值 <span class="peak-value">{{ result.peak_value.toFixed(2) }}</span> 万吨CO₂
          </div>
        </div>
      </div>
      
      <!-- 生产总值图表 -->
      <div class="chart-container">
        <h3>生产总值预测</h3>
        <canvas ref="gdpChart"></canvas>
      </div>
      
      <!-- 能耗图表 -->
      <div class="chart-container">
        <h3>能源消费预测（含能源结构）</h3>
        <canvas ref="energyChart"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js';

export default {
  name: 'SimplePredictor',
  data() {
    return {
      scenarios: [],
      newScenario: {
        name: '',
        model_type: 'leap',
        gdp_growth_rate: 0.05,
        efficiency_improvement_rate: 0.03,
        renewable_increase_rate: 0.015,
      },
      forecastYears: 30,
      loading: false,
      predictionResults: [],
      charts: {
        co2: null,
        gdp: null,
        energy: null,
      }
    };
  },
  mounted() {
    this.loadScenarios();
  },
  methods: {
    async loadScenarios() {
      try {
        const response = await fetch('http://localhost:5001/api/simple/scenarios');
        this.scenarios = await response.json();
      } catch (error) {
        console.error('加载场景失败:', error);
        alert('加载场景失败');
      }
    },
    
    async addScenario() {
      if (!this.newScenario.name) {
        alert('请输入场景名称');
        return;
      }
      
      try {
        const response = await fetch('http://localhost:5001/api/simple/scenarios', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.newScenario)
        });
        
        if (response.ok) {
          await this.loadScenarios();
          this.newScenario.name = '';
          alert('场景添加成功');
        }
      } catch (error) {
        console.error('添加场景失败:', error);
        alert('添加场景失败');
      }
    },
    
    async deleteScenario(index) {
      if (!confirm('确定要删除这个场景吗?')) return;
      
      try {
        const response = await fetch(`http://localhost:5001/api/simple/scenarios/${index}`, {
          method: 'DELETE'
        });
        
        if (response.ok) {
          await this.loadScenarios();
        }
      } catch (error) {
        console.error('删除场景失败:', error);
        alert('删除场景失败');
      }
    },
    
    async runPrediction() {
      if (this.scenarios.length === 0) {
        alert('请先添加至少一个场景');
        return;
      }
      
      this.loading = true;
      
      try {
        const response = await fetch('http://localhost:5001/api/simple/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ forecast_years: this.forecastYears })
        });
        
        this.predictionResults = await response.json();
        
        // 等待DOM更新后绘制图表
        this.$nextTick(() => {
          this.drawCharts();
        });
        
      } catch (error) {
        console.error('预测失败:', error);
        alert('预测失败: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    drawCharts() {
      this.drawCO2Chart();
      this.drawGDPChart();
      this.drawEnergyChart();
    },
    
    drawCO2Chart() {
      if (this.charts.co2) {
        this.charts.co2.destroy();
      }
      
      const ctx = this.$refs.co2Chart.getContext('2d');
      const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6'];
      
      const datasets = this.predictionResults.map((result, index) => {
        const allYears = [...result.historical.years, ...result.forecast.years];
        const allCO2 = [...result.historical.co2, ...result.forecast.co2];
        
        // 计算点的大小数组
        const pointRadii = allYears.map(year => year === result.peak_year ? 8 : 3);
        
        return {
          label: `${result.name} (${result.model_type.toUpperCase()})`,
          data: allCO2,
          borderColor: colors[index % colors.length],
          backgroundColor: colors[index % colors.length] + '20',
          lineTension: 0.3,
          fill: false,
          pointRadius: pointRadii
        };
      });
      
      // 使用第一个结果的年份作为labels
      const allYears = [...this.predictionResults[0].historical.years, ...this.predictionResults[0].forecast.years];
      
      this.charts.co2 = new Chart(ctx, {
        type: 'line',
        data: {
          labels: allYears,
          datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          legend: {
            display: true,
            position: 'bottom'
          },
          scales: {
            xAxes: [{
              scaleLabel: {
                display: true,
                labelString: '年份'
              }
            }],
            yAxes: [{
              scaleLabel: {
                display: true,
                labelString: '碳排放 (万吨CO₂)'
              }
            }]
          }
        }
      });
    },
    
    drawGDPChart() {
      if (this.charts.gdp) {
        this.charts.gdp.destroy();
      }
      
      const ctx = this.$refs.gdpChart.getContext('2d');
      const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6'];
      
      const datasets = this.predictionResults.map((result, index) => {
        const allYears = [...result.historical.years, ...result.forecast.years];
        const allGDP = [...result.historical.gdp, ...result.forecast.gdp];
        
        return {
          label: result.name,
          data: allGDP.map(gdp => gdp / 10000), // 转换为亿元
          borderColor: colors[index % colors.length],
          backgroundColor: colors[index % colors.length] + '20',
          lineTension: 0.3,
          fill: false
        };
      });
      
      const allYears = [...this.predictionResults[0].historical.years, ...this.predictionResults[0].forecast.years];
      
      this.charts.gdp = new Chart(ctx, {
        type: 'line',
        data: {
          labels: allYears,
          datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          legend: {
            display: true,
            position: 'bottom'
          },
          scales: {
            xAxes: [{
              scaleLabel: {
                display: true,
                labelString: '年份'
              }
            }],
            yAxes: [{
              scaleLabel: {
                display: true,
                labelString: '生产总值 (亿元)'
              }
            }]
          }
        }
      });
    },
    
    drawEnergyChart() {
      if (this.charts.energy) {
        this.charts.energy.destroy();
      }
      
      const ctx = this.$refs.energyChart.getContext('2d');
      
      // 选择第一个场景的数据来显示能源结构
      const result = this.predictionResults[0];
      const allYears = [...result.historical.years, ...result.forecast.years];
      
      // 历史数据：假设全部为非可再生能源
      const historicalNonRenewable = result.historical.energy;
      const historicalRenewable = result.historical.energy.map(() => 0);
      
      // 预测数据
      const forecastNonRenewable = result.forecast.nonrenewable_energy;
      const forecastRenewable = result.forecast.renewable_energy;
      
      // 合并数据
      const allNonRenewable = [...historicalNonRenewable, ...forecastNonRenewable];
      const allRenewable = [...historicalRenewable, ...forecastRenewable];
      
      this.charts.energy = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: allYears,
          datasets: [
            {
              label: '非可再生能源',
              data: allNonRenewable,
              backgroundColor: '#95a5a6'
            },
            {
              label: '可再生能源 (零排放)',
              data: allRenewable,
              backgroundColor: '#2ecc71'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          title: {
            display: true,
            text: `能源结构 (${result.name})`
          },
          legend: {
            display: true,
            position: 'bottom'
          },
          scales: {
            xAxes: [{
              stacked: true,
              scaleLabel: {
                display: true,
                labelString: '年份'
              }
            }],
            yAxes: [{
              stacked: true,
              scaleLabel: {
                display: true,
                labelString: '能源消费 (万吨标煤)'
              },
              ticks: {
                beginAtZero: true
              }
            }]
          }
        }
      });
    }
  }
};
</script>

<style scoped>
.simple-predictor {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 30px;
}

h2 {
  color: #34495e;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
  margin-top: 30px;
}

h3 {
  color: #7f8c8d;
  margin-top: 20px;
}

.scenarios-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.scenarios-list {
  margin: 20px 0;
}

.scenario-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-bottom: 10px;
}

.scenario-name {
  font-weight: 500;
  color: #2c3e50;
}

.add-scenario-form {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #34495e;
}

.form-group input,
.form-group select {
  width: 300px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group .hint {
  margin-left: 10px;
  color: #7f8c8d;
  font-size: 14px;
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-add {
  background: #3498db;
  color: white;
}

.btn-add:hover {
  background: #2980b9;
}

.btn-delete {
  background: #e74c3c;
  color: white;
}

.btn-delete:hover {
  background: #c0392b;
}

.predict-section {
  margin-top: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
}

.btn-predict {
  background: #2ecc71;
  color: white;
  font-size: 16px;
  padding: 12px 30px;
  margin-top: 10px;
}

.btn-predict:hover:not(:disabled) {
  background: #27ae60;
}

.btn-predict:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.charts-section {
  margin-top: 30px;
}

.chart-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-container canvas {
  max-height: 400px;
}

.peak-info {
  margin-top: 20px;
  padding: 15px;
  background: #ecf0f1;
  border-radius: 5px;
}

.peak-item {
  margin: 8px 0;
  font-size: 15px;
}

.peak-year {
  color: #e74c3c;
  font-weight: bold;
  font-size: 18px;
}

.peak-value {
  color: #3498db;
  font-weight: bold;
}
</style>
