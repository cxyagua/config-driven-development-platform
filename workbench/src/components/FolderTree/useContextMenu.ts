import { ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import type { TreeNode } from './types'

interface UseContextMenuOptions {
  onFolderCommand: (cmd: string, data: TreeNode) => void
  onConfigCommand: (cmd: string, data: TreeNode) => void
  onSelectNode: (key: string) => void
}

export function useContextMenu(options: UseContextMenuOptions) {
  const { onFolderCommand, onConfigCommand, onSelectNode } = options

  const folderDropdownRef = ref()
  const configDropdownRef = ref()

  const contextMenuData = ref<TreeNode | null>(null)
  const contextMenuPosition = ref({ x: 0, y: 0 })

  /** 虚拟锚点：getBoundingClientRect 返回鼠标位置 */
  const contextMenuAnchor = {
    getBoundingClientRect: () => DOMRect.fromRect({
      x: contextMenuPosition.value.x,
      y: contextMenuPosition.value.y,
      width: 0,
      height: 0,
    }),
  }

  const handleContextMenu = (event: MouseEvent, type: 'folder' | 'config', data: TreeNode) => {
    event.preventDefault()
    contextMenuPosition.value = { x: event.clientX, y: event.clientY }
    contextMenuData.value = data
    onSelectNode(data.__key)

    if (type === 'folder') {
      configDropdownRef.value?.handleClose()
      folderDropdownRef.value?.handleOpen()
    } else {
      folderDropdownRef.value?.handleClose()
      configDropdownRef.value?.handleOpen()
    }
  }

  const onFolderMenuCommand = (cmd: string) => {
    if (contextMenuData.value) onFolderCommand(cmd, contextMenuData.value)
  }

  const onConfigMenuCommand = (cmd: string) => {
    if (contextMenuData.value) onConfigCommand(cmd, contextMenuData.value)
  }

  return {
    folderDropdownRef,
    configDropdownRef,
    contextMenuAnchor,
    handleContextMenu,
    onFolderMenuCommand,
    onConfigMenuCommand,
  }
}

// ── 重命名 / 删除弹窗工具函数 ────────────────────────────────────────

export function promptRenameFolder(data: TreeNode, onConfirm: (newName: string) => void) {
  ElMessageBox.prompt('请输入新的文件夹名称', '重命名文件夹', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValue: data.name,
    inputValidator: (val) => {
      if (!val || !val.trim()) return '文件夹名称不能为空'
      return true
    },
  }).then(({ value }) => {
    const newName = value.trim()
    if (newName && newName !== data.name) onConfirm(newName)
  }).catch(() => {})
}

export function promptRenameConfig(data: TreeNode, onConfirm: (newName: string) => void) {
  ElMessageBox.prompt('请输入新的配置名称', '重命名配置', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValue: data.name,
    inputValidator: (val) => {
      if (!val || !val.trim()) return '配置名称不能为空'
      return true
    },
  }).then(({ value }) => {
    const newName = value.trim()
    if (newName && newName !== data.name) onConfirm(newName)
  }).catch(() => {})
}

export function confirmDeleteFolder(data: TreeNode, onConfirm: () => void) {
  ElMessageBox.confirm(
    `此操作将同时删除文件夹内的所有配置，确定要删除文件夹"${data.name}"吗？`,
    '删除文件夹',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger',
    }
  ).then(onConfirm).catch(() => {})
}

export function confirmDeleteConfig(data: TreeNode, onConfirm: () => void) {
  ElMessageBox.confirm(
    `确定要删除配置"${data.name}"吗？`,
    '删除配置',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger',
    }
  ).then(onConfirm).catch(() => {})
}
