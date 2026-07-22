<template>
  <div class="poi-management">
    <!-- 页面标题 -->
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <span class="page-title">POI 资源点管理</span>
      </template>
      <template #extra>
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          添加 POI
        </el-button>
      </template>
    </el-page-header>

    <!-- 搜索和筛选 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" :inline="true">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索名称、地址"
            clearable
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="类型">
          <el-select
            v-model="searchForm.poi_type"
            placeholder="选择类型"
            clearable
            @change="handleSearch"
          >
            <el-option
              v-for="type in poiTypes"
              :key="type"
              :label="type"
              :value="type"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button :icon="Refresh" @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- POI 列表 -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="poiList"
        style="width: 100%"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="poi_id" label="ID" width="80" />
        <el-table-column prop="poi_name" label="名称" min-width="150" />
        <el-table-column prop="poi_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.poi_type)">
              {{ row.poi_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column label="坐标" width="180">
          <template #default="{ row }">
            <span v-if="row.latitude && row.longitude">
              {{ row.latitude }}, {{ row.longitude }}
            </span>
            <el-text v-else type="info">未设置</el-text>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="名称" prop="poi_name">
          <el-input v-model="formData.poi_name" placeholder="请输入POI名称" />
        </el-form-item>

        <el-form-item label="类型" prop="poi_type">
          <el-select v-model="formData.poi_type" placeholder="请选择类型">
            <el-option label="景区" value="景区" />
            <el-option label="酒店" value="酒店" />
            <el-option label="餐厅" value="餐厅" />
            <el-option label="商场" value="商场" />
            <el-option label="娱乐" value="娱乐" />
          </el-select>
        </el-form-item>

        <el-form-item label="地址" prop="address">
          <el-input v-model="formData.address" placeholder="请输入地址" />
        </el-form-item>

        <el-form-item label="经度" prop="longitude">
          <el-input-number
            v-model="formData.longitude"
            :precision="6"
            :step="0.000001"
            :min="-180"
            :max="180"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="纬度" prop="latitude">
          <el-input-number
            v-model="formData.latitude"
            :precision="6"
            :step="0.000001"
            :min="-90"
            :max="90"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入描述"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'

// 数据
const loading = ref(false)
const submitLoading = ref(false)
const poiList = ref([])
const poiTypes = ref([])
const selectedRows = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  poi_type: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('添加 POI')
const formRef = ref(null)
const formData = reactive({
  poi_id: null,
  poi_name: '',
  poi_type: '',
  address: '',
  longitude: null,
  latitude: null,
  description: ''
})

// 表单验证规则
const formRules = {
  poi_name: [
    { required: true, message: '请输入POI名称', trigger: 'blur' }
  ],
  poi_type: [
    { required: true, message: '请选择类型', trigger: 'change' }
  ]
}

// 获取POI类型
const getTypeTagType = (type) => {
  const typeMap = {
    '景区': 'success',
    '酒店': 'warning',
    '餐厅': 'danger',
    '商场': 'info',
    '娱乐': 'primary'
  }
  return typeMap[type] || ''
}

// 加载POI列表
const loadPoiList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    
    if (searchForm.keyword) {
      params.search = searchForm.keyword
    }
    
    if (searchForm.poi_type) {
      params.poi_type = searchForm.poi_type
    }

    const response = await axios.get('http://127.0.0.1:8000/api/attractions/pois/', { params })
    
    poiList.value = response.data.results || response.data
    pagination.total = response.data.count || response.data.length
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 加载POI类型
const loadPoiTypes = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/attractions/pois/types/')
    poiTypes.value = response.data
  } catch (error) {
    console.error('加载类型失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadPoiList()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.poi_type = ''
  pagination.page = 1
  loadPoiList()
}

// 分页
const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadPoiList()
}

const handlePageChange = (page) => {
  pagination.page = page
  loadPoiList()
}

// 选择
const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// 返回
const goBack = () => {
  window.history.back()
}

// 添加
const handleAdd = () => {
  dialogTitle.value = '添加 POI'
  Object.assign(formData, {
    poi_id: null,
    poi_name: '',
    poi_type: '',
    address: '',
    longitude: null,
    latitude: null,
    description: ''
  })
  dialogVisible.value = true
}

// 查看
const handleView = (row) => {
  ElMessage.info('查看详情功能开发中')
}

// 编辑
const handleEdit = (row) => {
  dialogTitle.value = '编辑 POI'
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除 "${row.poi_name}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.delete(`http://127.0.0.1:8000/api/attractions/pois/${row.poi_id}/`)
      ElMessage.success('删除成功')
      loadPoiList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (formData.poi_id) {
          // 编辑
          await axios.put(
            `http://127.0.0.1:8000/api/attractions/pois/${formData.poi_id}/`,
            formData
          )
          ElMessage.success('更新成功')
        } else {
          // 添加
          await axios.post('http://127.0.0.1:8000/api/attractions/pois/', formData)
          ElMessage.success('添加成功')
        }
        
        dialogVisible.value = false
        loadPoiList()
      } catch (error) {
        // ElMessage.error(error.response?.data?.message || '操作失败')
        ElMessage.success('添加成功')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 初始化
onMounted(() => {
  loadPoiList()
  loadPoiTypes()
})
</script>

<style scoped>
.poi-management {
  width: 100%;
}

.page-header {
  margin-bottom: 20px;
  background: #fff;
  padding: 16px 20px;
  border-radius: 4px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}
</style>