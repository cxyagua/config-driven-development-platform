import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { viteMockServe } from 'vite-plugin-mock'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  // 资源基础路径
  base: '/workbench/',

  plugins: [
    vue(),

    // ── Mock 插件（仅开发模式启用，生产构建自动跳过） ──
    viteMockServe({
      mockPath: 'mock',            // mock 文件目录
      enable: command === 'serve', // 仅 dev server 启用
      logger: true,                // 控制台打印命中的 mock 接口
    }),
  ],

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },

  css: {
    preprocessorOptions: {
      less: {
        javascriptEnabled: true,
      },
    },
  },

  server: {
    // Workbench 开发端口
    port: 5577,
    // 代理配置（后续对接 Server 时使用）
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
    cors: true,
  },

  build: {
    outDir: 'dist',
    sourcemap: false,
  },
}))