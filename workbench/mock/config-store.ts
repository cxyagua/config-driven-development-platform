/**
 * Workbench Mock — 配置内容仓库
 *
 * 每个 key 对应一个 configId，value 为该配置的完整 JSON 内容。
 * 真实场景下这些数据由后端数据库存储并通过接口返回。
 */

// ── 订单风险顶部筛选器 ──────────────────────────────────
const orderRiskFilter = {
  id: 'order-risk-filter',
  name: '订单风险筛选',
  cols: 5,
  noLabel: true,
  fields: [
    {
      key: 'bdCode',
      label: '事业部',
      type: 'select',
      placeholder: '事业部',
      options: [],
      defaultValue: 'M105',
      attrs: { clearable: false },
    },
    {
      key: 'productCategory',
      label: '产品线/品类',
      type: 'cascader',
      placeholder: '产品线/品类',
      options: [],
      selectAll: { enabled: true, mode: 'all' },
      attrs: {
        props: { multiple: true, value: 'value', label: 'label', children: 'childNode' },
      },
    },
    {
      key: 'regionDistrict',
      label: '大区/区域',
      type: 'cascader',
      placeholder: '大区/区域',
      options: [],
      selectAll: { enabled: true, mode: 'all' },
      attrs: {
        props: { multiple: true, value: 'code', label: 'name', children: 'districts' },
      },
    },
    {
      key: 'buNames',
      label: 'BU',
      type: 'select',
      placeholder: 'BU',
      options: [],
      attrs: { multiple: true },
    },
    {
      key: 'ouNames',
      label: 'OU',
      type: 'select',
      placeholder: 'OU',
      options: [],
      attrs: { multiple: true },
    },
    {
      key: 'factoryData',
      label: '工厂',
      type: 'select',
      placeholder: '工厂',
      options: [],
      attrs: { multiple: true },
    },
    {
      key: 'customerNames',
      label: '客户名称',
      type: 'select',
      placeholder: '客户名称',
      options: [],
      attrs: { multiple: true },
    },
    {
      key: 'obmOemData',
      label: 'OBM/OEM',
      type: 'select',
      placeholder: 'OBM/OEM',
      options: [],
      attrs: { multiple: true },
    },
    {
      key: 'month',
      label: '月份',
      type: 'date',
      attrs: { valueFormat: 'YYYY-MM', type: 'month' },
      defaultValue: '2026-06',
    },
    {
      key: 'radio',
      label: '单位',
      type: 'radioButton',
      defaultValue: 1,
      options: [
        { label: '数量', value: 1 },
        { label: '金额', value: 0 },
      ],
    },
  ],
}

// ── 履约进度分析筛选器（usage-filter）────────────────────
const usageFilter = {
  id: 'usage-filter',
  name: '履约进度筛选',
  cols: 5,
  noLabel: true,
  fields: [
    {
      key: 'salesMan',
      label: '业务员',
      type: 'autocomplete',
      autocomplete: {
        api: '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/searchSalesMans',
        keywordParam: 'keyWord',
        dataPath: 'data',
        labelField: 'label',
        valueField: 'value',
      },
    },
  ],
}

