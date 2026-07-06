import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { viteMockServe } from 'vite-plugin-mock'

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const useMock = env.VITE_USE_MOCK !== 'false'

  return {
    // 资源基础路径
    base: '/workbench/',

    plugins: [
      vue(),

      // ── Mock 插件（仅开发模式 + VITE_USE_MOCK=true 时启用） ──
      viteMockServe({
        mockPath: 'mock',
        enable: command === 'serve' && useMock,
        logger: true,
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
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
        // ── 对接 Server 时：将 /workbench/api 代理到后端 ──
        '/workbench/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => '/api' + path,
        },
      },
      cors: true,
    },

    build: {
      outDir: 'dist',
      sourcemap: false,
    },
  }
})