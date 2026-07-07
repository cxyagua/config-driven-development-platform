# Config-Driven Development Platform Server

Config-Driven Development Platform（CDDP）的后端服务，基于 [FastAPI](https://fastapi.tiangolo.com/) + [SQLAlchemy 2.0](https://docs.sqlalchemy.org/) 异步实现，为前端 Workbench 提供**配置驱动开发**所需的文件夹/配置项管理、配置内容读写、跨空间同步等能力。

## 核心特性

- 基于 FastAPI 异步框架，性能高、自带 OpenAPI 文档
- SQLAlchemy 2.0 AsyncSession，支持 SQLite / MySQL
- 「空间（Space）— 节点（Node）— 配置内容（ConfigStore）」三层结构，支持文件夹树和配置项统一管理
- 内置只读空间保护机制（如 `prod` 空间禁止写操作）
- 软删除策略，保留历史痕迹
- 支持文件夹/配置项的跨空间同步（Sync）
- 启动时自动建表并初始化示例数据

## 技术栈

| 分类 | 组件 |
| --- | --- |
| Web 框架 | FastAPI ^0.115 |
| ASGI 服务器 | Uvicorn ^0.31 |
| ORM | SQLAlchemy ^2.0.34（async） |
| 配置管理 | pydantic-settings ^2.5 |
| MySQL 驱动 | aiomysql ^0.2.0 |
| SQLite 驱动 | aiosqlite（按需安装） |
| Python | ≥ 3.10 |

## 项目结构

```
server/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── health.py            # 健康检查
│   │   │   └── workbench.py         # Workbench 业务接口
│   │   └── router.py                # 路由聚合
│   ├── core/
│   │   └── config.py                # 全局配置（基于 pydantic-settings）
│   ├── models/
│   │   └── workbench.py             # SQLAlchemy ORM 模型
│   ├── schemas/
│   │   └── workbench.py             # 请求 / 响应 Pydantic 模型
│   ├── services/
│   │   └── workbench_service_db.py  # 业务服务层（CRUD、同步、树构建）
│   ├── database.py                  # 异步引擎与会话工厂
│   ├── db_init.py                   # 启动时建表与示例数据初始化
│   └── main.py                      # FastAPI 应用入口
├── sql/
│   ├── 001_init.sql                 # 初始建表脚本（MySQL）
│   └── 002_add_deleted_field.sql    # 软删除字段迁移脚本
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 数据模型

应用包含三张核心表，定义见 [app/models/workbench.py](app/models/workbench.py)：

### 1. `spaces` — 空间表

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | VARCHAR(50) PK | 空间唯一标识，如 `uat` / `prod` / `dev` |
| name | VARCHAR(100) | 空间名称 |
| readonly | BOOLEAN | 是否只读，只读空间禁止任何写操作 |
| created_at / updated_at | DATETIME | 创建 / 更新时间 |

### 2. `nodes` — 节点表

文件夹和配置项统一存储在同一张表，通过 `node_type` 区分。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | INT PK AUTO | 节点 ID |
| space_id | VARCHAR(50) FK | 所属空间 |
| node_type | ENUM(`folder`, `config`) | 节点类型 |
| name | VARCHAR(200) | 节点名称 |
| parent_id | INT | 父节点 ID，0 表示根 |
| config_id | VARCHAR(100) | 配置唯一标识（仅 `config` 类型有值） |
| component_type | VARCHAR(50) | 组件类型，如 `BiFilter` / `BiTable` / `BiChart` / `others` |
| created_by | VARCHAR(100) | 创建人 |
| deleted / deleted_at / deleted_by | - | 软删除相关字段 |
| created_at / updated_at | DATETIME | 创建 / 更新时间 |

### 3. `config_store` — 配置内容表

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| config_id | VARCHAR(100) PK | 配置唯一标识，与 `nodes.config_id` 对应 |
| content | JSON | 配置内容，由前端组件结构定义 |
| deleted | BOOLEAN | 是否已删除 |
| created_at / updated_at | DATETIME | 创建 / 更新时间 |

## API 概览

所有业务接口统一挂在 `/api` 前缀下，响应包使用统一的 `ApiResponse` 结构：

```json
{ "code": 0, "message": "ok", "data": null }
```

`code = 0` 表示成功；非 0 时 `message` 描述错误原因（如 `404` 资源不存在、`403` 只读空间禁止操作、`409` 同级名称已存在等）。

### Health

| Method | Path | 说明 |
| --- | --- | --- |
| GET | `/api/health/` | 健康检查，返回应用名与版本 |

### Workbench — 空间与节点树

| Method | Path | 说明 |
| --- | --- | --- |
| GET | `/api/workbench/api/spaces` | 获取全部空间列表 |
| GET | `/api/workbench/api/spaces/{space_id}/nodes` | 获取指定空间的节点树（已构建为树形结构） |

### Workbench — 文件夹

| Method | Path | 说明 |
| --- | --- | --- |
| POST | `/api/workbench/api/spaces/{space_id}/folders` | 新建文件夹 |
| PATCH | `/api/workbench/api/spaces/{space_id}/folders/rename` | 重命名文件夹 |
| DELETE | `/api/workbench/api/spaces/{space_id}/folders/delete` | 删除文件夹（含子节点，软删除） |
| PATCH | `/api/workbench/api/spaces/{space_id}/folders/move` | 移动文件夹（含校验：禁止移到自身子目录） |
| POST | `/api/workbench/api/spaces/{space_id}/folders/{folder_id}/sync` | 将文件夹（含子树和配置）同步到目标空间 |

### Workbench — 配置项

| Method | Path | 说明 |
| --- | --- | --- |
| POST | `/api/workbench/api/spaces/{space_id}/configs` | 新建配置项（按 `componentType` 注入模板内容） |
| PATCH | `/api/workbench/api/configs/{config_id}/rename` | 重命名配置项 |
| DELETE | `/api/workbench/api/configs/{config_id}` | 删除配置项（软删除） |
| PATCH | `/api/workbench/api/configs/{config_id}/move` | 移动配置项到目标文件夹 |
| PATCH | `/api/workbench/api/configs/{config_id}/type` | 修改配置项的组件类型 |
| GET | `/api/workbench/api/configs/{config_id}/content` | 获取配置内容（JSON） |
| PUT | `/api/workbench/api/configs/{config_id}/content` | 保存配置内容 |
| POST | `/api/workbench/api/configs/{config_id}/sync` | 将配置项同步到目标空间 |

### Workbench — 其他

| Method | Path | 说明 |
| --- | --- | --- |
| POST | `/api/workbench/api/preview/mock-data` | 预览 mock 数据接口，固定返回空列表 |

> 接口实现的入参、出参 schema 详见 [app/schemas/workbench.py](app/schemas/workbench.py)，业务逻辑详见 [app/services/workbench_service_db.py](app/services/workbench_service_db.py)。

## 业务规则要点

- **只读空间保护**：写操作前会校验 `space.readonly`，若为只读则返回 `403 只读空间，禁止操作`。例如默认初始化的 `prod` 空间即被标记为只读。
- **同级名称唯一**：同一父节点下的文件夹名称不可重复，否则返回 `409`。
- **软删除**：`nodes` 与 `config_store` 均通过 `deleted` 标记删除，删除文件夹时会级联软删除其全部子文件夹与配置项。
- **移动自校验**：移动文件夹时禁止将文件夹移动到其自身的子文件夹中。
- **配置模板**：新建配置项时根据 `componentType` 注入默认模板（`BiFilter` / `BiTable` / `BiChart` / `others`），未匹配时使用 `others` 空模板。
- **跨空间同步**：同步文件夹/配置项时，会按源路径在目标空间自动重建文件夹结构，并对已存在的配置项进行更新、对不存在的进行新建；同时复制 `config_store` 内容。
- **统一返回新树**：写操作完成后通常返回该空间的最新节点树，便于前端直接刷新视图。

## 配置

复制 `.env.example` 为 `.env` 并按需修改：

```bash
cp .env.example .env
```

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `APP_NAME` | `Config-Driven Development Platform` | 应用名称，用于健康检查与 OpenAPI 标题 |
| `APP_VERSION` | `1.0.0` | 应用版本 |
| `DEBUG` | `true` | 是否开启调试（开启后 SQLAlchemy 输出 SQL 日志） |
| `DEFAULT_USER_ID` | `admin` | 默认操作人 ID，写入 `created_by` / `deleted_by` |
| `DEFAULT_USER_NAME` | `管理员` | 默认操作人名称 |
| `DATABASE_URL` | （空） | 数据库连接串，见下文示例 |

### 数据库连接串示例

```bash
# SQLite（开发默认，需额外安装 aiosqlite）
DATABASE_URL=sqlite+aiosqlite:///./cddp.db

# MySQL（生产推荐）
DATABASE_URL=mysql+aiomysql://用户名:密码@localhost:3306/数据库名?charset=utf8mb4
```

> 服务启动时会调用 [app/db_init.py](app/db_init.py) 的 `init_db()` 自动 `create_all` 建表；当表为空时会自动写入示例空间（`uat` / `prod` / `dev`）、示例文件夹与配置项，以及对应的 `config_store` 内容，便于联调。
>
> 如需手工初始化 MySQL，可执行 [sql/001_init.sql](sql/001_init.sql)；如已有旧库需补充软删除字段，可执行 [sql/002_add_deleted_field.sql](sql/002_add_deleted_field.sql)。

## 安装

### 使用 Poetry（推荐）

```bash
poetry install
```

### 使用 pip + venv

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> 若使用 SQLite，请额外安装异步驱动：`pip install aiosqlite`。

## 运行

### 开发模式（热重载）

```bash
lsof -ti:8000 | xargs kill -9   # 可选：释放被占用的 8000 端口
cd server
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
cd server
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API 文档

服务启动后可直接访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
- 根路径: http://localhost:8000/ （返回 `{ "message": "<APP_NAME> API" }`）
