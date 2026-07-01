// ── FolderTree 共享类型定义 ──────────────────────────────────────────

/**
 * 接口返回 / 数据库存储的统一节点（扁平行）
 * - nodeType === 'folder'：文件夹节点，有 parentId / children（组装后）
 * - nodeType === 'config'：配置节点，叶子节点
 */
export interface Node {
  nodeType: 'folder' | 'config'
  name: string
  // folder only
  id?: number
  parentId?: number        // 0 表示根目录
  children?: Node[]
  // config only
  configId?: string
  componentType?: string
  updatedAt?: string
  createdBy?: string
}

/** el-tree 渲染层节点（在 Node 基础上附加 __key） */
export interface TreeNode extends Node {
  __key: string
  children?: TreeNode[]
}

export interface SpaceItem {
  id: string
  name: string
  /** 是否为只读空间：true 时禁止新增、删除、移动、编辑操作 */
  readonly?: boolean
}

// el-tree 内部 Node 对象（业务数据挂在 node.data 上）
export type DragNode = { data: TreeNode }
// allow-drop 的 type 实际值为 'prev' | 'inner' | 'next'
export type AllowDropType = 'prev' | 'inner' | 'next'
// node-drop 事件的 dropType 实际值为 'before' | 'after' | 'inner'
export type DropType = 'before' | 'after' | 'inner'