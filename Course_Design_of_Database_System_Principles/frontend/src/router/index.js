import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import SidebarLayout from '../components/Layout/SidebarLayout.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: SidebarLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { requiresAuth: true, title: '数据概览' }
      },
      {
        path: 'poi',
        name: 'PoiManagement',
        component: () => import('../views/PoiManagement.vue'),
        meta: { requiresAuth: true, title: 'POI 管理' }
      },
      {
        path: 'scenic-spots',
        name: 'ScenicSpots',
        component: () => import('../views/ScenicSpots.vue'),
        meta: { requiresAuth: true, title: '景点详情' }
      },
      {
        path: 'hotel-details',
        name: 'HotelDetails',
        component: () => import('../views/HotelDetails.vue'),
        meta: { requiresAuth: true, title: '酒店详情' }
      },
      {
        path: 'dynamic-data',
        name: 'DynamicData',
        component: () => import('../views/DynamicData.vue'),
        meta: { requiresAuth: true, title: '动态数据' }
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('../views/Analytics.vue'),
        meta: { requiresAuth: true, title: '数据分析' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
        meta: { requiresAuth: true, title: '个人信息' }
      },
      {
        path: 'map-poi',
        name: 'MapPoiView',
        component: () => import('../views/MapPoiView.vue'),
        meta: { requiresAuth: true, title: '地图POI' }
      },
      {
        path: 'enterprise-query',
        name: 'EnterpriseQuery',
        component: () => import('../views/EnterpriseQuery.vue'),
        meta: { requiresAuth: true, title: '企业查询' }
      },
      {
        path: 'weather-alert',
        name: 'WeatherAlert',
        component: () => import('../views/WeatherAlert.vue'),
        meta: { requiresAuth: true, title: '天气预警' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router