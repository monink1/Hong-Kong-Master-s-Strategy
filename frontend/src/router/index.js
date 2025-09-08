import { createRouter, createWebHistory } from 'vue-router'
// 用 @ 别名导入（@ 指向 src 目录，绝对路径，不会错）
import AppList from '@/components/Applist.vue'  

const routes = [
  {
    path: '/',
    name: 'Applist',
    component: AppList
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router