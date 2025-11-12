<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>碳达峰预测系统</h1>
      </el-header>
      <el-main>
        <el-tabs v-model="activeTab">
          <el-tab-pane label="数据来源" name="upload">
            <data-upload @data-loaded="handleDataLoaded"></data-upload>
          </el-tab-pane>
          <el-tab-pane label="情景设置" name="scenarios" :disabled="!dataLoaded">
            <scenario-manager @prediction-completed="handlePredictionCompleted"></scenario-manager>
          </el-tab-pane>
          <el-tab-pane label="预测结果" name="results" :disabled="!dataLoaded">
            <prediction-results ref="predictionResults" :key="resultsKey"></prediction-results>
          </el-tab-pane>
        </el-tabs>
      </el-main>
      <el-footer>
        <p>© 2023 碳达峰预测系统 - 基于LEAP模型算法</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import DataUpload from './components/DataUpload.vue'
import ScenarioManager from './components/ScenarioManager.vue'
import PredictionResults from './components/PredictionResults.vue'

export default {
  name: 'App',
  components: {
    DataUpload,
    ScenarioManager,
    PredictionResults
  },
  data() {
    return {
      activeTab: 'upload',  // 从数据上传页面开始
      dataLoaded: false,    // 初始状态为未加载
      resultsKey: 0 // 用于强制刷新预测结果组件
    }
  },
  methods: {
    handleDataLoaded(success) {
      this.dataLoaded = success
      if (success) {
        this.activeTab = 'scenarios'
      }
    },
    handlePredictionCompleted() {
      // 预测完成后，强制刷新预测结果组件
      this.resultsKey += 1
      this.activeTab = 'results'
    }
  }
}
</script>

<style>
#app {
  font-family: 'Microsoft YaHei', 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin: 0;
  padding: 0;
  height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: white;
  line-height: 60px;
}

.el-footer {
  background-color: #f7f7f7;
  color: #666;
  line-height: 60px;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
  height: calc(100vh - 120px);
  overflow-y: auto;
}

h1 {
  margin: 0;
  font-size: 24px;
}
</style> 