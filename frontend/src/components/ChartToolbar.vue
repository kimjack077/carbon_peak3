<!-- frontend/src/components/ChartToolbar.vue -->
<template>
  <div class="chart-toolbar">
    <el-tooltip content="重置缩放" placement="top">
      <el-button size="mini" icon="el-icon-refresh" @click="$emit('reset')" circle />
    </el-tooltip>
    <el-tooltip content="下载图表" placement="top">
      <el-button size="mini" icon="el-icon-download" @click="$emit('download')" circle />
    </el-tooltip>
    <el-tooltip content="全屏查看" placement="top">
      <el-button size="mini" icon="el-icon-full-screen" @click="toggleFullscreen" circle />
    </el-tooltip>
    <el-tooltip content="数据表格" placement="top">
      <el-button size="mini" icon="el-icon-s-data" @click="$emit('toggle-table')" circle />
    </el-tooltip>
  </div>
</template>

<script>
export default {
  name: 'ChartToolbar',
  methods: {
    toggleFullscreen() {
      const chartContainer = this.$parent.$el.querySelector('.echarts-container')
      if (!document.fullscreenElement) {
        chartContainer?.requestFullscreen()
      } else {
        document.exitFullscreen()
      }
    }
  }
}
</script>

<style scoped>
.chart-toolbar {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  z-index: 10;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.chart-toolbar:hover {
  opacity: 1;
}

.chart-toolbar .el-button {
  background: rgba(15, 118, 110, 0.2);
  border: 1px solid rgba(15, 118, 110, 0.4);
  color: #14b8a6;
}

.chart-toolbar .el-button:hover {
  background: rgba(15, 118, 110, 0.4);
  box-shadow: 0 0 10px rgba(15, 118, 110, 0.5);
}
</style>