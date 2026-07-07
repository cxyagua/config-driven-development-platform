# Server API 参考

服务端基于 FastAPI，提供以下 API 端点。

## 健康检查

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/health` | 健康检查接口 |

## Workbench 接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/workbench/...` | 工作台相关接口 |

::: tip
完整的交互式 API 文档请在服务启动后访问：

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc
:::

## 数据库初始化

服务端使用 SQL 脚本进行建表，位于 `server/sql/`：

- `001_init.sql` — 初始化表结构
- `002_add_deleted_field.sql` — 新增软删除字段

## 启动顺序

```bash
cd server
source venv/bin/activate
# 1. 初始化数据库（如需要）
# 2. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
