import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  role: 'admin', // 'guest' | 'user' | 'admin' - 默认管理员权限
  token: 'dev-token',
  userId: 'admin',
  username: '管理员',
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setAuth: (state, action) => {
      state.role = action.payload.role || 'guest'
      state.token = action.payload.token || null
      state.userId = action.payload.userId || null
      state.username = action.payload.username || null
    },
    clearAuth: (state) => {
      state.role = 'guest'
      state.token = null
      state.userId = null
      state.username = null
    },
  },
})

export const { setAuth, clearAuth } = authSlice.actions
export default authSlice.reducer
