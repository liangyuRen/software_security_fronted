# VulSystem Frontend

Vue 3 + Vite 前端应用，提供用户界面和与后端 API 的交互。

## 📋 项目结构

```
vulsystem-frontend/
├── src/
│   ├── components/       # Vue 组件
│   ├── views/            # 页面视图
│   ├── router/           # 路由配置
│   ├── store/            # 状态管理
│   ├── services/         # API 服务
│   ├── styles/           # 全局样式
│   ├── utils/            # 工具函数
│   ├── App.vue           # 根组件
│   └── main.ts           # 应用入口
├── public/               # 静态资源
├── vite.config.ts        # Vite 配置
├── tsconfig.json         # TypeScript 配置
├── package.json          # 项目配置和依赖
├── Dockerfile            # Docker 镜像定义
└── README.md
```

## 🚀 本地开发

### 前置要求
- Node.js 14+
- npm 6+ 或 yarn

### 安装依赖

```bash
cd /root/vulsystem-frontend
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动。

### 构建生产版本

```bash
npm run build
```

构建输出将在 `dist/` 目录。

## 🐳 Docker 运行

### 构建镜像

```bash
cd /root/vulsystem-orchestration
docker compose build vulsystem-frontend
```

### 运行容器

```bash
docker compose up -d vulsystem-frontend
```

应用将在 `http://localhost:80` 启动。

## 🔧 环境配置

创建 `.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8081
VITE_APP_TITLE=VulSystem
```

## 📡 页面功能

- **登录页面** (`/login`) - 账户登录和认证
- **仪表盘** (`/dashboard`) - 数据统计和概览
- **项目管理** (`/projects`) - 创建和管理项目
- **漏洞管理** (`/vulnerabilities`) - 查看漏洞列表和详情
- **扫描报告** (`/reports`) - 报告生成和导出
- **设置** (`/settings`) - 个人和系统设置

## 🔗 相关链接

- [Vue 3 官方文档](https://vuejs.org/)
- [Vite 官方文档](https://vitejs.dev/)
- [TypeScript 文档](https://www.typescriptlang.org/)

---

**最后更新**: 2025-11-07
**技术栈**: Vue 3, Vite, TypeScript
