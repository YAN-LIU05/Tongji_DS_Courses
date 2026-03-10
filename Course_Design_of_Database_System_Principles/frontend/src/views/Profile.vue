<template>
  <div class="profile">
    <h1 class="page-title">个人信息</h1>
    
    <el-row :gutter="20">
      <el-col :xs="24" :md="8">
        <el-card shadow="never">
          <template #header>
            <span class="card-title">基本资料</span>
          </template>
          <div class="profile-avatar">
            <el-avatar :size="100" :style="{ backgroundColor: '#409eff' }">
              {{ username.charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="profile-name">{{ username }}</div>
            <div class="profile-role">管理员</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="16">
        <el-card shadow="never">
          <template #header>
            <span class="card-title">个人信息</span>
          </template>
          <el-form label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="username" disabled />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="email" placeholder="未设置" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="phone" placeholder="未设置" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary">保存修改</el-button>
              <el-button>重置密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const username = ref(localStorage.getItem('username') || '用户')
const email = ref('')
const phone = ref('')
</script>

<style scoped>
.profile {
  padding: 0;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 20px 0;
  color: #303133;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.profile-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.profile-name {
  margin-top: 16px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.profile-role {
  margin-top: 8px;
  font-size: 14px;
  color: #909399;
}
</style>