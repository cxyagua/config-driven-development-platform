# 项目结构

CDDP 采用 monorepo 方式组织，整体目录如下：

```
config-driven-development-platform/
├── workbench/      # 工作台前端（配置管理、即时预览）
├── server/         # 服务端（配置解析、验证、执行）
├── skills/         # 技能库（规划中：配置模板、代码示例）
├── reference/      # 参考（规划中：配置模板、代码示例）
├── docs/           # 文档中心（VitePress）
├── components/     # 组件库（规划中：可复用的配置组件）
└── playground/     # 实验平台（规划中：快速验证配置）
```

## workbench（工作台）

Vue 3 + TypeScript + Vite 构建的前端应用，核心目录：

```
workbench/
├── mock/                      # Mock 数据
├── src/
│   ├── components/            # 组件（FolderTree、JsonEditorPane、PreviewPane）
│   ├── composables/           # 组合式函数
│   ├── pages/                 # 页面（ConfigCenter）
│   ├── router/                # 路由
│   └── http.ts                # HTTP 封装
└── vite.config.ts
```

## server（服务端）

FastAPI 构建的后端服务，核心目录：

```
server/
├── app/
│   ├── api/endpoints/         # API 端点
│   ├── core/                  # 配置
│   ├── models/                # 数据模型
│   ├── schemas/               # 数据契约
│   ├── services/              # 业务服务
│   ├── database.py            # 数据库
│   └── main.py                # 入口
└── sql/                       # 建表脚本
```

## docs（文档中心）

使用 [VitePress](https://vitepress.dev) 构建，源文件位于 `docs/` 目录：

```
docs/
├── .vitepress/config.ts       # 站点配置
├── public/                    # 静态资源
├── guide/                     # 指南文档
├── reference/                 # 参考文档
└── index.md                   # 首页
```
