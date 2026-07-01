from typing import Any, Dict, List, Optional, Tuple
from app.schemas.workbench import Node, SpaceItem


SPACES: List[SpaceItem] = [
    SpaceItem(id='uat', name='UAT环境'),
    SpaceItem(id='prod', name='生产环境', readonly=True),
    SpaceItem(id='dev', name='开发环境'),
]

SPACE_DATA: Dict[str, List[Node]] = {
    'uat': [
        Node(nodeType='folder', id=1, parentId=0, name='业务订单风险', updatedAt='2026-06-01 09:00:00', createdBy='huangys26'),
        Node(nodeType='folder', id=2, parentId=1, name='整体概况', updatedAt='2026-06-01 09:05:00', createdBy='huangys26'),
        Node(nodeType='folder', id=3, parentId=1, name='履约进度分析', updatedAt='2026-06-01 09:10:00', createdBy='huangys26'),
        Node(nodeType='config', id=101, parentId=1, configId='order-risk-filter', name='订单风险筛选器', componentType='BiFilter', updatedAt='2026-06-01 10:00:00', createdBy='huangys26'),
        Node(nodeType='config', id=102, parentId=2, configId='order-today-indicators', name='今日指标', componentType='others', updatedAt='2026-06-01 10:25:00', createdBy='huangys26'),
        Node(nodeType='config', id=103, parentId=3, configId='order-risk-progress', name='履约进度分析', componentType='BiTable', updatedAt='2026-06-01 10:05:00', createdBy='huangys26'),
        Node(nodeType='config', id=104, parentId=3, configId='usage-filter', name='履约进度筛选器', componentType='BiFilter', updatedAt='2026-06-01 10:30:00', createdBy='huangys26'),
        Node(nodeType='config', id=105, parentId=2, configId='order-next-four-days', name='未来4天已下计划', componentType='BiChart', updatedAt='2026-06-01 10:15:00', createdBy='huangys26'),
        Node(nodeType='config', id=106, parentId=2, configId='order-delivery-promise', name='要求交期接单情况', componentType='BiChart', updatedAt='2026-06-01 10:10:00', createdBy='huangys26'),
        Node(nodeType='config', id=107, parentId=2, configId='order-valid-order', name='有效订单指标', componentType='others', updatedAt='2026-06-01 10:20:00', createdBy='huangys26'),
    ],
    'prod': [],
    'dev': [],
}

CONFIG_STORE: Dict[str, Any] = {}


