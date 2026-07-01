import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { TreeNode, DragNode, AllowDropType, DropType } from './types'

export function useTreeDrag(options: {
  onMoveFolder: (sourceId: number, targetParentId: number | null) => void
  onMoveConfig: (configId: string, targetFolderId: number) => void
}) {
  const { onMoveFolder, onMoveConfig } = options

  /**
   * folder 和 config 节点都允许被拖拽
   */
  const allowDrag = (_node: DragNode) => {
    return true
  }

  /**
   * 拖拽放置规则：
   * - 拖拽 folder：
   *   - inner：目标必须是 folder，且不能是自身或自身子孙
   *   - prev/next：目标是 folder 时允许（同层排序），目标是 config 时禁止
   * - 拖拽 config：
   *   - 只允许 inner 到 folder，禁止 prev/next（config 按名称排序，不支持手动排序）
   */
  const allowDrop = (draggingNode: DragNode, dropNode: DragNode, type: AllowDropType) => {
    const dragging = draggingNode.data
    const target = dropNode.data

    if (dragging.nodeType === 'config') {
      return target.nodeType === 'folder' && type === 'inner'
    }

    // dragging === folder
    if (target.nodeType === 'config') {
      return false
    }

    // 目标是 folder
    if (type === 'inner') {
      if (target.id === dragging.id) return false
      // 目标是被拖节点的子孙文件夹 → 禁止（防循环），通过 __key 前缀判断
      if (target.__key.startsWith(dragging.__key + '/')) return false
    }

    return true
  }

  /**
   * 拖拽完成：计算新的父 ID / 目标文件夹 ID，通知父组件
   */
  const handleDrop = (draggingNode: DragNode, dropNode: DragNode, dropType: DropType) => {
    const dragging = draggingNode.data

    if (dragging.nodeType === 'config') {
      const targetFolderId = dropNode.data.id!
      // 已在目标文件夹，无需操作
      if (dragging.parentId === targetFolderId) return
      onMoveConfig(dragging.configId!, targetFolderId)
      return
    }

    // dragging === folder
    let newParentId: number = 0

    if (dropType === 'inner') {
      newParentId = dropNode.data.id!
    } else {
      // prev/next：目标一定是 folder（allowDrop 已限制）
      newParentId = dropNode.data.parentId ?? 0
    }

    // 父 ID 没变则无需操作
    if (newParentId === dragging.parentId) return

    onMoveFolder(dragging.id!, newParentId)
  }

  return {
    allowDrag,
    allowDrop,
    handleDrop,
  }
}