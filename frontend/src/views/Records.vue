<template>
  <div class="records-container">
    <el-card>
      <template #header>
        <span>借阅记录</span>
      </template>
      
      <el-table :data="borrowRecords" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="借阅人" width="120" v-if="isAdmin" />
        <el-table-column prop="book_title" label="书名" width="250" />
        <el-table-column prop="borrow_date" label="借阅日期" width="180" />
        <el-table-column prop="return_date" label="归还日期" width="180">
          <template #default="scope">
            {{ scope.row.return_date || '未归还' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'borrowed' ? 'warning' : 'success'">
              {{ scope.row.status === 'borrowed' ? '借阅中' : '已归还' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right" v-if="isAdmin">
          <template #default="scope">
            <el-button
              type="primary"
              link
              @click="handleReturn(scope.row)"
              :disabled="scope.row.status !== 'borrowed'"
            >
              归还
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { borrowApi } from '../api'
import store from '../store'

const loading = ref(false)
const borrowRecords = ref([])

const isAdmin = computed(() => store.isAdmin())

const fetchBorrowRecords = async () => {
  loading.value = true
  try {
    const response = await borrowApi.getBorrowRecords()
    if (response.status === 200) {
      borrowRecords.value = response.data
    }
  } catch (error) {
    console.error('获取借阅记录失败:', error)
  } finally {
    loading.value = false
  }
}

const handleReturn = (row) => {
  ElMessageBox.confirm(`确定要为用户 ${row.username} 归还《${row.book_title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      const response = await borrowApi.returnBook(row.id)
      if (response.status === 200) {
        ElMessage.success('归还成功')
        fetchBorrowRecords()
      }
    } catch (error) {
      console.error('归还失败:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchBorrowRecords()
})
</script>

<style scoped>
.records-container {
  padding: 0;
}
</style>
