import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import store, { setVerifyTokenFunction } from './store'
import { authApi } from './api'

setVerifyTokenFunction(async () => {
  try {
    const response = await authApi.getCurrentUser()
    if (response.status === 200 && response.data) {
      store.updateUser(response.data)
      return true
    }
    return false
  } catch (error) {
    console.error('Token 验证失败:', error)
    store.logout()
    return false
  }
})

const app = createApp(App)

app.use(router)
app.use(ElementPlus)

app.mount('#app')
