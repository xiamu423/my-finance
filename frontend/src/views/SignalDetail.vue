<template>
  <div class="signal-detail" v-loading="loading">
    <div class="page-header" v-if="signal">
      <el-button @click="router.back()" :icon="Back" circle class="back-btn"></el-button>
      <div class="header-titles">
        <h2>{{ signal.company.name }} ({{ signal.company.stock_code }})</h2>
        <span class="sub-title">{{ signal.company.industry }} | {{ signal.company.board }}</span>
      </div>
    </div>

    <el-row :gutter="24" v-if="signal">
      <!-- Left Column: Signal Info -->
      <el-col :span="16">
        <el-card shadow="never" class="premium-card mb-24">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><Warning /></el-icon>
              <span>超预期信号生成逻辑</span>
              <el-tag :type="getStrengthTag(signal.strength)" effect="dark" class="ml-auto" size="large">
                {{ formatStrength(signal.strength) }} ({{ signal.score }}分)
              </el-tag>
            </div>
          </template>
          
          <div class="logic-content">
            <div class="logic-item">
              <div class="logic-label">核心支撑依据</div>
              <div class="logic-value highlight-reason">{{ signal.reasoning }}</div>
            </div>
            
            <div class="data-grid mt-24">
              <div class="data-box">
                <div class="data-title">提取预期增幅</div>
                <div class="data-number text-primary">{{ signal.expected_growth }}</div>
              </div>
              <div class="data-box">
                <div class="data-title">市场一致预期</div>
                <div class="data-number">{{ signal.market_expectation || '--' }}</div>
              </div>
              <div class="data-box" v-if="signal.historical_data">
                <div class="data-title">历史同期业绩</div>
                <div class="data-number">{{ signal.historical_data }}</div>
              </div>
            </div>
          </div>
        </el-card>

        <el-card shadow="never" class="premium-card">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><Document /></el-icon>
              <span>文本原文 ({{ signal.text_source?.source_type === 'announcement' ? '业绩预告' : '其他' }})</span>
            </div>
          </template>
          <div class="text-source">
            <h3 class="text-title">{{ signal.text_source?.title }}</h3>
            <p class="text-date">发布时间: {{ signal.text_source?.publish_date }}</p>
            <div class="text-content" v-html="highlightText(signal.text_source?.content)"></div>
          </div>
          
          <el-alert
            title="风险提示"
            type="warning"
            description="业绩预期基于文本表述，存在不及预期或修正风险，仅供投资参考。"
            show-icon
            :closable="false"
            class="mt-24 custom-alert"
          />
        </el-card>
      </el-col>

      <!-- Right Column: Valuation & Charts -->
      <el-col :span="8">
        <el-card shadow="never" class="premium-card mb-24">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><DataLine /></el-icon>
              <span>估值联动分析</span>
            </div>
          </template>
          
          <div class="valuation-grid" v-if="signal.company.valuation">
            <div class="val-item">
              <div class="val-label">市盈率 (PE)</div>
              <div class="val-value">{{ signal.company.valuation.pe.toFixed(2) }}</div>
            </div>
            <div class="val-item">
              <div class="val-label">市净率 (PB)</div>
              <div class="val-value">{{ signal.company.valuation.pb.toFixed(2) }}</div>
            </div>
            <div class="val-item">
              <div class="val-label">PEG</div>
              <div class="val-value" :class="{'text-safe': signal.company.valuation.peg < 1}">
                {{ signal.company.valuation.peg.toFixed(2) }}
              </div>
            </div>
          </div>
          <div v-else class="empty-text">暂无估值数据</div>
          
          <div class="advice-box mt-20" v-if="signal.company.valuation">
            <div class="advice-title">投资参考建议</div>
            <div class="advice-text" v-if="signal.strength === 'strong' && signal.company.valuation.peg < 1.5">
              信号强 + 估值合理，建议重点关注
            </div>
            <div class="advice-text text-warning" v-else-if="signal.strength === 'strong' && signal.company.valuation.pe > 50">
              信号强但估值偏高，注意回调风险
            </div>
            <div class="advice-text" v-else>
              建议结合行业景气度综合判断
            </div>
          </div>
        </el-card>

        <el-card shadow="never" class="premium-card chart-card">
          <template #header>
            <div class="card-header">
              <span>业绩对比可视化</span>
            </div>
          </template>
          <div ref="chartRef" class="echarts-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Back, Warning, Document, DataLine } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '../api'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const signal = ref(null)
const chartRef = ref(null)

const fetchSignalDetail = async () => {
  try {
    const response = await api.getSignal(route.params.id)
    signal.value = response.data
    
    // Initialize chart after data is loaded and DOM is updated
    nextTick(() => {
      initChart()
    })
  } catch (error) {
    console.error("Failed to fetch signal details", error)
  } finally {
    loading.value = false
  }
}

