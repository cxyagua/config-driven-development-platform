/**
 * Workbench Mock — 接口路由
 *
 * 接口设计：
 *   GET    /workbench/api/spaces                                       → 空间列表
 *   GET    /workbench/api/spaces/:spaceId/nodes                        → 统一节点树（文件夹+配置）
 *   POST   /workbench/api/spaces/:spaceId/folders                      → 新建文件夹
 *   PATCH  /workbench/api/spaces/:spaceId/folders/rename               → 重命名文件夹
 *   DELETE /workbench/api/spaces/:spaceId/folders/delete               → 删除文件夹
 *   PATCH  /workbench/api/spaces/:spaceId/folders/move                 → 移动文件夹
 *   POST   /workbench/api/spaces/:spaceId/folders/:folderId/sync       → 同步文件夹到目标空间
 *   POST   /workbench/api/spaces/:spaceId/configs                      → 新建配置
 *   PATCH  /workbench/api/configs/:configId/rename                     → 重命名配置
 *   DELETE /workbench/api/configs/:configId                            → 删除配置
 *   PATCH  /workbench/api/configs/:configId/move                       → 移动配置
 *   POST   /workbench/api/configs/:configId/sync                       → 同步配置到目标空间
 *   GET    /workbench/api/configs/:configId/content                    → 单条配置的 JSON 内容
 *   PUT    /workbench/api/configs/:configId/content                    → 保存配置内容
 */
import type { MockMethod } from 'vite-plugin-mock'
import type { Node } from '../src/components/FolderTree/types'
import { CONFIG_STORE } from './config-store'

// ─────────────────────────────────────────────
// Mock 数据：空间列表
// ─────────────────────────────────────────────

const SPACES = [
  { id: 'uat',  name: 'UAT环境' },
  { id: 'prod', name: '生产环境', readonly: true },
  { id: 'dev',  name: '开发环境' },
]

// ─────────────────────────────────────────────
// Mock 数据：各环境的扁平节点列表（模拟数据库行）
// nodeType='folder': id, parentId, name
// nodeType='config': configId, parentId(=所在文件夹id), name, ...
// 约定：parentId=0 表示挂在根目录下
// ─────────────────────────────────────────────

const SPACE_DATA: Record<string, Node[]> = {
  uat: [
    // ── 文件夹 ──
    { nodeType: 'folder', id: 1, parentId: 0, name: '业务订单风险',  updatedAt: '2026-06-01 09:00:00', createdBy: 'huangys26' },
    { nodeType: 'folder', id: 2, parentId: 1, name: '整体概况',      updatedAt: '2026-06-01 09:05:00', createdBy: 'huangys26' },
    { nodeType: 'folder', id: 3, parentId: 1, name: '履约进度分析',  updatedAt: '2026-06-01 09:10:00', createdBy: 'huangys26' },
    // ── 配置 ──
    { nodeType: 'config', id: 101, parentId: 1, configId: 'order-risk-filter',     name: '订单风险筛选器',  componentType: 'BiFilter', updatedAt: '2026-06-01 10:00:00', createdBy: 'huangys26' },
    { nodeType: 'config', id: 102, parentId: 2, configId: 'order-today-indicators',name: '今日指标',        componentType: 'others',   updatedAt: '2026-06-01 10:25:00', createdBy: 'huangys26' },
    { nodeType: 'config', id: 103, parentId: 3, configId: 'order-risk-progress',   name: '履约进度分析',    componentType: 'BiTable',  updatedAt: '2026-06-01 10:05:00', createdBy: 'huangys26' },
    { nodeType: 'config', id: 104, parentId: 3, configId: 'usage-filter',          name: '履约进度筛选器',  componentType: 'BiFilter', updatedAt: '2026-06-01 10:30:00', createdBy: 'huangys26' },
    { nodeType: 'config', id: 105, parentId: 2, configId: 'order-next-four-days',  name: '未来4天已下计划', componentType: 'BiChart',  updatedAt: '2026-06-01 10:15:00', createdBy: 'huangys26' },
    { nodeType: 'config', id: 106, parentId: 2, configId: 'order-delivery-promise',name: '要求交期接单情况',componentType: 'BiChart',  updatedAt: '2026-06-01 10:10:00', createdBy: 'huangys26' },
    { nodeType: 'config', id: 107, parentId: 2, configId: 'order-valid-order',     name: '有效订单指标',    componentType: 'others',   updatedAt: '2026-06-01 10:20:00', createdBy: 'huangys26' },
  ],
  // prod / dev 暂无数据
  prod: [],
  dev:  [],
}

