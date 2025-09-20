<!-- src/App.vue -->
<template>
  <!-- 路由出口：所有页面会在这里渲染 -->
  <router-view />
</template>

<script setup>
// Vue3 语法糖：无需 export default，直接编写逻辑
// 此处仅作为路由容器，无需额外代码
</script>

<style>
/* 全局样式：清除默认边距，统一背景 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: #f0f2f5;
  min-height: 100vh;
}
</style>