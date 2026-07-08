CREATE TABLE IF NOT EXISTS config_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '历史记录ID',
    config_id VARCHAR(100) NOT NULL COMMENT '配置唯一标识',
    content JSON NOT NULL COMMENT '配置内容快照',
    version INT NOT NULL COMMENT '版本号',
    change_type ENUM('create', 'modify', 'sync') NOT NULL DEFAULT 'modify' COMMENT '变更类型：create-新增/modify-修改/sync-同步',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_config_id (config_id),
    INDEX idx_version (version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配置历史记录表';