def _init_config_store():
    CONFIG_STORE['order-risk-filter'] = {
        'id': 'order-risk-filter',
        'name': '订单风险筛选',
        'cols': 5,
        'noLabel': True,
        'fields': [
            {'key': 'bdCode', 'label': '事业部', 'type': 'select', 'placeholder': '事业部', 'options': [], 'defaultValue': 'M105', 'attrs': {'clearable': False}},
            {'key': 'productCategory', 'label': '产品线/品类', 'type': 'cascader', 'placeholder': '产品线/品类', 'options': [], 'selectAll': {'enabled': True, 'mode': 'all'}, 'attrs': {'props': {'multiple': True, 'value': 'value', 'label': 'label', 'children': 'childNode'}}},
            {'key': 'regionDistrict', 'label': '大区/区域', 'type': 'cascader', 'placeholder': '大区/区域', 'options': [], 'selectAll': {'enabled': True, 'mode': 'all'}, 'attrs': {'props': {'multiple': True, 'value': 'code', 'label': 'name', 'children': 'districts'}}},
            {'key': 'buNames', 'label': 'BU', 'type': 'select', 'placeholder': 'BU', 'options': [], 'attrs': {'multiple': True}},
            {'key': 'ouNames', 'label': 'OU', 'type': 'select', 'placeholder': 'OU', 'options': [], 'attrs': {'multiple': True}},
            {'key': 'factoryData', 'label': '工厂', 'type': 'select', 'placeholder': '工厂', 'options': [], 'attrs': {'multiple': True}},
            {'key': 'customerNames', 'label': '客户名称', 'type': 'select', 'placeholder': '客户名称', 'options': [], 'attrs': {'multiple': True}},
            {'key': 'obmOemData', 'label': 'OBM/OEM', 'type': 'select', 'placeholder': 'OBM/OEM', 'options': [], 'attrs': {'multiple': True}},
            {'key': 'month', 'label': '月份', 'type': 'date', 'attrs': {'valueFormat': 'YYYY-MM', 'type': 'month'}, 'defaultValue': '2026-06'},
            {'key': 'radio', 'label': '单位', 'type': 'radioButton', 'defaultValue': 1, 'options': [{'label': '数量', 'value': 1}, {'label': '金额', 'value': 0}]},
        ],
    }
    CONFIG_STORE['usage-filter'] = {
        'id': 'usage-filter',
        'name': '履约进度筛选',
        'cols': 5,
        'noLabel': True,
        'fields': [
            {'key': 'salesMan', 'label': '业务员', 'type': 'autocomplete', 'autocomplete': {'api': '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/searchSalesMans', 'keywordParam': 'keyWord', 'dataPath': 'data', 'labelField': 'label', 'valueField': 'value'}},
        ],
    }
    CONFIG_STORE['order-risk-progress'] = {
        'id': 'order-risk-progress',
        'name': '履约进度分析',
        'api': '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getProgressData',
        'usePublicFilter': True,
        'filterId': ['order-risk-filter', 'usage-filter'],
        'maxFixedCols': 4,
        'fieldDict': [
            {'key': 'salesRegionName', 'label': '大区', 'type': 'text', 'category': 'dimension'},
            {'key': 'salesCenShortName', 'label': '区域', 'type': 'text', 'category': 'dimension'},
            {'key': 'ouName', 'label': 'OU', 'type': 'text', 'category': 'dimension'},
            {'key': 'salesMan', 'label': '业务员', 'type': 'text', 'category': 'dimension'},
            {'key': 'quoteCustomerName', 'label': '客户', 'type': 'text', 'category': 'dimension'},
            {'key': 'quoteMfgOrgName', 'label': '工厂', 'type': 'text', 'category': 'dimension'},
            {'key': 'productLine', 'label': '产品线', 'type': 'text', 'category': 'dimension'},
            {'key': 'categoryName', 'label': '品类', 'type': 'text', 'category': 'dimension'},
            {'key': 'mtdPlanTotal', 'label': '发货任务', 'type': 'number', 'category': 'metric', 'description': '取出货分析的销售计划内的月度任务数量或金额'},
            {'key': 'orderPoolMonth', 'label': '本月订单池', 'type': 'number', 'category': 'metric', 'description': '全月已确定发货+无SO的要求交期落在本月的数量'},
            {'key': 'confirmedShipment', 'label': '全月已确定发货', 'type': 'number', 'category': 'metric', 'description': '截止昨日已发+今日已发+本月已有SO未过最晚装柜日期的待发数量/金额'},
            {'key': 'shippedMonth', 'label': '截止昨日已发', 'type': 'number', 'category': 'metric', 'description': '实际出货日期为本月，截止昨日的实际出货数量/金额'},
            {'key': 'progressToYesterdayRate', 'label': '截止昨日发货进度%', 'type': 'percentage', 'category': 'metric', 'decimals': 1, 'description': '截止昨日已发/本月发货任务'},
            {'key': 'shippedToday', 'label': '今日已发', 'type': 'number', 'category': 'metric', 'description': '实际出货日期落在当天的实际出货数量和金额'},
            {'key': 'totalExpectedToday', 'label': '今日预计可发', 'type': 'number', 'category': 'metric', 'description': '今日已发+今日有柜号待发+今日无柜号待发'},
            {'key': 'totalShipmentPlan', 'label': '全月总发货计划', 'type': 'number', 'category': 'metric', 'description': '截止昨日已发+今日已发+订舱预计发货日期在本月且大于等于今日的出货通知书数量/金额'},
            {'key': 'confirmedShipmentGap', 'label': '全月已确定发货缺口', 'type': 'number', 'category': 'metric', 'description': '本月任务-全月已确定发货'},
            {'key': 'inventoryQty', 'label': '库存现有量', 'type': 'number', 'category': 'metric', 'description': '取ibos/oms库存现有量和完工未中转合计'},
            {'key': 'completedNoShip', 'label': '本月完工未发', 'type': 'number', 'category': 'metric', 'description': '最晚完工日期为当月的已完工未发数量/金额'},
        ],
        'fieldPicker': {'enable': True, 'dimensions': True, 'metrics': True, 'mode': 'inline', 'sortable': True, 'sortableDimensions': False, 'defaultDimensions': ['salesRegionName', 'salesCenShortName']},
        'columns': [
            {'key': 'salesRegionName', 'fixed': 'left'},
            {'key': 'salesCenShortName', 'fixed': 'left'},
            {'key': 'ouName', 'fixed': 'left', 'width': 200, 'ellipsis': True},
            {'key': 'salesMan', 'fixed': 'left'},
            {'key': 'quoteCustomerName', 'fixed': 'left', 'width': 200, 'ellipsis': True},
            {'key': 'quoteMfgOrgName', 'fixed': 'left'},
            {'key': 'productLine', 'fixed': 'left'},
            {'key': 'categoryName', 'fixed': 'left'},
            {'key': 'mtdPlanTotal', 'label': '发货任务', 'sortable': True, 'showCaliber': True},
            {'key': 'orderPoolMonth', 'label': '本月订单池', 'sortable': True, 'showCaliber': True},
            {'label': '发货进度', 'expandable': True, 'children': [
                {'key': 'confirmedShipment', 'sortable': True, 'showCaliber': True},
                {'key': 'shippedMonth', 'sortable': True, 'showCaliber': True, 'alwaysShow': True},
                {'key': 'progressToYesterdayRate', 'sortable': True, 'showCaliber': True},
                {'key': 'shippedToday', 'sortable': True, 'showCaliber': True, 'alwaysShow': True},
                {'key': 'totalExpectedToday', 'sortable': True, 'showCaliber': True, 'alwaysShow': True},
            ]},
            {'label': '发货计划', 'expandable': True, 'children': [
                {'key': 'totalShipmentPlan', 'sortable': True, 'showCaliber': True, 'alwaysShow': True},
                {'key': 'confirmedShipmentGap', 'sortable': True, 'showCaliber': True, 'alwaysShow': True},
            ]},
            {'label': '完工未发', 'expandable': True, 'children': [
                {'key': 'inventoryQty', 'sortable': True, 'showCaliber': True, 'alwaysShow': True},
                {'key': 'completedNoShip', 'sortable': True, 'showCaliber': True, 'alwaysShow': True},
            ]},
        ],
    }
    CONFIG_STORE['order-delivery-promise'] = {
        'id': 'order-delivery-promise',
        'name': '要求交期接单情况',
        'title': '要求交期接单情况',
        'type': 'bar',
        'api': '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getDeliveryPromiseData',
        'filterId': 'order-risk-filter',
        'usePublicFilter': True,
        'dimensions': [{'key': 'month', 'label': '月份'}],
        'metrics': [{'key': 'orderQuantity', 'label': '接单数量'}, {'key': 'samePeriodQuantity', 'label': '同期出货数量'}],
        'attrs': {'barWidth': 20},
    }
    CONFIG_STORE['order-next-four-days'] = {
        'id': 'order-next-four-days',
        'name': '未来4天已下计划',
        'type': 'line',
        'api': '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getNextFourDaysData',
        'filterId': 'order-risk-filter',
        'usePublicFilter': True,
        'dimensions': [{'key': 'date', 'label': '日期'}],
        'metrics': [{'key': 'expectedShipment', 'label': '预计发货'}],
        'autoYAxis': True,
        'attrs': {'smooth': True, 'showLabel': True, 'showSymbol': True, 'lineWidth': 2, 'legend': {'show': False}, 'grid': {'top': 30, 'left': 10, 'right': 10, 'bottom': 10}},
    }
    CONFIG_STORE['order-valid-order'] = {
        'id': 'order-valid-order',
        'name': '有效订单指标',
        'type': 'custom',
        'api': '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getValidOrderData',
        'filterId': 'order-risk-filter',
        'usePublicFilter': True,
        'unit': {'quantity': '台', 'amount': '万元'},
    }
    CONFIG_STORE['order-today-indicators'] = {
        'id': 'order-today-indicators',
        'name': '今日指标',
        'type': 'custom',
        'api': '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getValidOrderData',
        'filterId': 'order-risk-filter',
        'usePublicFilter': True,
        'unit': {'quantity': '台', 'amount': '万元'},
    }


