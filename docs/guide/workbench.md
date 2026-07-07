# 工作台 Workbench

工作台是 CDDP 的可视化前端，用于配置文件的管理、编辑与即时预览。

## 核心功能

- 📦 **空间管理**：管理不同环境的配置空间（dev / uat / prod）
- 📊 **配置管理**：创建、编辑、删除配置文件
- 📁 **文件夹组织**：支持树形结构的文件夹管理，配置文件可拖拽移动
- ✏️ **JSON 编辑器**：基于 `vue3-ts-jsoneditor` 的专业 JSON 编辑体验
- 👁️ **预览面板**：配置实时预览区域（预留组件渲染位置）
- 🔄 **多环境同步**：一键将配置同步到其他环境

## 技术栈

| 类别 | 技术 |
| --- | --- |
| 框架 | Vue 3 + TypeScript |
| 构建 | Vite 6 |
| 组件库 | Element Plus 2.x |
| 图标 | @element-plus/icons-vue |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| 样式 | Less |
| HTTP | Axios |
| JSON 编辑器 | vue3-ts-jsoneditor |
| Mock | vite-plugin-mock + Mock.js |

## 页面布局

工作台主页面采用「左 + 右」布局：

```
┌─────────────┬──────────────────────────────┐
│             │  顶部操作栏                  │
│  FolderTree ├──────────────┬───────────────┤
│  文件夹树    │  预览面板    │  JSON 编辑器  │
│             │              │               │
└─────────────┴──────────────┴───────────────┘
```

## FolderTree 组件

FolderTree 采用组合式设计，将不同关注点拆分到多个 `use` 函数：

| 函数 | 职责 |
| --- | --- |
| `useTreeData` | 数据层：CRUD、空间切换 |
| `useTreeDrag` | 拖拽逻辑 |
| `useContextMenu` | 右键菜单 |
| `useSync` | 多环境同步 |

## 路由

| 路由 | 页面 | 说明 |
| --- | --- | --- |
| `/workbench/` | 配置中心 | 默认重定向到配置中心 |
| `/workbench/config-center` | 配置中心 | 主页面 |

## 开发说明

### Mock 服务

开发模式下使用 `vite-plugin-mock`：

- Mock 文件位于 `mock/` 目录
- 仅在开发服务器启动时启用（`command === 'serve'`）
- 生产构建自动跳过 Mock 插件

### API 代理

```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```
