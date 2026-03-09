<template>
  <el-config-provider>
    <div class="app-container">
      <el-container>
        <el-header height="60px" class="premium-header">
          <div class="logo">
            <el-icon :size="24" color="#409EFC" style="margin-right: 10px"><TrendCharts /></el-icon>
            <span class="logo-text">A股业绩超预期信号挖掘系统</span>
          </div>
          <div class="header-right">
            <span class="user-info">Beta V1.0</span>
          </div>
        </el-header>
        <el-main>
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { TrendCharts } from '@element-plus/icons-vue'
</script>

<style>
/* Global CSS */
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Inter', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
  background-color: #f0f4f8; /* Light blue/gray background */
  color: #1f2937;
}

#app {
  height: 100%;
}

.app-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.el-container {
  height: 100%;
}

.premium-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  z-index: 10;
  padding: 0 24px;
}

.logo {
  display: flex;
  align-items: center;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  background: linear-gradient(90deg, #1e40af, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.user-info {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.el-main {
  background-color: #f0f4f8;
  padding: 24px;
  overflow-x: hidden;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
