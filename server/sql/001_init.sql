CREATE TABLE IF NOT EXISTS spaces (
    id VARCHAR(50) PRIMARY KEY COMMENT '空间唯一标识',
    name VARCHAR(100) NOT NULL COMMENT '空间名称',
    readonly BOOLEAN DEFAULT FALSE COMMENT '是否只读',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='空间表';


CREATE TABLE IF NOT EXISTS nodes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '节点ID',
    space_id VARCHAR(50) NOT NULL COMMENT '所属空间ID',
    node_type ENUM('folder', 'config') NOT NULL COMMENT '节点类型',
    name VARCHAR(200) NOT NULL COMMENT '节点名称',
    parent_id BIGINT DEFAULT 0 COMMENT '父节点ID',
    config_id VARCHAR(100) COMMENT '配置唯一标识（仅config类型有值）',
    component_type VARCHAR(50) DEFAULT 'others' COMMENT '组件类型',
    created_by VARCHAR(100) COMMENT '创建人',
    deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    deleted_at DATETIME COMMENT '删除时间',
    deleted_by VARCHAR(100) COMMENT '删除人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_space_id (space_id),
    INDEX idx_parent_id (parent_id),
    INDEX idx_config_id (config_id),
    INDEX idx_node_type (node_type),
    INDEX idx_deleted (deleted),
    FOREIGN KEY (space_id) REFERENCES spaces(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='节点表（文件夹和配置统一存储）';


CREATE TABLE IF NOT EXISTS config_store (
    config_id VARCHAR(100) PRIMARY KEY COMMENT '配置唯一标识',
    content JSON NOT NULL COMMENT '配置内容（JSON格式）',
    deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配置内容存储表';


INSERT INTO spaces (id, name, readonly) VALUES
('uat', 'UAT环境', FALSE),
('prod', '生产环境', TRUE),
('dev', '开发环境', FALSE);


INSERT INTO nodes (space_id, node_type, name, parent_id, config_id, component_type, created_by, created_at) VALUES
('uat', 'folder', '业务订单风险', 0, NULL, NULL, 'huangys26', '2026-06-01 09:00:00'),
('uat', 'folder', '整体概况', 1, NULL, NULL, 'huangys26', '2026-06-01 09:05:00'),
('uat', 'folder', '履约进度分析', 1, NULL, NULL, 'huangys26', '2026-06-01 09:10:00'),
('uat', 'config', '订单风险筛选器', 1, 'order-risk-filter', 'BiFilter', 'huangys26', '2026-06-01 10:00:00'),
('uat', 'config', '今日指标', 2, 'order-today-indicators', 'others', 'huangys26', '2026-06-01 10:25:00'),
('uat', 'config', '履约进度分析', 3, 'order-risk-progress', 'BiTable', 'huangys26', '2026-06-01 10:05:00'),
('uat', 'config', '履约进度筛选器', 3, 'usage-filter', 'BiFilter', 'huangys26', '2026-06-01 10:30:00'),
('uat', 'config', '未来4天已下计划', 2, 'order-next-four-days', 'BiChart', 'huangys26', '2026-06-01 10:15:00'),
('uat', 'config', '要求交期接单情况', 2, 'order-delivery-promise', 'BiChart', 'huangys26', '2026-06-01 10:10:00'),
('uat', 'config', '有效订单指标', 2, 'order-valid-order', 'others', 'huangys26', '2026-06-01 10:20:00');


INSERT INTO config_store (config_id, content) VALUES
('order-risk-filter', '{\"id\":\"order-risk-filter\",\"name\":\"订单风险筛选\",\"cols\":5,\"noLabel\":true,\"fields\":[{\"key\":\"bdCode\",\"label\":\"事业部\",\"type\":\"select\",\"placeholder\":\"事业部\",\"options\":[],\"defaultValue\":\"M105\",\"attrs\":{\"clearable\":false}},{\"key\":\"productCategory\",\"label\":\"产品线/品类\",\"type\":\"cascader\",\"placeholder\":\"产品线/品类\",\"options\":[],\"selectAll\":{\"enabled\":true,\"mode\":\"all\"},\"attrs\":{\"props\":{\"multiple\":true,\"value\":\"value\",\"label\":\"label\",\"children\":\"childNode\"}}},{\"key\":\"regionDistrict\",\"label\":\"大区/区域\",\"type\":\"cascader\",\"placeholder\":\"大区/区域\",\"options\":[],\"selectAll\":{\"enabled\":true,\"mode\":\"all\"},\"attrs\":{\"props\":{\"multiple\":true,\"value\":\"code\",\"label\":\"name\",\"children\":\"districts\"}}},{\"key\":\"buNames\",\"label\":\"BU\",\"type\":\"select\",\"placeholder\":\"BU\",\"options\":[],\"attrs\":{\"multiple\":true}},{\"key\":\"ouNames\",\"label\":\"OU\",\"type\":\"select\",\"placeholder\":\"OU\",\"options\":[],\"attrs\":{\"multiple\":true}},{\"key\":\"factoryData\",\"label\":\"工厂\",\"type\":\"select\",\"placeholder\":\"工厂\",\"options\":[],\"attrs\":{\"multiple\":true}},{\"key\":\"customerNames\",\"label\":\"客户名称\",\"type\":\"select\",\"placeholder\":\"客户名称\",\"options\":[],\"attrs\":{\"multiple\":true}},{\"key\":\"obmOemData\",\"label\":\"OBM/OEM\",\"type\":\"select\",\"placeholder\":\"OBM/OEM\",\"options\":[],\"attrs\":{\"multiple\":true}},{\"key\":\"month\",\"label\":\"月份\",\"type\":\"date\",\"attrs\":{\"valueFormat\":\"YYYY-MM\",\"type\":\"month\"},\"defaultValue\":\"2026-06\"},{\"key\":\"radio\",\"label\":\"单位\",\"type\":\"radioButton\",\"defaultValue\":1,\"options\":[{\"label\":\"数量\",\"value\":1},{\"label\":\"金额\",\"value\":0}]}]}'),
('usage-filter', '{\"id\":\"usage-filter\",\"name\":\"履约进度筛选\",\"cols\":5,\"noLabel\":true,\"fields\":[{\"key\":\"salesMan\",\"label\":\"业务员\",\"type\":\"autocomplete\",\"autocomplete\":{\"api\":\"/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/searchSalesMans\",\"keywordParam\":\"keyWord\",\"dataPath\":\"data\",\"labelField\":\"label\",\"valueField\":\"value\"}}]}'),
('order-risk-progress', '{\"id\":\"order-risk-progress\",\"name\":\"履约进度分析\",\"api\":\"/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getProgressData\",\"usePublicFilter\":true,\"filterId\":[\"order-risk-filter\",\"usage-filter\"],\"maxFixedCols\":4,\"fieldDict\":[{\"key\":\"salesRegionName\",\"label\":\"大区\",\"type\":\"text\",\"category\":\"dimension\"},{\"key\":\"salesCenShortName\",\"label\":\"区域\",\"type\":\"text\",\"category\":\"dimension\"},{\"key\":\"ouName\",\"label\":\"OU\",\"type\":\"text\",\"category\":\"dimension\"},{\"key\":\"salesMan\",\"label\":\"业务员\",\"type\":\"text\",\"category\":\"dimension\"},{\"key\":\"quoteCustomerName\",\"label\":\"客户\",\"type\":\"text\",\"category\":\"dimension\"},{\"key\":\"quoteMfgOrgName\",\"label\":\"工厂\",\"type\":\"text\",\"category\":\"dimension\"},{\"key\":\"productLine\",\"label\":\"产品线\",\"type\":\"text\",\"category\":\"dimension\"},{\"key\":\"categoryName\",\"label\":\"品类\",\"type\":\"text\",\"category\":\"dimension\"},{\"key\":\"mtdPlanTotal\",\"label\":\"发货任务\",\"type\":\"number\",\"category\":\"metric\",\"description\":\"取出货分析的销售计划内的月度任务数量或金额\"},{\"key\":\"orderPoolMonth\",\"label\":\"本月订单池\",\"type\":\"number\",\"category\":\"metric\",\"description\":\"全月已确定发货+无SO的要求交期落在本月的数量\"},{\"key\":\"confirmedShipment\",\"label\":\"全月已确定发货\",\"type\":\"number\",\"category\":\"metric\",\"description\":\"截止昨日已发+今日已发+本月已有SO未过最晚装柜日期的待发数量/金额\"},{\"key\":\"shippedMonth\",\"label\":\"截止昨日已发\",\"type\":\"number\",\"category\":\"metric\",\"description\":\"实际出货日期为本月，截止昨日的实际出货数量/金额\"},{\"key\":\"progressToYesterdayRate\",\"label\":\"截止昨日发货进度%\",\"type\":\"percentage\",\"category\":\"metric\",\"decimals\":1,\"description\":\"截止昨日已发/本月发货任务\"},{\"key\":\"shippedToday\",\"label\":\"今日已发\",\"type\":\"number\",\"category\":\"metric\",\"description\":\"实际出货日期落在当天的实际出货数量和金额\"},{\"key\":\"totalExpectedToday\",\"label\":\"今日预计可发\",\"type\":\"number\",\"category\":\"metric\",\"description\":\"今日已发+今日有柜号待发+今日无柜号待发\"},{\"key\":\"totalShipmentPlan\",\"label\":\"全月总发货计划\",\"type\":\"number\",\"category\":\"metric\",\"description\":\"截止昨日已发+今日已发+订舱预计发货日期在本月且大于等于今日的出货通知书数量/金额\"},{\"key\":\"confirmedShipmentGap\",\"label\":\"全月已确定发货缺口\",\"type\":\"number\",\"category\":\"metric\",\"description\":\"本月任务-全月已确定发货\"},{\"key\":\"inventoryQty\",\"label\":\"库存现有量\",\"type\":\"number\",\"category\":\"metric\",\"description\":\"取ibos/oms库存现有量和完工未中转合计\"},{\"key\":\"completedNoShip\",\"label\":\"本月完工未发\",\"type\":\"number\",\"category\":\"metric\",\"description\":\"最晚完工日期为当月的已完工未发数量/金额\"}],\"fieldPicker\":{\"enable\":true,\"dimensions\":true,\"metrics\":true,\"mode\":\"inline\",\"sortable\":true,\"sortableDimensions\":false,\"defaultDimensions\":[\"salesRegionName\",\"salesCenShortName\"]},\"columns\":[{\"key\":\"salesRegionName\",\"fixed\":\"left\"},{\"key\":\"salesCenShortName\",\"fixed\":\"left\"},{\"key\":\"ouName\",\"fixed\":\"left\",\"width\":200,\"ellipsis\":true},{\"key\":\"salesMan\",\"fixed\":\"left\"},{\"key\":\"quoteCustomerName\",\"fixed\":\"left\",\"width\":200,\"ellipsis\":true},{\"key\":\"quoteMfgOrgName\",\"fixed\":\"left\"},{\"key\":\"productLine\",\"fixed\":\"left\"},{\"key\":\"categoryName\",\"fixed\":\"left\"},{\"key\":\"mtdPlanTotal\",\"label\":\"发货任务\",\"sortable\":true,\"showCaliber\":true},{\"key\":\"orderPoolMonth\",\"label\":\"本月订单池\",\"sortable\":true,\"showCaliber\":true},{\"label\":\"发货进度\",\"expandable\":true,\"children\":[{\"key\":\"confirmedShipment\",\"sortable\":true,\"showCaliber\":true},{\"key\":\"shippedMonth\",\"sortable\":true,\"showCaliber\":true,\"alwaysShow\":true},{\"key\":\"progressToYesterdayRate\",\"sortable\":true,\"showCaliber\":true},{\"key\":\"shippedToday\",\"sortable\":true,\"showCaliber\":true,\"alwaysShow\":true},{\"key\":\"totalExpectedToday\",\"sortable\":true,\"showCaliber\":true,\"alwaysShow\":true}]},{\"label\":\"发货计划\",\"expandable\":true,\"children\":[{\"key\":\"totalShipmentPlan\",\"sortable\":true,\"showCaliber\":true,\"alwaysShow\":true},{\"key\":\"confirmedShipmentGap\",\"sortable\":true,\"showCaliber\":true,\"alwaysShow\":true}]},{\"label\":\"完工未发\",\"expandable\":true,\"children\":[{\"key\":\"inventoryQty\",\"sortable\":true,\"showCaliber\":true,\"alwaysShow\":true},{\"key\":\"completedNoShip\",\"sortable\":true,\"showCaliber\":true,\"alwaysShow\":true}]}]}'),
('order-delivery-promise', '{\"id\":\"order-delivery-promise\",\"name\":\"要求交期接单情况\",\"title\":\"要求交期接单情况\",\"type\":\"bar\",\"api\":\"/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getDeliveryPromiseData\",\"filterId\":\"order-risk-filter\",\"usePublicFilter\":true,\"dimensions\":[{\"key\":\"month\",\"label\":\"月份\"}],\"metrics\":[{\"key\":\"orderQuantity\",\"label\":\"接单数量\"},{\"key\":\"samePeriodQuantity\",\"label\":\"同期出货数量\"}],\"attrs\":{\"barWidth\":20}}'),
('order-next-four-days', '{\"id\":\"order-next-four-days\",\"name\":\"未来4天已下计划\",\"type\":\"line\",\"api\":\"/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getNextFourDaysData\",\"filterId\":\"order-risk-filter\",\"usePublicFilter\":true,\"dimensions\":[{\"key\":\"date\",\"label\":\"日期\"}],\"metrics\":[{\"key\":\"expectedShipment\",\"label\":\"预计发货\"}],\"autoYAxis\":true,\"attrs\":{\"smooth\":true,\"showLabel\":true,\"showSymbol\":true,\"lineWidth\":2,\"legend\":{\"show\":false},\"grid\":{\"top\":30,\"left\":10,\"right\":10,\"bottom\":10}}}'),
('order-valid-order', '{\"id\":\"order-valid-order\",\"name\":\"有效订单指标\",\"type\":\"custom\",\"api\":\"/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getValidOrderData\",\"filterId\":\"order-risk-filter\",\"usePublicFilter\":true,\"unit\":{\"quantity\":\"台\",\"amount\":\"万元\"}}'),
('order-today-indicators', '{\"id\":\"order-today-indicators\",\"name\":\"今日指标\",\"type\":\"custom\",\"api\":\"/D-OBD/d-obd-java-waixiao-dashboard/dashboard/order/risk/getValidOrderData\",\"filterId\":\"order-risk-filter\",\"usePublicFilter\":true,\"unit\":{\"quantity\":\"台\",\"amount\":\"万元\"}}');