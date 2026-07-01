# CDDP Workbench

配置驱动开发平台 - 工作台

## 项目简介

CDDP (Config-Driven Development Platform) Workbench 是一个配置驱动开发的可视化管理平台，用于管理和编辑配置文件，支持实时预览和多环境同步。

**核心功能：**

- 📦 **空间管理**：管理不同环境的配置空间（dev / uat / prod）
- 📊 **配置管理**：创建、编辑、删除配置文件
- 📁 **文件夹组织**：支持树形结构的文件夹管理，配置文件可拖拽移动
- ✏️ **JSON 编辑器**：基于 vue3-ts-jsoneditor 的专业 JSON 编辑体验
- 👁️ **预览面板**：配置实时预览区域（预留组件渲染位置）
- 🔄 **多环境同步**：一键将配置同步到其他环境

## 技术栈

- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite 6
- **组件库**：Element Plus 2.x
- **图标库**：@element-plus/icons-vue
- **状态管理**：Pinia
- **路由**：Vue Router 4
- **样式**：Less
- **HTTP 客户端**：Axios
- **JSON 编辑器**：vue3-ts-jsoneditor
- **Mock 服务**：vite-plugin-mock + Mock.js
- **工具库**：lodash-es

## 快速开始

### 安装依赖

```bash
pnpm install
```

### 启动开发服务器

```bash
pnpm dev
```

开发服务器将在 `http://localhost:5577/workbench/` 启动，内置 Mock 服务模拟后端 API。

### 构建生产版本

```bash
pnpm build
```

### 预览生产构建

```bash
pnpm preview
```

## 项目结构

```
workbench/
├── mock/                    # Mock 数据配置
│   ├── config-store.ts      # 配置数据存储
│   └── index.ts             # Mock 接口定义
├── public/                  # 静态资源
├── src/
│   ├── assets/              # 资源文件
│   ├── components/          # 组件
│   │   ├── FolderTree/      # 文件夹树组件
│   │   ├── JsonEditorPane.vue    # JSON 编辑器面板
│   │   └── PreviewPane.vue       # 预览面板
│   ├── composables/         # 组合式函数
│   │   ├── useActiveConfig.ts    # 活跃配置管理
│   │   ├── useComponentType.ts   # 组件类型切换
│   │   └── useEditorResize.ts    # 编辑器尺寸调整
│   ├── pages/               # 页面
│   │   └── ConfigCenter.vue     # 配置中心（主页面）
│   ├── router/              # 路由配置
│   ├── http.ts              # HTTP 客户端封装
│   ├── App.vue              # 根组件
│   ├── main.ts              # 入口文件
│   └── style.css            # 全局样式
├── index.html               # HTML 模板
├── vite.config.ts           # Vite 配置
├── tsconfig.json            # TypeScript 配置
└── package.json             # 项目配置
```

## 页面路由

| 路由 | 页面 | 说明 |
|------|------|------|
| `/workbench/` | 配置中心 | 默认重定向到配置中心 |
| `/workbench/config-center` | 配置中心 | 主页面，左侧文件夹树 + 右侧编辑器 |

## 开发说明

### Mock 服务

开发模式下，项目使用 `vite-plugin-mock` 提供 Mock 数据：

- Mock 文件位于 `mock/` 目录
- 仅在开发服务器启动时启用（`command === 'serve'`）
- 生产构建自动跳过 Mock 插件

### API 代理

后端 API 代理配置在 `vite.config.ts` 中：

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

### 组件架构

**FolderTree 组件**：
- 组合式设计，使用多个 `use` 函数拆分关注点
- `useTreeData`: 数据层（CRUD、空间切换）
- `useTreeDrag`: 拖拽逻辑
- `useContextMenu`: 右键菜单
- `useSync`: 同步功能

**ConfigCenter 页面**：
- 左侧 FolderTree（配置文件管理）
- 右侧上下布局（顶部操作栏 + 底部编辑区域）
- 编辑区域左右分栏（预览面板 + JSON 编辑器）

## License

MIT