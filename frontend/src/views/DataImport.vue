<template>
  <div class="data-import-container">
    <h1>数据导入</h1>
    <el-upload
      class="upload-demo"
      drag
      action="/api/import-data"
      :on-success="handleSuccess"
      :on-error="handleError"
      :before-upload="beforeUpload"
      :file-list="fileList"
      accept=".xlsx"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      <div class="el-upload__tip" slot="tip">只能上传xlsx格式文件</div>
    </el-upload>
    
    <el-progress 
      v-if="progressVisible" 
      :percentage="progressPercent" 
      :status="progressStatus"
      style="margin-top: 20px"
    />
    
    <el-collapse v-if="importResults.length > 0" style="margin-top: 20px">
      <el-collapse-item title="导入结果">
        <div v-for="(result, index) in importResults" :key="index">
          <el-alert 
            :title="`${result.sheet}: ${result.message}`" 
            :type="result.success ? 'success' : 'error'"
            show-icon
            style="margin-bottom: 10px"
          />
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script>
export default {
  data() {
    return {
      fileList: [],
      progressVisible: false,
      progressPercent: 0,
      progressStatus: '',
      importResults: []
    }
  },
  methods: {
    beforeUpload(file) {
      const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      if (!isExcel) {
        this.$message.error('只能上传Excel文件!');
      }
      return isExcel;
    },
    handleSuccess(response, file) {
      this.progressVisible = true;
      this.progressPercent = 100;
      this.progressStatus = 'success';
      
      if (response.success) {
        this.importResults = response.results;
        this.$message.success('数据导入成功!');
      } else {
        this.$message.error(response.message || '导入过程中发生错误');
      }
    },
    handleError(err, file) {
      this.progressVisible = true;
      this.progressPercent = 100;
      this.progressStatus = 'exception';
      this.$message.error('文件上传失败!');
      console.error(err);
    }
  }
}
</script>

<style scoped>
.data-import-container {
  padding: 20px;
}

.upload-demo {
  margin-top: 20px;
}
</style>