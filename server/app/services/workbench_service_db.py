from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select, delete, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workbench import Space, Node, ConfigStore, ConfigHistory
from app.schemas.workbench import Node as NodeSchema
from app.core.config import settings

CONFIG_TEMPLATES: Dict[str, Any] = {
    'BiFilter': {'id': '__PLACEHOLDER__', 'name': '新建筛选器', 'cols': 4, 'noLabel': False, 'fields': []},
    'BiTable': {'id': '__PLACEHOLDER__', 'name': '新建表格', 'api': '', 'usePublicFilter': False, 'fieldDict': [], 'columns': []},
    'BiChart': {'id': '__PLACEHOLDER__', 'name': '新建图表', 'type': 'bar', 'api': '', 'usePublicFilter': False, 'dimensions': [], 'metrics': []},
    'others': {},
}


def node_to_schema(db_node: Node) -> NodeSchema:
    return NodeSchema(
        nodeType=db_node.node_type,
        name=db_node.name,
        id=db_node.id,
        parentId=db_node.parent_id,
        configId=db_node.config_id,
        componentType=db_node.component_type,
        updatedAt=db_node.updated_at.strftime('%Y-%m-%d %H:%M:%S') if db_node.updated_at else None,
        createdBy=db_node.created_by,
    )


def build_tree(nodes: List[NodeSchema]) -> List[NodeSchema]:
    node_map: Dict[int, NodeSchema] = {}
    roots: List[NodeSchema] = []

    for node in nodes:
        if node.nodeType == 'folder':
            node_map[node.id] = node.model_copy(update={'children': []})

    for node in nodes:
        parent_id = node.parentId or 0

        if node.nodeType == 'folder':
            mapped = node_map.get(node.id)
            if mapped:
                if parent_id == 0:
                    roots.append(mapped)
                else:
                    parent = node_map.get(parent_id)
                    if parent:
                        parent.children.append(mapped)
                    else:
                        roots.append(mapped)
        else:
            if parent_id == 0:
                roots.append(node)
            else:
                parent = node_map.get(parent_id)
                if parent:
                    parent.children.append(node)
                else:
                    roots.append(node)

    return roots


async def get_spaces(db: AsyncSession) -> List[Dict[str, Any]]:
    result = await db.execute(select(Space))
    spaces = result.scalars().all()
    return [{'id': s.id, 'name': s.name, 'readonly': s.readonly} for s in spaces]


async def is_space_readonly(db: AsyncSession, space_id: str) -> bool:
    result = await db.execute(select(Space).where(Space.id == space_id))
    space = result.scalar_one_or_none()
    return space is not None and space.readonly is True


async def get_nodes(db: AsyncSession, space_id: str) -> Tuple[Optional[List[NodeSchema]], Optional[str]]:
    result = await db.execute(select(Space).where(Space.id == space_id))
    if result.scalar_one_or_none() is None:
        return None, f'空间 "{space_id}" 不存在'

    result = await db.execute(select(Node).where(and_(Node.space_id == space_id, Node.deleted == False)).order_by(Node.id))
    nodes = result.scalars().all()
    return [node_to_schema(n) for n in nodes], None


async def collect_descendant_folder_ids(db: AsyncSession, space_id: str, root_id: int) -> List[int]:
    ids: List[int] = [root_id]
    result = await db.execute(
        select(Node.id).where(
            and_(Node.space_id == space_id, Node.node_type == 'folder', Node.parent_id == root_id, Node.deleted == False)
        )
    )
    children = result.scalars().all()
    for child in children:
        ids.extend(await collect_descendant_folder_ids(db, space_id, child))
    return ids


async def find_space_id_by_config_id(db: AsyncSession, config_id: str) -> Optional[str]:
    result = await db.execute(
        select(Node.space_id).where(and_(Node.node_type == 'config', Node.config_id == config_id, Node.deleted == False))
    )
    return result.scalar_one_or_none()


