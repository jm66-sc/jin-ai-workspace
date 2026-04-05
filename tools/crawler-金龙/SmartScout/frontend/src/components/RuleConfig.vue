<template>
  <div class="rule-config">
    <div class="card-title">
      <el-icon><Setting /></el-icon>
      <span>规则配置</span>
    </div>

    <div class="form-row">
      <div class="form-label">URL列表（每行一个URL）</div>
      <el-input
        v-model="store.urls[0]"
        type="textarea"
        :rows="3"
        placeholder="请输入招标网站URL"
        resize="none"
      />
      <div class="form-tip">提示：目前支持中国政府招标网URL格式</div>
    </div>

    <div class="form-row">
      <div class="form-label">初始黑名单</div>
      <el-input
        v-model="newBlackTag"
        placeholder="输入关键词后按Enter添加"
        @keyup.enter="addInitialBlackTag"
        clearable
      >
        <template #append>
          <el-button @click="addInitialBlackTag">
            <el-icon><Plus /></el-icon>
          </el-button>
        </template>
      </el-input>
      <div class="tag-container">
        <el-tag
          v-for="tag in store.initialBlacklist"
          :key="tag"
          closable
          type="danger"
          @close="removeInitialBlackTag(tag)"
        >
          {{ tag }}
        </el-tag>
      </div>
    </div>

    <div class="form-row">
      <div class="form-label">初始白名单</div>
      <el-input
        v-model="newWhiteTag"
        placeholder="输入关键词后按Enter添加"
        @keyup.enter="addInitialWhiteTag"
        clearable
      >
        <template #append>
          <el-button @click="addInitialWhiteTag">
            <el-icon><Plus /></el-icon>
          </el-button>
        </template>
      </el-input>
      <div class="tag-container">
        <el-tag
          v-for="tag in store.initialWhitelist"
          :key="tag"
          closable
          type="success"
          @close="removeInitialWhiteTag(tag)"
        >
          {{ tag }}
        </el-tag>
      </div>
    </div>

    <div class="button-group">
      <el-button
        type="primary"
        :loading="store.isLoading"
        @click="handleRuleDiagnosis"
        :disabled="!store.urls[0]"
      >
        <el-icon><MagicStick /></el-icon>
        开始规则确诊
      </el-button>
      <el-button @click="resetForm">
        <el-icon><Refresh /></el-icon>
        重置
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useSmartScoutStore } from '@/stores/smartscout'
import { Setting, Plus, MagicStick, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const store = useSmartScoutStore()
const newBlackTag = ref('')
const newWhiteTag = ref('')

const addInitialBlackTag = () => {
  if (newBlackTag.value.trim() && !store.initialBlacklist.includes(newBlackTag.value.trim())) {
    store.initialBlacklist.push(newBlackTag.value.trim())
    newBlackTag.value = ''
  }
}

const removeInitialBlackTag = (tag) => {
  const index = store.initialBlacklist.indexOf(tag)
  if (index > -1) {
    store.initialBlacklist.splice(index, 1)
  }
}

const addInitialWhiteTag = () => {
  if (newWhiteTag.value.trim() && !store.initialWhitelist.includes(newWhiteTag.value.trim())) {
    store.initialWhitelist.push(newWhiteTag.value.trim())
    newWhiteTag.value = ''
  }
}

const removeInitialWhiteTag = (tag) => {
  const index = store.initialWhitelist.indexOf(tag)
  if (index > -1) {
    store.initialWhitelist.splice(index, 1)
  }
}

const handleRuleDiagnosis = async () => {
  try {
    await store.performRuleDiagnosis()
    ElMessage.success('规则确诊成功！')
  } catch (error) {
    ElMessage.error('规则确诊失败：' + (error.detail || error.message))
  }
}

const resetForm = () => {
  store.urls[0] = 'https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&kw=消防'
  store.initialBlacklist = []
  store.initialWhitelist = []
  newBlackTag.value = ''
  newWhiteTag.value = ''
}
</script>

<style scoped>
.rule-config {
  height: 100%;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}
</style>