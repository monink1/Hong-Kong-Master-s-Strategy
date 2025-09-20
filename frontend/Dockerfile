# 第一阶段：构建前端项目（编译生成静态文件）
FROM node:20-alpine as build-stage
WORKDIR /app

# 1. 复制依赖配置文件（优先复制package文件，利用Docker缓存）
COPY package*.json ./

# 2. 安装所有依赖（含开发依赖，确保npm run build能正常执行）
RUN npm install

# 3. 复制前端所有源代码
COPY . .

# 4. 构建生产环境静态文件（生成dist目录，含index.html、css、js等）
RUN npm run build


# 第二阶段：部署前端（用Nginx默认配置，无需自定义nginx.conf）
FROM nginx:alpine as production-stage

# 关键：直接使用Nginx自带的默认配置，不删除、不替换nginx.conf
# Nginx默认会加载/etc/nginx/conf.d/default.conf，默认配置已满足静态资源访问需求

# 1. 从构建阶段复制编译好的dist目录到Nginx静态文件目录
# Nginx默认静态资源目录：/usr/share/nginx/html（与默认配置路径对齐）
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 2. 暴露容器80端口（Nginx默认监听80端口，与docker-compose.yml的8080:80映射对齐）
EXPOSE 80

# 3. 启动Nginx（前台运行，确保容器不退出，Nginx默认配置会自动生效）
CMD ["nginx", "-g", "daemon off;"]