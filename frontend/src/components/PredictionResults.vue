<template>
  <div class="prediction-results">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="chart-card">
          <div slot="header">
            <h2>碳排放达峰预测</h2>
          </div>
          <div v-if="loading" class="loading-container">
            <i class="el-icon-loading"></i>
            <p>正在生成预测结果，请稍候...</p>
          </div>
          <div v-else-if="error" class="error-container">
            <i class="el-icon-warning"></i>
            <p>{{ error }}</p>
            <el-button type="primary" @click="runAutoPrediction">重新运行预测</el-button>
          </div>
          <div v-else class="chart-container">
            <div id="carbon-peak-chart" class="echarts-container" ref="carbonChart"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">
            <h2>工业生产总值</h2>
          </div>
          <div v-if="loading" class="loading-container">
            <i class="el-icon-loading"></i>
            <p>加载中...</p>
          </div>
          <div v-else-if="error" class="error-container">
            <i class="el-icon-warning"></i>
            <p>{{ error }}</p>
          </div>
          <div v-else class="chart-container">
            <div id="gdp-chart" class="echarts-container" ref="gdpChart"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">
            <h2>综合能源消费量</h2>
          </div>
          <div v-if="loading" class="loading-container">
            <i class="el-icon-loading"></i>
            <p>加载中...</p>
          </div>
          <div v-else-if="error" class="error-container">
            <i class="el-icon-warning"></i>
            <p>{{ error }}</p>
          </div>
          <div v-else class="chart-container">
            <div id="energy-consumption-chart" class="echarts-container" ref="energyConsumptionChart"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="data-card">
          <div slot="header">
            <div class="header-with-select">
              <h2>预测数据详情</h2>
              <el-select v-model="selectedScenario" placeholder="选择情景" @change="loadScenarioResults">
                <el-option
                  v-for="scenario in scenarios"
                  :key="scenario"
                  :label="scenario"
                  :value="scenario">
                </el-option>
              </el-select>
            </div>
          </div>
          <div v-if="loadingData" class="loading-container">
            <i class="el-icon-loading"></i>
            <p>加载中...</p>
          </div>
          <div v-else-if="dataError" class="error-container">
            <i class="el-icon-warning"></i>
            <p>{{ dataError }}</p>
          </div>
          <div v-else>
            <el-table
              v-if="scenarioResults.length > 0"
              :data="scenarioResults"
              style="width: 100%"
              height="400"
              border>
              <el-table-column
                prop="year"
                label="年份"
                width="100"
                fixed="left">
              </el-table-column>
              <el-table-column
                prop="data_type"
                label="数据类型"
                width="100"
                fixed="left">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.data_type === 'historical' ? 'info' : 'success'" size="small">
                    {{ scope.row.data_type === 'historical' ? '历史' : '预测' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="energy_consumption"
                label="综合能源消费量(万吨标准煤)"
                width="200">
                <template slot-scope="scope">
                  {{ scope.row.energy_consumption ? scope.row.energy_consumption.toFixed(2) : 'N/A' }}
                </template>
              </el-table-column>
              <el-table-column
                prop="gdp"
                label="工业总产值(现价)(万元)"
                width="200">
                <template slot-scope="scope">
                  {{ scope.row.gdp ? scope.row.gdp.toFixed(2) : 'N/A' }}
                </template>
              </el-table-column>
              <el-table-column
                prop="co2_emission"
                label="二氧化碳排放量合计(万吨二氧化碳当量)"
                width="280">
                <template slot-scope="scope">
                  {{ scope.row.co2_emission ? scope.row.co2_emission.toFixed(2) : 'N/A' }}
                </template>
              </el-table-column>
            </el-table>
            <div v-else class="empty-data">
              <i class="el-icon-info"></i>
              <p>暂无预测数据，请先运行预测</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row style="margin-top: 20px;">
      <el-col :span="24" style="text-align: center;">
        <el-button type="primary" @click="downloadResults">下载预测结果</el-button>
        <el-button type="success" @click="saveCharts">导出图表</el-button>
        <el-button @click="goToScenarios">返回情景设置</el-button>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  name: 'PredictionResults',
  data() {
    return {
      loading: true,
      error: null,
      chartData: {},
      carbonPeakChart: null,
      gdpChart: null,
      energyConsumptionChart: null,
      scenarios: [],
      selectedScenario: '',
      scenarioResults: [],
      loadingData: false,
      dataError: null,
      forecastYears: 30
    }
  },
  watch: {
    // 监听父组件的activeTab变化
    '$parent.$parent.activeTab'(newTab) {
      if (newTab === 'results') {
        this.$nextTick(() => {
          setTimeout(() => {
            this.forceResizeCharts()
          }, 200)
        })
      }
    }
  },
  created() {
    this.checkPredictionStatus()
  },
  activated() {
    // 当组件被激活时（比如从其他tab切换过来），重新检查预测状态
    this.checkPredictionStatus()

    // 强制resize图表
    this.$nextTick(() => {
      this.forceResizeCharts()
    })
  },
  mounted() {
    // 组件挂载后，监听窗口大小变化
    this.handleResize = () => {
      if (this.carbonPeakChart) {
        this.carbonPeakChart.resize()
      }
      if (this.gdpChart) {
        this.gdpChart.resize()
      }
      if (this.energyConsumptionChart) {
        this.energyConsumptionChart.resize()
      }
    }
    window.addEventListener('resize', this.handleResize)

    // 监听页面可见性变化
    this.handleVisibilityChange = () => {
      if (!document.hidden) {
        setTimeout(() => {
          this.forceResizeCharts()
        }, 100)
      }
    }
    document.addEventListener('visibilitychange', this.handleVisibilityChange)

    // 监听tab切换
    this.handleTabChange = () => {
      setTimeout(() => {
        this.forceResizeCharts()
      }, 100)
    }

    // 使用ResizeObserver监听容器尺寸变化
    if (window.ResizeObserver) {
      this.resizeObserver = new ResizeObserver(() => {
        this.forceResizeCharts()
      })
    }

    // 使用IntersectionObserver监听容器可见性
    if (window.IntersectionObserver) {
      this.intersectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setTimeout(() => {
              this.forceResizeCharts()
            }, 100)
          }
        })
      }, { threshold: 0.1 })
    }
  },
  beforeDestroy() {
    // 组件销毁前，移除事件监听器
    if (this.handleResize) {
      window.removeEventListener('resize', this.handleResize)
    }
    if (this.handleVisibilityChange) {
      document.removeEventListener('visibilitychange', this.handleVisibilityChange)
    }
    if (this.resizeObserver) {
      this.resizeObserver.disconnect()
    }
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect()
    }
    // 销毁图表实例
    if (this.carbonPeakChart) {
      this.carbonPeakChart.dispose()
    }
    if (this.gdpChart) {
      this.gdpChart.dispose()
    }
    if (this.energyConsumptionChart) {
      this.energyConsumptionChart.dispose()
    }
  },
  methods: {
    checkPredictionStatus() {
      this.loading = true
      this.error = null
      
      // 检查是否已有预测结果
      axios.post('/api/predict/status')
        .then(response => {
          this.scenarios = response.data.scenarios || []
          if (this.scenarios.length > 0) {
            this.selectedScenario = this.scenarios[0]
            this.loadScenarioResults()
            this.loadChartData()
          } else {
            // 如果没有预测结果，自动运行预测
            this.runAutoPrediction()
          }
        })
        .catch(error => {
          console.error('检查预测状态失败:', error)
          // 如果检查失败，尝试自动运行预测
          this.runAutoPrediction()
        })
    },
    loadChartData() {
      axios.get('/api/chart-data')
        .then(response => {
          // 验证响应数据是否为对象
          if (typeof response.data === 'string') {
            console.error('API returned string instead of object:', response.data.substring(0, 100))
            this.error = 'API返回数据格式错误'
            this.loading = false
            return
          }
          
          if (response.data && response.data.error) {
            this.error = response.data.error
            this.loading = false
            return
          }
          
          this.chartData = response.data || {}
          console.log('Chart data loaded:', this.chartData)
          this.loading = false
          
          if (Object.keys(this.chartData).length > 0) {
            // 在DOM更新后初始化图表
            this.$nextTick(() => {
              try {
                this.initCarbonPeakChart()
              } catch (e) {
                console.error('Carbon peak chart init failed:', e)
              }
              
              try {
                this.initGdpChart()
              } catch (e) {
                console.error('GDP chart init failed:', e)
              }
              
              try {
                this.initEnergyConsumptionChart()
              } catch (e) {
                console.error('Energy consumption chart init failed:', e)
              }

              // 使用多个延时确保图表正确显示
              setTimeout(() => {
                this.forceResizeCharts()
              }, 100)

              setTimeout(() => {
                this.forceResizeCharts()
              }, 300)

              setTimeout(() => {
                this.forceResizeCharts()
                // 启动ResizeObserver
                this.startResizeObserver()
              }, 500)
            })
          }
        })
        .catch(error => {
          console.error('加载图表数据失败:', error)
          this.error = '加载图表数据失败，请检查后端服务是否正常运行'
          this.loading = false
        })
    },
    initCarbonPeakChart() {
      // 初始化碳排放达峰图表
      const chartDom = document.getElementById('carbon-peak-chart')
      if (!chartDom) {
        console.error('Chart container not found')
        return
      }

      // 确保容器有尺寸
      if (chartDom.offsetWidth === 0 || chartDom.offsetHeight === 0) {
        console.warn('Chart container has no size, retrying...')
        setTimeout(() => this.initCarbonPeakChart(), 100)
        return
      }

      this.carbonPeakChart = echarts.init(chartDom)
      
      // 准备图表数据
      const series = []
      const markPoints = []
      
      // 添加历史数据系列（只添加一次）
      const firstScenario = Object.keys(this.chartData)[0]
      if (firstScenario && this.chartData[firstScenario].historical_years && 
          this.chartData[firstScenario].historical_years.length > 0 &&
          this.chartData[firstScenario].emissions) {
        const historicalYears = this.chartData[firstScenario].historical_years
        const historicalEmissions = this.chartData[firstScenario].historical_emissions || []
        
        series.push({
          name: '历史数据',
          type: 'line',
          data: historicalYears.map((year, i) => [year, historicalEmissions[i]]),
          lineStyle: {
            width: 2.5,
            type: 'dashed',
            color: '#333333'
          },
          symbol: 'rect',
          symbolSize: 6,
          itemStyle: {
            color: '#333333'
          },
          z: 10  // 确保在最上层
        })
      }
      
      // 为每个情景添加一条线和一个标记点
      Object.keys(this.chartData).forEach((scenarioName, index) => {
        const data = this.chartData[scenarioName]
        if (!data || !data.years || !data.emissions || !data.peak) {
          console.warn(`Incomplete data for scenario: ${scenarioName}`)
          return
        }
        const years = data.years
        const emissions = data.emissions
        const peak = data.peak
        
        // 线数据
        series.push({
          name: scenarioName,
          type: 'line',
          data: years.map((year, i) => [year, emissions[i]]),
          smooth: true,
          lineStyle: {
            width: 3
          },
          symbol: 'circle',
          symbolSize: 8,
          emphasis: {
            focus: 'series',
            scale: true,
            lineStyle: {
              width: 4
            }
          }
        })
        
        // 峰值点标记
        markPoints.push({
          name: `${scenarioName}峰值`,
          coord: [peak.year, peak.value],
          value: `${peak.year}年: ${peak.value.toFixed(2)}万吨`,
          itemStyle: {
            color: this.getColorByIndex(index)
          }
        })
      })
      
      // 图表选项
      const legendNames = series.map(s => s.name)
      const option = {
        title: {
          text: '碳排放达峰预测',
          left: 'center',
          top: 10,
          textStyle: {
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderColor: '#ccc',
          borderWidth: 1,
          textStyle: {
            color: '#333'
          },
          formatter: function(params) {
            const year = params[0].value[0]
            let result = `<div style="font-weight:bold;margin-bottom:5px;">${year}年</div>`
            
            params.forEach(param => {
              const scenarioName = param.seriesName
              const emission = param.value[1].toFixed(2)
              const color = param.color
              result += `<div style="display:flex;align-items:center;margin:3px 0">
                <span style="display:inline-block;width:10px;height:10px;background:${color};margin-right:6px;border-radius:50%"></span>
                <span style="margin-right:8px;">${scenarioName}:</span>
                <span style="font-weight:bold">${emission}万吨</span>
              </div>`
            })
            
            return result
          },
          axisPointer: {
            type: 'cross',
            lineStyle: {
              color: '#aaa',
              width: 1,
              type: 'dashed'
            }
          }
        },
        legend: {
          data: legendNames,
          bottom: 10,
          icon: 'roundRect',
          itemWidth: 12,
          itemHeight: 12,
          textStyle: {
            fontSize: 12
          }
        },
        grid: {
          left: '5%',
          right: '5%',
          top: '15%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: '年份',
          nameLocation: 'middle',
          nameGap: 30,
          nameTextStyle: {
            fontWeight: 'bold'
          },
          min: 2019,
          max: 2060,
          minorTick: {
            show: true
          },
          minorSplitLine: {
            show: true,
            lineStyle: {
              color: '#f5f5f5'
            }
          },
          axisLabel: {
            formatter: '{value}',
            fontWeight: 'bold'
          },
          axisLine: {
            lineStyle: {
              color: '#333'
            }
          },
          splitLine: {
            lineStyle: {
              color: '#eee'
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '碳排放量(万吨)',
          nameLocation: 'middle',
          nameGap: 50,
          nameTextStyle: {
            fontWeight: 'bold'
          },
          axisLabel: {
            formatter: '{value}',
            fontWeight: 'bold'
          },
          axisLine: {
            lineStyle: {
              color: '#333'
            }
          },
          splitLine: {
            lineStyle: {
              color: '#eee'
            }
          }
        },
        series: series.map((serie, index) => {
          // 历史数据系列不需要markPoint
          if (serie.name === '历史数据') {
            return serie;
          }
          
          // 计算markPoint的正确索引（考虑历史数据系列）
          const hasHistorical = series[0] && series[0].name === '历史数据';
          const markPointIndex = hasHistorical ? index - 1 : index;
          
          if (markPointIndex < 0 || markPointIndex >= markPoints.length) {
            return serie;
          }
          
          return {
            ...serie,
            markPoint: {
              data: [markPoints[markPointIndex]],
              symbol: 'pin',
              symbolSize: 60,
              itemStyle: {
                shadowColor: 'rgba(0, 0, 0, 0.3)',
                shadowBlur: 10,
                shadowOffsetX: 2,
                shadowOffsetY: 2
              },
              label: {
                formatter: function(params) {
                  return `${params.data.coord[0]}年`;
                },
                position: 'top',
                fontSize: 12,
                fontWeight: 'bold'
              },
              emphasis: {
                label: {
                  formatter: '{c}',
                  show: true,
                  fontSize: 12
                },
                itemStyle: {
                  shadowBlur: 20
                }
              }
            },
            markLine: {
              silent: true,
              lineStyle: {
                color: this.getColorByIndex(markPointIndex),
                type: 'dashed',
                opacity: 0.5
              },
              data: [
                {
                  xAxis: markPoints[markPointIndex].coord[0],
                  label: {
                    formatter: function(params) {
                      return `${params.value}年`;
                    },
                    position: 'end'
                  }
                }
              ]
            }
          };
        })
      }
      
      // 设置图表选项
      this.carbonPeakChart.setOption(option)

      // 初始化后立即调用resize确保图表正确显示
      this.$nextTick(() => {
        if (this.carbonPeakChart) {
          this.carbonPeakChart.resize()
        }
      })

      setTimeout(() => {
        if (this.carbonPeakChart) {
          this.carbonPeakChart.resize()
        }
      }, 100)

      setTimeout(() => {
        if (this.carbonPeakChart) {
          this.carbonPeakChart.resize()
        }
      }, 300)
    },
    initGdpChart() {
      const chartDom = document.getElementById('gdp-chart')
      if (!chartDom) {
        console.error('GDP chart container not found')
        return
      }

      if (chartDom.offsetWidth === 0 || chartDom.offsetHeight === 0) {
        console.warn('GDP chart container has no size, retrying...')
        setTimeout(() => this.initGdpChart(), 100)
        return
      }

      this.gdpChart = echarts.init(chartDom)
      
      // 准备图表数据
      const series = []
      
      // 添加历史数据系列
      const firstScenario = Object.keys(this.chartData)[0]
      if (firstScenario && this.chartData[firstScenario].historical_years && 
          this.chartData[firstScenario].historical_years.length > 0 &&
          this.chartData[firstScenario].gdp) {
        const historicalYears = this.chartData[firstScenario].historical_years
        const historicalGdp = this.chartData[firstScenario].historical_gdp || []
        
        if (historicalGdp.length > 0) {
          series.push({
            name: '历史数据',
            type: 'line',
            data: historicalYears.map((year, i) => [year, historicalGdp[i]]),
            lineStyle: {
              width: 2.5,
              type: 'dashed',
              color: '#333333'
            },
            symbol: 'rect',
            symbolSize: 6,
            itemStyle: {
              color: '#333333'
            },
            z: 10
          })
        }
      }
      
      Object.keys(this.chartData).forEach((scenarioName) => {
        const data = this.chartData[scenarioName]
        if (!data || !data.years) {
          console.warn(`Incomplete data for scenario: ${scenarioName}`)
          return
        }
        const years = data.years
        const gdpData = data.gdp || []
        
        if (gdpData.length > 0) {
          series.push({
            name: scenarioName,
            type: 'line',
            data: years.map((year, i) => [year, gdpData[i] || 0]),
            smooth: true,
            lineStyle: { width: 3 },
            symbol: 'circle',
            symbolSize: 8
          })
        }
      })
      
      const legendNames = series.map(s => s.name)
      const option = {
        title: {
          text: '工业生产总值预测',
          left: 'center',
          textStyle: { fontSize: 16, fontWeight: 'bold' }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderColor: '#ccc',
          borderWidth: 1
        },
        legend: {
          data: legendNames,
          bottom: 10
        },
        grid: { left: '10%', right: '5%', top: '15%', bottom: '15%', containLabel: true },
        xAxis: {
          type: 'value',
          name: '年份',
          nameLocation: 'middle',
          nameGap: 30,
          min: 2019,
          max: 2060
        },
        yAxis: {
          type: 'value',
          name: '工业总产值(万元)',
          nameLocation: 'middle',
          nameGap: 50
        },
        series: series
      }
      
      this.gdpChart.setOption(option)
      this.$nextTick(() => {
        if (this.gdpChart) this.gdpChart.resize()
      })
    },
    initEnergyConsumptionChart() {
      const chartDom = document.getElementById('energy-consumption-chart')
      if (!chartDom) {
        console.error('Energy consumption chart container not found')
        return
      }

      if (chartDom.offsetWidth === 0 || chartDom.offsetHeight === 0) {
        console.warn('Energy consumption chart container has no size, retrying...')
        setTimeout(() => this.initEnergyConsumptionChart(), 100)
        return
      }

      this.energyConsumptionChart = echarts.init(chartDom)
      
      const series = []
      
      // 添加历史数据系列
      const firstScenario = Object.keys(this.chartData)[0]
      if (firstScenario && this.chartData[firstScenario].historical_years && 
          this.chartData[firstScenario].historical_years.length > 0 &&
          this.chartData[firstScenario].energy_mix && 
          this.chartData[firstScenario].energy_mix.total) {
        const historicalYears = this.chartData[firstScenario].historical_years
        const historicalEnergy = this.chartData[firstScenario].historical_energy || []
        
        if (historicalEnergy.length > 0) {
          series.push({
            name: '历史数据',
            type: 'line',
            data: historicalYears.map((year, i) => [year, historicalEnergy[i]]),
            lineStyle: {
              width: 2.5,
              type: 'dashed',
              color: '#333333'
            },
            symbol: 'rect',
            symbolSize: 6,
            itemStyle: {
              color: '#333333'
            },
            z: 10
          })
        }
      }
      
      Object.keys(this.chartData).forEach((scenarioName) => {
        const data = this.chartData[scenarioName]
        if (!data || !data.years) {
          console.warn(`Incomplete data for scenario: ${scenarioName}`)
          return
        }
        const years = data.years
        const energyData = data.energy_mix && data.energy_mix.total ? data.energy_mix.total : years.map(() => 0)
        
        series.push({
          name: scenarioName,
          type: 'line',
          data: years.map((year, i) => [year, energyData[i] || 0]),
          smooth: true,
          lineStyle: { width: 3 },
          symbol: 'circle',
          symbolSize: 8
        })
      })
      
      const legendNames = series.map(s => s.name)
      const option = {
        title: {
          text: '综合能源消费量预测',
          left: 'center',
          textStyle: { fontSize: 16, fontWeight: 'bold' }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderColor: '#ccc',
          borderWidth: 1
        },
        legend: {
          data: legendNames,
          bottom: 10
        },
        grid: { left: '10%', right: '5%', top: '15%', bottom: '15%', containLabel: true },
        xAxis: {
          type: 'value',
          name: '年份',
          nameLocation: 'middle',
          nameGap: 30,
          min: 2019,
          max: 2060
        },
        yAxis: {
          type: 'value',
          name: '综合能源消赹量(万吨标准煤)',
          nameLocation: 'middle',
          nameGap: 50
        },
        series: series
      }
      
      this.energyConsumptionChart.setOption(option)
      this.$nextTick(() => {
        if (this.energyConsumptionChart) this.energyConsumptionChart.resize()
      })
    },
    getColorByIndex(index) {
      // 预定义一组颜色
      const colors = [
        '#409EFF', // 蓝色
        '#67C23A', // 绿色
        '#E6A23C', // 橙色
        '#F56C6C', // 红色
        '#909399', // 灰色
        '#9966CC', // 紫色
        '#00CCFF', // 天蓝
        '#FF9900'  // 橙黄
      ]
      return colors[index % colors.length]
    },
    runAutoPrediction() {
      this.loading = true
      this.error = null
      
      // 先获取所有情景
      axios.get('/api/scenarios')
        .then(response => {
          const scenarios = Object.keys(response.data)
          if (scenarios.length === 0) {
            // 如果没有情景，显示错误信息
            this.loading = false
            this.error = '没有可用的预测情景，请先创建情景'
            return
          }
          
          // 使用所有情景运行预测
          const loadingInstance = this.$loading({
            lock: true,
            text: '正在运行预测，请稍候...',
            spinner: 'el-icon-loading',
            background: 'rgba(0, 0, 0, 0.7)'
          })
          
          axios.post('/api/predict', {
            scenarios: scenarios,
            forecast_years: this.forecastYears
          })
            .then(() => {
              loadingInstance.close()
              this.$message.success('预测完成')
              // 重新加载结果
              this.checkPredictionStatus()
            })
            .catch(error => {
              loadingInstance.close()
              console.error('预测失败:', error)
              this.loading = false
              this.error = '预测失败，请检查后端服务是否正常运行'
            })
        })
        .catch(error => {
          console.error('获取情景失败:', error)
          this.loading = false
          this.error = '获取情景失败，请检查后端服务是否正常运行'
        })
    },
    loadScenarioResults() {
      if (!this.selectedScenario) return
      
      this.loadingData = true
      this.dataError = null
      
      axios.get(`/api/results/${this.selectedScenario}`)
        .then(response => {
          this.scenarioResults = response.data
          this.loadingData = false
        })
        .catch(error => {
          console.error('加载情景数据失败:', error)
          this.dataError = '加载情景数据失败'
          this.loadingData = false
        })
    },
    downloadResults() {
      if (!this.selectedScenario) {
        this.$message.warning('请先选择一个情景')
        return
      }

      // 创建下载链接
      const link = document.createElement('a')
      link.href = `/api/results/${this.selectedScenario}/download`
      link.download = `${this.selectedScenario}_预测结果.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    forceResizeCharts() {
      // 强制resize所有图表
      const resizeChart = (chart) => {
        if (chart) {
          try {
            chart.resize()
          } catch (e) {
            console.warn('Chart resize failed:', e)
          }
        }
      }

      // 立即resize
      resizeChart(this.carbonPeakChart)
      resizeChart(this.gdpChart)
      resizeChart(this.energyConsumptionChart)

      // 延时resize
      setTimeout(() => {
        resizeChart(this.carbonPeakChart)
        resizeChart(this.gdpChart)
        resizeChart(this.energyConsumptionChart)
      }, 100)

      setTimeout(() => {
        resizeChart(this.carbonPeakChart)
        resizeChart(this.gdpChart)
        resizeChart(this.energyConsumptionChart)
      }, 300)

      setTimeout(() => {
        resizeChart(this.carbonPeakChart)
        resizeChart(this.gdpChart)
        resizeChart(this.energyConsumptionChart)
      }, 500)
    },
    startResizeObserver() {
      if (this.resizeObserver) {
        const carbonContainer = document.getElementById('carbon-peak-chart')
        const gdpContainer = document.getElementById('gdp-chart')
        const energyConsumptionContainer = document.getElementById('energy-consumption-chart')

        if (carbonContainer) {
          this.resizeObserver.observe(carbonContainer)
        }
        if (gdpContainer) {
          this.resizeObserver.observe(gdpContainer)
        }
        if (energyConsumptionContainer) {
          this.resizeObserver.observe(energyConsumptionContainer)
        }
      }

      if (this.intersectionObserver) {
        const carbonContainer = document.getElementById('carbon-peak-chart')
        const gdpContainer = document.getElementById('gdp-chart')
        const energyConsumptionContainer = document.getElementById('energy-consumption-chart')

        if (carbonContainer) {
          this.intersectionObserver.observe(carbonContainer)
        }
        if (gdpContainer) {
          this.intersectionObserver.observe(gdpContainer)
        }
        if (energyConsumptionContainer) {
          this.intersectionObserver.observe(energyConsumptionContainer)
        }
      }
    },
    saveCharts() {
      if (this.carbonPeakChart) {
        const url = this.carbonPeakChart.getDataURL({
          type: 'png',
          pixelRatio: 2,
          backgroundColor: '#fff'
        })
        const link = document.createElement('a')
        link.download = '碳排放达峰预测.png'
        link.href = url
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
      
      if (this.gdpChart) {
        setTimeout(() => {
          const url = this.gdpChart.getDataURL({
            type: 'png',
            pixelRatio: 2,
            backgroundColor: '#fff'
          })
          const link = document.createElement('a')
          link.download = '工业生产总值.png'
          link.href = url
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        }, 100)
      }

      if (this.energyConsumptionChart) {
        setTimeout(() => {
          const url = this.energyConsumptionChart.getDataURL({
            type: 'png',
            pixelRatio: 2,
            backgroundColor: '#fff'
          })
          const link = document.createElement('a')
          link.download = '综合能源消费量.png'
          link.href = url
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        }, 200)
      }
    },
    goToScenarios() {
      this.$parent.$parent.activeTab = 'scenarios'
    }
  }
}
</script>

<style scoped>
.prediction-results {
  margin-bottom: 20px;
}

.chart-card, .data-card {
  margin-bottom: 20px;
}

.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.echarts-container {
  width: 100% !important;
  height: 500px !important;
  min-width: 600px !important;
  min-height: 400px !important;
}

.loading-container, .error-container, .empty-data {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  color: #909399;
}

.loading-container i, .error-container i, .empty-data i {
  font-size: 40px;
  margin-bottom: 10px;
}

.header-with-select {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-with-select h2 {
  margin: 0;
}
</style> 
