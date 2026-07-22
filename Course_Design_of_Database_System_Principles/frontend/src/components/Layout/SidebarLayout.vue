<template>
  <el-container class="sidebar-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
      <!-- Logo 区域 -->
      <div class="logo-container" :class="{ 'logo-collapse': isCollapse }">
        <el-icon v-if="isCollapse" :size="28" color="#409eff">
          <Location />
        </el-icon>
        <template v-else>
          <h2>旅游管理系统</h2>
          <p>Tourism System</p>
        </template>
      </div>

      <!-- 菜单 -->
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        :collapse-transition="false"
      >
        <!-- 首页 -->
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <template #title>数据概览</template>
        </el-menu-item>

        <!-- POI 管理 -->
        <el-menu-item index="/poi">
          <el-icon><Location /></el-icon>
          <template #title>POI 管理</template>
        </el-menu-item>

        <!-- 景点管理 -->
        <el-menu-item index="/scenic-spots">
          <el-icon><Sunset /></el-icon>
          <template #title>景点详情</template>
        </el-menu-item>

        <!-- 酒店管理 -->
        <el-menu-item index="/hotel-details">
          <el-icon><House /></el-icon>
          <template #title>酒店详情</template>
        </el-menu-item>

        <!-- 动态数据 -->
        <el-menu-item index="/dynamic-data">
          <el-icon><TrendCharts /></el-icon>
          <template #title>动态数据</template>
        </el-menu-item>

        <!-- 数据分析 -->
        <el-menu-item index="/analytics">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>数据分析</template>
        </el-menu-item>

        <!-- 地图POI -->
        <el-menu-item index="/map-poi">
          <el-icon><Location /></el-icon>
          <template #title>地图POI</template>
        </el-menu-item>

        <!-- 企业查询 -->
        <el-menu-item index="/enterprise-query">
          <el-icon><TrendCharts /></el-icon>
          <template #title>企业查询</template>
        </el-menu-item>

        <!-- 天气预警 -->
        <el-menu-item index="/weather-alert">
          <el-icon><Sunny /></el-icon>
          <template #title>天气预警</template>
        </el-menu-item>

        <!-- 个人信息 -->
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <template #title>个人信息</template>
        </el-menu-item>
      </el-menu>

      <!-- 折叠按钮 -->
      <div class="collapse-btn" @click="toggleCollapse">
        <el-icon>
          <Fold v-if="!isCollapse" />
          <Expand v-else />
        </el-icon>
      </div>
    </el-aside>

    <!-- 主容器 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-content">
          <!-- 左侧面包屑 -->
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
                {{ item.name }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <!-- 右侧用户信息 -->
          <div class="header-right">
            <!-- 全屏按钮 -->
            <el-tooltip content="全屏" placement="bottom">
              <div class="header-icon" @click="toggleFullscreen">
                <el-icon :size="20"><FullScreen /></el-icon>
              </div>
            </el-tooltip>

            <!-- 用户下拉菜单 -->
            <el-dropdown @command="handleCommand" class="user-dropdown">
              <div class="user-info">
                <el-avatar :size="36" :style="{ backgroundColor: '#409eff' }">
                  {{ username.charAt(0).toUpperCase() }}
                </el-avatar>
                <span class="username">{{ username }}</span>
                <el-icon class="el-icon--right">
                  <arrow-down />
                </el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    <span>个人信息</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="settings">
                    <el-icon><Setting /></el-icon>
                    <span>系统设置</span>
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    <span>退出登录</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>

      <!-- 页脚 -->
      <el-footer class="footer">
        <div class="footer-content">
          <span>© 2025 上海旅游管理系统 - Tourism Management System</span>
          <span>Version 1.0.0</span>
        </div>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowDown,
  House,
  Location,
  Sunset,
  TrendCharts,
  DataAnalysis,
  User,
  Setting,
  SwitchButton,
  Fold,
  Expand,
  FullScreen,
  Sunny
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const username = ref('用户')
const isCollapse = ref(false)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 面包屑导航
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    path: item.path,
    name: item.meta.title
  }))
})

// 获取用户信息
onMounted(() => {
  // 从 localStorage 获取用户名
  username.value = localStorage.getItem('username') || '用户'
})

// 切换侧边栏折叠
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 全屏切换
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    ElMessage.success('已进入全屏模式')
  } else {
    document.exitFullscreen()
    ElMessage.success('已退出全屏模式')
  }
}

// 处理下拉菜单命令
const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？',
    '退出确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      draggable: true
    }
  ).then(() => {
    // 清除登录信息
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
    localStorage.removeItem('username')
    localStorage.removeItem('isAuthenticated')

    ElMessage.success('退出成功')
    router.push('/login')
  }).catch(() => {
    // 用户取消
  })
}
</script>

<style scoped>
.sidebar-layout {
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow-x: hidden;
}

.logo-container {
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4a;
  transition: all 0.3s;
  padding: 0 16px;
}

.logo-container h2 {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
}

.logo-container p {
  color: #bfcbd9;
  font-size: 12px;
  margin: 4px 0 0 0;
}

.logo-collapse {
  padding: 0;
}

.el-menu {
  border-right: none;
  height: calc(100vh - 120px);
  overflow-y: auto;
}

.el-menu::-webkit-scrollbar {
  width: 6px;
}

.el-menu::-webkit-scrollbar-thumb {
  background: #48576a;
  border-radius: 3px;
}

.collapse-btn {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #263445;
  cursor: pointer;
  color: #bfcbd9;
  transition: all 0.3s;
}

.collapse-btn:hover {
  background-color: #1f2d3d;
  color: #409eff;
}

/* 顶部导航栏 */
.header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
  height: 60px;
}

.header-content {
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
  color: #606266;
}

.header-icon:hover {
  background-color: #f5f7fa;
  color: #409eff;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 主要内容 */
.main-content {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 120px);
}

.main-content::-webkit-scrollbar {
  width: 8px;
}

.main-content::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 4px;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}

/* 页脚 */
.footer {
  height: 60px;
  background: #fff;
  border-top: 1px solid #e6e6e6;
  padding: 0 20px;
}

.footer-content {
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #909399;
}

/* 下拉菜单样式 */
:deep(.el-dropdown-menu__item) {
  padding: 10px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-dropdown-menu__item i) {
  font-size: 16px;
}

/* 过渡动画 */
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>