async def create_folder(db: AsyncSession, space_id: str, name: str, parent_id: int = 0) -> Tuple[Optional[List[NodeSchema]], Optional[str]]:
    result = await db.execute(select(Space).where(Space.id == space_id))
    if result.scalar_one_or_none() is None:
        return None, f'空间 "{space_id}" 不存在'

    if await is_space_readonly(db, space_id):
        return None, '只读空间，禁止操作'

    if not name:
        return None, '文件夹名称不能为空'

    result = await db.execute(
        select(Node).where(
            and_(Node.space_id == space_id, Node.node_type == 'folder', Node.parent_id == parent_id, Node.name == name, Node.deleted == False)
        )
    )
    if result.scalar_one_or_none() is not None:
        return None, '同级文件夹名称已存在'

    new_folder = Node(
        space_id=space_id,
        node_type='folder',
        name=name,
        parent_id=parent_id,
    )
    db.add(new_folder)
    await db.commit()
    await db.refresh(new_folder)

    nodes, _ = await get_nodes(db, space_id)
    return build_tree(nodes), None


async def rename_folder(db: AsyncSession, space_id: str, folder_id: int, new_name: str) -> Tuple[Optional[List[NodeSchema]], Optional[str]]:
    result = await db.execute(select(Space).where(Space.id == space_id))
    if result.scalar_one_or_none() is None:
        return None, f'空间 "{space_id}" 不存在'

    if await is_space_readonly(db, space_id):
        return None, '只读空间，禁止操作'

    if not folder_id or not new_name:
        return None, 'id 和 newName 不能为空'

    result = await db.execute(
        select(Node).where(and_(Node.space_id == space_id, Node.node_type == 'folder', Node.id == folder_id, Node.deleted == False))
    )
    folder = result.scalar_one_or_none()
    if not folder:
        return None, f'文件夹 ID "{folder_id}" 不存在'

    folder.name = new_name
    await db.commit()

    nodes, _ = await get_nodes(db, space_id)
    return build_tree(nodes), None


async def delete_folder(db: AsyncSession, space_id: str, folder_id: int) -> Tuple[Optional[List[NodeSchema]], Optional[str]]:
    result = await db.execute(select(Space).where(Space.id == space_id))
    if result.scalar_one_or_none() is None:
        return None, f'空间 "{space_id}" 不存在'

    if await is_space_readonly(db, space_id):
        return None, '只读空间，禁止操作'

    if not folder_id:
        return None, 'id 不能为空'

    result = await db.execute(
        select(Node).where(and_(Node.space_id == space_id, Node.node_type == 'folder', Node.id == folder_id, Node.deleted == False))
    )
    folder = result.scalar_one_or_none()
    if not folder:
        return None, f'文件夹 ID "{folder_id}" 不存在'

    folder_ids = await collect_descendant_folder_ids(db, space_id, folder_id)

    result = await db.execute(
        select(Node.config_id).where(
            and_(Node.space_id == space_id, Node.node_type == 'config', Node.parent_id.in_(folder_ids), Node.deleted == False)
        )
    )
    config_ids = result.scalars().all()
    for config_id in config_ids:
        await db.execute(update(ConfigStore).where(ConfigStore.config_id == config_id).values(deleted=True))

    await db.execute(
        update(Node).where(
            and_(Node.space_id == space_id, or_(
                and_(Node.node_type == 'folder', Node.id.in_(folder_ids)),
                and_(Node.node_type == 'config', Node.parent_id.in_(folder_ids))
            ))
        ).values(deleted=True, deleted_at=func.now(), deleted_by=settings.DEFAULT_USER_ID)
    )
    await db.commit()

    nodes, _ = await get_nodes(db, space_id)
    return build_tree(nodes), None


