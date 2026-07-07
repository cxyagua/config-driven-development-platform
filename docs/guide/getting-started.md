# 快速开始

本节带你从零启动 CDDP 的前端工作台与后端服务。

## 环境要求

| 工具 | 版本 | 用途 |
| --- | --- | --- |
| Node.js | ≥ 18 | 运行工作台 |
| pnpm | ≥ 9 | 包管理 |
| Python | ≥ 3.10 | 运行服务端 |

## 启动工作台 Workbench

```bash
cd workbench
pnpm install
pnpm dev
```

开发服务器将在 `http://localhost:5577/workbench/` 启动，内置 Mock 服务模拟后端 API，无需后端即可体验完整界面。

## 启动服务端 Server

```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后可访问：

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

## 连接前后端

工作台默认使用 Mock 数据。若要对接真实后端，启动时关闭 Mock：

```bash
pnpm dev:server
```

`vite.config.ts` 已将 `/api` 代理到 `http://localhost:8000`，前后端可无缝联调。

## 生产构建

```bash
# 工作台
cd workbench && pnpm build

# 预览构建产物
pnpm preview
```

## 下一步

- [工作台 Workbench](./workbench) — 了解前端模块设计
- [服务端 Server](./server) — 了解后端 API 设计
