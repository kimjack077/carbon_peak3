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
      <el-col :span="24">
        <el-card class="chart-card">
          <div slot="header">
            <div class="header-with-select">
              <h2>能源结构变化</h2>
              <el-select v-model="selectedScenarioForEnergyMix" placeholder="选择情景" @change="updateEnergyMixChart">
                <el-option
                  v-for="scenarioName in Object.keys(chartData)"
                  :key="scenarioName"
                  :label="scenarioName"
                  :value="scenarioName">
                </el-option>
              </el-select>
            </div>
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
            <div id="energy-mix-chart" class="echarts-container" ref="energyChart"></div>
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
                width="80">
              </el-table-column>
              <el-table-column
                prop="gdp"
                label="GDP(万亿元)"
                width="120">
                <template slot-scope="scope">
                  {{ scope.row.gdp.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="population"
                label="人口(万人)"
                width="120">
                <template slot-scope="scope">
                  {{ scope.row.population.toFixed(0) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="energy_consumption"
                label="能源消费(万吨标煤)"
                width="160">
                <template slot-scope="scope">
                  {{ scope.row.energy_consumption.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="total_emission"
                label="碳排放量(万吨)"
                width="140">
                <template slot-scope="scope">
                  {{ scope.row.total_emission.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="emission_per_capita"
                label="人均碳排放(吨/人)"
                width="160">
                <template slot-scope="scope">
                  {{ scope.row.emission_per_capita.toFixed(4) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="emission_per_gdp"
                label="单位GDP碳排放(吨/万元)"
                width="180">
                <template slot-scope="scope">
                  {{ scope.row.emission_per_gdp.toFixed(4) }}
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
      energyMixChart: null,
      scenarios: [],
      selectedScenario: '',
      selectedScenarioForEnergyMix: '',
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
      if (this.energyMixChart) {
        this.energyMixChart.resize()
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
    if (this.energyMixChart) {
      this.energyMixChart.dispose()
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
          this.chartData = response.data
          this.loading = false
          
          if (Object.keys(this.chartData).length > 0) {
            this.selectedScenarioForEnergyMix = Object.keys(this.chartData)[0]
            
            // 在DOM更新后初始化图表
            this.$nextTick(() => {
              this.initCarbonPeakChart()
              this.updateEnergyMixChart()

              // 使用多个延时确保图表正确显示
              setTimeout(() => {
                if (this.carbonPeakChart) {
                  this.carbonPeakChart.resize()
                }
                if (this.energyMixChart) {
                  this.energyMixChart.resize()
                }
              }, 100)

              setTimeout(() => {
                if (this.carbonPeakChart) {
                  this.carbonPeakChart.resize()
                }
                if (this.energyMixChart) {
                  this.energyMixChart.resize()
                }
              }, 300)

              setTimeout(() => {
                if (this.carbonPeakChart) {
                  this.carbonPeakChart.resize()
                }
                if (this.energyMixChart) {
                  this.energyMixChart.resize()
                }

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
      
      // 为每个情景添加一条线和一个标记点
      Object.keys(this.chartData).forEach((scenarioName, index) => {
        const data = this.chartData[scenarioName]
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
          data: Object.keys(this.chartData),
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
          min: Math.min(...Object.values(this.chartData).map(data => Math.min(...data.years))),
          max: Math.max(...Object.values(this.chartData).map(data => Math.max(...data.years))),
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
        series: series.map((serie, index) => ({
          ...serie,
          markPoint: {
            data: [markPoints[index]],
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
                // 确保显示的年份与横坐标对应的位置一致
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
              color: this.getColorByIndex(index),
              type: 'dashed',
              opacity: 0.5
            },
            data: [
              {
                xAxis: markPoints[index].coord[0],
                label: {
                  formatter: function(params) {
                    // 确保显示的年份与横坐标对应的位置一致
                    return `${params.value}年`;
                  },
                  position: 'end'
                }
              }
            ]
          }
        }))
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
    updateEnergyMixChart() {
      if (!this.selectedScenarioForEnergyMix || !this.chartData[this.selectedScenarioForEnergyMix]) {
        return
      }
      
      // 获取选中情景的能源结构数据
      const data = this.chartData[this.selectedScenarioForEnergyMix]
      const years = data.years
      const coalData = data.energy_mix.coal
      const elecData = data.energy_mix.elec
      const otherData = data.energy_mix.other
      
      // 计算总能耗和能源占比
      const totalData = years.map((_, i) => coalData[i] + elecData[i] + otherData[i])
      const coalPercentData = years.map((_, i) => (coalData[i] / totalData[i] * 100).toFixed(1))
      const elecPercentData = years.map((_, i) => (elecData[i] / totalData[i] * 100).toFixed(1))
      const otherPercentData = years.map((_, i) => (otherData[i] / totalData[i] * 100).toFixed(1))
      
      // 初始化能源结构图表
      const chartDom = document.getElementById('energy-mix-chart')
      if (!chartDom) {
        console.error('Energy mix chart container not found')
        return
      }

      // 确保容器有尺寸
      if (chartDom.offsetWidth === 0 || chartDom.offsetHeight === 0) {
        console.warn('Energy mix chart container has no size, retrying...')
        setTimeout(() => this.updateEnergyMixChart(), 100)
        return
      }

      if (!this.energyMixChart) {
        this.energyMixChart = echarts.init(chartDom)
      }
      
      // 图表选项
      const option = {
        title: {
          text: '能源结构变化预测',
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
          axisPointer: {
            type: 'shadow'
          },
          formatter: function(params) {
            const year = params[0].name
            let result = `<div style="font-weight:bold;margin-bottom:5px;">${year}年</div>`
            
            // 柱状图数据
            const barParams = params.filter(param => param.seriesType === 'bar')
            const totalEnergy = barParams.reduce((sum, param) => sum + param.value, 0).toFixed(2)
            result += `<div style="margin:3px 0;font-weight:bold;">总能耗: ${totalEnergy}万吨标煤</div>`
            
            barParams.forEach(param => {
              const color = param.color
              const value = param.value.toFixed(2)
              const percentage = (param.value / totalEnergy * 100).toFixed(1)
              result += `<div style="display:flex;align-items:center;margin:3px 0">
                <span style="display:inline-block;width:10px;height:10px;background:${color};margin-right:6px;border-radius:50%"></span>
                <span style="margin-right:8px;">${param.seriesName}:</span>
                <span style="font-weight:bold">${value}万吨标煤 (${percentage}%)</span>
              </div>`
            })
            
            // 折线图数据
            const lineParams = params.filter(param => param.seriesType === 'line')
            if (lineParams.length > 0) {
              result += `<div style="margin-top:8px;border-top:1px dashed #ccc;padding-top:5px;">能源占比:</div>`
              lineParams.forEach(param => {
                const color = param.color
                result += `<div style="display:flex;align-items:center;margin:3px 0">
                  <span style="display:inline-block;width:10px;height:10px;background:${color};margin-right:6px;border-radius:50%"></span>
                  <span style="margin-right:8px;">${param.seriesName}:</span>
                  <span style="font-weight:bold">${param.value}%</span>
                </div>`
              })
            }
            
            return result
          }
        },
        legend: {
          data: ['煤炭', '电力', '其他清洁能源', '煤炭占比', '电力占比', '清洁能源占比'],
          bottom: 10,
          icon: 'roundRect',
          itemWidth: 12,
          itemHeight: 12
        },
        grid: {
          left: '5%',
          right: '5%',
          top: '15%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: years,
          name: '年份',
          nameLocation: 'middle',
          nameGap: 30,
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
            show: false
          },
          axisTick: {
            alignWithLabel: true
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '能源消费(万吨标煤)',
            position: 'left',
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
          {
            type: 'value',
            name: '占比(%)',
            position: 'right',
            nameLocation: 'middle',
            nameGap: 50,
            nameTextStyle: {
              fontWeight: 'bold'
            },
            min: 0,
            max: 100,
            axisLabel: {
              formatter: '{value}%',
              fontWeight: 'bold'
            },
            axisLine: {
              lineStyle: {
                color: '#333'
              }
            },
            splitLine: {
              show: false
            }
          }
        ],
        series: [
          {
            name: '煤炭',
            type: 'bar',
            stack: '能源',
            emphasis: {
              focus: 'series'
            },
            data: coalData,
            itemStyle: {
              color: '#777',
              borderRadius: [0, 0, 0, 0]
            },
            barWidth: '60%'
          },
          {
            name: '电力',
            type: 'bar',
            stack: '能源',
            emphasis: {
              focus: 'series'
            },
            data: elecData,
            itemStyle: {
              color: '#409EFF',
              borderRadius: [0, 0, 0, 0]
            }
          },
          {
            name: '其他清洁能源',
            type: 'bar',
            stack: '能源',
            emphasis: {
              focus: 'series'
            },
            data: otherData,
            itemStyle: {
              color: '#67C23A',
              borderRadius: [4, 4, 0, 0]
            }
          },
          {
            name: '煤炭占比',
            type: 'line',
            yAxisIndex: 1,
            data: coalPercentData,
            symbol: 'circle',
            symbolSize: 8,
            smooth: true,
            lineStyle: {
              width: 3,
              type: 'dashed',
              color: '#777'
            },
            itemStyle: {
              color: '#777',
              borderWidth: 2,
              borderColor: '#fff'
            },
            emphasis: {
              scale: true,
              focus: 'series'
            }
          },
          {
            name: '电力占比',
            type: 'line',
            yAxisIndex: 1,
            data: elecPercentData,
            symbol: 'circle',
            symbolSize: 8,
            smooth: true,
            lineStyle: {
              width: 3,
              type: 'dashed',
              color: '#409EFF'
            },
            itemStyle: {
              color: '#409EFF',
              borderWidth: 2,
              borderColor: '#fff'
            },
            emphasis: {
              scale: true,
              focus: 'series'
            }
          },
          {
            name: '清洁能源占比',
            type: 'line',
            yAxisIndex: 1,
            data: otherPercentData,
            symbol: 'circle',
            symbolSize: 8,
            smooth: true,
            lineStyle: {
              width: 3,
              type: 'dashed',
              color: '#67C23A'
            },
            itemStyle: {
              color: '#67C23A',
              borderWidth: 2,
              borderColor: '#fff'
            },
            emphasis: {
              scale: true,
              focus: 'series'
            }
          }
        ]
      }
      
      // 设置图表选项
      this.energyMixChart.setOption(option, true)

      // 初始化后立即调用resize确保图表正确显示
      this.$nextTick(() => {
        if (this.energyMixChart) {
          this.energyMixChart.resize()
        }
      })

      setTimeout(() => {
        if (this.energyMixChart) {
          this.energyMixChart.resize()
        }
      }, 100)

      setTimeout(() => {
        if (this.energyMixChart) {
          this.energyMixChart.resize()
        }
      }, 300)
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
      resizeChart(this.energyMixChart)

      // 延时resize
      setTimeout(() => {
        resizeChart(this.carbonPeakChart)
        resizeChart(this.energyMixChart)
      }, 100)

      setTimeout(() => {
        resizeChart(this.carbonPeakChart)
        resizeChart(this.energyMixChart)
      }, 300)

      setTimeout(() => {
        resizeChart(this.carbonPeakChart)
        resizeChart(this.energyMixChart)
      }, 500)
    },
    startResizeObserver() {
      if (this.resizeObserver) {
        const carbonContainer = document.getElementById('carbon-peak-chart')
        const energyContainer = document.getElementById('energy-mix-chart')

        if (carbonContainer) {
          this.resizeObserver.observe(carbonContainer)
        }
        if (energyContainer) {
          this.resizeObserver.observe(energyContainer)
        }
      }

      if (this.intersectionObserver) {
        const carbonContainer = document.getElementById('carbon-peak-chart')
        const energyContainer = document.getElementById('energy-mix-chart')

        if (carbonContainer) {
          this.intersectionObserver.observe(carbonContainer)
        }
        if (energyContainer) {
          this.intersectionObserver.observe(energyContainer)
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
      
      if (this.energyMixChart) {
        setTimeout(() => {
          const url = this.energyMixChart.getDataURL({
            type: 'png',
            pixelRatio: 2,
            backgroundColor: '#fff'
          })
          const link = document.createElement('a')
          link.download = '能源结构变化.png'
          link.href = url
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        }, 100)
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
