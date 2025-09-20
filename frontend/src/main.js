// src/main.js（Vue3 + Vite 入口，适配模块化导入）
import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 引入路由

// 创建 Vue 实例并挂载（Vue3 标准语法）
createApp(App)
  .use(router) // 注册路由
  .mount('#app')