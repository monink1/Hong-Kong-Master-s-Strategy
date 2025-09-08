<template>
  <div class="app-container">
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
  </div>
</template>

<script>
export default {
  data() {
    return {
      types: [],
      apps: [],
      selectedType: '',
      selectedApp: null,
      randomThing: null,
      usedRanks: new Set()
    };
  },
  mounted() {
    this.fetchTypes();
  },
  methods: {
    async fetchTypes() {
      try {
        const res = await fetch('http://localhost:5000/api/apps/types');
        this.types = (await res.json()).data;
      } catch (err) {
        console.error('获取应用类型失败:', err);
      }
    },
    async fetchApps() {
      if (!this.selectedType) {
        this.apps = [];
        return;
      }
      try {
        const res = await fetch(`http://localhost:5000/api/apps/by-type/${this.selectedType}`);
        this.apps = (await res.json()).data;
      } catch (err) {
        console.error('获取应用列表失败:', err);
      }
    },
    showAppDetails(app) {
      this.selectedApp = app;
    },
    async fetchRandomThing() {
      try {
        const usedRankStr = Array.from(this.usedRanks).join(',');
        const res = await fetch(`http://localhost:5000/api/things/random?usedRanks=${usedRankStr}`);
        const data = await res.json();
        if (data.code === 200 && data.data) {
          this.randomThing = data.data;
          this.usedRanks.add(data.data.Rank);
        } else if (data.code === 404) {
          alert('所有事项已展示完毕～');
          this.randomThing = null;
        } else {
          console.error('获取随机事项失败:', data.msg);
        }
      } catch (err) {
        console.error('网络错误:', err);
      }
    }
  }
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background-color: #f0f2f5;
  gap: 20px;
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
</style>