async def move_folder(db: AsyncSession, space_id: str, source_id: int, target_parent_id: int = 0) -> Tuple[Optional[List[NodeSchema]], Optional[str]]:
    result = await db.execute(select(Space).where(Space.id == space_id))
    if result.scalar_one_or_none() is None:
        return None, f'空间 "{space_id}" 不存在'

    if await is_space_readonly(db, space_id):
        return None, '只读空间，禁止操作'

    if not source_id:
        return None, 'sourceId 不能为空'

    result = await db.execute(
        select(Node).where(and_(Node.space_id == space_id, Node.node_type == 'folder', Node.id == source_id, Node.deleted == False))
    )
    folder = result.scalar_one_or_none()
    if not folder:
        return None, f'文件夹 ID "{source_id}" 不存在'

    descendants = await collect_descendant_folder_ids(db, space_id, source_id)
    if target_parent_id != 0 and target_parent_id in descendants:
        return None, '不能将文件夹移动到自身的子文件夹中'

    folder.parent_id = target_parent_id
    await db.commit()

    nodes, _ = await get_nodes(db, space_id)
    return build_tree(nodes), None


async def create_config(db: AsyncSession, space_id: str, config_id: str, name: str, component_type: str = 'others', folder_id: int = 0) -> Tuple[Optional[List[NodeSchema]], Optional[str]]:
    result = await db.execute(select(Space).where(Space.id == space_id))
    if result.scalar_one_or_none() is None:
        return None, f'空间 "{space_id}" 不存在'

    if await is_space_readonly(db, space_id):
        return None, '只读空间，禁止操作'

    if not config_id or not name:
        return None, 'configId 和 name 不能为空'

    result = await db.execute(select(Node).where(and_(Node.node_type == 'config', Node.config_id == config_id, Node.deleted == False)))
    if result.scalar_one_or_none() is not None:
        return None, f'配置 ID "{config_id}" 已存在'

    new_config = Node(
        space_id=space_id,
        node_type='config',
        name=name,
        parent_id=folder_id,
        config_id=config_id,
        component_type=component_type,
        created_by=settings.DEFAULT_USER_ID,
    )
    db.add(new_config)

    tpl_key = component_type if component_type in CONFIG_TEMPLATES else 'others'
    tpl = CONFIG_TEMPLATES[tpl_key]
    if tpl and isinstance(tpl, dict) and 'id' in tpl:
        config_store = ConfigStore(config_id=config_id, content={**tpl, 'id': config_id, 'name': name})
    else:
        config_store = ConfigStore(config_id=config_id, content={})
    db.add(config_store)

    await db.commit()

    nodes, _ = await get_nodes(db, space_id)
    return build_tree(nodes), None


async def rename_config(db: AsyncSession, config_id: str, new_name: str) -> Tuple[Optional[List[NodeSchema]], Optional[str]]:
    if not new_name:
        return None, 'newName 不能为空'

    owner_space = await find_space_id_by_config_id(db, config_id)
    if owner_space and await is_space_readonly(db, owner_space):
        return None, '只读空间，禁止操作'

    result = await db.execute(select(Node).where(and_(Node.node_type == 'config', Node.config_id == config_id, Node.deleted == False)))
    config = result.scalar_one_or_none()
    if not config:
        return None, f'配置 "{config_id}" 不存在'

    config.name = new_name
    await db.commit()

    result = await db.execute(select(ConfigStore).where(ConfigStore.config_id == config_id))
    stored = result.scalar_one_or_none()
    if stored and isinstance(stored.content, dict):
        stored.content['name'] = new_name
        await db.commit()

    nodes, _ = await get_nodes(db, config.space_id)
    return build_tree(nodes), None


