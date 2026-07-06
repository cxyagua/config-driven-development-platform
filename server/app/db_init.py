import asyncio
import json
from app.database import engine, Base
from app.models.workbench import Space, Node, ConfigStore
from app.core.config import settings


CONFIG_DATA = {
    'order-risk-filter': {
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
    },
    'usage-filter': {
        'id': 'usage-filter',
        'name': '履约进度筛选',
        'cols': 5,
        'noLabel': True,
        'fields': [
            {'key': 'salesMan', 'label': '业务员', 'type': 'autocomplete', 'autocomplete': {'api': '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/searchSalesMans', 'keywordParam': 'keyWord', 'dataPath': 'data', 'labelField': 'label', 'valueField': 'value'}},
        ],
    },
    'order-risk-progress': {
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
    },
    'order-delivery-promise': {
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
    },
    'order-next-four-days': {
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
    },
    'order-valid-order': {
        'id': 'order-valid-order',
        'name': '有效订单指标',
        'type': 'custom',
        'api': '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getValidOrderData',
        'filterId': 'order-risk-filter',
        'usePublicFilter': True,
        'unit': {'quantity': '台', 'amount': '万元'},
    },
    'order-today-indicators': {
        'id': 'order-today-indicators',
        'name': '今日指标',
        'type': 'custom',
        'api': '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getValidOrderData',
        'filterId': 'order-risk-filter',
        'usePublicFilter': True,
        'unit': {'quantity': '台', 'amount': '万元'},
    },
}


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        from sqlalchemy import select, func

        result = await conn.execute(select(func.count(Space.id)))
        if result.scalar() == 0:
            spaces_data = [
                {'id': 'uat', 'name': 'UAT环境', 'readonly': False},
                {'id': 'prod', 'name': '生产环境', 'readonly': True},
                {'id': 'dev', 'name': '开发环境', 'readonly': False},
            ]
            for data in spaces_data:
                await conn.execute(Space.__table__.insert().values(**data))

        result = await conn.execute(select(func.count(Node.id)))
        if result.scalar() == 0:
            nodes_data = [
                {'space_id': 'uat', 'node_type': 'folder', 'name': '业务订单风险', 'parent_id': 0, 'created_by': settings.DEFAULT_USER_ID},
                {'space_id': 'uat', 'node_type': 'folder', 'name': '整体概况', 'parent_id': 1, 'created_by': settings.DEFAULT_USER_ID},
                {'space_id': 'uat', 'node_type': 'folder', 'name': '履约进度分析', 'parent_id': 1, 'created_by': settings.DEFAULT_USER_ID},
                {'space_id': 'uat', 'node_type': 'config', 'name': '订单风险筛选器', 'parent_id': 1, 'config_id': 'order-risk-filter', 'component_type': 'BiFilter', 'created_by': settings.DEFAULT_USER_ID},
                {'space_id': 'uat', 'node_type': 'config', 'name': '今日指标', 'parent_id': 2, 'config_id': 'order-today-indicators', 'component_type': 'others', 'created_by': settings.DEFAULT_USER_ID},
                {'space_id': 'uat', 'node_type': 'config', 'name': '履约进度分析', 'parent_id': 3, 'config_id': 'order-risk-progress', 'component_type': 'BiTable', 'created_by': settings.DEFAULT_USER_ID},
                {'space_id': 'uat', 'node_type': 'config', 'name': '履约进度筛选器', 'parent_id': 3, 'config_id': 'usage-filter', 'component_type': 'BiFilter', 'created_by': settings.DEFAULT_USER_ID},
                {'space_id': 'uat', 'node_type': 'config', 'name': '未来4天已下计划', 'parent_id': 2, 'config_id': 'order-next-four-days', 'component_type': 'BiChart', 'created_by': settings.DEFAULT_USER_ID},
                {'space_id': 'uat', 'node_type': 'config', 'name': '要求交期接单情况', 'parent_id': 2, 'config_id': 'order-delivery-promise', 'component_type': 'BiChart', 'created_by': settings.DEFAULT_USER_ID},
                {'space_id': 'uat', 'node_type': 'config', 'name': '有效订单指标', 'parent_id': 2, 'config_id': 'order-valid-order', 'component_type': 'others', 'created_by': settings.DEFAULT_USER_ID},
            ]
            for data in nodes_data:
                await conn.execute(Node.__table__.insert().values(**data))

        result = await conn.execute(select(func.count(ConfigStore.config_id)))
        if result.scalar() == 0:
            for config_id, content in CONFIG_DATA.items():
                await conn.execute(ConfigStore.__table__.insert().values(config_id=config_id, content=content))

        await conn.commit()

    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())