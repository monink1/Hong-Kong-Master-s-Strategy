// src/router/index.js（适配 components 目录，保留懒加载优化）
import { createRouter, createWebHistory } from 'vue-router'

// 懒加载优化：组件在需要时才加载，减少初始加载时间（推荐保留）
const Login = () => import('@/components/Login.vue') // 懒加载写法
const Applist = () => import('@/components/Applist.vue')

const routes = [
  {
    path: '/',
    redirect: '/login' // 默认重定向到登录页
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/applist',
    name: 'Applist',
    component: Applist,
    // 路由守卫：未登录跳回登录页
    beforeEnter: (to, from, next) => {
      const token = localStorage.getItem('token')
      token ? next() : next('/login')
    }
  }
]

const router = createRouter({
  history: createWebHistory(), // 无 # 号的路由模式
  routes
})

export default router