async def delete_config(db: AsyncSession, config_id: str) -> Tuple[Optional[List[NodeSchema]], Optional[str]]:
    owner_space = await find_space_id_by_config_id(db, config_id)
    if owner_space and await is_space_readonly(db, owner_space):
        return None, '只读空间，禁止操作'

    result = await db.execute(select(Node).where(and_(Node.node_type == 'config', Node.config_id == config_id, Node.deleted == False)))
    config = result.scalar_one_or_none()
    if not config:
        return None, f'配置 "{config_id}" 不存在'

    space_id = config.space_id

    await db.execute(update(Node).where(and_(Node.node_type == 'config', Node.config_id == config_id)).values(deleted=True, deleted_at=func.now(), deleted_by=settings.DEFAULT_USER_ID))
    await db.execute(update(ConfigStore).where(ConfigStore.config_id == config_id).values(deleted=True))
    await db.commit()

    nodes, _ = await get_nodes(db, space_id)
    return build_tree(nodes), None


async def move_config(db: AsyncSession, config_id: str, target_folder_id: int) -> Tuple[Optional[List[NodeSchema]], Optional[str]]:
    if target_folder_id is None:
        return None, 'targetFolderId 不能为空'

    owner_space = await find_space_id_by_config_id(db, config_id)
    if owner_space and await is_space_readonly(db, owner_space):
        return None, '只读空间，禁止操作'

    result = await db.execute(select(Node).where(and_(Node.node_type == 'config', Node.config_id == config_id, Node.deleted == False)))
    config = result.scalar_one_or_none()
    if not config:
        return None, f'配置 "{config_id}" 不存在'

    config.parent_id = target_folder_id
    await db.commit()

    nodes, _ = await get_nodes(db, config.space_id)
    return build_tree(nodes), None


async def get_config_content(db: AsyncSession, config_id: str) -> Tuple[Optional[Any], Optional[str]]:
    result = await db.execute(select(ConfigStore).where(and_(ConfigStore.config_id == config_id, ConfigStore.deleted == False)))
    stored = result.scalar_one_or_none()
    if not stored:
        return None, f'配置 "{config_id}" 不存在'
    return stored.content, None


async def save_config_content(db: AsyncSession, config_id: str, content: Any) -> Tuple[bool, Optional[str]]:
    result = await db.execute(select(ConfigStore).where(and_(ConfigStore.config_id == config_id, ConfigStore.deleted == False)))
    stored = result.scalar_one_or_none()
    if not stored:
        return False, f'配置 "{config_id}" 不存在'

    owner_space = await find_space_id_by_config_id(db, config_id)
    if owner_space and await is_space_readonly(db, owner_space):
        return False, '只读空间，禁止操作'

    result = await db.execute(select(func.max(ConfigHistory.version)).where(ConfigHistory.config_id == config_id))
    max_version = result.scalar_one_or_none()
    new_version = (max_version or 0) + 1

    history = ConfigHistory(
        config_id=config_id,
        content=stored.content,
        version=new_version,
    )
    db.add(history)

    stored.content = content
    await db.commit()
    return True, None


async def get_config_history(db: AsyncSession, config_id: str) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    result = await db.execute(select(ConfigStore).where(and_(ConfigStore.config_id == config_id, ConfigStore.deleted == False)))
    stored = result.scalar_one_or_none()
    if not stored:
        return None, f'配置 "{config_id}" 不存在'

    result = await db.execute(
        select(ConfigHistory).where(ConfigHistory.config_id == config_id).order_by(ConfigHistory.version.desc())
    )
    histories = result.scalars().all()

    return [
        {
            'id': h.id,
            'configId': h.config_id,
            'content': h.content,
            'version': h.version,
            'createdAt': h.created_at.strftime('%Y-%m-%d %H:%M:%S') if h.created_at else None,
        }
        for h in histories
    ], None