// ─────────────────────────────────────────────
// buildTree：将扁平 Node[] 组装为嵌套树
// ─────────────────────────────────────────────
function buildTree(nodes: Node[]): Node[] {
  const map = new Map<number, Node>()
  const roots: Node[] = []

  // 第一遍：建立 id→node 映射，并初始化 folder 的 children
  for (const node of nodes) {
    if (node.nodeType === 'folder') {
      map.set(node.id!, { ...node, children: [] })
    }
  }

  // 第二遍：将 config 和 folder 挂载到父节点
  // parentId=0 表示根目录
  for (const node of nodes) {
    const parentId = node.parentId ?? 0

    if (node.nodeType === 'folder') {
      const mapped = map.get(node.id!)!
      if (parentId === 0) {
        roots.push(mapped)
      } else {
        const parent = map.get(parentId)
        if (parent) {
          parent.children!.push(mapped)
        } else {
          roots.push(mapped) // 父节点不存在时挂根
        }
      }
    } else {
      // config 节点
      if (parentId === 0) {
        roots.push(node)
      } else {
        const parent = map.get(parentId)
        if (parent) {
          parent.children!.push(node)
        } else {
          roots.push(node)
        }
      }
    }
  }

  return roots
}

// ─────────────────────────────────────────────
// 工具：生成当前时间字符串
// ─────────────────────────────────────────────
function nowStr(): string {
  return new Date().toISOString().replace('T', ' ').slice(0, 19)
}

// ─────────────────────────────────────────────
// 工具：计算下一个可用 ID（全局自增）
// ─────────────────────────────────────────────
function nextId(nodes: Node[]): number {
  return nodes.reduce((max, n) => Math.max(max, n.id ?? 0), 0) + 1
}

// ─────────────────────────────────────────────
// 工具：递归收集指定 folder id 及其所有子孙 folder id
// ─────────────────────────────────────────────
function collectDescendantFolderIds(nodes: Node[], rootId: number): number[] {
  const ids: number[] = [rootId]
  const children = nodes.filter((n) => n.nodeType === 'folder' && n.parentId === rootId)
  for (const child of children) {
    ids.push(...collectDescendantFolderIds(nodes, child.id!))
  }
  return ids
}

// ─────────────────────────────────────────────
// 各组件类型的最小 JSON 模板
// ─────────────────────────────────────────────
const CONFIG_TEMPLATES: Record<string, unknown> = {
  BiFilter: { id: '__PLACEHOLDER__', name: '新建筛选器', cols: 4, noLabel: false, fields: [] },
  BiTable:  { id: '__PLACEHOLDER__', name: '新建表格',  api: '', usePublicFilter: false, fieldDict: [], columns: [] },
  BiChart:  { id: '__PLACEHOLDER__', name: '新建图表',  type: 'bar', api: '', usePublicFilter: false, dimensions: [], metrics: [] },
  others:   {},
}

// ─────────────────────────────────────────────
// 工具：判断空间是否为只读
// ─────────────────────────────────────────────
function isSpaceReadonly(spaceId: string): boolean {
  return SPACES.some((s) => s.id === spaceId && s.readonly === true)
}

// 工具：根据 configId 找到所在的 spaceId
function findSpaceIdByConfigId(configId: string): string | null {
  for (const [spaceId, nodes] of Object.entries(SPACE_DATA)) {
    if (nodes.some((n) => n.nodeType === 'config' && n.configId === configId)) {
      return spaceId
    }
  }
  return null
}

// ─────────────────────────────────────────────
// 同步工具函数
// ─────────────────────────────────────────────

/**
 * 在目标空间中按路径自动建目录（已存在则复用），返回最终 folderId
 * folderPath: 从根到叶的文件夹名称数组，如 ['业务订单风险', '整体概况']
 */
