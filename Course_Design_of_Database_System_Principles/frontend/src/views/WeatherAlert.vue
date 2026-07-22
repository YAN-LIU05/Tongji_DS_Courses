<template>
  <div class="weather-alert">
    <div class="page-header">
      <h2>天气预报与预警管理</h2>
    </div>

    <!-- 搜索和筛选区域 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" :inline="true" @submit.prevent>
        <el-form-item label="城市">
          <el-select 
            v-model="searchForm.city" 
            placeholder="选择城市" 
            clearable
            filterable
            style="width: 200px;"
          >
            <el-option label="上海" value="上海" />
            <el-option label="北京" value="北京" />
            <el-option label="广州" value="广州" />
            <el-option label="深圳" value="深圳" />
            <el-option label="杭州" value="杭州" />
          </el-select>
        </el-form-item>
        <el-form-item label="预警级别">
          <el-select v-model="searchForm.level" placeholder="选择预警级别" clearable>
            <el-option label="蓝色" value="蓝色" />
            <el-option label="黄色" value="黄色" />
            <el-option label="橙色" value="橙色" />
            <el-option label="红色" value="红色" />
          </el-select>
        </el-form-item>
        <el-form-item label="预警状态">
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
            <el-option label="生效中" value="生效中" />
            <el-option label="已解除" value="已解除" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="searchData">搜索</el-button>
          <el-button :icon="Refresh" @click="resetSearch">重置</el-button>
          <el-button type="success" :icon="Plus" @click="showCreateAlertDialog">新增预警</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 天气信息卡片 -->
    <el-row :gutter="20" class="weather-cards">
      <el-col :span="6" v-for="location in weatherLocations" :key="location.location_id">
        <el-card class="weather-card" shadow="hover">
          <div class="weather-header">
            <h3>{{ location.location_name }}</h3>
            <el-tag :type="getWeatherTagType(location.conditions)">{{ location.conditions }}</el-tag>
          </div>
          <div class="weather-main">
            <div class="temperature">{{ location.temperature }}°C</div>
            <div class="coordinates">({{ location.latitude }}, {{ location.longitude }})</div>
          </div>
          <div class="weather-footer">
            <div class="update-time">更新时间: {{ formatDate(location.update_time) }}</div>
            <el-button type="primary" size="small" @click="viewLocationDetails(location)">详情</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 预警列表 -->
    <el-card class="alerts-card" shadow="never">
      <div class="table-header">
        <h3>天气预警列表</h3>
        <div class="table-actions">
          <el-button :icon="Refresh" @click="loadAlerts" :loading="alertsLoading">
            刷新
          </el-button>
        </div>
      </div>
      
      <el-table 
        :data="alertsList" 
        v-loading="alertsLoading"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="alert_id" label="ID" width="80" />
        <el-table-column prop="title" label="预警标题" min-width="150" show-overflow-tooltip />
        <el-table-column prop="level" label="预警级别" width="120">
          <template #default="{ row }">
            <el-tag :type="getAlertLevelTag(row.level)">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getAlertStatusTag(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publish_time" label="发布时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.publish_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewAlertDetails(row)">
              查看
            </el-button>
            <el-button link type="primary" size="small" @click="editAlert(row)" v-if="row.status === '生效中'">
              编辑
            </el-button>
            <el-button link type="primary" size="small" @click="showAffectedPois(row)">
              受影响POI
            </el-button>
            <el-button link type="primary" size="small" @click="activateAlert(row)" v-if="row.status === '已解除'">
              激活
            </el-button>
            <el-button link type="danger" size="small" @click="deleteAlert(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="alertsPagination.page"
          v-model:page-size="alertsPagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="alertsPagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleAlertSizeChange"
          @current-change="handleAlertCurrentChange"
        />
      </div>
    </el-card>

    <!-- 位置详情对话框 -->
    <el-dialog
      v-model="locationDialogVisible"
      title="位置天气详情"
      width="600px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="位置ID">
          {{ currentLocation.location_id }}
        </el-descriptions-item>
        <el-descriptions-item label="城市名称">
          {{ currentLocation.location_name }}
        </el-descriptions-item>
        <el-descriptions-item label="经度">
          {{ currentLocation.longitude }}
        </el-descriptions-item>
        <el-descriptions-item label="纬度">
          {{ currentLocation.latitude }}
        </el-descriptions-item>
        <el-descriptions-item label="温度">
          {{ currentLocation.temperature }}°C
        </el-descriptions-item>
        <el-descriptions-item label="天气状况">
          <el-tag :type="getWeatherTagType(currentLocation.conditions)">
            {{ currentLocation.conditions }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatDate(currentLocation.update_time) }}
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="locationDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="updateWeather(currentLocation)">更新天气</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 预警详情对话框 -->
    <el-dialog
      v-model="alertDialogVisible"
      title="预警详情"
      width="600px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="预警ID">
          {{ currentAlert.alert_id }}
        </el-descriptions-item>
        <el-descriptions-item label="预警标题">
          {{ currentAlert.title }}
        </el-descriptions-item>
        <el-descriptions-item label="预警级别">
          <el-tag :type="getAlertLevelTag(currentAlert.level)">
            {{ currentAlert.level }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getAlertStatusTag(currentAlert.status)">
            {{ currentAlert.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发布时间">
          {{ formatDate(currentAlert.publish_time) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 预警编辑/创建对话框 -->
    <el-dialog
      v-model="editAlertDialogVisible"
      :title="isEditAlert ? '编辑预警' : '新增预警'"
      width="600px"
    >
      <el-form
        :model="editAlertForm"
        :rules="alertFormRules"
        ref="editAlertFormRef"
        label-width="100px"
      >
        <el-form-item label="预警标题" prop="title">
          <el-input v-model="editAlertForm.title" placeholder="请输入预警标题" />
        </el-form-item>
        <el-form-item label="预警级别" prop="level">
          <el-select v-model="editAlertForm.level" placeholder="请选择预警级别" style="width: 100%">
            <el-option label="蓝色" value="蓝色" />
            <el-option label="黄色" value="黄色" />
            <el-option label="橙色" value="橙色" />
            <el-option label="红色" value="红色" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="editAlertForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="生效中" value="生效中" />
            <el-option label="已解除" value="已解除" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editAlertDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAlert" :loading="submitAlertLoading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 受影响POI对话框 -->
    <el-dialog
      v-model="affectedPoiDialogVisible"
      title="受预警影响的POI"
      width="800px"
    >
      <div class="affected-poi-header">
        <h4>{{ currentAlert.title }} - 受影响POI</h4>
        <el-button type="primary" @click="showAddAffectedPoiDialog">添加POI</el-button>
      </div>

      <el-table 
        :data="affectedPois" 
        v-loading="affectedPoiLoading"
        stripe
        border
        style="width: 100%; margin-top: 16px;"
      >
        <el-table-column prop="poi_name" label="POI名称" min-width="150" />
        <el-table-column prop="poi_address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link type="danger" size="small" @click="removeAffectedPoi(row)">
              移除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="affectedPoiDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 添加受影响POI对话框 -->
    <el-dialog
      v-model="addAffectedPoiDialogVisible"
      title="添加受预警影响的POI"
      width="600px"
    >
      <el-form :model="addAffectedPoiForm" label-width="100px">
        <el-form-item label="POI选择">
          <el-select
            v-model="addAffectedPoiForm.poi"
            filterable
            remote
            reserve-keyword
            placeholder="请输入POI名称搜索"
            :remote-method="searchPois"
            :loading="searchPoiLoading"
            style="width: 100%"
          >
            <el-option
              v-for="item in poiOptions"
              :key="item.poi_id"
              :label="item.poi_name"
              :value="item.poi_id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addAffectedPoiDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addAffectedPoi" :loading="addAffectedPoiLoading">
            添加
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 天气更新对话框 -->
    <el-dialog
      v-model="updateWeatherDialogVisible"
      title="更新天气信息"
      width="500px"
    >
      <el-form :model="weatherUpdateForm" label-width="100px">
        <el-form-item label="温度">
          <el-input-number 
            v-model="weatherUpdateForm.temperature" 
            :min="-50" 
            :max="60" 
            :step="0.1" 
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="天气状况">
          <el-select v-model="weatherUpdateForm.conditions" placeholder="请选择天气状况" style="width: 100%">
            <el-option label="晴" value="晴" />
            <el-option label="多云" value="多云" />
            <el-option label="阴" value="阴" />
            <el-option label="雨" value="雨" />
            <el-option label="雪" value="雪" />
            <el-option label="雾" value="雾" />
            <el-option label="霾" value="霾" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="updateWeatherDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmUpdateWeather" :loading="updateWeatherLoading">
            更新
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import axios from 'axios'

// 搜索表单
const searchForm = reactive({
  city: '',
  level: '',
  status: ''
})

// 天气位置数据
const weatherLocations = ref([])
const weatherLoading = ref(false)

// 预警列表
const alertsList = ref([])
const alertsLoading = ref(false)

// 分页信息
const alertsPagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 对话框控制
const locationDialogVisible = ref(false)
const alertDialogVisible = ref(false)
const editAlertDialogVisible = ref(false)
const affectedPoiDialogVisible = ref(false)
const addAffectedPoiDialogVisible = ref(false)
const updateWeatherDialogVisible = ref(false)

// 当前选中项
const currentLocation = ref({})
const currentAlert = ref({})
const isEditAlert = ref(false)

// 预警表单
const editAlertFormRef = ref(null)
const editAlertForm = reactive({
  alert_id: null,
  title: '',
  level: '',
  status: '生效中'
})

// 预警表单验证规则
const alertFormRules = {
  title: [
    { required: true, message: '请输入预警标题', trigger: 'blur' },
    { min: 2, max: 100, message: '预警标题长度在2-100个字符', trigger: 'blur' }
  ],
  level: [
    { required: true, message: '请选择预警级别', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 提交加载状态
const submitAlertLoading = ref(false)
const updateWeatherLoading = ref(false)

// 受影响POI相关
const affectedPois = ref([])
const affectedPoiLoading = ref(false)
const addAffectedPoiLoading = ref(false)
const searchPoiLoading = ref(false)

// 添加受影响POI表单
const addAffectedPoiForm = reactive({
  poi: null
})

// POI选项
const poiOptions = ref([])

// 天气更新表单
const weatherUpdateForm = reactive({
  temperature: null,
  conditions: ''
})

// 获取天气标签类型
const getWeatherTagType = (condition) => {
  const conditionMap = {
    '晴': 'warning',
    '多云': 'info',
    '阴': 'primary',
    '雨': 'primary',
    '雪': 'info',
    '雾': 'info',
    '霾': 'danger'
  }
  return conditionMap[condition] || 'info'
}

// 获取预警级别标签类型
const getAlertLevelTag = (level) => {
  const levelMap = {
    '蓝色': 'info',
    '黄色': 'warning',
    '橙色': 'danger',
    '红色': 'danger'
  }
  return levelMap[level] || 'info'
}

// 获取预警状态标签类型
const getAlertStatusTag = (status) => {
  const statusMap = {
    '生效中': 'danger',
    '已解除': 'success'
  }
  return statusMap[status] || 'info'
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 加载天气位置信息
const loadWeatherLocations = async () => {
  weatherLoading.value = true
  try {
    const params = {}
    if (searchForm.city) {
      params.city = searchForm.city
    }

    const response = await axios.get('http://127.0.0.1:8000/api/reviews/locations/', { params })
    weatherLocations.value = response.data.results || response.data
  } catch (error) {
    console.error('加载天气位置信息失败:', error)
    ElMessage.error('加载天气位置信息失败')
  } finally {
    weatherLoading.value = false
  }
}

// 加载预警列表
const loadAlerts = async () => {
  alertsLoading.value = true
  try {
    const params = {
      page: alertsPagination.page,
      page_size: alertsPagination.pageSize
    }

    if (searchForm.level) {
      params.level = searchForm.level
    }

    if (searchForm.status) {
      params.status = searchForm.status
    }

    const response = await axios.get('http://127.0.0.1:8000/api/reviews/alerts/', { params })
    const data = response.data
    
    alertsList.value = data.results || data
    alertsPagination.total = data.count || (Array.isArray(data) ? data.length : 0)
  } catch (error) {
    console.error('加载预警列表失败:', error)
    ElMessage.error('加载预警列表失败')
  } finally {
    alertsLoading.value = false
  }
}

// 搜索数据
const searchData = () => {
  alertsPagination.page = 1
  loadWeatherLocations()
  loadAlerts()
}

// 重置搜索
const resetSearch = () => {
  searchForm.city = ''
  searchForm.level = ''
  searchForm.status = ''
  alertsPagination.page = 1
  loadWeatherLocations()
  loadAlerts()
}

// 分页处理 - 预警
const handleAlertSizeChange = (size) => {
  alertsPagination.pageSize = size
  alertsPagination.page = 1
  loadAlerts()
}

const handleAlertCurrentChange = (page) => {
  alertsPagination.page = page
  loadAlerts()
}

// 查看位置详情
const viewLocationDetails = (location) => {
  currentLocation.value = { ...location }
  locationDialogVisible.value = true
}

// 查看预警详情
const viewAlertDetails = (alert) => {
  currentAlert.value = { ...alert }
  alertDialogVisible.value = true
}

// 编辑预警
const editAlert = (alert) => {
  isEditAlert.value = true
  Object.assign(editAlertForm, {
    alert_id: alert.alert_id,
    title: alert.title,
    level: alert.level,
    status: alert.status
  })
  editAlertDialogVisible.value = true
}

// 显示创建预警对话框
const showCreateAlertDialog = () => {
  isEditAlert.value = false
  Object.assign(editAlertForm, {
    alert_id: null,
    title: '',
    level: '',
    status: '生效中'
  })
  editAlertDialogVisible.value = true
}

// 提交预警信息
const submitAlert = async () => {
  if (!editAlertFormRef.value) return

  await editAlertFormRef.value.validate(async (valid) => {
    if (valid) {
      submitAlertLoading.value = true
      try {
        if (isEditAlert.value) {
          // 更新预警
          await axios.put(
            `http://127.0.0.1:8000/api/reviews/alerts/${editAlertForm.alert_id}/`,
            {
              title: editAlertForm.title,
              level: editAlertForm.level,
              status: editAlertForm.status
            }
          )
          ElMessage.success('预警信息更新成功')
        } else {
          // 创建预警
          await axios.post('http://127.0.0.1:8000/api/reviews/alerts/', {
            title: editAlertForm.title,
            level: editAlertForm.level,
            status: editAlertForm.status
          })
          ElMessage.success('预警创建成功')
        }
        
        editAlertDialogVisible.value = false
        loadAlerts()
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error(error.response?.data?.message || '操作失败')
      } finally {
        submitAlertLoading.value = false
      }
    }
  })
}

// 删除预警
const deleteAlert = (row) => {
  ElMessageBox.confirm(
    `确定要删除预警 "${row.title}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.delete(`http://127.0.0.1:8000/api/reviews/alerts/${row.alert_id}/`)
      ElMessage.success('删除成功')
      loadAlerts()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  })
}

// 显示受预警影响的POI
const showAffectedPois = async (alert) => {
  currentAlert.value = { ...alert }
  await loadAffectedPois(alert.alert_id)
  affectedPoiDialogVisible.value = true
}

// 加载受预警影响的POI
const loadAffectedPois = async (alertId) => {
  affectedPoiLoading.value = true
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/reviews/alert-affected-pois`)
    affectedPois.value = response.data.results || response.data
  } catch (error) {
    console.error('加载受预警影响的POI失败:', error)
    ElMessage.error('加载受预警影响的POI失败')
    affectedPois.value = []
  } finally {
    affectedPoiLoading.value = false
  }
}

// 显示添加受预警影响的POI对话框
const showAddAffectedPoiDialog = () => {
  addAffectedPoiForm.poi = null
  poiOptions.value = []
  addAffectedPoiDialogVisible.value = true
}

// 搜索POIs
const searchPois = async (query) => {
  if (!query) {
    poiOptions.value = []
    return
  }

  searchPoiLoading.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/attractions/pois/', {
      params: {
        search: query,
        page_size: 20
      }
    })
    poiOptions.value = response.data.results || response.data
  } catch (error) {
    console.error('搜索POI失败:', error)
    poiOptions.value = []
  } finally {
    searchPoiLoading.value = false
  }
}

// 添加受预警影响的POI
const addAffectedPoi = async () => {
  if (!addAffectedPoiForm.poi) {
    ElMessage.warning('请选择POI')
    return
  }

  addAffectedPoiLoading.value = true
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/reviews/alerts/${currentAlert.value.alert_id}/add_poi/`,
      {
        poi: addAffectedPoiForm.poi
      }
    )
    ElMessage.success('POI添加成功')
    addAffectedPoiDialogVisible.value = false
    await loadAffectedPois(currentAlert.value.alert_id)
  } catch (error) {
    console.error('添加POI失败:', error)
    ElMessage.error(error.response?.data?.message || '添加POI失败')
  } finally {
    addAffectedPoiLoading.value = false
  }
}

// 移除受预警影响的POI
const removeAffectedPoi = (row) => {
  ElMessageBox.confirm(
    `确定要移除POI "${row.poi_name}" 的预警关联吗？`,
    '移除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      // 由于API没有直接的移除方法，我们使用删除受影响POI关联的方法
      // 这里可能需要根据实际API调整
      ElMessage.warning('移除功能待实现')
    } catch (error) {
      console.error('移除POI失败:', error)
      ElMessage.error('移除POI失败')
    }
  })
}

// 更新天气
const updateWeather = (location) => {
  currentLocation.value = { ...location }
  weatherUpdateForm.temperature = location.temperature
  weatherUpdateForm.conditions = location.conditions
  updateWeatherDialogVisible.value = true
}

// 确认更新天气
const confirmUpdateWeather = async () => {
  updateWeatherLoading.value = true
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/reviews/locations/${currentLocation.value.location_id}/update_weather/`,
      {
        temperature: weatherUpdateForm.temperature,
        conditions: weatherUpdateForm.conditions
      }
    )
    ElMessage.success('天气信息更新成功')
    updateWeatherDialogVisible.value = false
    loadWeatherLocations()
  } catch (error) {
    console.error('更新天气失败:', error)
    ElMessage.error(error.response?.data?.message || '更新天气失败')
  } finally {
    updateWeatherLoading.value = false
  }
}

// 激活预警
const activateAlert = async (row) => {
  try {
    await axios.post(`http://127.0.0.1:8000/api/reviews/alerts/${row.alert_id}/activate/`)
    ElMessage.success('预警激活成功')
    loadAlerts()
  } catch (error) {
    console.error('激活预警失败:', error)
    ElMessage.error(error.response?.data?.message || '激活预警失败')
  }
}

// 初始化
onMounted(() => {
  loadWeatherLocations()
  loadAlerts()
})
</script>

<style scoped>
.weather-alert {
  padding: 20px;
}

.page-header h2 {
  margin: 0 0 20px 0;
  color: #303133;
  font-weight: 600;
}

.search-card {
  margin-bottom: 20px;
}

.weather-cards {
  margin-bottom: 20px;
}

.weather-card {
  cursor: pointer;
  transition: all 0.3s;
}

.weather-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.weather-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.weather-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.weather-main {
  text-align: center;
  margin-bottom: 16px;
}

.temperature {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.coordinates {
  font-size: 12px;
  color: #909399;
}

.weather-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #ebeef5;
  padding-top: 12px;
}

.update-time {
  font-size: 12px;
  color: #909399;
}

.alerts-card {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.affected-poi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.affected-poi-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}
</style>