async def rollback_config(db: AsyncSession, config_id: str, version: int) -> Tuple[bool, Optional[str]]:
    result = await db.execute(select(ConfigStore).where(and_(ConfigStore.config_id == config_id, ConfigStore.deleted == False)))
    stored = result.scalar_one_or_none()
    if not stored:
        return False, f'配置 "{config_id}" 不存在'

    owner_space = await find_space_id_by_config_id(db, config_id)
    if owner_space and await is_space_readonly(db, owner_space):
        return False, '只读空间，禁止操作'

    result = await db.execute(
        select(ConfigHistory).where(and_(ConfigHistory.config_id == config_id, ConfigHistory.version == version))
    )
    history = result.scalar_one_or_none()
    if not history:
        return False, f'版本 "{version}" 不存在'

    result = await db.execute(select(func.max(ConfigHistory.version)).where(ConfigHistory.config_id == config_id))
    max_version = result.scalar_one_or_none()
    new_version = (max_version or 0) + 1

    backup = ConfigHistory(
        config_id=config_id,
        content=stored.content,
        version=new_version,
    )
    db.add(backup)

    stored.content = history.content
    await db.commit()
    return True, None


async def update_config_type(db: AsyncSession, config_id: str, component_type: str) -> Tuple[Optional[List[NodeSchema]], Optional[str]]:
    if not component_type:
        return None, 'componentType 不能为空'

    owner_space = await find_space_id_by_config_id(db, config_id)
    if owner_space and await is_space_readonly(db, owner_space):
        return None, '只读空间，禁止操作'

    result = await db.execute(select(Node).where(and_(Node.node_type == 'config', Node.config_id == config_id, Node.deleted == False)))
    config = result.scalar_one_or_none()
    if not config:
        return None, f'配置 "{config_id}" 不存在'

    config.component_type = component_type
    await db.commit()

    nodes, _ = await get_nodes(db, config.space_id)
    return build_tree(nodes), None


