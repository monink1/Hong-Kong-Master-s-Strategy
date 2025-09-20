<template>
  <div class="app-container">
    <div class="header">
      <h1>应用中心</h1>
      <button @click="handleLogout" class="logout-btn">退出登录</button>
    </div>
    
    <!-- 应用列表区域 -->
    <div class="content-box">
      <h2>应用程序列表</h2>
      <div class="form-group">
        <label for="type-select">选择应用类型：</label>
        <select 
          id="type-select"
          v-model="selectedType" 
          @change="fetchApps"
          class="type-select"
        >
          <option value="">请选择类型</option>
          <option v-for="type in types" :key="type" :value="type">
            {{ type }}
          </option>
        </select>
      </div>
      <div v-if="apps.length > 0" class="app-buttons">
        <button 
          v-for="app in apps" 
          :key="app.App_name" 
          @click="showAppDetails(app)"
          class="app-btn"
        >
          {{ app.App_name }}
        </button>
      </div>
      <div v-else-if="selectedType === ''" class="info-message">
        请选择一个应用类型
      </div>
      <div v-else class="info-message">
        该类型下没有应用程序
      </div>
      <div v-if="selectedApp" class="app-details">
        <h3>{{ selectedApp.App_name }}</h3>
        <p><strong>使用说明:</strong> {{ selectedApp.App_use }}</p>
        <p><strong>相关应用:</strong> {{ selectedApp.Related_app }}</p>
      </div>
    </div>

    <!-- 随机事项区域 -->
    <div class="content-box random-box">
      <h2>随机探索事项</h2>
      <button @click="fetchRandomThing" class="random-btn">获取随机事项</button>
      <div v-if="randomThing" class="thing-details">
        <p class="thing-rank">No.{{ randomThing.Rank }}</p>
        <p class="thing-ch">{{ randomThing["Things-Ch"] }}</p>
        <p class="thing-en">{{ randomThing["Things-English"] }}</p>
      </div>
      <div v-else class="info-message">
        点击上方按钮获取随机事项
      </div>
    </div>

    <!-- 游戏筛选器区域 -->
    <div class="content-box filter-section">
      <h2>游戏筛选器（Genre + Platform + Publisher）</h2>
      <div class="filter-controls">
        <div class="filter-item">
          <label>选择类型：</label>
          <select v-model="selectedGenre" @change="handleFilterChange">
            <option value="">-- 请选择 --</option>
            <option v-for="genre in allGenres" :key="genre">{{ genre }}</option>
          </select>
        </div>
        <div class="filter-item">
          <label>选择平台：</label>
          <select v-model="selectedPlatform" @change="handleFilterChange">
            <option value="">-- 请选择 --</option>
            <option v-for="platform in allPlatforms" :key="platform">{{ platform }}</option>
          </select>
        </div>
        <div class="filter-item">
          <label>选择发行商：</label>
          <select v-model="selectedPublisher" @change="handleFilterChange">
            <option value="">-- 请选择 --</option>
            <option v-for="publisher in allPublishers" :key="publisher">{{ publisher }}</option>
          </select>
        </div>
        <button
          class="query-btn"
          @click="fetchFilteredGames"
          :disabled="!isFilterComplete"
        >
          查询符合条件的游戏
        </button>
      </div>
      <!-- 筛选结果表格 -->
      <div v-if="filteredGames.length > 0" class="result-table">
        <h3>筛选结果（共 {{ filteredGames.length }} 款）</h3>
        <table>
          <thead>
            <tr>
              <th>排名</th>
              <th>游戏名称</th>
              <th>类型</th>
              <th>平台</th>
              <th>发行商</th>
              <th>全球销量（百万）</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(game, index) in filteredGames" :key="index + game.Name">
              <td>{{ index + 1 }}</td>
              <td>{{ game.Name }}</td>
              <td>{{ game.Genre }}</td>
              <td>{{ game.Platform }}</td>
              <td>{{ game.Publisher }}</td>
              <td>{{ Number(game.Global_Sales).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="isFilterComplete && filteredGames.length === 0" class="info-message">
        没有找到符合条件的游戏，请重新选择筛选条件
      </div>
    </div>
  </div>
</template>

<script setup>
// Vue3 语法糖：Composition API 适配
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// 1. 响应式数据（替代 Vue2 的 data）
const types = ref([])
const apps = ref([])
const selectedType = ref('')
const selectedApp = ref(null)
const randomThing = ref(null)
const usedRanks = ref(new Set(JSON.parse(localStorage.getItem('usedRanks') || '[]')))
const allGenres = ref([])
const allPlatforms = ref([])
const allPublishers = ref([])
const selectedGenre = ref('')
const selectedPlatform = ref('')
const selectedPublisher = ref('')
const filteredGames = ref([])
const router = useRouter()

// 2. 计算属性（替代 Vue2 的 computed）
const isFilterComplete = computed(() => {
  return !!selectedGenre.value && !!selectedPlatform.value && !!selectedPublisher.value
})

// 3. 生命周期钩子（替代 Vue2 的 mounted）
onMounted(() => {
  // 验证登录状态：无 token 跳回登录页
  if (!localStorage.getItem('token')) {
    router.push('/login')
    return
  }
  // 加载初始数据
  fetchTypes()
  fetchFilterMeta()
})

// 4. 方法定义（替代 Vue2 的 methods）
// 退出登录
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.setItem('usedRanks', JSON.stringify(Array.from(usedRanks.value)))
  router.push('/login')
}

// 获取应用类型
const fetchTypes = async () => {
  try {
    const res = await fetch('http://localhost:5000/api/apps/types')
    const data = await res.json()
    if (data.code === 200) {
      types.value = data.data || []
    } else {
      console.error('获取应用类型失败:', data.msg)
    }
  } catch (err) {
    console.error('获取应用类型网络错误:', err)
  }
}

// 获取应用列表
const fetchApps = async () => {
  if (!selectedType.value) {
    apps.value = []
    return
  }
  try {
    const res = await fetch(`http://localhost:5000/api/apps/by-type/${selectedType.value}`)
    const data = await res.json()
    if (data.code === 200) {
      apps.value = data.data || []
    } else {
      console.error('获取应用列表失败:', data.msg)
    }
  } catch (err) {
    console.error('获取应用列表网络错误:', err)
  }
}

// 显示应用详情
const showAppDetails = (app) => {
  selectedApp.value = app
}

// 获取随机事项
const fetchRandomThing = async () => {
  try {
    const usedRankStr = Array.from(usedRanks.value).join(',')
    const res = await fetch(`http://localhost:5000/api/things/random?usedRanks=${usedRankStr}`)
    const data = await res.json()
    if (data.code === 200 && data.data) {
      randomThing.value = data.data
      usedRanks.value.add(data.data.Rank)
    } else if (data.code === 404) {
      alert('所有事项已展示完毕～')
      randomThing.value = null
    } else {
      console.error('获取随机事项失败:', data.msg)
    }
  } catch (err) {
    console.error('获取随机事项网络错误:', err)
  }
}

// 获取筛选器元数据
const fetchFilterMeta = async () => {
  try {
    const res = await fetch('http://localhost:5000/api/filters/meta')
    const data = await res.json()
    if (data.code === 200) {
      allGenres.value = data.genres || []
      allPlatforms.value = data.platforms || []
      allPublishers.value = data.publishers || []
    } else {
      console.error('获取筛选器元数据失败:', data.msg)
    }
  } catch (err) {
    console.error('获取筛选器元数据网络错误:', err)
  }
}

// 筛选条件变化时清空结果
const handleFilterChange = () => {
  filteredGames.value = []
}

// 获取筛选后的游戏
const fetchFilteredGames = async () => {
  if (!isFilterComplete.value) return
  try {
    const url = new URL('http://localhost:5000/api/games/filtered')
    url.searchParams.append('genre', selectedGenre.value)
    url.searchParams.append('platform', selectedPlatform.value)
    url.searchParams.append('publisher', selectedPublisher.value)
    const res = await fetch(url.toString())
    const data = await res.json()
    if (data.code === 200) {
      filteredGames.value = data.data || []
    } else {
      console.error('筛选游戏失败:', data.msg)
      alert(`查询失败: ${data.msg}`)
    }
  } catch (err) {
    console.error('筛选游戏网络错误:', err)
    alert('查询失败，请重试')
  }
}
</script>

<style scoped>
/* 原有样式不变，直接保留 */
.app-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background-color: #f0f2f5;
  gap: 20px;
}
.header {
  width: 100%;
  max-width: 800px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.header h1 {
  color: #303133;
  margin: 0;
}
.logout-btn {
  padding: 8px 16px;
  background-color: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.logout-btn:hover {
  background-color: #f78989;
}
.content-box {
  width: 100%;
  max-width: 800px;
  padding: 30px;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}
h2 {
  text-align: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
  color: #303133;
}
.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: inline-block;
  width: 120px;
  color: #606266;
  font-weight: 500;
}
.type-select {
  width: calc(100% - 130px);
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  color: #303133;
  background-color: #fff;
}
.type-select:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}
.app-buttons {
  margin: 25px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.app-btn {
  padding: 8px 16px;
  background-color: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}
.app-btn:hover {
  background-color: #66b1ff;
  transform: translateY(-2px);
}
.info-message {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin: 25px 0;
  color: #606266;
}
.app-details {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}
.app-details h3 {
  margin-top: 0;
  color: #303133;
}
.app-details p {
  color: #606266;
  line-height: 1.6;
}
.random-box .random-btn {
  display: block;
  margin: 0 auto 25px;
  padding: 10px 20px;
  background-color: #67c23a;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s;
}
.random-box .random-btn:hover {
  background-color: #85ce61;
}
.thing-details {
  text-align: center;
  margin-top: 20px;
}
.thing-rank {
  font-weight: bold;
  color: #e6a23c;
  margin-bottom: 10px;
  font-size: 18px;
}
.thing-ch, .thing-en {
  color: #606266;
  line-height: 1.8;
  margin: 5px 0;
}
.filter-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin: 20px 0;
  align-items: center;
}
.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.filter-item select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  min-width: 180px;
  font-size: 14px;
}
.query-btn {
  padding: 8px 20px;
  background-color: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: auto;
  font-size: 14px;
}
.query-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.result-table {
  margin-top: 20px;
  overflow-x: auto;
}
.result-table table {
  width: 100%;
  border-collapse: collapse;
}
.result-table th,
.result-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}
.result-table th {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #303133;
}
/* 响应式调整 */
@media (max-width: 768px) {
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .query-btn {
    margin-left: 0;
    width: 100%;
  }

  .filter-item {
    width: 100%;
  }

  .filter-item select {
    width: 100%;
  }

  .form-group label {
    display: block;
    margin-bottom: 8px;
  }

  .type-select {
    width: 100%;
  }
}
</style>