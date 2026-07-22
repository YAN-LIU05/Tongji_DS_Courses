import { defineStore } from 'pinia'
import userApi from '../api/user'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: null
  }),
  
  actions: {
    async login(loginForm) {
      try {
        const res = await userApi.login(loginForm)
        console.log('Login API Response:', res); // <<< 添加这一行
        console.log('Token from response:', res.data?.token); // <<< 添加这一行
        
        if (res.data && res.data.token) { // 增加一个检查，确保res.data和token存在
          this.token = res.data.token
          localStorage.setItem('token', res.data.token)
          return res
        } else {
          // 如果响应中没有token，则抛出错误
          throw new Error('登录成功但服务器未返回有效的token')
        }
      } catch (error) {
        console.error('Login action failed:', error); // 捕获错误时也打印
        return Promise.reject(error)
      }
    },
    
    async register(registerForm) {
      try {
        const res = await userApi.register(registerForm)
        return res
      } catch (error) {
        return Promise.reject(error)
      }
    },
    
    async getUserInfo() {
      try {
        const res = await userApi.getProfile()
        this.userInfo = res.data
        return res
      } catch (error) {
        return Promise.reject(error)
      }
    },
    
    async logout() {
      try {
        await userApi.logout()
        this.token = ''
        this.userInfo = null
        localStorage.removeItem('token')
      } catch (error) {
        console.error(error)
      }
    }
  }
})