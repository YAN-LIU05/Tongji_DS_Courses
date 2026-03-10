<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
      <div class="logo" :class="{ 'logo-collapse': isCollapse }">
        <el-icon v-if="isCollapse" size="24"><Location /></el-icon>
        <span v-else>上海旅游系统</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>数据概览</template>
        </el-menu-item>
        
        <el-menu-item index="/poi">
          <el-icon><Location /></el-icon>
          <template #title>POI管理</template>
        </el-menu-item>
        
        <el-menu-item index="/scenic-spots">
          <el-icon><Sunset /></el-icon>
          <template #title>景点详情</template>
        </el-menu-item>
        
        <el-menu-item index="/dynamic-data">
          <el-icon><TrendCharts /></el-icon>
          <template #title>动态数据</template>
        </el-menu-item>
        
        <el-menu-item index="/analytics">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>数据分析</template>
        </el-menu-item>
        
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <template #title>个人信息</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon 
            class="collapse-icon" 
            size="20"
            @click="toggleCollapse"
          >
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
        </div>
        
        <div class="header-right">
          <span class="username">{{ username }}</span>
          <el-dropdown @command="handleCommand">
            <el-avatar :size="36" :icon="UserFilled" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区域 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Location, 
  Odometer, 
  Sunset, 
  TrendCharts, 
  DataAnalysis, 
  User,
  UserFilled,
  SwitchButton,
  Fold,
  Expand
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const isCollapse = ref(false)
const username = ref('')

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 切换侧边栏折叠状态
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 处理下拉菜单命令
const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      
      // 清除登录信息
      localStorage.removeItem('token')
      localStorage.removeItem('userId')
      localStorage.removeItem('username')
      localStorage.removeItem('isAuthenticated')
      
      ElMessage.success('退出成功')
      router.push('/login')
    } catch {
      // 用户取消
    }
  }
}

onMounted(() => {
  // 从 localStorage 获取用户名
  username.value = localStorage.getItem('username') || '游客'
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #001529;
  transition: width 0.3s;
  overflow-x: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
}

.logo-collapse {
  padding: 0;
}

.el-menu {
  border-right: none;
  background-color: #001529;
}

:deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.65);
}

:deep(.el-menu-item:hover) {
  color: #fff;
  background-color: rgba(64, 158, 255, 0.1) !important;
}

:deep(.el-menu-item.is-active) {
  color: #fff;
  background-color: #1890ff !important;
}

.header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-icon {
  cursor: pointer;
  transition: color 0.3s;
}

.collapse-icon:hover {
  color: #409eff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.username {
  font-size: 14px;
  color: #606266;
}

.el-avatar {
  cursor: pointer;
  transition: transform 0.3s;
}

.el-avatar:hover {
  transform: scale(1.1);
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 1000;
  }
  
  .main-content {
    padding: 12px;
  }
}
</style>