_init_config_store()

CONFIG_TEMPLATES: Dict[str, Any] = {
    'BiFilter': {'id': '__PLACEHOLDER__', 'name': '新建筛选器', 'cols': 4, 'noLabel': False, 'fields': []},
    'BiTable': {'id': '__PLACEHOLDER__', 'name': '新建表格', 'api': '', 'usePublicFilter': False, 'fieldDict': [], 'columns': []},
    'BiChart': {'id': '__PLACEHOLDER__', 'name': '新建图表', 'type': 'bar', 'api': '', 'usePublicFilter': False, 'dimensions': [], 'metrics': []},
    'others': {},
}


def get_spaces() -> List[SpaceItem]:
    return SPACES


def is_space_readonly(space_id: str) -> bool:
    space = next((s for s in SPACES if s.id == space_id), None)
    return space is not None and space.readonly is True


def get_nodes(space_id: str) -> Tuple[Optional[List[Node]], Optional[str]]:
    if space_id not in SPACE_DATA:
        return None, f'空间 "{space_id}" 不存在'
    return SPACE_DATA[space_id], None


def build_tree(nodes: List[Node]) -> List[Node]:
    node_map: Dict[int, Node] = {}
    roots: List[Node] = []

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


def now_str() -> str:
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def next_id(nodes: List[Node]) -> int:
    max_id = max((n.id for n in nodes if n.id is not None), default=0)
    return max_id + 1


