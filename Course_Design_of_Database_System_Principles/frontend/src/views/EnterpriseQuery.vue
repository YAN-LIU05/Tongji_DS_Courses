<template>
  <div class="enterprise-query">
    <div class="query-header">
      <h2>企业查询管理</h2>
    </div>

    <!-- 企业查询搜索区域 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" :inline="true" @submit.prevent>
        <el-form-item label="企业名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="输入企业名称" 
            clearable
            @keyup.enter="searchEnterprises"
          />
        </el-form-item>
        <el-form-item label="企业类型">
          <el-select v-model="searchForm.type" placeholder="选择企业类型" clearable>
            <el-option label="旅行社" value="旅行社" />
            <el-option label="旅游集团" value="旅游集团" />
            <el-option label="景区管理" value="景区管理" />
            <el-option label="酒店集团" value="酒店集团" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="searchEnterprises">搜索</el-button>
          <el-button :icon="Refresh" @click="resetSearch">重置</el-button>
          <el-button type="success" :icon="Plus" @click="showCreateDialog">新增企业</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 企业列表 -->
    <el-card class="list-card" shadow="never">
      <div class="table-header">
        <h3>企业列表</h3>
        <div class="table-actions">
          <el-button 
            :icon="Refresh" 
            @click="loadEnterprises" 
            :loading="loading"
          >
            刷新
          </el-button>
        </div>
      </div>
      
      <el-table 
        :data="enterpriseList" 
        v-loading="loading"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="enterprise_id" label="ID" width="80" />
        <el-table-column prop="enterprise_name" label="企业名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="enterprise_type" label="企业类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getEnterpriseTypeTag(row.enterprise_type)">
              {{ row.enterprise_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewEnterprise(row)">
              查看
            </el-button>
            <el-button link type="primary" size="small" @click="editEnterprise(row)">
              编辑
            </el-button>
            <el-button link type="primary" size="small" @click="showPoiLinks(row)">
              POI关联
            </el-button>
            <el-button link type="danger" size="small" @click="deleteEnterprise(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 企业详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="企业详情"
      width="600px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="企业ID">
          {{ currentEnterprise.enterprise_id }}
        </el-descriptions-item>
        <el-descriptions-item label="企业名称">
          {{ currentEnterprise.enterprise_name }}
        </el-descriptions-item>
        <el-descriptions-item label="企业类型">
          <el-tag :type="getEnterpriseTypeTag(currentEnterprise.enterprise_type)">
            {{ currentEnterprise.enterprise_type }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(currentEnterprise.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatDate(currentEnterprise.updated_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 企业编辑/创建对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="isEdit ? '编辑企业' : '新增企业'"
      width="500px"
    >
      <el-form
        :model="editForm"
        :rules="formRules"
        ref="editFormRef"
        label-width="100px"
      >
        <el-form-item label="企业名称" prop="enterprise_name">
          <el-input 
            v-model="editForm.enterprise_name" 
            placeholder="请输入企业名称"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item label="企业类型" prop="enterprise_type">
          <el-select v-model="editForm.enterprise_type" placeholder="请选择企业类型" style="width: 100%">
            <el-option label="旅行社" value="旅行社" />
            <el-option label="旅游集团" value="旅游集团" />
            <el-option label="景区管理" value="景区管理" />
            <el-option label="酒店集团" value="酒店集团" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEnterprise" :loading="submitLoading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- POI关联管理对话框 -->
    <el-dialog
      v-model="poiLinkDialogVisible"
      title="POI关联管理"
      width="800px"
    >
      <div class="poi-link-header">
        <h4>{{ currentEnterprise.enterprise_name }} - POI关联</h4>
        <el-button type="primary" @click="showAddPoiDialog">添加POI关联</el-button>
      </div>

      <el-table 
        :data="poiLinks" 
        v-loading="poiLinksLoading"
        stripe
        border
        style="width: 100%; margin-top: 16px;"
      >
        <el-table-column prop="poi_name" label="POI名称" min-width="150" />
        <el-table-column prop="poi_address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="relationship_type" label="关联类型" width="120">
          <template #default="{ row }">
            <el-tag type="info">{{ row.relationship_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link type="danger" size="small" @click="removePoiLink(row)">
              移除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="poiLinkDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 添加POI对话框 -->
    <el-dialog
      v-model="addPoiDialogVisible"
      title="添加POI关联"
      width="600px"
    >
      <el-form :model="addPoiForm" label-width="100px">
        <el-form-item label="POI选择">
          <el-select
            v-model="addPoiForm.poi"
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
        <el-form-item label="关联类型">
          <el-select v-model="addPoiForm.relationship_type" placeholder="请选择关联类型" style="width: 100%">
            <el-option label="管理" value="管理" />
            <el-option label="合作" value="合作" />
            <el-option label="运营" value="运营" />
            <el-option label="投资" value="投资" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addPoiDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addPoiToEnterprise" :loading="addPoiLoading">
            添加
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 企业POI关联管理 -->
    <el-card class="link-management-card" shadow="never">
      <div class="table-header">
        <h3>企业POI关联管理</h3>
        <div class="table-actions">
          <el-button type="primary" @click="showCreateLinkDialog">新增关联</el-button>
          <el-button :icon="Refresh" @click="loadEnterprisePoiLinks" :loading="linksLoading">
            刷新
          </el-button>
        </div>
      </div>

      <el-table
        :data="enterprisePoiLinks"
        v-loading="linksLoading"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="enterprise" label="ID" width="80" />
        <el-table-column prop="enterprise_name" label="企业名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="poi_name" label="POI名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="relationship_type" label="关联类型" width="120">
          <template #default="{ row }">
            <el-tag type="info">{{ row.relationship_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="editLink(row)">
              编辑
            </el-button>
            <el-button link type="danger" size="small" @click="deleteLink(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="linksPagination.page"
          v-model:page-size="linksPagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="linksPagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleLinkSizeChange"
          @current-change="handleLinkCurrentChange"
        />
      </div>
    </el-card>

    <!-- 企业POI关联编辑/创建对话框 -->
    <el-dialog
      v-model="linkDialogVisible"
      :title="isLinkEdit ? '编辑关联' : '新增关联'"
      width="600px"
    >
      <el-form
        :model="linkForm"
        :rules="linkFormRules"
        ref="linkFormRef"
        label-width="100px"
      >
        <el-form-item label="企业" prop="enterprise">
          <el-select
            v-model="linkForm.enterprise"
            placeholder="请选择企业"
            filterable
            :loading="enterprisesLoading"
            style="width: 100%"
            :disabled="isLinkEdit"
          >
            <el-option
              v-for="item in allEnterprises"
              :key="item.enterprise_id"
              :label="item.enterprise_name"
              :value="item.enterprise_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="POI" prop="poi">
          <el-select
            v-model="linkForm.poi"
            placeholder="请选择POI"
            filterable
            remote
            reserve-keyword
            :remote-method="searchAllPois"
            :loading="allPoiLoading"
            style="width: 100%"
            :disabled="isLinkEdit"
          >
            <el-option
              v-for="item in allPoiOptions"
              :key="item.poi_id"
              :label="item.poi_name"
              :value="item.poi_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关联类型" prop="relationship_type">
          <el-select v-model="linkForm.relationship_type" placeholder="请选择关联类型" style="width: 100%">
            <el-option label="管理" value="管理" />
            <el-option label="合作" value="合作" />
            <el-option label="运营" value="运营" />
            <el-option label="投资" value="投资" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="linkDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitLink" :loading="linkSubmitLoading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue' // Added nextTick
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import axios from 'axios'

// --- Enterprise Management ---
const searchForm = reactive({
  name: '',
  type: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const enterpriseList = ref([])
const loading = ref(false)
const submitLoading = ref(false)

const viewDialogVisible = ref(false)
const editDialogVisible = ref(false)

const currentEnterprise = ref({})
const isEdit = ref(false)

const editFormRef = ref(null)
const editForm = reactive({
  enterprise_id: null,
  enterprise_name: '',
  enterprise_type: ''
})

const formRules = {
  enterprise_name: [
    { required: true, message: '请输入企业名称', trigger: 'blur' },
    { min: 2, max: 100, message: '企业名称长度在2-100个字符', trigger: 'blur' }
  ],
  enterprise_type: [
    { required: true, message: '请选择企业类型', trigger: 'change' }
  ]
}

const getEnterpriseTypeTag = (type) => {
  const typeMap = {
    '旅行社': 'warning',
    '旅游集团': 'success',
    '景区管理': 'primary',
    '酒店集团': 'danger',
    '事业单位': 'info',
    '上市公司': 'success',
    '政府机构': 'warning',
    '民营企业': 'primary',
    '其他': 'info'
  }
  return typeMap[type] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadEnterprises = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    if (searchForm.name) {
      params.enterprise_name = searchForm.name
    }

    if (searchForm.type) {
      params.enterprise_type = searchForm.type
    }

    const response = await axios.get('http://127.0.0.1:8000/api/orders/enterprises/', { params })
    const data = response.data
    
    enterpriseList.value = data.results || []
    pagination.total = data.count || 0
  } catch (error) {
    console.error('加载企业列表失败:', error)
    ElMessage.error('加载企业列表失败')
  } finally {
    loading.value = false
  }
}

const searchEnterprises = () => {
  pagination.page = 1
  loadEnterprises()
}

const resetSearch = () => {
  searchForm.name = ''
  searchForm.type = ''
  pagination.page = 1
  loadEnterprises()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  loadEnterprises()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadEnterprises()
}

const viewEnterprise = (row) => {
  currentEnterprise.value = { ...row }
  viewDialogVisible.value = true
}

const editEnterprise = (row) => {
  isEdit.value = true
  Object.assign(editForm, {
    enterprise_id: row.enterprise_id,
    enterprise_name: row.enterprise_name,
    enterprise_type: row.enterprise_type
  })
  editDialogVisible.value = true
}

const showCreateDialog = () => {
  isEdit.value = false
  Object.assign(editForm, {
    enterprise_id: null,
    enterprise_name: '',
    enterprise_type: ''
  })
  // Ensure the form is cleared and validated correctly for new creation
  if (editFormRef.value) {
    nextTick(() => {
      editFormRef.value.clearValidate()
    })
  }
  editDialogVisible.value = true
}

const submitEnterprise = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await axios.put(
            `http://127.0.0.1:8000/api/orders/enterprises/${editForm.enterprise_id}/`,
            {
              enterprise_name: editForm.enterprise_name,
              enterprise_type: editForm.enterprise_type
            }
          )
          ElMessage.success('企业信息更新成功')
        } else {
          await axios.post('http://127.0.0.1:8000/api/orders/enterprises/', {
            enterprise_name: editForm.enterprise_name,
            enterprise_type: editForm.enterprise_type
          })
          ElMessage.success('企业创建成功')
        }
        
        editDialogVisible.value = false
        loadEnterprises()
        // Also refresh the allEnterprises list for link creation/editing
        loadAllEnterprises() 
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error(error.response?.data?.message || '操作失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const deleteEnterprise = (row) => {
  ElMessageBox.confirm(
    `确定要删除企业 "${row.enterprise_name}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.delete(`http://127.0.0.1:8000/api/orders/enterprises/${row.enterprise_id}/`)
      ElMessage.success('删除成功')
      loadEnterprises()
      loadEnterprisePoiLinks() // Refresh the general link table
      loadAllEnterprises(); // Refresh all enterprises for selection dropdowns
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  })
}

// --- POI Association for a specific Enterprise (within its own dialog) ---
const poiLinkDialogVisible = ref(false)
const addPoiDialogVisible = ref(false)
const poiLinks = ref([]) // Links specific to `currentEnterprise`
const poiLinksLoading = ref(false)
const addPoiLoading = ref(false)
const searchPoiLoading = ref(false)

const addPoiForm = reactive({
  poi_id: null, // Corrected to poi_id
  relationship_type: '合作'
})

const poiOptions = ref([]) // POIs for the "add POI" dropdown

const showPoiLinks = async (row) => {
  currentEnterprise.value = { ...row }
  await loadPoiLinksForEnterprise(row.enterprise_id)
  poiLinkDialogVisible.value = true
}

// Loads POI links specific to the current enterprise
const loadPoiLinksForEnterprise = async (enterpriseId) => {
  poiLinksLoading.value = true
  try {
    // This endpoint should return links filtered by enterprise_id
    const response = await axios.get('http://127.0.0.1:8000/api/orders/enterprise-poi-links/', {
      params: { enterprise: enterpriseId, page_size: 100 } // Filter by enterprise ID
    })
    // Assuming response.data.results has the structure:
    // { id, enterprise: { enterprise_id, ... }, poi: { poi_id, ... }, relationship_type }
    poiLinks.value = response.data.results || []
  } catch (error) {
    console.error(`加载企业 ${enterpriseId} 的POI关联失败:`, error)
    ElMessage.error('加载特定企业POI关联失败')
    poiLinks.value = []
  } finally {
    poiLinksLoading.value = false
  }
}

const showAddPoiDialog = () => {
  addPoiForm.poi_id = null
  addPoiForm.relationship_type = '合作'
  poiOptions.value = [] // Clear previous search results
  addPoiDialogVisible.value = true
}

const searchPois = async (query) => {
  if (!query) {
    poiOptions.value = []
    return
  }
  searchPoiLoading.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/attractions/pois/', {
      params: { search: query, page_size: 20 }
    })
    poiOptions.value = response.data.results || []
  } catch (error) {
    console.error('搜索POI失败:', error)
    poiOptions.value = []
  } finally {
    searchPoiLoading.value = false
  }
}

const addPoiToEnterprise = async () => {
  if (!addPoiForm.poi_id) {
    ElMessage.warning('请选择POI')
    return
  }
  addPoiLoading.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/orders/enterprise-poi-links/', {
      enterprise: currentEnterprise.value.enterprise_id,
      poi: addPoiForm.poi_id,
      relationship_type: addPoiForm.relationship_type
    })
    ElMessage.success('POI关联成功')
    addPoiDialogVisible.value = false
    await loadPoiLinksForEnterprise(currentEnterprise.value.enterprise_id) // Refresh specific enterprise's links
    loadEnterprisePoiLinks() // Refresh the main links table
  } catch (error) {
    console.error('添加POI关联失败:', error)
    ElMessage.error(error.response?.data?.detail || error.response?.data?.message || '添加POI关联失败')
  } finally {
    addPoiLoading.value = false
  }
}

const removePoiLink = (row) => {
  ElMessageBox.confirm(
    `确定要移除POI "${row.poi?.poi_name || '未知'}" 的关联吗？`,
    '移除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      // Use the link's ID for deletion
      await axios.delete(`http://127.0.0.1:8000/api/orders/enterprise-poi-links/${row.id}/`)
      ElMessage.success('移除关联成功')
      await loadPoiLinksForEnterprise(currentEnterprise.value.enterprise_id) // Refresh specific enterprise's links
      loadEnterprisePoiLinks() // Refresh the main links table
    } catch (error) {
      console.error('移除关联失败:', error)
      ElMessage.error('移除关联失败')
    }
  })
}

