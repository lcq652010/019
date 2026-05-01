<template>
  <div class="borrow-container">
    <el-card>
      <template #header>
        <span>我的借阅</span>
      </template>
      
      <el-table :data="borrowRecords" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
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
        <el-table-column label="操作" width="120" fixed="right">
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const borrowRecords = ref([])

const fetchBorrowRecords = async () => {
  loading.value = true
  const token = localStorage.getItem('token')
  try {
    const response = await fetch('/api/borrow-records', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    const data = await response.json()
    if (response.ok) {
      borrowRecords.value = data.filter(record => record.status === 'borrowed')
    }
  } catch (error) {
    ElMessage.error('获取借阅记录失败')
  } finally {
    loading.value = false
  }
}

const handleReturn = (row) => {
  ElMessageBox.confirm(`确定要归还《${row.book_title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    const token = localStorage.getItem('token')
    try {
      const response = await fetch(`/api/return/${row.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      const data = await response.json()
      
      if (response.ok) {
        ElMessage.success('归还成功')
        fetchBorrowRecords()
      } else {
        ElMessage.error(data.message || '归还失败')
      }
    } catch (error) {
      ElMessage.error('网络错误')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchBorrowRecords()
})
</script>

<style scoped>
.borrow-container {
  padding: 0;
}
</style>
