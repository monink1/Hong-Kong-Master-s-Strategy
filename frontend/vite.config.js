import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'  // 用于处理路径

export default defineConfig({
  plugins: [vue()],
  resolve: {
    // 配置路径别名：@ 指向 src 目录
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})