// --- General Enterprise-POI Link Management (bottom table) ---
const enterprisePoiLinks = ref([])
const linksLoading = ref(false)
const linksPagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const linkDialogVisible = ref(false)
const isLinkEdit = ref(false)
const linkSubmitLoading = ref(false)
const enterprisesLoading = ref(false)
const allPoiLoading = ref(false)

const allEnterprises = ref([]) // All enterprises for dropdown
const allPoiOptions = ref([]) // All POIs for dropdown (can be searched)

const linkFormRef = ref(null)
const linkForm = reactive({
  id: null,
  enterprise: null, // enterprise_id
  poi: null, // poi_id
  relationship_type: '合作'
})

const linkFormRules = {
  enterprise: [
    { required: true, message: '请选择企业', trigger: 'change' }
  ],
  poi: [
    { required: true, message: '请选择POI', trigger: 'change' }
  ],
  relationship_type: [
    { required: true, message: '请选择关联类型', trigger: 'change' }
  ]
}

const loadEnterprisePoiLinks = async () => {
  linksLoading.value = true
  try {
    const params = {
      page: linksPagination.page,
      page_size: linksPagination.pageSize
    }
    const response = await axios.get('http://127.0.0.1:8000/api/orders/enterprise-poi-links/', { params })
    const data = response.data
    enterprisePoiLinks.value = data.results || []
    linksPagination.total = data.count || 0
  } catch (error) {
    console.error('加载企业POI关联失败:', error)
    ElMessage.error('加载企业POI关联失败')
  } finally {
    linksLoading.value = false
  }
}

