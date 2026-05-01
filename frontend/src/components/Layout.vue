<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="logo">
        <el-icon :size="24"><Book /></el-icon>
        <span class="title">图书借阅管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        mode="horizontal"
        background-color="#409EFF"
        text-color="#fff"
        active-text-color="#ffd04b"
        class="header-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/books">
          <el-icon><Reading /></el-icon>
          <span>图书管理</span>
        </el-menu-item>
        <el-menu-item index="/borrow">
          <el-icon><Goods /></el-icon>
          <span>借阅管理</span>
        </el-menu-item>
        <el-menu-item index="/records">
          <el-icon><Document /></el-icon>
          <span>借阅记录</span>
        </el-menu-item>
      </el-menu>
      <div class="user-info">
        <span class="username">{{ user.username }}</span>
        <el-tag v-if="user.is_admin" type="warning" size="small">管理员</el-tag>
        <el-button type="text" class="logout-btn" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </el-header>
    <el-main class="layout-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Book, Reading, Goods, Document, SwitchButton } from '@element-plus/icons-vue'
import store from '../store'
import { authApi } from '../api'

const router = useRouter()
const route = useRoute()

const user = computed(() => store.state.user)

const activeMenu = computed(() => {
  return route.path
})

const fetchCurrentUser = async () => {
  try {
    const response = await authApi.getCurrentUser()
    if (response.status === 200) {
      store.updateUser(response.data)
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const handleMenuSelect = (index) => {
  router.push(index)
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    store.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }).catch(() => {})
}

onMounted(() => {
  if (store.state.isLoggedIn) {
    fetchCurrentUser()
  }
})
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.layout-header {
  background-color: #409EFF;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  color: #fff;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
}

.title {
  margin-left: 8px;
}

.header-menu {
  flex: 1;
  border-bottom: none;
  margin-left: 30px;
}

.header-menu :deep(.el-menu-item) {
  border-bottom: none;
  background-color: transparent;
}

.header-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.username {
  font-size: 14px;
}

.logout-btn {
  color: #fff;
  padding: 0;
}

.logout-btn:hover {
  color: #ecf5ff;
}

.layout-main {
  background-color: #f5f7fa;
  padding: 20px;
}
</style>