def collect_descendant_folder_ids(nodes: List[Node], root_id: int) -> List[int]:
    ids: List[int] = [root_id]
    children = [n for n in nodes if n.nodeType == 'folder' and n.parentId == root_id]
    for child in children:
        if child.id:
            ids.extend(collect_descendant_folder_ids(nodes, child.id))
    return ids


def find_space_id_by_config_id(config_id: str) -> Optional[str]:
    for space_id, nodes in SPACE_DATA.items():
        if any(n.nodeType == 'config' and n.configId == config_id for n in nodes):
            return space_id
    return None


def ensure_folder_path(target_nodes: List[Node], folder_path: List[str]) -> int:
    parent_id = 0
    for folder_name in folder_path:
        existing = next(
            (n for n in target_nodes
             if n.nodeType == 'folder' and (n.parentId or 0) == parent_id and n.name == folder_name),
            None
        )
        if existing:
            parent_id = existing.id
        else:
            new_id = next_id(target_nodes)
            new_folder = Node(nodeType='folder', id=new_id, parentId=parent_id, name=folder_name)
            target_nodes.append(new_folder)
            parent_id = new_id
    return parent_id


def build_folder_path(nodes: List[Node], folder_id: int) -> List[str]:
    path: List[str] = []
    current_id: Optional[int] = folder_id
    while current_id and current_id != 0:
        folder = next((n for n in nodes if n.nodeType == 'folder' and n.id == current_id), None)
        if not folder:
            break
        path.insert(0, folder.name)
        current_id = folder.parentId
    return path


