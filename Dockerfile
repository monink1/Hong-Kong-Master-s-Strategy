# 第一阶段：构建前端
FROM node:20-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 第二阶段：用 serve 启动（无 Nginx）
FROM node:20-alpine as production-stage
WORKDIR /app
RUN npm install -g serve
COPY --from=build-stage /app/dist ./dist
EXPOSE 3000  # serve 默认端口 3000
CMD ["serve", "-s", "dist", "-l", "3000"]