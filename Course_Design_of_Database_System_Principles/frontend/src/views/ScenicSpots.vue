<template>
  <div class="scenic-spots">
    <h1 class="page-title">景点详情管理</h1>
    
    <el-card shadow="never">
      <el-table :data="scenicList" v-loading="loading" stripe border>
        <el-table-column prop="s_id" label="ID" width="80" />
        <el-table-column label="景区名称" min-width="200">
          <template #default="{ row }">
            {{ getPoiName(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.level" type="success">{{ row.level }}</el-tag>
            <el-text v-else type="info">未评级</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="max_capacity" label="最大承载量" width="150">
          <template #default="{ row }">
            {{ row.max_capacity ? row.max_capacity.toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" size="small">查看</el-button>
            <el-button link type="primary" size="small">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- ⬇️⬇️⬇️ 分页组件在这里添加 ⬇️⬇️⬇️ -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
      <!-- ⬆️⬆️⬆️ 分页组件结束 ⬆️⬆️⬆️ -->
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE = 'http://127.0.0.1:8000/api/attractions'

const loading = ref(false)
const scenicList = ref([])

// ⬇️⬇️⬇️ 添加分页相关变量 ⬇️⬇️⬇️
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
// ⬆️⬆️⬆️ 分页变量结束 ⬆️⬆️⬆️

// 获取POI名称
const getPoiName = (row) => {
  if (!row) return '-'
  if (row.poi_info?.poi_name) return row.poi_info.poi_name
  if (row.poi?.poi_name) return row.poi.poi_name
  if (typeof row.poi_name === 'string') return row.poi_name
  if (row.poi_name?.poi_name) return row.poi_name.poi_name
  return '-'
}

const loadScenicSpots = async () => {
  loading.value = true
  try {
    // ⬇️⬇️⬇️ 添加分页参数 ⬇️⬇️⬇️
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    console.log('请求景点数据:', params)
    const response = await axios.get(`${API_BASE}/details/`, { params })
    console.log('景点数据响应:', response.data)

    const data = response.data
    if (data.results) {
      // Django REST Framework 分页格式
      scenicList.value = data.results
      total.value = data.count || 0
    } else if (Array.isArray(data)) {
      // 简单数组格式 - should not happen with proper pagination
      // We need to make a separate request to get the total count
      scenicList.value = data
      // Get total count with a separate request with page_size=1 to minimize data transfer
      const countResponse = await axios.get(`${API_BASE}/details/`, { params: { page: 1, page_size: 1 } })
      const countData = countResponse.data
      total.value = countData.count || (Array.isArray(countData) ? countData.length : 0)
    } else {
      scenicList.value = []
      total.value = 0
    }
    // ⬆️⬆️⬆️ 分页数据处理结束 ⬆️⬆️⬆️

    console.log('景点列表:', scenicList.value)
    console.log('总数:', total.value)
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// ⬇️⬇️⬇️ 添加分页事件处理函数 ⬇️⬇️⬇️
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadScenicSpots()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadScenicSpots()
}
// ⬆️⬆️⬆️ 分页函数结束 ⬆️⬆️⬆️

onMounted(() => {
  loadScenicSpots()
})
</script>

<style scoped>
.scenic-spots {
  padding: 0;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 20px 0;
  color: #303133;
}

/* ⬇️⬇️⬇️ 添加分页样式 ⬇️⬇️⬇️ */
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
/* ⬆️⬆️⬆️ 分页样式结束 ⬆️⬆️⬆️ */
</style>