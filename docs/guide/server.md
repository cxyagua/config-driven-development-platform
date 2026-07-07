# 服务端 Server

服务端是 CDDP 的后端，基于 FastAPI 构建，负责配置的解析、验证与执行。

## 环境要求

- Python 3.10+
- Poetry 或 pip

## 安装

```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 运行

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API 文档

服务启动后可访问交互式 API 文档：

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

## 目录结构

```
server/
├── app/
│   ├── api/
│   │   ├── endpoints/         # API 端点（health、workbench 等）
│   │   ├── router.py          # 路由聚合
│   │   └── __init__.py
│   ├── core/
│   │   └── config.py          # 应用配置
│   ├── models/                # 数据模型
│   ├── schemas/               # 数据契约
│   ├── services/              # 业务服务
│   ├── database.py            # 数据库连接
│   ├── db_init.py             # 数据库初始化
│   └── main.py                # 应用入口
├── sql/                       # 建表脚本
│   ├── 001_init.sql
│   └── 002_add_deleted_field.sql
├── .env.example
├── pyproject.toml
└── requirements.txt
```

## 配置

复制 `.env.example` 为 `.env` 并填写：

```bash
cp .env.example .env
```

### 环境变量

| 变量 | 说明 |
| --- | --- |
| `APP_NAME` | 应用名称 |
| `APP_VERSION` | 应用版本 |
| `DEBUG` | 调试模式（true/false） |
| `DATABASE_URL` | 数据库连接 URL |