async def ensure_folder_path(db: AsyncSession, space_id: str, folder_path: List[str]) -> int:
    parent_id = 0
    for folder_name in folder_path:
        result = await db.execute(
            select(Node).where(
                and_(Node.space_id == space_id, Node.node_type == 'folder', Node.parent_id == parent_id, Node.name == folder_name, Node.deleted == False)
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            parent_id = existing.id
        else:
            new_folder = Node(space_id=space_id, node_type='folder', name=folder_name, parent_id=parent_id)
            db.add(new_folder)
            await db.commit()
            await db.refresh(new_folder)
            parent_id = new_folder.id
    return parent_id


async def build_folder_path(db: AsyncSession, space_id: str, folder_id: int) -> List[str]:
    path: List[str] = []
    current_id: Optional[int] = folder_id
    while current_id and current_id != 0:
        result = await db.execute(
            select(Node).where(and_(Node.space_id == space_id, Node.node_type == 'folder', Node.id == current_id, Node.deleted == False))
        )
        folder = result.scalar_one_or_none()
        if not folder:
            break
        path.insert(0, folder.name)
        current_id = folder.parent_id
    return path


async def collect_folder_tree(db: AsyncSession, space_id: str, root_folder_id: int, path_prefix: List[str]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = [{'id': root_folder_id, 'path': path_prefix}]
    result_children = await db.execute(
        select(Node).where(and_(Node.space_id == space_id, Node.node_type == 'folder', Node.parent_id == root_folder_id, Node.deleted == False))
    )
    children = result_children.scalars().all()
    for child in children:
        result.extend(await collect_folder_tree(db, space_id, child.id, path_prefix + [child.name]))
    return result


async def sync_folder(db: AsyncSession, space_id: str, folder_id: int, target_space_id: str) -> Tuple[bool, Optional[str]]:
    if not target_space_id:
        return False, 'targetSpaceId 不能为空'
    if target_space_id == space_id:
        return False, '源空间与目标空间不能相同'

    result = await db.execute(select(Space).where(Space.id == space_id))
    if result.scalar_one_or_none() is None:
        return False, f'源空间 "{space_id}" 不存在'

    result = await db.execute(select(Space).where(Space.id == target_space_id))
    if result.scalar_one_or_none() is None:
        return False, f'目标空间 "{target_space_id}" 不存在'

    result = await db.execute(
        select(Node).where(and_(Node.space_id == space_id, Node.node_type == 'folder', Node.id == folder_id, Node.deleted == False))
    )
    root_folder = result.scalar_one_or_none()
    if not root_folder:
        return False, f'文件夹 ID "{folder_id}" 不存在'

    parent_path = await build_folder_path(db, space_id, root_folder.parent_id or 0)
    root_path = parent_path + [root_folder.name]

    folder_tree = await collect_folder_tree(db, space_id, folder_id, root_path)
    id_map: Dict[int, int] = {}
    for item in folder_tree:
        target_folder_id = await ensure_folder_path(db, target_space_id, item['path'])
        id_map[item['id']] = target_folder_id

    src_folder_ids = [f['id'] for f in folder_tree]
    result = await db.execute(
        select(Node).where(and_(Node.space_id == space_id, Node.node_type == 'config', Node.parent_id.in_(src_folder_ids)))
    )
    configs_to_sync = result.scalars().all()

    for config in configs_to_sync:
        target_folder_id = id_map.get(config.parent_id or 0, 0)

        result = await db.execute(
            select(Node).where(and_(Node.space_id == target_space_id, Node.node_type == 'config', Node.config_id == config.config_id))
        )
        existing_config = result.scalar_one_or_none()

        if existing_config:
            existing_config.name = config.name
            existing_config.component_type = config.component_type
            existing_config.parent_id = target_folder_id
        else:
            new_config = Node(
                space_id=target_space_id,
                node_type='config',
                name=config.name,
                parent_id=target_folder_id,
                config_id=config.config_id,
                component_type=config.component_type,
                created_by=config.created_by,
            )
            db.add(new_config)

        result = await db.execute(select(ConfigStore).where(ConfigStore.config_id == config.config_id))
        stored = result.scalar_one_or_none()
        if stored:
            result = await db.execute(select(ConfigStore).where(and_(ConfigStore.config_id == config.config_id)))
            tgt_stored = result.scalar_one_or_none()
            if not tgt_stored:
                db.add(ConfigStore(config_id=config.config_id, content=stored.content))

    await db.commit()
    return True, None


async def sync_config(db: AsyncSession, config_id: str, target_space_id: str) -> Tuple[bool, Optional[str]]:
    if not target_space_id:
        return False, 'targetSpaceId 不能为空'

    owner_space = await find_space_id_by_config_id(db, config_id)
    if not owner_space:
        return False, f'配置 "{config_id}" 不存在'
    if target_space_id == owner_space:
        return False, '源空间与目标空间不能相同'

    result = await db.execute(select(Space).where(Space.id == target_space_id))
    if result.scalar_one_or_none() is None:
        return False, f'目标空间 "{target_space_id}" 不存在'

    result = await db.execute(select(Node).where(and_(Node.node_type == 'config', Node.config_id == config_id)))
    config = result.scalar_one_or_none()
    if not config:
        return False, f'配置 "{config_id}" 不存在'

    folder_path = await build_folder_path(db, config.space_id, config.parent_id or 0)
    target_folder_id = await ensure_folder_path(db, target_space_id, folder_path)

    result = await db.execute(
        select(Node).where(and_(Node.space_id == target_space_id, Node.node_type == 'config', Node.config_id == config_id))
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.name = config.name
        existing.component_type = config.component_type
        existing.parent_id = target_folder_id
    else:
        new_config = Node(
            space_id=target_space_id,
            node_type='config',
            name=config.name,
            parent_id=target_folder_id,
            config_id=config.config_id,
            component_type=config.component_type,
            created_by=config.created_by,
        )
        db.add(new_config)

    result = await db.execute(select(ConfigStore).where(ConfigStore.config_id == config_id))
    stored = result.scalar_one_or_none()
    if stored:
        result = await db.execute(select(ConfigStore).where(and_(ConfigStore.config_id == config_id)))
        tgt_stored = result.scalar_one_or_none()
        if not tgt_stored:
            db.add(ConfigStore(config_id=config_id, content=stored.content))

    await db.commit()
    return True, None