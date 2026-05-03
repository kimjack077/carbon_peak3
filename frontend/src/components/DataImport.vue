<!-- frontend/src/components/DataImport.vue -->
<template>
  <glassmorphic-card>
    <template #header>
      <div class="import-header">
        <h3>数据导入</h3>
        <help-tooltip content="支持CSV格式，需包含year、gdp、energy_consumption、co2_emission列" />
      </div>
    </template>

    <el-upload
      drag
      action="#"
      :auto-upload="false"
      :on-change="handleFileChange"
      accept=".csv"
      :limit="1"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">拖拽文件到此处，或<em>点击上传</em></div>
      <template #tip>
        <div class="el-upload__tip">仅支持 CSV 格式文件</div>
      </template>
    </el-upload>

    <div v-if="validationResult" class="validation-result">
      <el-alert
        :type="validationResult.valid ? 'success' : 'error'"
        :title="validationResult.message"
        show-icon
      />
      <div v-if="validationResult.details" class="validation-details">
        <p v-for="detail in validationResult.details" :key="detail">{{ detail }}</p>
      </div>
    </div>

    <template #footer>
      <el-button type="primary" :disabled="!canUpload" @click="uploadData">
        确认导入
      </el-button>
    </template>
  </glassmorphic-card>
</template>

<script>
import { dataApi } from '@/utils/api'
import GlassmorphicCard from './GlassmorphicCard.vue'
import HelpTooltip from './HelpTooltip.vue'

export default {
  name: 'DataImport',
  components: { GlassmorphicCard, HelpTooltip },
  data() {
    return {
      file: null,
      validationResult: null
    }
  },
  computed: {
    canUpload() {
      return this.file && this.validationResult?.valid
    }
  },
  methods: {
    handleFileChange(file) {
      this.file = file.raw
      this.validateFile()
    },
    async validateFile() {
      if (!this.file) return

      const reader = new FileReader()
      reader.onload = async (e) => {
        try {
          const text = e.target.result
          const lines = text.split('\n')
          const headers = lines[0].split(',').map(h => h.trim().toLowerCase())

          const requiredCols = ['year', 'gdp', 'energy_consumption', 'co2_emission']
          const missing = requiredCols.filter(col => !headers.includes(col))

          if (missing.length > 0) {
            this.validationResult = {
              valid: false,
              message: '数据列不完整',
              details: [`缺少必需列: ${missing.join(', ')}`]
            }
          } else {
            this.validationResult = {
              valid: true,
              message: '数据格式正确',
              details: [`包含 ${lines.length - 1} 条数据记录`]
            }
          }
        } catch (err) {
          this.validationResult = { valid: false, message: '文件解析失败' }
        }
      }
      reader.readAsText(this.file)
    },
    async uploadData() {
      const formData = new FormData()
      formData.append('file', this.file)

      try {
        await dataApi.uploadCustom(formData)
        this.$message.success('数据导入成功')
        this.$emit('data-imported', true)
      } catch (err) {
        this.$message.error(err.message || '导入失败')
      }
    }
  }
}
</script>

<style scoped>
.import-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.import-header h3 {
  margin: 0;
  color: #e2e8f0;
}
.validation-result {
  margin-top: 16px;
}
.validation-details {
  margin-top: 8px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}
</style>