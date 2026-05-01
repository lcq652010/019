<template>
  <div class="books-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>图书列表</span>
          <el-button type="primary" @click="handleAdd" v-if="isAdmin">
            <el-icon><Plus /></el-icon>
            添加图书
          </el-button>
        </div>
      </template>
      
      <el-table :data="books" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="书名" width="200" />
        <el-table-column prop="author" label="作者" width="150" />
        <el-table-column prop="isbn" label="ISBN" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="total_copies" label="总册数" width="100" />
        <el-table-column prop="available_copies" label="可借册数" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.available_copies > 0 ? 'success' : 'danger'">
              {{ scope.row.available_copies }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <el-button type="primary" link @click="handleBorrow(scope.row)" :disabled="scope.row.available_copies <= 0">
              借阅
            </el-button>
            <el-button type="warning" link @click="handleEdit(scope.row)" v-if="isAdmin">
              编辑
            </el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)" v-if="isAdmin">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑图书' : '添加图书'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="bookFormRef"
        :model="bookForm"
        :rules="bookRules"
        label-width="80px"
      >
        <el-form-item label="书名" prop="title">
          <el-input v-model="bookForm.title" placeholder="请输入书名" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="bookForm.author" placeholder="请输入作者" />
        </el-form-item>
        <el-form-item label="ISBN" prop="isbn">
          <el-input v-model="bookForm.isbn" placeholder="请输入ISBN" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="bookForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
        <el-form-item label="总册数" prop="total_copies">
          <el-input-number
            v-model="bookForm.total_copies"
            :min="1"
            :max="100"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { bookApi } from '../api'
import store from '../store'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const bookFormRef = ref(null)
const books = ref([])

const isAdmin = computed(() => store.isAdmin())

const bookForm = reactive({
  id: null,
  title: '',
  author: '',
  isbn: '',
  description: '',
  total_copies: 1
})

const bookRules = {
  title: [
    { required: true, message: '请输入书名', trigger: 'blur' }
  ],
  author: [
    { required: true, message: '请输入作者', trigger: 'blur' }
  ],
  isbn: [
    { required: true, message: '请输入ISBN', trigger: 'blur' }
  ],
  total_copies: [
    { required: true, message: '请输入总册数', trigger: 'blur' }
  ]
}

const fetchBooks = async () => {
  loading.value = true
  try {
    const response = await bookApi.getBooks()
    if (response.status === 200) {
      books.value = response.data
    }
  } catch (error) {
    console.error('获取图书列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  bookForm.id = null
  bookForm.title = ''
  bookForm.author = ''
  bookForm.isbn = ''
  bookForm.description = ''
  bookForm.total_copies = 1
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  bookForm.id = row.id
  bookForm.title = row.title
  bookForm.author = row.author
  bookForm.isbn = row.isbn
  bookForm.description = row.description || ''
  bookForm.total_copies = row.total_copies
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除图书《${row.title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const response = await bookApi.deleteBook(row.id)
      if (response.status === 200) {
        ElMessage.success('删除成功')
        fetchBooks()
      }
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!bookFormRef.value) return
  
  await bookFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      
      try {
        let response
        
        if (isEdit.value) {
          response = await bookApi.updateBook(bookForm.id, {
            title: bookForm.title,
            author: bookForm.author,
            isbn: bookForm.isbn,
            description: bookForm.description,
            total_copies: bookForm.total_copies
          })
        } else {
          response = await bookApi.createBook({
            title: bookForm.title,
            author: bookForm.author,
            isbn: bookForm.isbn,
            description: bookForm.description,
            total_copies: bookForm.total_copies
          })
        }
        
        if (response.status === 200 || response.status === 201) {
          ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
          dialogVisible.value = false
          fetchBooks()
        }
      } catch (error) {
        console.error('操作失败:', error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleBorrow = async (row) => {
  ElMessageBox.confirm(`确定要借阅《${row.title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      const response = await bookApi.borrowBook(row.id)
      if (response.status === 200 || response.status === 201) {
        ElMessage.success('借阅成功')
        fetchBooks()
      }
    } catch (error) {
      console.error('借阅失败:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchBooks()
})
</script>

<style scoped>
.books-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
