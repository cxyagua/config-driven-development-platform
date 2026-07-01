import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  // base 与 vite.config.ts 中的 base 保持一致
  history: createWebHistory('/workbench/'),

  routes: [
    {
      path: '/',
      redirect: '/config-center',
    },
    {
      path: '/config-center',
      name: 'ConfigCenter',
      component: () => import('@/pages/ConfigCenter.vue'),
      meta: { title: 'CDDP Workbench — 工作台' },
    },
    // 404 兜底：重定向到配置中心
    {
      path: '/:pathMatch(.*)*',
      redirect: '/config-center',
    },
  ],
})

// 更新页面标题
router.afterEach((to) => {
  const title = to.meta?.title as string | undefined
  if (title) document.title = title
})

export default router
