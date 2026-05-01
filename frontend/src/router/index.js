import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import Login from '../views/Login.vue'
import Books from '../views/Books.vue'
import Borrow from '../views/Borrow.vue'
import Records from '../views/Records.vue'
import Layout from '../components/Layout.vue'
import store from '../store'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/books',
    children: [
      {
        path: 'books',
        name: 'Books',
        component: Books,
        meta: { requiresAuth: true, title: '图书管理' }
      },
      {
        path: 'borrow',
        name: 'Borrow',
        component: Borrow,
        meta: { requiresAuth: true, title: '借阅管理' }
      },
      {
        path: 'records',
        name: 'Records',
        component: Records,
        meta: { requiresAuth: true, title: '借阅记录' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 图书借阅管理系统` : '图书借阅管理系统'
  
  if (to.meta.requiresAuth) {
    if (!store.hasAuth()) {
      ElMessage.warning('请先登录')
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
    
    const isValid = await store.verifyToken()
    if (!isValid) {
      ElMessage.warning('登录已过期，请重新登录')
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
    
    next()
  } else if (to.path === '/login' && store.hasAuth()) {
    next('/books')
  } else {
    next()
  }
})

export default router
