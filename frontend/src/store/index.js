import { reactive } from 'vue'

const USER_KEY = 'user'
const TOKEN_KEY = 'token'

const savedUser = localStorage.getItem(USER_KEY)
const savedToken = localStorage.getItem(TOKEN_KEY)

const state = reactive({
  user: savedUser ? JSON.parse(savedUser) : null,
  token: savedToken || null,
  isLoggedIn: !!savedToken
})

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
