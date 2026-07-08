from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, JSON, Enum, Text
from sqlalchemy.sql import func
from app.database import Base


class Space(Base):
    __tablename__ = "spaces"

    id = Column(String(50), primary_key=True, comment="空间唯一标识")
    name = Column(String(100), nullable=False, comment="空间名称")
    readonly = Column(Boolean, default=False, comment="是否只读")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="节点ID")
    space_id = Column(String(50), ForeignKey("spaces.id"), nullable=False, comment="所属空间ID")
    node_type = Column(Enum("folder", "config"), nullable=False, comment="节点类型")
    name = Column(String(200), nullable=False, comment="节点名称")
    parent_id = Column(Integer, default=0, comment="父节点ID")
    config_id = Column(String(100), comment="配置唯一标识")
    component_type = Column(String(50), default="others", comment="组件类型")
    created_by = Column(String(100), comment="创建人")
    deleted = Column(Boolean, default=False, comment="是否已删除")
    deleted_at = Column(DateTime, comment="删除时间")
    deleted_by = Column(String(100), comment="删除人")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class ConfigStore(Base):
    __tablename__ = "config_store"

    config_id = Column(String(100), primary_key=True, comment="配置唯一标识")
    content = Column(JSON, nullable=False, comment="配置内容")
    deleted = Column(Boolean, default=False, comment="是否已删除")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class ConfigHistory(Base):
    __tablename__ = "config_history"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="历史记录ID")
    config_id = Column(String(100), nullable=False, comment="配置唯一标识")
    content = Column(JSON, nullable=False, comment="配置内容快照")
    version = Column(Integer, nullable=False, comment="版本号")
    change_type = Column(Enum("create", "modify", "sync"), nullable=False, default="modify", comment="变更类型：create-新增/modify-修改/sync-同步")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")