function ensureFolderPath(targetNodes: Node[], folderPath: string[]): number {
  let parentId = 0
  for (const folderName of folderPath) {
    const existing = targetNodes.find(
      (n) => n.nodeType === 'folder' && (n.parentId ?? 0) === parentId && n.name === folderName
    )
    if (existing) {
      parentId = existing.id!
    } else {
      const newId = nextId(targetNodes)
      const newFolder: Node = { nodeType: 'folder', id: newId, parentId, name: folderName }
      targetNodes.push(newFolder)
      parentId = newId
    }
  }
  return parentId
}

/**
 * 在扁平节点列表中，从根到 folderId 构建层级路径（文件夹名称数组）
 */
function buildFolderPath(nodes: Node[], folderId: number): string[] {
  const path: string[] = []
  let currentId: number | undefined = folderId
  while (currentId && currentId !== 0) {
    const folder = nodes.find((n) => n.nodeType === 'folder' && n.id === currentId)
    if (!folder) break
    path.unshift(folder.name)
    currentId = folder.parentId
  }
  return path
}

/**
 * 递归收集指定 folderId 下所有子孙文件夹 id（含自身）
 * 返回 Map<旧id, 路径数组>，用于构建同步目标目录
 */
function collectFolderTree(
  nodes: Node[],
  rootFolderId: number,
  pathPrefix: string[]
): Array<{ id: number; path: string[] }> {
  const result: Array<{ id: number; path: string[] }> = [{ id: rootFolderId, path: pathPrefix }]
  const children = nodes.filter((n) => n.nodeType === 'folder' && n.parentId === rootFolderId)
  for (const child of children) {
    result.push(...collectFolderTree(nodes, child.id!, [...pathPrefix, child.name]))
  }
  return result
}

