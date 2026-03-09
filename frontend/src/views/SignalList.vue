<template>
  <div class="signal-list">
    <!-- Filter Section -->
    <el-card shadow="never" class="premium-card filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="信号强度">
          <el-select v-model="filters.strength" placeholder="全部强度" clearable style="width: 140px">
            <el-option label="强信号" value="strong" />
            <el-option label="中等信号" value="medium" />
            <el-option label="弱信号" value="weak" />
            <el-option label="负面信号" value="negative" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="fetchSignals" class="search-btn">筛选</el-button>
          <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Data Table -->
    <el-card shadow="never" class="premium-card table-card" v-loading="loading" element-loading-background="rgba(255, 255, 255, 0.8)">
      <template #header>
        <div class="card-header">
          <span>挖掘结果 ({{ total }})</span>
        </div>
      </template>
      
      <el-table :data="tableData" style="width: 100%" :row-class-name="tableRowClassName" @row-click="goToDetail">
        <el-table-column prop="company.stock_code" label="代码" width="100" />
        <el-table-column prop="company.name" label="名称" width="120" />
        <el-table-column prop="score" label="信号评分" width="120" sortable>
          <template #default="scope">
            <div class="score-container">
              <span class="score-text" :class="getScoreClass(scope.row.score)">{{ scope.row.score }}</span>
              <el-progress 
                :percentage="scope.row.score" 
                :color="getScoreColor(scope.row.score)" 
                :show-text="false"
                :stroke-width="4"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="strength" label="信号强度" width="120">
          <template #default="scope">
            <el-tag :type="getStrengthTag(scope.row.strength)" effect="dark" class="strength-tag">
              {{ formatStrength(scope.row.strength) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="expected_growth" label="提取预期增幅" width="120" />
        <el-table-column prop="reasoning" label="核心支撑依据" min-width="250" show-overflow-tooltip />
        <el-table-column prop="text_source.publish_date" label="业绩公告发布时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.text_source?.publish_date) }}
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Refresh } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const filters = reactive({
  strength: ''
})

const fetchSignals = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      strength: filters.strength || undefined
    }
    const response = await api.getSignals(params)
    tableData.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    console.error("Failed to fetch signals", error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.strength = ''
  currentPage.value = 1
  fetchSignals()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchSignals()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchSignals()
}

const goToDetail = (row) => {
  router.push({ name: 'signal-detail', params: { id: row.id } })
}

// Helpers
const getStrengthTag = (strength) => {
  const map = {
    'strong': 'danger',
    'medium': 'warning',
    'weak': 'info',
    'negative': 'success'
  }
  return map[strength] || 'info'
}

const formatStrength = (strength) => {
  const map = {
    'strong': '强信号',
    'medium': '中信号',
    'weak': '弱信号',
    'negative': '无/负面'
  }
  return map[strength] || strength
}

const getScoreColor = (score) => {
  if (score >= 80) return '#ef4444' // red-500
  if (score >= 60) return '#f59e0b' // amber-500
  if (score >= 40) return '#3b82f6' // blue-500
  return '#22c55e' // green-500
}

const getScoreClass = (score) => {
  if (score >= 80) return 'text-strong'
  if (score >= 60) return 'text-medium'
  return ''
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (dateString.length <= 10) {
    // It's just a date 'YYYY-MM-DD'
    return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`
  }
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')} ${String(date.getHours()).padStart(2,'0')}:${String(date.getMinutes()).padStart(2,'0')}`
}

const tableRowClassName = ({ row }) => {
  return 'clickable-row'
}

onMounted(() => {
  fetchSignals()
})
</script>

<style scoped>
.signal-list {
  max-width: 1400px;
  margin: 0 auto;
}

.premium-card {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  margin-bottom: 24px;
}

.premium-card :deep(.el-card__header) {
  border-bottom: 1px solid #e5e7eb;
  padding: 16px 24px;
}

.card-header {
  font-weight: 600;
  font-size: 1.125rem;
  color: #1f2937;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 0;
}

.filter-form :deep(.el-form-item__label) {
  color: #4b5563;
}

.search-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
}

.search-btn:hover {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
}

.score-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.score-text {
  font-weight: 700;
  font-size: 1.1rem;
}

.text-strong { color: #ef4444; }
.text-medium { color: #f59e0b; }

.strength-tag {
  font-weight: 600;
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

/* Table styling for light theme */
:deep(.el-table) {
  background-color: transparent;
  --el-table-border-color: #e5e7eb;
  --el-table-header-bg-color: #f9fafb;
  --el-table-header-text-color: #6b7280;
  --el-table-tr-bg-color: transparent;
  --el-table-row-hover-bg-color: #f3f4f6;
}

:deep(.el-table th.el-table__cell) {
  background-color: var(--el-table-header-bg-color);
}

:deep(.el-table td.el-table__cell), :deep(.el-table th.el-table__cell.is-leaf) {
  border-bottom: 1px solid var(--el-table-border-color);
}

:deep(.el-table tr) {
  background-color: var(--el-table-tr-bg-color);
  transition: background-color 0.2s;
}

:deep(.clickable-row) {
  cursor: pointer;
}

:deep(.el-progress-bar__outer) {
  background-color: #e5e7eb;
}
</style>
