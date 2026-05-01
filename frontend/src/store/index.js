import { reactive } from 'vue'

const USER_KEY = 'user'
const TOKEN_KEY = 'token'

const savedUser = localStorage.getItem(USER_KEY)
const savedToken = localStorage.getItem(TOKEN_KEY)

const state = reactive({
  user: savedUser ? JSON.parse(savedUser) : null,
  token: savedToken || null,
  isLoggedIn: !!savedToken,
  isCheckingAuth: false
})

let isVerifyingToken = false
let verifyTokenFunction = null

export function setVerifyTokenFunction(fn) {
  verifyTokenFunction = fn
}

const actions = {
  login(userData, token) {
    state.user = userData
    state.token = token
    state.isLoggedIn = true
    localStorage.setItem(USER_KEY, JSON.stringify(userData))
    localStorage.setItem(TOKEN_KEY, token)
  },
  
  logout() {
    state.user = null
    state.token = null
    state.isLoggedIn = false
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(TOKEN_KEY)
  },
  
  updateUser(userData) {
    state.user = userData
    localStorage.setItem(USER_KEY, JSON.stringify(userData))
  },
  
  isAdmin() {
    return state.user?.is_admin || false
  },
  
  getToken() {
    return state.token || localStorage.getItem(TOKEN_KEY)
  },
  
  async verifyToken() {
    if (isVerifyingToken) {
      return state.isLoggedIn
    }
    
    const token = this.getToken()
    if (!token) {
      this.logout()
      return false
    }
    
    if (verifyTokenFunction) {
      isVerifyingToken = true
      state.isCheckingAuth = true
      
      try {
        const result = await verifyTokenFunction()
        isVerifyingToken = false
        state.isCheckingAuth = false
        return result
      } catch (error) {
        console.error('Token 验证失败:', error)
        this.logout()
        isVerifyingToken = false
        state.isCheckingAuth = false
        return false
      }
    }
    
    return state.isLoggedIn
  },
  
  hasAuth() {
    return state.isLoggedIn
  }
}

export function useStore() {
  return {
    state,
    ...actions
  }
}

export default {
  state,
  ...actions
}
