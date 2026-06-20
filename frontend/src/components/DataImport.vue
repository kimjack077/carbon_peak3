<!-- 数据导入组件 - 紧凑版 -->
<template>
  <div class="data-import">
    <div class="import-row">
      <el-button type="primary" size="small" icon="el-icon-upload2" @click="triggerUpload">
        导入数据
      </el-button>
      <input
        ref="fileInput"
        type="file"
        accept=".csv,.xlsx,.xls"
        style="display: none"
        @change="handleFileChange"
      />
      <el-button size="small" icon="el-icon-download" @click.prevent="downloadSample">
        下载样例
      </el-button>
      <span class="file-info" v-if="file">{{ file.name }}</span>
      <span class="format-hint">支持 CSV / Excel 格式</span>
    </div>

    <div v-if="validationResult" :class="['validation-msg', validationResult.valid ? 'success' : 'error']">
      <i :class="validationResult.valid ? 'el-icon-success' : 'el-icon-error'"></i>
      <span>{{ validationResult.message }}</span>
      <el-button v-if="validationResult.valid" type="text" size="mini" @click.prevent="uploadData" :loading="uploading">
        点击导入
      </el-button>
    </div>
  </div>
</template>

<script>
import { dataApi } from '@/utils/api'

export default {
  name: 'DataImport',
  data() {
    return {
      file: null,
      validationResult: null,
      uploading: false
    }
  },
  methods: {
    triggerUpload() {
      this.$refs.fileInput.click()
    },
    handleFileChange(e) {
      const files = e.target.files
      if (files && files.length > 0) {
        this.file = files[0]
        this.validateFile()
      }
      // 清空input，允许重新选择同一文件
      e.target.value = ''
    },
    validateFile() {
      if (!this.file) return

      const filename = this.file.name.toLowerCase()
      const isValidFormat = filename.endsWith('.csv') || filename.endsWith('.xlsx') || filename.endsWith('.xls')

      if (!isValidFormat) {
        this.validationResult = {
          valid: false,
          message: '请上传CSV或Excel文件'
        }
        return
      }

      this.validationResult = {
        valid: true,
        message: '已选择: ' + this.file.name
      }
    },
    uploadData() {
      if (!this.file) return

      this.uploading = true
      var formData = new FormData()
      formData.append('file', this.file)

      var self = this
      dataApi.uploadCustom(formData)
        .then(function(result) {
          self.$emit('data-imported', result)
          self.file = null
          self.validationResult = null
          self.$message.success('数据导入成功')
        })
        .catch(function(err) {
          var msg = '导入失败'
          if (err.response && err.response.data && err.response.data.error) {
            msg = err.response.data.error
          } else if (err.message) {
            msg = err.message
          }
          self.$message.error(msg)
        })
        .finally(function() {
          self.uploading = false
        })
    },
    downloadSample(e) {
      if (e) e.preventDefault()
      window.open('/api/download/sample', '_blank')
    }
  }
}
</script>

<style scoped>
.data-import {
  padding: 0;
}

.import-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.file-info {
  font-size: 12px;
  color: var(--cp-primary, #1E40AF);
  font-weight: 500;
}

.format-hint {
  font-size: 11px;
  color: var(--cp-text-muted, #94A3B8);
}

.validation-msg {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.validation-msg.success {
  background: var(--cp-success-light, #D1FAE5);
  color: var(--cp-success, #059669);
}

.validation-msg.error {
  background: var(--cp-danger-light, #FEE2E2);
  color: var(--cp-danger, #DC2626);
}
</style>
