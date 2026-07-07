# Workbench 配置参考

工作台 Vite 配置项参考。

## package.json scripts

| 脚本 | 说明 |
| --- | --- |
| `pnpm dev` | 启动开发服务器（含 Mock） |
| `pnpm dev:server` | 关闭 Mock，对接真实后端 |
| `pnpm build` | 构建生产版本（`vue-tsc -b && vite build`） |
| `pnpm preview` | 预览生产构建 |

## vite.config.ts 关键配置

```typescript
export default defineConfig({
  plugins: [
    vue(),
    viteMockServe({
      mockPath: 'mock',
      enable: command === 'serve'
    })
  ],
  base: '/workbench/',
  server: {
    port: 5577,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    }
  }
})
```

## 主要依赖

| 依赖 | 版本 | 说明 |
| --- | --- | --- |
| vue | ^3.5.13 | 框架 |
| element-plus | ^2.14.2 | 组件库 |
| pinia | ^2.3.0 | 状态管理 |
| vue-router | ^4.6.4 | 路由 |
| axios | ^1.17.0 | HTTP |
| vue3-ts-jsoneditor | ^3.4.1 | JSON 编辑器 |
| lodash-es | ^4.17.21 | 工具库 |
