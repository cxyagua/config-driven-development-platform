import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'zh-CN',
  title: 'CDDP',
  description: '配置驱动开发平台 — Config-Driven Development Platform',

  lastUpdated: true,
  cleanUrls: true,

  // 忽略指向本地开发服务的链接（如 FastAPI 的 /docs、/redoc）
  ignoreDeadLinks: [
    /^https?:\/\/localhost/,
    /^https?:\/\/127\.0\.0\.1/
  ],

  head: [
    ['meta', { name: 'theme-color', content: '#3c8772' }],
    ['link', { rel: 'icon', href: '/favicon.svg' }]
  ],

  themeConfig: {
    nav: nav(),
    sidebar: {
      '/guide/': sidebarGuide(),
      '/reference/': sidebarReference()
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/cxyagua/config-driven-development-platform' }
    ],

    search: {
      provider: 'local',
      options: {
        translations: {
          button: {
            buttonText: '搜索文档',
            buttonAriaLabel: '搜索文档'
          },
          modal: {
            noResultsText: '无法找到相关结果',
            resetButtonTitle: '清除查询条件',
            footer: {
              selectText: '选择',
              navigateText: '切换'
            }
          }
        }
      }
    },

    footer: {
      message: '基于 MIT 协议发布',
      copyright: 'Copyright © 2026 cxyagua'
    },

    docFooter: {
      prev: '上一页',
      next: '下一页'
    },

    outline: {
      label: '本页目录',
      level: [2, 3]
    },

    lastUpdated: {
      text: '最后更新于'
    },

    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '菜单',
    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式'
  }
})

function nav() {
  return [
    { text: '指南', link: '/guide/introduction', activeMatch: '/guide/' },
    { text: '参考', link: '/reference/workbench', activeMatch: '/reference/' },
    { text: 'GitHub', link: 'https://github.com/cxyagua/config-driven-development-platform' }
  ]
}

function sidebarGuide() {
  return [
    {
      text: '开始',
      collapsed: false,
      items: [
        { text: '简介', link: '/guide/introduction' },
        { text: '快速开始', link: '/guide/getting-started' },
        { text: '项目结构', link: '/guide/structure' }
      ]
    },
    {
      text: '模块',
      collapsed: false,
      items: [
        { text: '工作台 Workbench', link: '/guide/workbench' },
        { text: '服务端 Server', link: '/guide/server' }
      ]
    }
  ]
}

function sidebarReference() {
  return [
    {
      text: '参考',
      collapsed: false,
      items: [
        { text: 'Workbench 配置', link: '/reference/workbench' },
        { text: 'Server API', link: '/reference/server-api' }
      ]
    }
  ]
}
