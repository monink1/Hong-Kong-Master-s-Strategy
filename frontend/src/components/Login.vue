<template>
  <div class="login-container">
    <div class="auth-card">
      <h2>{{ isRegisterMode ? '注册账号' : '添加账号' }}</h2>

      <!-- 表单容器 -->
      <div class="auth-form">
        <div class="form-group">
          <input
            type="text"
            v-model="username"
            placeholder="输入账号"
            class="auth-input"
          >
        </div>
        <div class="form-group">
          <input
            type="password"
            v-model="password"
            placeholder="输入密码"
            class="auth-input"
          >
        </div>

        <!-- 登录/注册按钮：直接绑定 click 事件，确保触发 -->
        <button
          type="button"
          @click="handleAuth"
          class="auth-btn"
        >
          {{ isRegisterMode ? '注册' : '登录' }}
        </button>
      </div>

      <!-- 服务协议勾选框 -->
      <div class="agreement">
        <input
          type="checkbox"
          v-model="agreeTerms"
          id="agreement"
          class="agreement-checkbox"
        >
        <label for="agreement" class="agreement-label">已阅读并同意服务协议</label>
      </div>

      <!-- 切换登录/注册模式 -->
      <p class="toggle-link" @click="toggleMode">
        {{ isRegisterMode ? '已有账号？去登录' : '没有账号？去注册' }}
      </p>

      <!-- 错误提示：点击后有问题会实时显示 -->
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup>
// Vue3 语法糖：Composition API，解决 Options API 兼容问题
import { ref } from 'vue' // Vue3 响应式数据核心
import { useRouter } from 'vue-router' // Vue3 路由 hooks

// 1. 响应式数据（替代 Vue2 的 data 函数）
const username = ref('')
const password = ref('')
const isRegisterMode = ref(false)
const agreeTerms = ref(false)
const errorMessage = ref('')

// 2. 路由实例（替代 Vue2 的 this.$router）
const router = useRouter()

// 3. 切换登录/注册模式
const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value
  // 重置表单和错误提示
  errorMessage.value = ''
  username.value = ''
  password.value = ''
  agreeTerms.value = false
}

// 4. 登录/注册核心逻辑（合并为一个方法，简化代码）
const handleAuth = async () => {
  // 表单验证：先检查协议和账号密码
  if (!agreeTerms.value) {
    errorMessage.value = '请阅读并同意服务协议'
    return
  }
  if (!username.value.trim() || !password.value.trim()) {
    errorMessage.value = '账号和密码不能为空'
    return
  }

  // 准备请求参数和地址
  const requestData = {
    username: username.value.trim(),
    password: password.value.trim()
  }
  const url = isRegisterMode.value
    ? 'http://localhost:5000/api/auth/register'
    : 'http://localhost:5000/api/auth/login'

  try {
    // 发送请求（Vue3 无需额外引入 axios，用原生 fetch 即可）
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData),
      credentials: 'include' // 处理跨域凭证
    })

    const data = await response.json()

    // 处理后端响应
    if (data.code === 200) {
      errorMessage.value = ''
      if (isRegisterMode.value) {
        // 注册成功：切换到登录模式并提示
        toggleMode()
        alert('注册成功，请登录')
      } else {
        // 登录成功：保存 token 并跳转到 Applist
        localStorage.setItem('token', data.token)
        router.push('/applist') // Vue3 路由跳转
      }
    } else {
      // 后端返回错误（如账号已存在、密码错误）
      errorMessage.value = data.msg || '操作失败，请重试'
    }
  } catch (error) {
    // 网络错误（如后端未启动、接口地址错误）
    console.error('请求失败:', error)
    errorMessage.value = '网络错误，请检查后端服务是否启动'
  }
}
</script>

<style scoped>
/* 登录页面样式：确保按钮可点击、布局居中 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 320px;
  background-color: #fff;
  padding: 30px 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

h2 {
  text-align: center;
  margin: 0 0 22px;
  color: #333;
  font-size: 22px;
  font-weight: 600;
}

.auth-form {
  width: 100%;
  margin-bottom: 16px;
}

.form-group {
  margin: 0 0 18px;
  width: 100%;
}

.auth-input {
  width: 100%;
  max-width: 260px;
  margin: 0 auto;
  padding: 10px 14px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  transition: border-color 0.3s;
}

.auth-input:focus {
  outline: none;
  border-color: #409eff;
}

/* 按钮样式：确保层级最高，不被遮挡 */
.auth-btn {
  width: 100%;
  max-width: 260px;
  margin: 0 auto;
  padding: 11px 0;
  background-color: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 15px;
  cursor: pointer;
  transition: background-color 0.3s;
  position: relative;
  z-index: 10; /* 防止被其他元素遮挡 */
}

.auth-btn:hover {
  background-color: #66b1ff;
}

.agreement {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 0 20px;
  font-size: 12px;
  color: #666;
}

.agreement-checkbox {
  width: 13px;
  height: 13px;
  margin: 0 6px 0 0;
  cursor: pointer;
}

.toggle-link {
  text-align: center;
  margin: 0 0 12px;
  color: #409eff;
  cursor: pointer;
  font-size: 14px;
}

.error-message {
  color: #f56c6c;
  text-align: center;
  font-size: 13px;
}
</style>