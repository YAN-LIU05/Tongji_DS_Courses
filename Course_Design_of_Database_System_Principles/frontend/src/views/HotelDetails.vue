<template>
  <div class="hotel-details">
    <h1 class="page-title">酒店详情管理</h1>

    <el-card shadow="never">
      <el-table :data="hotelList" v-loading="loading" stripe border>
        <el-table-column prop="h_id" label="ID" width="80" />
        <el-table-column prop="hotel_name" label="酒店名称" min-width="200" />
        <el-table-column prop="star_rating" label="星级" width="120" />
        <el-table-column prop="address" label="地址" min-width="200" />
        <el-table-column prop="room_count" label="房间数量" width="120">
          <template #default="{ row }">
            {{ row.room_count ? row.room_count : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" size="small">查看</el-button>
            <el-button link type="primary" size="small">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE = 'http://127.0.0.1:8000/api/hotels'

const loading = ref(false)
const hotelList = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 获取酒店名称
const getHotelName = (row) => {
  if (!row) return '-'
  if (row.hotel_name) return row.hotel_name
  return '-'
}


const loadHotelDetails = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    console.log('请求酒店数据:', params)
    const response = await axios.get(`${API_BASE}/hotels/`, { params })
    console.log('酒店数据响应:', response.data)

    const data = response.data
    if (data.results) {
      // Django REST Framework 分页格式
      hotelList.value = data.results
      total.value = data.count || 0
    } else if (Array.isArray(data)) {
      // 简单数组格式
      hotelList.value = data
      // 获取总数
      const countResponse = await axios.get(`${API_BASE}/hotels/`, { params: { page: 1, page_size: 1 } })
      const countData = countResponse.data
      total.value = countData.count || (Array.isArray(countData) ? countData.length : 0)
    } else {
      hotelList.value = []
      total.value = 0
    }

    console.log('酒店列表:', hotelList.value)
    console.log('总数:', total.value)
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 分页事件处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadHotelDetails()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadHotelDetails()
}

onMounted(() => {
  loadHotelDetails()
})
</script>

<style scoped>
.hotel-details {
  padding: 0;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 20px 0;
  color: #303133;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>