const handleLinkSizeChange = (size) => {
  linksPagination.pageSize = size
  linksPagination.page = 1
  loadEnterprisePoiLinks()
}

const handleLinkCurrentChange = (page) => {
  linksPagination.page = page
  loadEnterprisePoiLinks()
}

const showCreateLinkDialog = async () => {
  isLinkEdit.value = false
  Object.assign(linkForm, {
    id: null,
    enterprise: null,
    poi: null,
    relationship_type: '合作'
  })
  
  await loadAllEnterprises()
  allPoiOptions.value = [] // Clear for new search

  // Ensure form validation is reset for new entry
  if (linkFormRef.value) {
    nextTick(() => {
      linkFormRef.value.clearValidate()
    })
  }
  linkDialogVisible.value = true
}

const loadAllEnterprises = async () => {
  enterprisesLoading.value = true
  try {
    // Fetch all enterprises, perhaps with a larger page_size or no pagination
    const response = await axios.get('http://127.0.0.1:8000/api/orders/enterprises/', {
      params: { page_size: 1000 } // Adjust as needed
    })
    allEnterprises.value = response.data.results || []
  } catch (error) {
    console.error('加载所有企业选项失败:', error)
    ElMessage.error('加载所有企业选项失败')
  } finally {
    enterprisesLoading.value = false
  }
}

