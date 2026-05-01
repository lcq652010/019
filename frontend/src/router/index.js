import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Books from '../views/Books.vue'
import Borrow from '../views/Borrow.vue'
import Records from '../views/Records.vue'
import Layout from '../components/Layout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
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
        meta: { requiresAuth: true }
      },
      {
        path: 'borrow',
        name: 'Borrow',
        component: Borrow,
        meta: { requiresAuth: true }
      },
      {
        path: 'records',
        name: 'Records',
        component: Records,
        meta: { requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/books')
  } else {
    next()
  }
})

export default router
