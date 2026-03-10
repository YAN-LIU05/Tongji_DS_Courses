import request from '@/utils/request'

export default {
  // 登录
  login(data) {
    return request({
      url: '/users/login/',
      method: 'post',
      data
    })
  },
  
  // 注册
  register(data) {
    return request({
      url: '/users/register/',
      method: 'post',
      data
    })
  },
  
  // 获取当前用户信息
  getProfile() {
    return request({
      url: '/users/profile/',
      method: 'get'
    })
  },
  
  // 登出
  logout() {
    return request({
      url: '/users/logout/',
      method: 'post'
    })
  }
}