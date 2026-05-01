import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('请求错误:', error)
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessageBox.confirm('登录状态已过期，请重新登录', '提示', {
            confirmButtonText: '重新登录',
            cancelButtonText: '取消',
            type: 'warning',
            showClose: false,
            showCancelButton: false
          }).then(() => {
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            router.push('/login')
          })
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 400:
          if (error.response.data && error.response.data.message) {
            ElMessage.error(error.response.data.message)
          } else {
            ElMessage.error('请求参数错误')
          }
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(error.response.data?.message || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default request