// ── 履约进度分析表格 ──────────────────────────────────────
const orderRiskProgress = {
  id: 'order-risk-progress',
  name: '履约进度分析',
  api: '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getProgressData',
  usePublicFilter: true,
  filterId: ['order-risk-filter', 'usage-filter'],
  maxFixedCols: 4,
  fieldDict: [
    { key: 'salesRegionName',   label: '大区',   type: 'text', category: 'dimension' },
    { key: 'salesCenShortName', label: '区域',   type: 'text', category: 'dimension' },
    { key: 'ouName',            label: 'OU',     type: 'text', category: 'dimension' },
    { key: 'salesMan',          label: '业务员', type: 'text', category: 'dimension' },
    { key: 'quoteCustomerName', label: '客户',   type: 'text', category: 'dimension' },
    { key: 'quoteMfgOrgName',   label: '工厂',   type: 'text', category: 'dimension' },
    { key: 'productLine',       label: '产品线', type: 'text', category: 'dimension' },
    { key: 'categoryName',      label: '品类',   type: 'text', category: 'dimension' },
    { key: 'mtdPlanTotal',            label: '发货任务',          type: 'number',     category: 'metric', description: '取出货分析的销售计划内的月度任务数量或金额' },
    { key: 'orderPoolMonth',          label: '本月订单池',        type: 'number',     category: 'metric', description: '全月已确定发货+无SO的要求交期落在本月的数量' },
    { key: 'confirmedShipment',       label: '全月已确定发货',    type: 'number',     category: 'metric', description: '截止昨日已发+今日已发+本月已有SO未过最晚装柜日期的待发数量/金额' },
    { key: 'shippedMonth',            label: '截止昨日已发',      type: 'number',     category: 'metric', description: '实际出货日期为本月，截止昨日的实际出货数量/金额' },
    { key: 'progressToYesterdayRate', label: '截止昨日发货进度%', type: 'percentage', category: 'metric', decimals: 1, description: '截止昨日已发/本月发货任务' },
    { key: 'shippedToday',            label: '今日已发',          type: 'number',     category: 'metric', description: '实际出货日期落在当天的实际出货数量和金额' },
    { key: 'totalExpectedToday',      label: '今日预计可发',      type: 'number',     category: 'metric', description: '今日已发+今日有柜号待发+今日无柜号待发' },
    { key: 'totalShipmentPlan',       label: '全月总发货计划',    type: 'number',     category: 'metric', description: '截止昨日已发+今日已发+订舱预计发货日期在本月且大于等于今日的出货通知书数量/金额' },
    { key: 'confirmedShipmentGap',    label: '全月已确定发货缺口',type: 'number',     category: 'metric', description: '本月任务-全月已确定发货' },
    { key: 'inventoryQty',            label: '库存现有量',        type: 'number',     category: 'metric', description: '取ibos/oms库存现有量和完工未中转合计' },
    { key: 'completedNoShip',         label: '本月完工未发',      type: 'number',     category: 'metric', description: '最晚完工日期为当月的已完工未发数量/金额' },
  ],
  fieldPicker: {
    enable: true,
    dimensions: true,
    metrics: true,
    mode: 'inline',
    sortable: true,
    sortableDimensions: false,
    defaultDimensions: ['salesRegionName', 'salesCenShortName'],
  },
  columns: [
    { key: 'salesRegionName',   fixed: 'left' },
    { key: 'salesCenShortName', fixed: 'left' },
    { key: 'ouName',            fixed: 'left', width: 200, ellipsis: true },
    { key: 'salesMan',          fixed: 'left' },
    { key: 'quoteCustomerName', fixed: 'left', width: 200, ellipsis: true },
    { key: 'quoteMfgOrgName',   fixed: 'left' },
    { key: 'productLine',       fixed: 'left' },
    { key: 'categoryName',      fixed: 'left' },
    { key: 'mtdPlanTotal',   label: '发货任务',   sortable: true, showCaliber: true },
    { key: 'orderPoolMonth', label: '本月订单池', sortable: true, showCaliber: true },
    {
      label: '发货进度',
      expandable: true,
      children: [
        { key: 'confirmedShipment',       sortable: true, showCaliber: true },
        { key: 'shippedMonth',            sortable: true, showCaliber: true, alwaysShow: true },
        { key: 'progressToYesterdayRate', sortable: true, showCaliber: true },
        { key: 'shippedToday',            sortable: true, showCaliber: true, alwaysShow: true },
        { key: 'totalExpectedToday',      sortable: true, showCaliber: true, alwaysShow: true },
      ],
    },
    {
      label: '发货计划',
      expandable: true,
      children: [
        { key: 'totalShipmentPlan',    sortable: true, showCaliber: true, alwaysShow: true },
        { key: 'confirmedShipmentGap', sortable: true, showCaliber: true, alwaysShow: true },
      ],
    },
    {
      label: '完工未发',
      expandable: true,
      children: [
        { key: 'inventoryQty',    sortable: true, showCaliber: true, alwaysShow: true },
        { key: 'completedNoShip', sortable: true, showCaliber: true, alwaysShow: true },
      ],
    },
  ],
}

// ── 要求交期接单情况（柱状图）────────────────────────────
const orderDeliveryPromise = {
  id: 'order-delivery-promise',
  name: '要求交期接单情况',
  title: '要求交期接单情况',
  type: 'bar',
  api: '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getDeliveryPromiseData',
  filterId: 'order-risk-filter',
  usePublicFilter: true,
  dimensions: [{ key: 'month', label: '月份' }],
  metrics: [
    { key: 'orderQuantity',      label: '接单数量' },
    { key: 'samePeriodQuantity', label: '同期出货数量' },
  ],
  attrs: { barWidth: 20 },
}

// ── 未来4天已下计划（折线图）─────────────────────────────
const orderNextFourDays = {
  id: 'order-next-four-days',
  name: '未来4天已下计划',
  type: 'line',
  api: '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getNextFourDaysData',
  filterId: 'order-risk-filter',
  usePublicFilter: true,
  dimensions: [{ key: 'date', label: '日期' }],
  metrics: [{ key: 'expectedShipment', label: '预计发货' }],
  autoYAxis: true,
  attrs: {
    smooth: true,
    showLabel: true,
    showSymbol: true,
    lineWidth: 2,
    legend: { show: false },
    grid: { top: 30, left: 10, right: 10, bottom: 10 },
  },
}

// ── 有效订单指标（自定义组件）────────────────────────────
const orderValidOrder = {
  id: 'order-valid-order',
  name: '有效订单指标',
  type: 'custom',
  api: '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getValidOrderData',
  filterId: 'order-risk-filter',
  usePublicFilter: true,
  unit: { quantity: '台', amount: '万元' },
}

// ── 今日指标（自定义组件）────────────────────────────────
const orderTodayIndicators = {
  id: 'order-today-indicators',
  name: '今日指标',
  type: 'custom',
  api: '/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getValidOrderData',
  filterId: 'order-risk-filter',
  usePublicFilter: true,
  unit: { quantity: '台', amount: '万元' },
}

// ─────────────────────────────────────────────
// 配置中心：configId → 配置内容
// ─────────────────────────────────────────────
export const CONFIG_STORE: Record<string, unknown> = {
  'order-risk-filter':      orderRiskFilter,
  'usage-filter':           usageFilter,
  'order-risk-progress':    orderRiskProgress,
  'order-delivery-promise': orderDeliveryPromise,
  'order-next-four-days':   orderNextFourDays,
  'order-valid-order':      orderValidOrder,
  'order-today-indicators': orderTodayIndicators,
}
