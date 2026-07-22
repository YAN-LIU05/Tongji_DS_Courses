<template>
  <div class="dynamic-data">
    <h1>动态数据管理</h1>

    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="POI名称">
          <el-input 
            v-model="searchForm.poiName" 
            placeholder="请输入POI名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="记录时间">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="handleReset" :icon="Refresh">重置</el-button>
          <el-button type="success" @click="handleAdd" :icon="Plus">新增记录</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table 
        :data="tableData" 
        style="width: 100%"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="record_id" label="记录ID" width="100" />
        <el-table-column label="POI名称" min-width="150">
          <template #default="scope">
            {{ getPoiName(scope.row) }}
          </template>
        </el-table-column>
        <el-table-column label="记录时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.record_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="passenger_flow" label="客流量" width="120">
          <template #default="scope">
            {{ formatNumber(scope.row.passenger_flow) }}
          </template>
        </el-table-column>
        <el-table-column label="占用率" width="100">
          <template #default="scope">
            <el-tag :type="getOccupancyType(scope.row.occupancy_rate)">
              {{ formatPercent(scope.row.occupancy_rate) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleView(scope.row)"
              :icon="View"
              link
            >
              查看
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="handleEdit(scope.row)"
              :icon="Edit"
              link
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)"
              :icon="Delete"
              link
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

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

    <!-- 查看对话框 -->
    <el-dialog 
      v-model="viewDialogVisible" 
      title="动态数据详情" 
      width="600px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="记录ID">
          {{ currentRow.record_id }}
        </el-descriptions-item>
        <el-descriptions-item label="POI名称">
          {{ getPoiName(currentRow) }}
        </el-descriptions-item>
        <el-descriptions-item label="记录时间" :span="2">
          {{ formatDateTime(currentRow.record_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="客流量">
          {{ formatNumber(currentRow.passenger_flow) }}
        </el-descriptions-item>
        <el-descriptions-item label="占用率">
          <el-tag :type="getOccupancyType(currentRow.occupancy_rate)">
            {{ formatPercent(currentRow.occupancy_rate) }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      :title="isEdit ? '编辑记录' : '新增记录'" 
      width="600px"
    >
      <el-form 
        :model="editForm" 
        :rules="rules" 
        ref="editFormRef" 
        label-width="100px"
      >
        <el-form-item label="关联POI" prop="poi">
          <el-select 
            v-model="editForm.poi" 
            placeholder="请选择POI"
            filterable
            :loading="poiLoading"
            style="width: 100%"
          >
            <el-option 
              v-for="poi in poiList" 
              :key="poi.poi_id" 
              :label="poi.poi_name" 
              :value="poi.poi_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="记录时间" prop="record_time">
          <el-date-picker
            v-model="editForm.record_time"
            type="datetime"
            placeholder="选择日期时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="客流量" prop="passenger_flow">
          <el-input-number 
            v-model="editForm.passenger_flow" 
            :min="0" 
            :step="100"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="占用率" prop="occupancy_rate">
          <el-input-number
            v-model="editForm.occupancy_rate"
            :min="0"
            :max="1"
            :step="0.01"
            :precision="4"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, View, Edit, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000/api/attractions'

// 搜索表单
const searchForm = reactive({
  poiName: '',
  dateRange: []
})

// 表格数据
const tableData = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// POI列表
const poiList = ref([])
const poiLoading = ref(false)

// 对话框
const viewDialogVisible = ref(false)
const editDialogVisible = ref(false)
const isEdit = ref(false)
const currentRow = ref({})
const editFormRef = ref(null)

const editForm = reactive({
  poi: null,
  record_time: '',
  passenger_flow: 0,
  occupancy_rate: 0
})

const rules = {
  poi: [{ required: true, message: '请选择POI', trigger: 'change' }],
  record_time: [{ required: true, message: '请选择记录时间', trigger: 'change' }],
  passenger_flow: [{ required: true, message: '请输入客流量', trigger: 'blur' }],
  occupancy_rate: [{ required: true, message: '请输入占用率', trigger: 'blur' }]
}

// 获取POI名称（兼容不同数据结构）
const getPoiName = (row) => {
  if (!row) return '-'
  // 可能的字段：poi_name, poi, poi_info
  if (typeof row.poi_name === 'string') return row.poi_name
  if (row.poi_name?.poi_name) return row.poi_name.poi_name
  if (row.poi?.poi_name) return row.poi.poi_name
  if (row.poi_info?.poi_name) return row.poi_info.poi_name
  return '-'
}

// 获取POI列表
const fetchPOIList = async () => {
  poiLoading.value = true
  try {
    const response = await axios.get(`${API_BASE}/pois/`)
    const data = response.data
    poiList.value = data.results || data
    console.log('POI列表:', poiList.value)
  } catch (error) {
    console.error('获取POI列表失败:', error)
    ElMessage.error('获取POI列表失败')
  } finally {
    poiLoading.value = false
  }
}

// 获取动态数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_time = searchForm.dateRange[0]
      params.end_time = searchForm.dateRange[1]
    }

    console.log('请求参数:', params)
    const response = await axios.get(`${API_BASE}/dynamic/`, { params })
    console.log('API响应:', response.data)

    const data = response.data
    let unfilteredData = []
    if (data.results) {
      // Django REST Framework 分页格式
      unfilteredData = data.results
      total.value = data.count || 0
    } else if (Array.isArray(data)) {
      // 简单数组格式 - should not happen with proper pagination
      // We need to make a separate request to get the total count
      unfilteredData = data
      // Get total count with a separate request with page_size=1 to minimize data transfer
      const countResponse = await axios.get(`${API_BASE}/dynamic/`, { params: { page: 1, page_size: 1 } })
      const countData = countResponse.data
      total.value = countData.count || (Array.isArray(countData) ? countData.length : 0)
    } else {
      unfilteredData = []
      total.value = 0
    }

    // Apply POI name filter to the unfiltered data
    if (searchForm.poiName) {
      tableData.value = unfilteredData.filter(item => {
        const name = getPoiName(item)
        return name && name.includes(searchForm.poiName)
      })
      // Note: When filtering, the total should reflect the unfiltered total
      // but the table shows filtered results. For UI consistency, we might want to show filtered count.
      // For now, keeping the original total from API
    } else {
      tableData.value = unfilteredData
    }

    console.log('表格数据:', tableData.value)
    console.log('总数:', total.value)
  } catch (error) {
    console.error('获取动态数据失败:', error)
    ElMessage.error('获取动态数据失败: ' + (error.response?.data?.detail || error.message))
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  // Create a date object from the string
  let date = new Date(dateStr)
  // If the date is invalid, return the original string
  if (isNaN(date.getTime())) {
    return dateStr
  }
  // Convert to local timezone (this handles the 8-hour difference)
  return date.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
  })
}

// 格式化数字
const formatNumber = (num) => {
  if (num == null) return '-'
  return num.toLocaleString()
}

// 格式化百分比
const formatPercent = (rate) => {
  if (rate == null) return '-'
  // If rate is already a decimal (0.x), multiply by 100 to convert to percentage
  // If rate is already a percentage (x), return as is
  const value = parseFloat(rate)
  if (value <= 1 && value >= 0) {
    return `${(value * 100).toFixed(2)}%`
  } else {
    return `${value.toFixed(2)}%`
  }
}

// 获取占用率标签类型
const getOccupancyType = (rate) => {
  if (!rate) return 'info'
  const value = parseFloat(rate)
  // If value is a decimal (0.x), convert to percentage for comparison
  const percentageValue = value <= 1 && value >= 0 ? value * 100 : value
  if (percentageValue >= 80) return 'danger'
  if (percentageValue >= 60) return 'warning'
  return 'success'
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// 重置
const handleReset = () => {
  searchForm.poiName = ''
  searchForm.dateRange = []
  currentPage.value = 1
  fetchData()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  Object.assign(editForm, {
    poi: null,
    record_time: '',
    passenger_flow: 0,
    occupancy_rate: 0
  })
  editDialogVisible.value = true
  fetchPOIList()
}

// 查看
const handleView = (row) => {
  currentRow.value = { ...row }
  viewDialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(editForm, {
    poi: row.poi,
    record_time: row.record_time,
    passenger_flow: row.passenger_flow,
    occupancy_rate: parseFloat(row.occupancy_rate),
    record_id: row.record_id
  })
  editDialogVisible.value = true
  fetchPOIList()
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除记录 ${row.record_id} 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`${API_BASE}/dynamic/${row.record_id}`)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  })
}

// 保存
const handleSave = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const submitData = {
          poi: editForm.poi,
          record_time: editForm.record_time,
          passenger_flow: editForm.passenger_flow,
          occupancy_rate: editForm.occupancy_rate
        }

        if (isEdit.value) {
          await axios.put(`${API_BASE}/dynamic/${editForm.record_id}`, submitData)
          ElMessage.success('更新成功')
        } else {
          await axios.post(`${API_BASE}/dynamic/`, submitData)
          ElMessage.success('新增成功')
        }
        editDialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('保存失败:', error)
        ElMessage.error(error.response?.data?.detail || '保存失败')
      }
    }
  })
}

// 分页
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dynamic-data {
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
  color: #303133;
}

.search-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>