const searchAllPois = async (query) => {
  if (!query) {
    allPoiOptions.value = []
    return
  }
  allPoiLoading.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/attractions/pois/', {
      params: { search: query, page_size: 20 }
    })
    allPoiOptions.value = response.data.results || []
  } catch (error) {
    console.error('搜索所有POI失败:', error)
    allPoiOptions.value = []
  } finally {
    allPoiLoading.value = false
  }
}

const editLink = async (row) => {
  isLinkEdit.value = true
  Object.assign(linkForm, {
    id: row.id,
    enterprise: row.enterprise.enterprise_id,
    poi: row.poi.poi_id,
    relationship_type: row.relationship_type
  })

  await loadAllEnterprises() // Load all enterprises for the dropdown

  // Ensure the current POI for editing is available in the options,
  // even if it wouldn't appear in a default remote search.
  if (row.poi && !allPoiOptions.value.some(p => p.poi_id === row.poi.poi_id)) {
      allPoiOptions.value = [row.poi, ...allPoiOptions.value];
  }

  // Ensure form validation is reset for editing
  if (linkFormRef.value) {
    nextTick(() => {
      linkFormRef.value.clearValidate()
    })
  }

  linkDialogVisible.value = true
}

const submitLink = async () => {
  if (!linkFormRef.value) return

  await linkFormRef.value.validate(async (valid) => {
    if (valid) {
      linkSubmitLoading.value = true
      try {
        if (isLinkEdit.value) {
          await axios.put(
            `http://127.0.0.1:8000/api/orders/enterprise-poi-links/${linkForm.id}/`,
            {
              enterprise: linkForm.enterprise,
              poi: linkForm.poi,
              relationship_type: linkForm.relationship_type
            }
          )
          ElMessage.success('关联信息更新成功')
        } else {
          await axios.post('http://127.0.0.1:8000/api/orders/enterprise-poi-links/', {
            enterprise: linkForm.enterprise,
            poi: linkForm.poi,
            relationship_type: linkForm.relationship_type
          })
          ElMessage.success('关联创建成功')
        }

        linkDialogVisible.value = false
        loadEnterprisePoiLinks() // Refresh the main links table
        // If the edited/created link affects the current enterprise's POI dialog, refresh that too
        if (currentEnterprise.value.enterprise_id === linkForm.enterprise && poiLinkDialogVisible.value) {
            loadPoiLinksForEnterprise(currentEnterprise.value.enterprise_id);
        }
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error(error.response?.data?.detail || error.response?.data?.message || '操作失败')
      } finally {
        linkSubmitLoading.value = false
      }
    }
  })
}

const deleteLink = (row) => {
  ElMessageBox.confirm(
    `确定要删除企业 "${row.enterprise.enterprise_name}" 与POI "${row.poi.poi_name}" 的关联吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.delete(`http://127.0.0.1:8000/api/orders/enterprise-poi-links/${row.id}/`)
      ElMessage.success('删除成功')
      loadEnterprisePoiLinks() // Refresh the main links table
      // If the deleted link was part of a currently viewed enterprise, refresh that too
      if (currentEnterprise.value.enterprise_id === row.enterprise.enterprise_id && poiLinkDialogVisible.value) {
          loadPoiLinksForEnterprise(currentEnterprise.value.enterprise_id);
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  })
}

// --- Initialization ---
onMounted(() => {
  loadEnterprises()
  loadEnterprisePoiLinks()
  loadAllEnterprises(); // Pre-load for link management
})
</script>