def collect_folder_tree(nodes: List[Node], root_folder_id: int, path_prefix: List[str]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = [{'id': root_folder_id, 'path': path_prefix}]
    children = [n for n in nodes if n.nodeType == 'folder' and n.parentId == root_folder_id]
    for child in children:
        if child.id:
            result.extend(collect_folder_tree(nodes, child.id, path_prefix + [child.name]))
    return result


def create_folder(space_id: str, name: str, parent_id: int = 0) -> Tuple[Optional[List[Node]], Optional[str]]:
    nodes = SPACE_DATA.get(space_id)
    if not nodes:
        return None, f'空间 "{space_id}" 不存在'
    if is_space_readonly(space_id):
        return None, '只读空间，禁止操作'
    if not name:
        return None, '文件夹名称不能为空'

    duplicate = any(n.nodeType == 'folder' and n.parentId == parent_id and n.name == name for n in nodes)
    if duplicate:
        return None, '同级文件夹名称已存在'

    new_folder = Node(nodeType='folder', id=next_id(nodes), parentId=parent_id, name=name)
    nodes.append(new_folder)
    return build_tree(nodes), None


def rename_folder(space_id: str, folder_id: int, new_name: str) -> Tuple[Optional[List[Node]], Optional[str]]:
    nodes = SPACE_DATA.get(space_id)
    if not nodes:
        return None, f'空间 "{space_id}" 不存在'
    if is_space_readonly(space_id):
        return None, '只读空间，禁止操作'
    if not folder_id or not new_name:
        return None, 'id 和 newName 不能为空'

    folder = next((n for n in nodes if n.nodeType == 'folder' and n.id == folder_id), None)
    if not folder:
        return None, f'文件夹 ID "{folder_id}" 不存在'

    folder.name = new_name
    return build_tree(nodes), None


def delete_folder(space_id: str, folder_id: int) -> Tuple[Optional[List[Node]], Optional[str]]:
    nodes = SPACE_DATA.get(space_id)
    if not nodes:
        return None, f'空间 "{space_id}" 不存在'
    if is_space_readonly(space_id):
        return None, '只读空间，禁止操作'
    if not folder_id:
        return None, 'id 不能为空'

    folder = next((n for n in nodes if n.nodeType == 'folder' and n.id == folder_id), None)
    if not folder:
        return None, f'文件夹 ID "{folder_id}" 不存在'

    folder_ids = collect_descendant_folder_ids(nodes, folder_id)

    for n in nodes:
        if n.nodeType == 'config' and n.parentId in folder_ids and n.configId:
            CONFIG_STORE.pop(n.configId, None)

    SPACE_DATA[space_id] = [
        n for n in nodes
        if not (n.nodeType == 'folder' and n.id in folder_ids)
        and not (n.nodeType == 'config' and n.parentId in folder_ids)
    ]
    return build_tree(SPACE_DATA[space_id]), None


def move_folder(space_id: str, source_id: int, target_parent_id: int = 0) -> Tuple[Optional[List[Node]], Optional[str]]:
    nodes = SPACE_DATA.get(space_id)
    if not nodes:
        return None, f'空间 "{space_id}" 不存在'
    if is_space_readonly(space_id):
        return None, '只读空间，禁止操作'
    if not source_id:
        return None, 'sourceId 不能为空'

    folder = next((n for n in nodes if n.nodeType == 'folder' and n.id == source_id), None)
    if not folder:
        return None, f'文件夹 ID "{source_id}" 不存在'

    descendants = collect_descendant_folder_ids(nodes, source_id)
    if target_parent_id != 0 and target_parent_id in descendants:
        return None, '不能将文件夹移动到自身的子文件夹中'

    folder.parentId = target_parent_id
    return build_tree(nodes), None


def create_config(space_id: str, config_id: str, name: str, component_type: str = 'others', folder_id: int = 0) -> Tuple[Optional[List[Node]], Optional[str]]:
    nodes = SPACE_DATA.get(space_id)
    if not nodes:
        return None, f'空间 "{space_id}" 不存在'
    if is_space_readonly(space_id):
        return None, '只读空间，禁止操作'
    if not config_id or not name:
        return None, 'configId 和 name 不能为空'

    if any(n.nodeType == 'config' and n.configId == config_id for n in nodes):
        return None, f'配置 ID "{config_id}" 已存在'

    new_config = Node(
        nodeType='config',
        id=next_id(nodes),
        parentId=folder_id,
        configId=config_id,
        name=name,
        componentType=component_type,
        updatedAt=now_str(),
        createdBy='mock-user',
    )
    nodes.append(new_config)

    tpl_key = component_type if component_type in CONFIG_TEMPLATES else 'others'
    tpl = CONFIG_TEMPLATES[tpl_key]
    if tpl and isinstance(tpl, dict) and 'id' in tpl:
        CONFIG_STORE[config_id] = {**tpl, 'id': config_id, 'name': name}
    else:
        CONFIG_STORE[config_id] = {}

    return build_tree(nodes), None


def rename_config(config_id: str, new_name: str) -> Tuple[Optional[List[Node]], Optional[str]]:
    if not new_name:
        return None, 'newName 不能为空'

    owner_space = find_space_id_by_config_id(config_id)
    if owner_space and is_space_readonly(owner_space):
        return None, '只读空间，禁止操作'

    found_nodes: Optional[List[Node]] = None
    for nodes in SPACE_DATA.values():
        config = next((n for n in nodes if n.nodeType == 'config' and n.configId == config_id), None)
        if config:
            config.name = new_name
            config.updatedAt = now_str()
            found_nodes = nodes
            break

    if not found_nodes:
        return None, f'配置 "{config_id}" 不存在'

    stored = CONFIG_STORE.get(config_id)
    if stored and isinstance(stored, dict):
        stored['name'] = new_name

    return build_tree(found_nodes), None


def delete_config(config_id: str) -> Tuple[Optional[List[Node]], Optional[str]]:
    owner_space = find_space_id_by_config_id(config_id)
    if owner_space and is_space_readonly(owner_space):
        return None, '只读空间，禁止操作'

    for space_id, nodes in SPACE_DATA.items():
        idx = next((i for i, n in enumerate(nodes) if n.nodeType == 'config' and n.configId == config_id), -1)
        if idx != -1:
            nodes.pop(idx)
            CONFIG_STORE.pop(config_id, None)
            return build_tree(SPACE_DATA[space_id]), None

    return None, f'配置 "{config_id}" 不存在'


def move_config(config_id: str, target_folder_id: int) -> Tuple[Optional[List[Node]], Optional[str]]:
    if target_folder_id is None:
        return None, 'targetFolderId 不能为空'

    owner_space = find_space_id_by_config_id(config_id)
    if owner_space and is_space_readonly(owner_space):
        return None, '只读空间，禁止操作'

    for nodes in SPACE_DATA.values():
        config = next((n for n in nodes if n.nodeType == 'config' and n.configId == config_id), None)
        if config:
            config.parentId = target_folder_id
            config.updatedAt = now_str()
            return build_tree(nodes), None

    return None, f'配置 "{config_id}" 不存在'


def get_config_content(config_id: str) -> Tuple[Optional[Any], Optional[str]]:
    if config_id not in CONFIG_STORE:
        return None, f'配置 "{config_id}" 不存在'
    return CONFIG_STORE[config_id], None


def save_config_content(config_id: str, content: Any) -> Tuple[bool, Optional[str]]:
    if config_id not in CONFIG_STORE:
        return False, f'配置 "{config_id}" 不存在'

    owner_space = find_space_id_by_config_id(config_id)
    if owner_space and is_space_readonly(owner_space):
        return False, '只读空间，禁止操作'

    CONFIG_STORE[config_id] = content
    return True, None


def update_config_type(config_id: str, component_type: str) -> Tuple[Optional[List[Node]], Optional[str]]:
    if not component_type:
        return None, 'componentType 不能为空'

    owner_space = find_space_id_by_config_id(config_id)
    if owner_space and is_space_readonly(owner_space):
        return None, '只读空间，禁止操作'

    for nodes in SPACE_DATA.values():
        config = next((n for n in nodes if n.nodeType == 'config' and n.configId == config_id), None)
        if config:
            config.componentType = component_type
            config.updatedAt = now_str()
            return build_tree(nodes), None

    return None, f'配置 "{config_id}" 不存在'


def sync_folder(space_id: str, folder_id: int, target_space_id: str) -> Tuple[bool, Optional[str]]:
    if not target_space_id:
        return False, 'targetSpaceId 不能为空'
    if target_space_id == space_id:
        return False, '源空间与目标空间不能相同'

    src_nodes = SPACE_DATA.get(space_id)
    if not src_nodes:
        return False, f'源空间 "{space_id}" 不存在'
    tgt_nodes = SPACE_DATA.get(target_space_id)
    if not tgt_nodes:
        return False, f'目标空间 "{target_space_id}" 不存在'

    root_folder = next((n for n in src_nodes if n.nodeType == 'folder' and n.id == folder_id), None)
    if not root_folder:
        return False, f'文件夹 ID "{folder_id}" 不存在'

    parent_path = build_folder_path(src_nodes, root_folder.parentId or 0)
    root_path = parent_path + [root_folder.name]

    folder_tree = collect_folder_tree(src_nodes, folder_id, root_path)
    id_map: Dict[int, int] = {}
    for item in folder_tree:
        target_folder_id = ensure_folder_path(tgt_nodes, item['path'])
        id_map[item['id']] = target_folder_id

    src_folder_ids = [f['id'] for f in folder_tree]
    configs_to_sync = [n for n in src_nodes if n.nodeType == 'config' and n.parentId in src_folder_ids]

    for config in configs_to_sync:
        target_folder_id = id_map.get(config.parentId or 0, 0)
        existing_config = next((n for n in tgt_nodes if n.nodeType == 'config' and n.configId == config.configId), None)

        if existing_config:
            existing_config.name = config.name
            existing_config.componentType = config.componentType
            existing_config.parentId = target_folder_id
            existing_config.updatedAt = now_str()
        else:
            tgt_nodes.append(Node(
                **config.model_dump(exclude={'id'}),
                id=next_id(tgt_nodes),
                parentId=target_folder_id,
                updatedAt=now_str(),
            ))

        if config.configId and config.configId in CONFIG_STORE:
            CONFIG_STORE[config.configId] = CONFIG_STORE[config.configId]

    return True, None


def sync_config(config_id: str, target_space_id: str) -> Tuple[bool, Optional[str]]:
    if not target_space_id:
        return False, 'targetSpaceId 不能为空'

    src_space_id = find_space_id_by_config_id(config_id)
    if not src_space_id:
        return False, f'配置 "{config_id}" 不存在'
    if target_space_id == src_space_id:
        return False, '源空间与目标空间不能相同'

    src_nodes = SPACE_DATA.get(src_space_id)
    tgt_nodes = SPACE_DATA.get(target_space_id)
    if not tgt_nodes:
        return False, f'目标空间 "{target_space_id}" 不存在'

    config = next((n for n in src_nodes if n.nodeType == 'config' and n.configId == config_id), None)
    if not config:
        return False, f'配置 "{config_id}" 不存在'

    folder_path = build_folder_path(src_nodes, config.parentId or 0)
    target_folder_id = ensure_folder_path(tgt_nodes, folder_path)

    existing = next((n for n in tgt_nodes if n.nodeType == 'config' and n.configId == config_id), None)
    if existing:
        existing.name = config.name
        existing.componentType = config.componentType
        existing.parentId = target_folder_id
        existing.updatedAt = now_str()
    else:
        tgt_nodes.append(Node(
            **config.model_dump(exclude={'id'}),
            id=next_id(tgt_nodes),
            parentId=target_folder_id,
            updatedAt=now_str(),
        ))

    if config_id in CONFIG_STORE:
        CONFIG_STORE[config_id] = CONFIG_STORE[config_id]

    return True, None