const initChart = () => {
  if (!chartRef.value || !signal.value) return
  
  const expected = parseFloat(signal.value.expected_growth) || 0
  const market = parseFloat(signal.value.market_expectation) || 0
  
  const xData = ['预期增幅', '一致预期']
  const seriesData = [
    { value: expected, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: '#3b82f6'}, {offset: 1, color: '#1d4ed8'}]) } },
    { value: market, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: '#8b5cf6'}, {offset: 1, color: '#6d28d9'}]) } }
  ]
  
  if (signal.value.historical_data) {
    const hist = parseFloat(signal.value.historical_data) || 0
    xData.push('历史同期')
    seriesData.push({ value: hist, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: '#10b981'}, {offset: 1, color: '#047857'}]) } })
  }
  
  const chart = echarts.init(chartRef.value)
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      top: 30,
      bottom: 30,
      left: 40,
      right: 20
    },
    xAxis: {
      type: 'category',
      data: xData,
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisLabel: { color: '#4b5563' }
    },
    yAxis: {
      type: 'value',
      name: '增幅(%)',
      nameTextStyle: { color: '#4b5563' },
      splitLine: {
        lineStyle: {
          color: '#e5e7eb',
          type: 'dashed'
        }
      },
      axisLabel: { color: '#4b5563' }
    },
    series: [
      {
        data: seriesData,
        type: 'bar',
        barWidth: '40%',
        itemStyle: { borderRadius: [4, 4, 0, 0] }
      }
    ]
  }
  chart.setOption(option)
  
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

const highlightText = (text) => {
  if (!text) return ''
  // Simple regex to highlight percentages and numbers
  return text.replace(/(\d+(?:\.\d+)?%|\d+亿元)/g, '<span class="text-highlight">$1</span>')
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
    'negative': '负面信号'
  }
  return map[strength] || strength
}

onMounted(() => {
  fetchSignalDetail()
})
</script>

<style scoped>
.signal-detail {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.back-btn {
  margin-right: 16px;
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  color: #4b5563;
}

.back-btn:hover {
  background-color: #f3f4f6;
  color: #1f2937;
}

.header-titles h2 {
  margin: 0 0 4px 0;
  font-size: 1.5rem;
  color: #1f2937;
}

.sub-title {
  color: #6b7280;
  font-size: 0.875rem;
}

.premium-card {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
}

.premium-card :deep(.el-card__header) {
  border-bottom: 1px solid #e5e7eb;
  padding: 16px 24px;
}

.card-header {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 1.125rem;
  color: #1f2937;
}

.header-icon {
  margin-right: 8px;
  color: #3b82f6;
}

.ml-auto {
  margin-left: auto;
}

.mb-24 {
  margin-bottom: 24px;
}

.mt-24 {
  margin-top: 24px;
}

.mt-20 {
  margin-top: 20px;
}

/* Logic Section */
.logic-item {
  margin-bottom: 16px;
}

.logic-label {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 8px;
}

.highlight-reason {
  background-color: #eff6ff;
  border-left: 4px solid #3b82f6;
  padding: 12px 16px;
  border-radius: 0 8px 8px 0;
  color: #1e3a8a;
  line-height: 1.6;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.data-box {
  background-color: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  text-align: center;
}

.data-title {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 8px;
}

.data-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.text-primary {
  color: #3b82f6;
}

/* Text Source */
.text-title {
  font-size: 1.125rem;
  margin: 0 0 8px 0;
  color: #1f2937;
}

.text-date {
  color: #6b7280;
  font-size: 0.875rem;
  margin-top: 0;
  margin-bottom: 16px;
}

.text-content {
  color: #374151;
  line-height: 1.8;
  font-size: 0.95rem;
  background-color: #f9fafb;
  padding: 16px;
  border-radius: 8px;
}

/* Valuation */
.valuation-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.val-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f9fafb;
  border-radius: 8px;
}

.val-label {
  color: #6b7280;
}

.val-value {
  font-weight: 600;
  font-size: 1.1rem;
  color: #1f2937;
}

.text-safe {
  color: #10b981;
}

.text-warning {
  color: #f59e0b !important;
}

.empty-text {
  color: #6b7280;
  text-align: center;
  padding: 20px 0;
}

.advice-box {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  padding: 16px;
}

.advice-title {
  font-size: 0.875rem;
  color: #9ca3af;
  margin-bottom: 8px;
}

.advice-text {
  color: #60a5fa;
  font-weight: 500;
  line-height: 1.5;
}

/* ECharts */
.echarts-container {
  height: 250px;
  width: 100%;
}
</style>