// ─────────────────────────────────────────────
// Mock 路由
// ─────────────────────────────────────────────
const mockRoutes: MockMethod[] = [

  // ── 获取空间列表 ──────────────────────────────
  {
    url: '/workbench/api/spaces',
    method: 'get',
    timeout: 100,
    response: () => ({ code: 0, message: 'ok', data: SPACES }),
  },

  // ── 获取统一节点树（文件夹 + 配置） ──────────
  {
    url: '/workbench/api/spaces/:spaceId/nodes',
    method: 'get',
    timeout: 150,
    response: (req: { url: string }) => {
      const parts = req.url.split('/')
      const spaceId = parts[parts.indexOf('spaces') + 1] ?? ''
      const nodes = SPACE_DATA[spaceId]
      if (!nodes) return { code: 404, message: `空间 "${spaceId}" 不存在`, data: null }
      return { code: 0, message: 'ok', data: buildTree(nodes) }
    },
  },

  // ── 新建文件夹 ────────────────────────────────
  {
    url: '/workbench/api/spaces/:spaceId/folders',
    method: 'post',
    timeout: 200,
    response: (req: { url: string; body?: any }) => {
      const parts = req.url.split('/')
      const spaceId = parts[parts.indexOf('spaces') + 1] ?? ''
      const nodes = SPACE_DATA[spaceId]
      if (!nodes) return { code: 404, message: `空间 "${spaceId}" 不存在`, data: null }
      if (isSpaceReadonly(spaceId)) return { code: 403, message: '只读空间，禁止操作', data: null }

      const { name, parentId = 0 } = req.body ?? {}
      if (!name) return { code: 400, message: '文件夹名称不能为空', data: null }

      // 同一父节点下名称不能重复
      const duplicate = nodes.some(
        (n) => n.nodeType === 'folder' && n.parentId === (parentId ?? 0) && n.name === name
      )
      if (duplicate) return { code: 409, message: '同级文件夹名称已存在', data: null }

      const newFolder: Node = { nodeType: 'folder', id: nextId(nodes), parentId: parentId ?? 0, name }
      nodes.push(newFolder)
      return { code: 0, message: 'ok', data: buildTree(nodes) }
    },
  },

  // ── 重命名文件夹 ──────────────────────────────
  {
    url: '/workbench/api/spaces/:spaceId/folders/rename',
    method: 'patch',
    timeout: 200,
    response: (req: { url: string; body?: any }) => {
      const parts = req.url.split('/')
      const spaceId = parts[parts.indexOf('spaces') + 1] ?? ''
      const nodes = SPACE_DATA[spaceId]
      if (!nodes) return { code: 404, message: `空间 "${spaceId}" 不存在`, data: null }
      if (isSpaceReadonly(spaceId)) return { code: 403, message: '只读空间，禁止操作', data: null }

      const { id, newName } = req.body ?? {}
      if (!id || !newName) return { code: 400, message: 'id 和 newName 不能为空', data: null }

      const folder = nodes.find((n) => n.nodeType === 'folder' && n.id === id)
      if (!folder) return { code: 404, message: `文件夹 ID "${id}" 不存在`, data: null }

      folder.name = newName
      return { code: 0, message: 'ok', data: buildTree(nodes) }
    },
  },

  // ── 删除文件夹 ────────────────────────────────
  {
    url: '/workbench/api/spaces/:spaceId/folders/delete',
    method: 'delete',
    timeout: 200,
    response: (req: { url: string; body?: any }) => {
      const parts = req.url.split('/')
      const spaceId = parts[parts.indexOf('spaces') + 1] ?? ''
      const nodes = SPACE_DATA[spaceId]
      if (!nodes) return { code: 404, message: `空间 "${spaceId}" 不存在`, data: null }
      if (isSpaceReadonly(spaceId)) return { code: 403, message: '只读空间，禁止操作', data: null }

      const { id } = req.body ?? {}
      if (!id) return { code: 400, message: 'id 不能为空', data: null }

      const folder = nodes.find((n) => n.nodeType === 'folder' && n.id === id)
      if (!folder) return { code: 404, message: `文件夹 ID "${id}" 不存在`, data: null }

      // 递归收集所有要删除的 folder id
      const folderIds = collectDescendantFolderIds(nodes, id)

      // 清理 CONFIG_STORE
      nodes
        .filter((n) => n.nodeType === 'config' && folderIds.includes(n.parentId!))
        .forEach((n) => { delete CONFIG_STORE[n.configId!] })

      // 从扁平列表删除：文件夹本身、子孙文件夹、这些文件夹下的配置
      SPACE_DATA[spaceId] = nodes.filter(
        (n) =>
          !(n.nodeType === 'folder' && folderIds.includes(n.id!)) &&
          !(n.nodeType === 'config' && folderIds.includes(n.parentId!))
      )
      return { code: 0, message: 'ok', data: buildTree(SPACE_DATA[spaceId]) }
    },
  },

  // ── 移动文件夹 ────────────────────────────────
  {
    url: '/workbench/api/spaces/:spaceId/folders/move',
    method: 'patch',
    timeout: 200,
    response: (req: { url: string; body?: any }) => {
      const parts = req.url.split('/')
      const spaceId = parts[parts.indexOf('spaces') + 1] ?? ''
      const nodes = SPACE_DATA[spaceId]
      if (!nodes) return { code: 404, message: `空间 "${spaceId}" 不存在`, data: null }
      if (isSpaceReadonly(spaceId)) return { code: 403, message: '只读空间，禁止操作', data: null }

      const { sourceId, targetParentId = 0 } = req.body ?? {}
      if (!sourceId) return { code: 400, message: 'sourceId 不能为空', data: null }

      const folder = nodes.find((n) => n.nodeType === 'folder' && n.id === sourceId)
      if (!folder) return { code: 404, message: `文件夹 ID "${sourceId}" 不存在`, data: null }

      // 防止移动到自身子孙
      const descendants = collectDescendantFolderIds(nodes, sourceId)
      if (targetParentId !== 0 && descendants.includes(targetParentId)) {
        return { code: 400, message: '不能将文件夹移动到自身的子文件夹中', data: null }
      }

      folder.parentId = targetParentId ?? 0
      return { code: 0, message: 'ok', data: buildTree(nodes) }
    },
  },

  // ── 新建配置 ─────────────────────────────────
  {
    url: '/workbench/api/spaces/:spaceId/configs',
    method: 'post',
    timeout: 200,
    response: (req: { url: string; body?: any }) => {
      const parts = req.url.split('/')
      const spaceId = parts[parts.indexOf('spaces') + 1] ?? ''
      const nodes = SPACE_DATA[spaceId]
      if (!nodes) return { code: 404, message: `空间 "${spaceId}" 不存在`, data: null }
      if (isSpaceReadonly(spaceId)) return { code: 403, message: '只读空间，禁止操作', data: null }

      const { configId, name, componentType, folderId = 0 } = req.body ?? {}
      if (!configId || !name) return { code: 400, message: 'configId 和 name 不能为空', data: null }

      if (nodes.some((n) => n.nodeType === 'config' && n.configId === configId)) {
        return { code: 409, message: `配置 ID "${configId}" 已存在`, data: null }
      }

      const newConfig: Node = {
        nodeType: 'config',
        id: nextId(nodes),
        parentId: folderId ?? 0,
        configId,
        name,
        componentType: componentType ?? 'others',
        updatedAt: nowStr(),
        createdBy: 'mock-user',
      }
      nodes.push(newConfig)

      // 写入 CONFIG_STORE
      const tplKey = CONFIG_TEMPLATES[componentType] ? componentType : 'others'
      const tpl = CONFIG_TEMPLATES[tplKey]
      CONFIG_STORE[configId] = tpl && typeof tpl === 'object' && 'id' in (tpl as any)
        ? { ...(tpl as any), id: configId, name }
        : {}

      return { code: 0, message: 'ok', data: buildTree(nodes) }
    },
  },

  // ── 重命名配置 ────────────────────────────────
  {
    url: '/workbench/api/configs/:configId/rename',
    method: 'patch',
    timeout: 200,
    response: (req: { url: string; body?: any }) => {
      const parts = req.url.split('/')
      const configIdx = parts.indexOf('configs')
      const configId = configIdx > 0 ? parts[configIdx + 1] : ''
      const { newName } = req.body ?? {}
      if (!newName) return { code: 400, message: 'newName 不能为空', data: null }
      const ownerSpace = findSpaceIdByConfigId(configId)
      if (ownerSpace && isSpaceReadonly(ownerSpace)) return { code: 403, message: '只读空间，禁止操作', data: null }

      let foundNodes: Node[] | null = null

      for (const nodes of Object.values(SPACE_DATA)) {
        const c = nodes.find((n) => n.nodeType === 'config' && n.configId === configId)
        if (c) {
          c.name = newName
          c.updatedAt = nowStr()
          foundNodes = nodes
          break
        }
      }
      if (!foundNodes) return { code: 404, message: `配置 "${configId}" 不存在`, data: null }

      // 同步 CONFIG_STORE
      const stored = CONFIG_STORE[configId]
      if (stored && typeof stored === 'object') {
        (CONFIG_STORE[configId] as any).name = newName
      }

      return { code: 0, message: 'ok', data: buildTree(foundNodes) }
    },
  },

  // ── 删除配置 ─────────────────────────────────
  {
    url: '/workbench/api/configs/:configId',
    method: 'delete',
    timeout: 200,
    response: (req: { url: string }) => {
      const parts = req.url.split('/')
      const configIdx = parts.indexOf('configs')
      const configId = configIdx > 0 ? parts[configIdx + 1] : ''
      const ownerSpace = findSpaceIdByConfigId(configId)
      if (ownerSpace && isSpaceReadonly(ownerSpace)) return { code: 403, message: '只读空间，禁止操作', data: null }

      for (const [spaceId, nodes] of Object.entries(SPACE_DATA)) {
        const idx = nodes.findIndex((n) => n.nodeType === 'config' && n.configId === configId)
        if (idx !== -1) {
          nodes.splice(idx, 1)
          delete CONFIG_STORE[configId]
          return { code: 0, message: 'ok', data: buildTree(SPACE_DATA[spaceId]) }
        }
      }
      return { code: 404, message: `配置 "${configId}" 不存在`, data: null }
    },
  },

  // ── 移动配置 ─────────────────────────────────
  {
    url: '/workbench/api/configs/:configId/move',
    method: 'patch',
    timeout: 200,
    response: (req: { url: string; body?: any }) => {
      const parts = req.url.split('/')
      const configIdx = parts.indexOf('configs')
      const configId = configIdx > 0 ? parts[configIdx + 1] : ''
      const { targetFolderId } = req.body ?? {}
      if (targetFolderId === undefined) return { code: 400, message: 'targetFolderId 不能为空', data: null }
      const ownerSpace = findSpaceIdByConfigId(configId)
      if (ownerSpace && isSpaceReadonly(ownerSpace)) return { code: 403, message: '只读空间，禁止操作', data: null }

      for (const nodes of Object.values(SPACE_DATA)) {
        const c = nodes.find((n) => n.nodeType === 'config' && n.configId === configId)
        if (c) {
          c.parentId = targetFolderId ?? 0
          c.updatedAt = nowStr()
          return { code: 0, message: 'ok', data: buildTree(nodes) }
        }
      }
      return { code: 404, message: `配置 "${configId}" 不存在`, data: null }
    },
  },

  // ── 获取单条配置的 JSON 内容 ──────────────────
  {
    url: '/workbench/api/configs/:configId/content',
    method: 'get',
    timeout: 200,
    response: (req: { url: string }) => {
      const parts = req.url.split('/')
      const contentIdx = parts.indexOf('content')
      const configId = contentIdx > 0 ? parts[contentIdx - 1] : ''
      const content = CONFIG_STORE[configId]
      if (content === undefined) return { code: 404, message: `配置 "${configId}" 不存在`, data: null }
      return { code: 0, message: 'ok', data: content }
    },
  },

  // ── 保存单条配置的 JSON 内容 ──────────────────
  {
    url: '/workbench/api/configs/:configId/content',
    method: 'put',
    timeout: 200,
    response: (req: { url: string; body?: unknown }) => {
      const parts = req.url.split('/')
      const contentIdx = parts.indexOf('content')
      const configId = contentIdx > 0 ? parts[contentIdx - 1] : ''
      if (!(configId in CONFIG_STORE)) return { code: 404, message: `配置 "${configId}" 不存在`, data: null }
      const ownerSpace = findSpaceIdByConfigId(configId)
      if (ownerSpace && isSpaceReadonly(ownerSpace)) return { code: 403, message: '只读空间，禁止操作', data: null }
      CONFIG_STORE[configId] = req.body ?? {}
      return { code: 0, message: 'ok', data: null }
    },
  },

  // ── 修改配置的组件类型 ───────────────────────────
  {
    url: '/workbench/api/configs/:configId/type',
    method: 'patch',
    timeout: 200,
    response: (req: { url: string; body?: any }) => {
      const parts = req.url.split('/')
      const configIdx = parts.indexOf('configs')
      const configId = configIdx > 0 ? parts[configIdx + 1] : ''
      const { componentType } = req.body ?? {}
      if (!componentType) return { code: 400, message: 'componentType 不能为空', data: null }
      const ownerSpace = findSpaceIdByConfigId(configId)
      if (ownerSpace && isSpaceReadonly(ownerSpace)) return { code: 403, message: '只读空间，禁止操作', data: null }

      for (const nodes of Object.values(SPACE_DATA)) {
        const c = nodes.find((n) => n.nodeType === 'config' && n.configId === configId)
        if (c) {
          c.componentType = componentType
          c.updatedAt = nowStr()
          return { code: 0, message: 'ok', data: buildTree(nodes) }
        }
      }
      return { code: 404, message: `配置 "${configId}" 不存在`, data: null }
    },
  },

  // ── 预览区通用 mock 接口 ──────────────────────
  {
    url: '/workbench/api/preview/mock-data',
    method: 'post',
    timeout: 50,
    response: () => ({ code: 0, message: 'ok', data: { list: [], total: 0 } }),
  },

  // ── 同步文件夹到目标空间 ──────────────────────
  // POST /workbench/api/spaces/:spaceId/folders/:folderId/sync
  {
    url: '/workbench/api/spaces/:spaceId/folders/:folderId/sync',
    method: 'post',
    timeout: 400,
    response: (req: { url: string; body?: any }) => {
      const parts = req.url.split('/')
      const spacesIdx = parts.indexOf('spaces')
      const spaceId = spacesIdx > 0 ? parts[spacesIdx + 1] : ''
      const foldersIdx = parts.indexOf('folders')
      const folderId = foldersIdx > 0 ? Number(parts[foldersIdx + 1]) : 0
      const { targetSpaceId } = req.body ?? {}

      if (!targetSpaceId) return { code: 400, message: 'targetSpaceId 不能为空', data: null }
      if (targetSpaceId === spaceId) return { code: 400, message: '源空间与目标空间不能相同', data: null }

      const srcNodes = SPACE_DATA[spaceId]
      if (!srcNodes) return { code: 404, message: `源空间 "${spaceId}" 不存在`, data: null }
      const tgtNodes = SPACE_DATA[targetSpaceId]
      if (!tgtNodes) return { code: 404, message: `目标空间 "${targetSpaceId}" 不存在`, data: null }

      // 找到根文件夹本身
      const rootFolder = srcNodes.find((n) => n.nodeType === 'folder' && n.id === folderId)
      if (!rootFolder) return { code: 404, message: `文件夹 ID "${folderId}" 不存在`, data: null }

      // 构建该文件夹在源空间的完整路径（含自身）
      const parentPath = buildFolderPath(srcNodes, rootFolder.parentId ?? 0)
      const rootPath = [...parentPath, rootFolder.name]

      // 收集文件夹树（含根）
      const folderTree = collectFolderTree(srcNodes, folderId, rootPath)
      // oldId → newTargetFolderId 映射
      const idMap = new Map<number, number>()
      for (const { id, path } of folderTree) {
        const targetFolderId = ensureFolderPath(tgtNodes, path)
        idMap.set(id, targetFolderId)
      }

      // 同步所有配置（属于这些文件夹的）
      const srcFolderIds = folderTree.map((f) => f.id)
      const configsToSync = srcNodes.filter(
        (n) => n.nodeType === 'config' && srcFolderIds.includes(n.parentId!)
      )
      for (const config of configsToSync) {
        const targetFolderId = idMap.get(config.parentId!) ?? 0
        // 已存在同 configId → 覆盖
        const existingConfig = tgtNodes.find((n) => n.nodeType === 'config' && n.configId === config.configId)
        if (existingConfig) {
          existingConfig.name = config.name
          existingConfig.componentType = config.componentType
          existingConfig.parentId = targetFolderId
          existingConfig.updatedAt = nowStr()
        } else {
          tgtNodes.push({
            ...config,
            id: nextId(tgtNodes),
            parentId: targetFolderId,
            updatedAt: nowStr(),
          })
        }
        // 同步 CONFIG_STORE（深拷贝内容）
        if (CONFIG_STORE[config.configId!] !== undefined) {
          CONFIG_STORE[config.configId!] = JSON.parse(JSON.stringify(CONFIG_STORE[config.configId!]))
        }
      }

      return { code: 0, message: 'ok', data: null }
    },
  },

  // ── 同步单个配置到目标空间 ────────────────────
  // POST /workbench/api/configs/:configId/sync
  {
    url: '/workbench/api/configs/:configId/sync',
    method: 'post',
    timeout: 400,
    response: (req: { url: string; body?: any }) => {
      const parts = req.url.split('/')
      const configIdx = parts.indexOf('configs')
      const configId = configIdx > 0 ? parts[configIdx + 1] : ''
      const { targetSpaceId } = req.body ?? {}

      if (!targetSpaceId) return { code: 400, message: 'targetSpaceId 不能为空', data: null }

      const srcSpaceId = findSpaceIdByConfigId(configId)
      if (!srcSpaceId) return { code: 404, message: `配置 "${configId}" 不存在`, data: null }
      if (targetSpaceId === srcSpaceId) return { code: 400, message: '源空间与目标空间不能相同', data: null }
      const srcNodes = SPACE_DATA[srcSpaceId]
      const tgtNodes = SPACE_DATA[targetSpaceId]
      if (!tgtNodes) return { code: 404, message: `目标空间 "${targetSpaceId}" 不存在`, data: null }

      const config = srcNodes.find((n) => n.nodeType === 'config' && n.configId === configId)!
      // 重建配置所在的文件夹路径，并在目标空间中建好
      const folderPath = buildFolderPath(srcNodes, config.parentId ?? 0)
      const targetFolderId = ensureFolderPath(tgtNodes, folderPath)

      // 已存在同 configId → 覆盖
      const existing = tgtNodes.find((n) => n.nodeType === 'config' && n.configId === configId)
      if (existing) {
        existing.name = config.name
        existing.componentType = config.componentType
        existing.parentId = targetFolderId
        existing.updatedAt = nowStr()
      } else {
        tgtNodes.push({
          ...config,
          id: nextId(tgtNodes),
          parentId: targetFolderId,
          updatedAt: nowStr(),
        })
      }
      // 同步 CONFIG_STORE（深拷贝内容）
      if (CONFIG_STORE[configId] !== undefined) {
        CONFIG_STORE[configId] = JSON.parse(JSON.stringify(CONFIG_STORE[configId]))
      }

      return { code: 0, message: 'ok', data: null }
    },
  },
]

export default mockRoutes