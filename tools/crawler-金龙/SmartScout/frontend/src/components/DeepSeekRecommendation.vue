<template>
  <div class="recommendation">
    <div class="card-title">
      <el-icon><Promotion /></el-icon>
      <span>DeepSeek推荐编辑</span>
    </div>

    <div v-if="!store.projectId" class="empty-state">
      <el-empty description="请先进行规则确诊" />
    </div>

    <div v-else>
      <div class="recommendation-info">
        <el-alert
          title="DeepSeek基于50个样本分析的推荐规则"
          type="info"
          :closable="false"
          show-icon
        />
        <div class="project-info">
          <span>项目ID: {{ store.projectId }}</span>
          <el-button
            size="small"
            type="text"
            @click="copyProjectId"
            :icon="DocumentCopy"
          >
            复制
          </el-button>
        </div>
      </div>

      <div class="recommendation-section">
        <div class="section-header">
          <h3>黑名单规则（不关心的内容）</h3>
          <span class="count-badge">{{ store.editedBlacklist.length }} 项</span>
        </div>
        <div class="tag-editor">
          <div class="tag-input-row">
            <el-input
              v-model="newBlackTag"
              placeholder="输入新关键词"
              size="small"
              @keyup.enter="addBlackTag"
              style="width: 200px"
            />
            <el-button type="primary" size="small" @click="addBlackTag">
              <el-icon><Plus /></el-icon>
              添加
            </el-button>
            <el-button type="danger" size="small" @click="clearBlacklist" plain>
              清空
            </el-button>
          </div>
          <div class="tag-container">
            <el-tag
              v-for="tag in store.editedBlacklist"
              :key="tag"
              closable
              type="danger"
              size="large"
              @close="store.removeBlacklistTag(tag)"
            >
              {{ tag }}
            </el-tag>
            <div v-if="store.editedBlacklist.length === 0" class="empty-tags">
              <span class="empty-text">暂无规则</span>
            </div>
          </div>
        </div>
      </div>

      <div class="recommendation-section">
        <div class="section-header">
          <h3>白名单规则（关心的内容）</h3>
          <span class="count-badge">{{ store.editedWhitelist.length }} 项</span>
        </div>
        <div class="tag-editor">
          <div class="tag-input-row">
            <el-input
              v-model="newWhiteTag"
              placeholder="输入新关键词"
              size="small"
              @keyup.enter="addWhiteTag"
              style="width: 200px"
            />
            <el-button type="primary" size="small" @click="addWhiteTag">
              <el-icon><Plus /></el-icon>
              添加
            </el-button>
            <el-button type="success" size="small" @click="clearWhitelist" plain>
              清空
            </el-button>
          </div>
          <div class="tag-container">
            <el-tag
              v-for="tag in store.editedWhitelist"
              :key="tag"
              closable
              type="success"
              size="large"
              @close="store.removeWhitelistTag(tag)"
            >
              {{ tag }}
            </el-tag>
            <div v-if="store.editedWhitelist.length === 0" class="empty-tags">
              <span class="empty-text">暂无规则</span>
            </div>
          </div>
        </div>
      </div>

      <div class="button-group">
        <el-button
          type="primary"
          :loading="store.isLoading"
          @click="handleSaveRules"
          :disabled="!store.editedBlacklist.length && !store.editedWhitelist.length"
        >
          <el-icon><Check /></el-icon>
          保存规则并进入下一步
        </el-button>
        <el-button @click="resetToRecommendation">
          <el-icon><RefreshLeft /></el-icon>
          恢复推荐
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useSmartScoutStore } from '@/stores/smartscout'
import { Promotion, Plus, Check, RefreshLeft, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const store = useSmartScoutStore()
const newBlackTag = ref('')
const newWhiteTag = ref('')

const addBlackTag = () => {
  if (newBlackTag.value.trim()) {
    store.addBlacklistTag(newBlackTag.value.trim())
    newBlackTag.value = ''
  }
}

const addWhiteTag = () => {
  if (newWhiteTag.value.trim()) {
    store.addWhitelistTag(newWhiteTag.value.trim())
    newWhiteTag.value = ''
  }
}

const clearBlacklist = () => {
  store.editedBlacklist = []
}

const clearWhitelist = () => {
  store.editedWhitelist = []
}

const resetToRecommendation = () => {
  store.editedBlacklist = [...store.recommendedBlacklist]
  store.editedWhitelist = [...store.recommendedWhitelist]
  ElMessage.success('已恢复为DeepSeek推荐规则')
}

const handleSaveRules = async () => {
  try {
    await store.saveRules()
    ElMessage.success('规则保存成功！现在可以进入"生产启动"步骤配置参数并开始爬取')
  } catch (error) {
    ElMessage.error('保存规则失败：' + (error.detail || error.message))
  }
}

const copyProjectId = () => {
  navigator.clipboard.writeText(store.projectId)
  ElMessage.success('项目ID已复制到剪贴板')
}
</script>

<style scoped>
.recommendation {
  height: 100%;
}

.empty-state {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recommendation-info {
  margin-bottom: 24px;
}

.project-info {
  margin-top: 12px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 4px;
  border-left: 4px solid #409eff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: monospace;
}

.recommendation-section {
  margin-bottom: 28px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.count-badge {
  background: #409eff;
  color: white;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.tag-editor {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
}

.tag-input-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}

.empty-tags {
  padding: 20px;
  text-align: center;
  color: #909399;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
}

.empty-text {
  font-size: 14px;
}
</style>