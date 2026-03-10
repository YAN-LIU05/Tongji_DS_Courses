<template>
  <div class="dashboard">
    <h1 class="page-title">数据概览</h1>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <div class="stats-icon" style="background: #ecf5ff;">
              <el-icon :size="32" color="#409eff"><Location /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ totalPois }}</div>
              <div class="stats-label">POI 总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <div class="stats-icon" style="background: #fef0f0;">
              <el-icon :size="32" color="#f56c6c"><Sunset /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ totalScenic }}</div>
              <div class="stats-label">景区数量</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <div class="stats-icon" style="background: #f0f9ff;">
              <el-icon :size="32" color="#67c23a"><TrendCharts /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ totalDynamic }}</div>
              <div class="stats-label">动态记录</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <div class="stats-icon" style="background: #fdf6ec;">
              <el-icon :size="32" color="#e6a23c"><User /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ todayVisitors }}</div>
              <div class="stats-label">今日访客</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card class="quick-actions" shadow="never">
      <template #header>
        <span class="card-title">快捷操作</span>
      </template>
      <div class="actions-grid">
        <div class="action-item" @click="$router.push('/poi')">
          <el-icon :size="24" color="#409eff"><Plus /></el-icon>
          <span>添加 POI</span>
        </div>
        <div class="action-item" @click="$router.push('/dynamic-data')">
          <el-icon :size="24" color="#67c23a"><DataLine /></el-icon>
          <span>查看数据</span>
        </div>
        <div class="action-item" @click="$router.push('/analytics')">
          <el-icon :size="24" color="#e6a23c"><DataAnalysis /></el-icon>
          <span>数据分析</span>
        </div>
        <div class="action-item" @click="$router.push('/profile')">
          <el-icon :size="24" color="#f56c6c"><Setting /></el-icon>
          <span>系统设置</span>
        </div>
      </div>
    </el-card>

    <!-- 最近动态 -->
    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">最新 POI</span>
              <el-button link type="primary" @click="$router.push('/poi')">查看更多</el-button>
            </div>
          </template>
          <el-table :data="recentPois" style="width: 100%" v-loading="loading">
            <el-table-column prop="poi_name" label="名称" show-overflow-tooltip />
            <el-table-column prop="poi_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="getTypeColor(row.poi_type)">
                  {{ row.poi_type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="address" label="地址" show-overflow-tooltip width="200" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">最新动态数据</span>
              <el-button link type="primary" @click="$router.push('/dynamic-data')">查看更多</el-button>
            </div>
          </template>
          <el-table :data="recentDynamic" style="width: 100%" v-loading="dynamicLoading">
            <el-table-column label="POI" show-overflow-tooltip>
              <template #default="{ row }">
                {{ getDynamicPoiName(row) }}
              </template>
            </el-table-column>
            <el-table-column label="客流量" width="100">
              <template #default="{ row }">
                {{ row.passenger_flow ? row.passenger_flow.toLocaleString() : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="占用率" width="100">
              <template #default="{ row }">
                <el-tag
                  v-if="row.occupancy_rate"
                  size="small"
                  :type="getRateType(row.occupancy_rate)"
                >
                  {{ formatOccupancyRate(row.occupancy_rate) }}%
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表展示 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>
            <span class="card-title">POI 类型分布</span>
          </template>
          <div style="height: 300px; display: flex; align-items: center; justify-content: center;">
            <el-empty v-if="!poiTypeData.length" description="暂无数据" :image-size="120" />
            <div v-else class="pie-chart-container">
              <div class="pie-chart">
                <!-- 饼图可视化 -->
                <svg width="200" height="200" viewBox="0 0 100 100" class="pie-svg">
                  <path
                    v-for="(item, index) in poiTypeData"
                    :key="item.type"
                    :d="getPiePath(index, poiTypeData)"
                    :fill="getTypeColorByIndex(index)"
                    stroke="#fff"
                    stroke-width="0.5"
                  />
                </svg>
                <div class="pie-center">
                  <div class="total-count">{{ totalPois }}</div>
                  <div class="total-label">总数</div>
                </div>
              </div>
              <div class="legend-container">
                <div v-for="(item, index) in poiTypeData" :key="item.type" class="legend-item">
                  <div class="legend-color" :style="{ backgroundColor: getTypeColorByIndex(index) }"></div>
                  <div class="legend-text">
                    <div class="legend-type">{{ item.type }}</div>
                    <div class="legend-value">{{ item.count }} ({{ item.percentage }}%)</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>
            <span class="card-title">热门景点 TOP 5</span>
          </template>
          <div style="height: 300px; display: flex; align-items: center; justify-content: center;">
            <el-empty v-if="!topScenic.length" description="暂无数据" :image-size="120" />
            <div v-else class="top-list">
              <div v-for="(item, index) in topScenic" :key="item.poi_id" class="top-item">
                <div class="rank" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
                <div class="top-info">
                  <div class="top-name">{{ item.poi_name }}</div>
                  <div class="top-desc">{{ item.address }}</div>
                </div>
                <div class="top-score">
                  <span>{{ item.avg_occupancy_rate ? item.avg_occupancy_rate.toFixed(2) + '%' : '-' }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Location, 
  Sunset, 
  TrendCharts, 
  User, 
  Plus, 
  DataLine, 
  DataAnalysis, 
  Setting,
  StarFilled 
} from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 统计数据
const totalPois = ref(0)
const totalScenic = ref(0)
const totalDynamic = ref(0)
const todayVisitors = ref(0)

// 列表数据
const loading = ref(false)
const dynamicLoading = ref(false)
const recentPois = ref([])
const recentDynamic = ref([])
const topScenic = ref([])

// POI 类型统计
const poiTypeData = ref([])

// 获取类型标签颜色
const getTypeColor = (type) => {
  const colors = {
    '景区': 'success',
    '酒店': 'warning',
    '餐厅': 'danger',
    '商场': 'info',
    '交通': 'primary'
  }
  return colors[type] || ''
}

// 获取占用率类型
const getRateType = (rate) => {
  const value = parseFloat(rate)
  // If value is a decimal (0.x), convert to percentage for comparison
  const percentageValue = value <= 1 && value >= 0 ? value * 100 : value
  if (percentageValue >= 80) return 'danger'
  if (percentageValue >= 60) return 'warning'
  return 'success'
}

// 格式化占用率显示
const formatOccupancyRate = (rate) => {
  if (rate == null) return '-'
  const value = parseFloat(rate)
  // If rate is already a decimal (0.x), multiply by 100 to convert to percentage
  // If rate is already a percentage (x), return as is
  if (value <= 1 && value >= 0) {
    return (value * 100).toFixed(2)
  } else {
    return value.toFixed(2)
  }
}

// 获取动态数据中的POI名称（兼容不同数据结构）
const getDynamicPoiName = (row) => {
  if (!row) return '-'
  // 尝试不同的可能字段路径
  if (row.poi?.poi_name) return row.poi.poi_name
  if (row.poi_name) return row.poi_name
  if (row.poi?.name) return row.poi.name
  if (row.poi_info?.poi_name) return row.poi_info.poi_name
  if (row.poi_id) return `POI ID: ${row.poi_id}` // fallback to show ID if name is not available
  return '-'
}

// 获取随机颜色
const getRandomColor = () => {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399']
  return colors[Math.floor(Math.random() * colors.length)]
}

// 计算饼图路径
const getPiePath = (index, data) => {
  if (!data || data.length === 0) return '';

  // 计算总百分比
  const totalPercentage = data.reduce((sum, item) => sum + item.percentage, 0);
  if (totalPercentage === 0) return '';

  // 计算当前项的起始角度和结束角度
  let startAngle = 0;
  for (let i = 0; i < index; i++) {
    startAngle += (data[i].percentage / totalPercentage) * 360;
  }
  const endAngle = startAngle + (data[index].percentage / totalPercentage) * 360;

  // 转换角度为弧度
  const startAngleRad = (startAngle - 90) * Math.PI / 180;
  const endAngleRad = (endAngle - 90) * Math.PI / 180;

  // 圆心坐标和半径
  const cx = 50;
  const cy = 50;
  const r = 40;

  // 计算起始点和终点坐标
  const x1 = cx + r * Math.cos(startAngleRad);
  const y1 = cy + r * Math.sin(startAngleRad);
  const x2 = cx + r * Math.cos(endAngleRad);
  const y2 = cy + r * Math.sin(endAngleRad);

  // 判断是否为大弧
  const largeArcFlag = (endAngle - startAngle) > 180 ? 1 : 0;

  // 构建路径
  return `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`;
}

// 根据索引获取类型颜色
const getTypeColorByIndex = (index) => {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#61c55d', '#d87a4c', '#a56eff', '#5d6ce6', '#e66e9c']
  return colors[index % colors.length]
}

// 加载统计数据
const loadStats = async () => {
  loading.value = true
  try {
    let allPois = []; // 用于存储所有页的 POI 数据
    let nextUrl = 'http://127.0.0.1:8000/api/attractions/pois/'; // 初始请求 URL

    // 循环请求所有分页
    while (nextUrl) {
      const response = await axios.get(nextUrl);
      const data = response.data;

      // 将当前页的 results 添加到 allPois 数组中
      allPois = allPois.concat(data.results);

      // 更新 nextUrl 为下一页的链接，如果 next 为 null，循环将停止
      nextUrl = data.next;
    }

    // 现在 allPois 包含了所有分页的 POI 数据
    totalPois.value = allPois.length; // 使用所有 POI 的总数
    recentPois.value = allPois.slice(0, 5); // 仍然取最新的5个

    // 统计 POI 类型分布 (使用 allPois 进行统计)
    const typeMap = {};
    allPois.forEach(poi => { // <--- 这里使用 allPois
      const type = poi.poi_type || '其他';
      typeMap[type] = (typeMap[type] || 0) + 1;
    });

    poiTypeData.value = Object.entries(typeMap).map(([type, count]) => ({
      type,
      count,
      percentage: Math.round((count / allPois.length) * 100) // <--- 这里使用 allPois.length
    }));

    // 加载景区数据总数
    const scenicCountResponse = await axios.get('http://127.0.0.1:8000/api/attractions/details/', {
      params: { page: 1, page_size: 1 }
    })
    const scenicData = scenicCountResponse.data
    totalScenic.value = scenicData.count || (Array.isArray(scenicData) ? scenicData.length : 0)

    // 加载热门景点 TOP 5 based on highest occupancy rate in dynamic data
    const dynamicResponse = await axios.get('http://127.0.0.1:8000/api/attractions/dynamic/', {
      params: { page: 1, page_size: 100 } // Get more records to find top 5
    })
    const dynamicData = dynamicResponse.data
    const dynamicRecords = dynamicData.results || dynamicData

    if (Array.isArray(dynamicRecords) && dynamicRecords.length > 0) {
      // Create a copy of records to avoid modifying original data
      let recordsWithPoiName = []
      for (const record of dynamicRecords) {
        const poiName = getDynamicPoiName(record) // Use the same function as in the template
        const rate = parseFloat(record.occupancy_rate)
        const percentageRate = !isNaN(rate) ? (rate <= 1 && rate >= 0 ? rate * 100 : rate) : 0

        recordsWithPoiName.push({
          ...record,
          poi_name: poiName,
          occupancy_rate_display: percentageRate
        })
      }

      // Sort by occupancy rate descending and get top 5 unique POIs
      const sortedRecords = recordsWithPoiName
        .sort((a, b) => b.occupancy_rate_display - a.occupancy_rate_display)

      // Get unique POIs (avoid duplicates) - take first occurrence of each unique POI
      const uniqueTop5 = []
      const seenPoiIds = new Set()

      for (const record of sortedRecords) {
        const poiId = record.poi?.poi_id || record.poi || record.poi_name
        if (!seenPoiIds.has(poiId) && uniqueTop5.length < 5) {
          seenPoiIds.add(poiId)
          uniqueTop5.push(record)
        }
      }

      // Format for display
      topScenic.value = uniqueTop5.map(record => ({
        poi_name: record.poi_name,
        address: record.poi?.address || record.address || '',
        avg_occupancy_rate: record.occupancy_rate_display
      }))
    }


  } catch (error) {
    console.error('加载统计数据失败:', error);
    ElMessage.error('加载数据失败');
  } finally {
    loading.value = false;
  }
};

// 加载动态数据
const loadDynamicData = async () => {
  dynamicLoading.value = true
  try {
    // 获取动态数据总数
    const dynamicCountResponse = await axios.get('http://127.0.0.1:8000/api/attractions/dynamic/', {
      params: { page: 1, page_size: 1 }
    })
    totalDynamic.value = dynamicCountResponse.data.count || (Array.isArray(dynamicCountResponse.data) ? dynamicCountResponse.data.length : 0)

    // 加载最新动态数据
    const response = await axios.get('http://127.0.0.1:8000/api/attractions/dynamic/', {
      params: { page: 1, page_size: 5 }
    })
    const dynamicData = response.data
    const dynamic = dynamicData.results || dynamicData
    recentDynamic.value = Array.isArray(dynamic) ? dynamic.slice(0, 5) : []
  } catch (error) {
    console.error('加载动态数据失败:', error)
  } finally {
    dynamicLoading.value = false
  }
}

onMounted(() => {
  loadStats()
  loadDynamicData()
  // 模拟今日访客数
  todayVisitors.value = Math.floor(Math.random() * 5000 + 3000)
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.pie-chart-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  width: 100%;
  height: 100%;
  padding: 20px;
}

.pie-chart {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pie-center {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.total-count {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.total-label {
  font-size: 12px;
  color: #909399;
}

.legend-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-text {
  display: flex;
  flex-direction: column;
}

.legend-type {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.legend-value {
  font-size: 12px;
  color: #909399;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 20px 0;
  color: #303133;
}

.stats-row {
  margin-bottom: 20px;
}

.stats-card {
  height: 120px;
  cursor: pointer;
  transition: all 0.3s;
}

.stats-card:hover {
  transform: translateY(-4px);
}

.stats-content {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 100%;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stats-info {
  flex: 1;
}

.stats-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stats-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.quick-actions {
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  gap: 12px;
}

.action-item:hover {
  background: #ecf5ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.action-item span {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.chart-placeholder {
  width: 100%;
  padding: 20px;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.type-name {
  width: 80px;
  font-size: 14px;
  color: #606266;
}

.type-count {
  width: 40px;
  text-align: right;
  font-weight: 600;
  color: #303133;
}

.top-list {
  width: 100%;
  padding: 20px;
}

.top-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  margin-bottom: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: all 0.3s;
}

.top-item:hover {
  background: #ecf5ff;
  transform: translateX(4px);
}

.rank {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: 600;
  font-size: 14px;
  background: #e4e7ed;
  color: #606266;
  flex-shrink: 0;
}

.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #fff;
}

.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
  color: #fff;
}

.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #e8a87c);
  color: #fff;
}

.top-info {
  flex: 1;
  min-width: 0;
}

.top-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.top-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.top-score {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  color: #f7ba2a;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .stats-row {
    margin-bottom: 16px;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-item {
    padding: 16px;
  }
}
</style>