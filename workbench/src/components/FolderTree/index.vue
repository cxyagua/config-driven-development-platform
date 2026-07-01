<template>
  <div class="folder-tree">
    <!-- ── 顶部标题栏 ── -->
    <FolderTreeHeader
      :spaces="spaces"
      :current-space-id="currentSpaceId"
      :selected-folder-name="selectedFolderDisplayName"
      :readonly="isReadonlySpace"
      @switch-space="handleSwitchSpace"
      @command="handleHeaderCommand"
    />

    <!-- ── 搜索 + 树内容 ── -->
    <FolderTreeContent
      ref="contentRef"
      v-model:search-keyword="searchKeyword"
      :filtered-tree="filteredTree"
      :selected-node-key="selectedNodeKey"
      :has-active-filter="hasActiveFilter"
      :default-expanded-keys="defaultExpandedKeys"
      :allow-drag="allowDrag"
      :allow-drop="allowDrop"
      @node-click="handleNodeClick"
      @node-drop="handleDrop"
      @contextmenu="handleContextMenu"
      @deselect="handleDeselect"
    />

    <!-- ── 底部工具栏 ── -->
    <FolderTreeFooter
      @expand-all="handleExpandAll"
      @collapse-all="handleCollapseAll"
    />

    <!-- ── 虚拟右键菜单：文件夹节点 ── -->
    <el-dropdown
      ref="folderDropdownRef"
      :virtual-ref="contextMenuAnchor"
      :show-arrow="false"
      virtual-triggering
      trigger="contextmenu"
      placement="bottom-start"
      popper-class="context-menu--no-animation"
      :popper-options="{ modifiers: [{ name: 'offset', options: { offset: [0, 0] } }] }"
      @command="onFolderMenuCommand"
    >
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item v-if="!isReadonlySpace" command="create-config">
            <el-icon><Document /></el-icon>
            新建配置
          </el-dropdown-item>
          <el-dropdown-item v-if="!isReadonlySpace" command="create-folder">
            <el-icon><Folder /></el-icon>
            新建文件夹
          </el-dropdown-item>
          <el-dropdown-item v-if="!isReadonlySpace" command="rename" divided>
            <el-icon><Edit /></el-icon>
            重命名
          </el-dropdown-item>
          <el-dropdown-item command="sync" :divided="isReadonlySpace">
            <el-icon><Refresh /></el-icon>
            同步到...
          </el-dropdown-item>
          <el-dropdown-item v-if="!isReadonlySpace" command="delete" divided danger>
            <el-icon><Delete /></el-icon>
            删除
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- ── 虚拟右键菜单：配置节点 ── -->
    <el-dropdown
      ref="configDropdownRef"
      :virtual-ref="contextMenuAnchor"
      :show-arrow="false"
      virtual-triggering
      trigger="contextmenu"
      placement="bottom-start"
      popper-class="context-menu--no-animation"
      :popper-options="{ modifiers: [{ name: 'offset', options: { offset: [0, 0] } }] }"
      @command="onConfigMenuCommand"
    >
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item v-if="!isReadonlySpace" command="rename">
            <el-icon><Edit /></el-icon>
            重命名
          </el-dropdown-item>
          <el-dropdown-item command="sync" :divided="!isReadonlySpace">
            <el-icon><Refresh /></el-icon>
            同步到...
          </el-dropdown-item>
          <el-dropdown-item v-if="!isReadonlySpace" command="delete" divided danger>
            <el-icon><Delete /></el-icon>
            删除
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- ── 同步对话框 ── -->
    <el-dialog
      v-model="syncDialog.visible"
      :title="`同步${syncDialog.nodeType === 'folder' ? '文件夹' : '配置'}`"
      width="480"
      :close-on-click-modal="false"
      append-to-body
      @closed="resetSyncDialog"
    >
      <el-form label-width="90px">
        <el-form-item label="同步到">
          <el-select
            v-model="syncDialog.targetSpaceId"
            placeholder="请选择目标空间"
            style="width: 100%"
          >
            <el-option
              v-for="s in syncableSpaces"
              :key="s.id"
              :label="s.name"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <el-alert
        type="warning"
        :title="`即将同步「${syncDialog.nodeName}」到「${syncTargetSpaceName}」，如已存在将被覆盖`"
        :closable="false"
        show-icon
      />

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="syncDialog.visible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="syncDialog.loading"
            :disabled="!syncDialog.targetSpaceId"
            @click="submitSync"
          >
            确定同步
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- ── 新建配置对话框 ── -->
    <el-dialog
      v-model="createConfigDialog.visible"
      title="新建配置"
      width="480"
      :close-on-click-modal="false"
      append-to-body
      @closed="resetCreateConfigForm"
    >
      <el-form
        ref="createConfigFormRef"
        :model="createConfigForm"
        :rules="createConfigRules"
        label-width="90px"
        @submit.prevent
      >
        <el-form-item label="配置名称" prop="name">
          <el-input
            v-model="createConfigForm.name"
            placeholder="请输入配置名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="配置 ID" prop="configId">
          <el-input
            v-model="createConfigForm.configId"
            placeholder="英文+数字+连字符，如 my-filter"
            clearable
          />
        </el-form-item>
        <el-form-item label="组件类型" prop="componentType">
          <el-select
            v-model="createConfigForm.componentType"
            placeholder="请选择组件类型"
            style="width: 100%"
          >
            <el-option label="BiFilter（筛选器）" value="BiFilter" />
            <el-option label="BiTable（数据表格）" value="BiTable" />
            <el-option label="BiChart（图表）" value="BiChart" />
            <el-option label="Others（其他）" value="others" />
          </el-select>
        </el-form-item>
        <el-form-item label="所在文件夹">
          <span class="create-config-folder">
            {{ createConfigDialog.folderId !== 0
              ? (findFolderName(mixedTree, createConfigDialog.folderId) ?? `ID: ${createConfigDialog.folderId}`)
              : '（根目录）' }}
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="createConfigDialog.visible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="createConfigDialog.loading"
            @click="submitCreateConfig"
          >
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Edit, Delete, Folder, Document, Refresh } from '@element-plus/icons-vue'

import FolderTreeHeader from './FolderTreeHeader.vue'
import FolderTreeContent from './FolderTreeContent.vue'
import FolderTreeFooter from './FolderTreeFooter.vue'

import { useFolderTree } from './useFolderTree'
import { useTreeDrag } from './useTreeDrag'
import { useTreeData } from './useTreeData'
import { useSync } from './useSync'
import {
  useContextMenu,
  promptRenameFolder,
  promptRenameConfig,
  confirmDeleteFolder,
  confirmDeleteConfig,
} from './useContextMenu'

import type {
  Node,
  TreeNode,
  DragNode,
  DropType,
} from './types'

// ── Props & Emits ─────────────────────────────────────────────────

interface Props {
  /** 当前高亮的配置 ID（外部切换时同步树的选中状态） */
  selectedConfigId?: string | null
}

interface Emits {
  (e: 'select-config', configId: string): void
  (e: 'config-deleted', configId: string): void
}

const props = withDefaults(defineProps<Props>(), {
  selectedConfigId: null,
})

const emit = defineEmits<Emits>()

// ── 数据层（完全内化） ────────────────────────────────────────────
const {
  spaces,
  currentSpaceId,
  tree,
  treeLoading,
  isReadonlySpace,
  init,
  handleSwitchSpace,
  handleCreateFolder,
  handleRenameFolder,
  handleDeleteFolder,
  handleMoveFolder,
  handleCreateConfig,
  handleRenameConfig,
  handleDeleteConfig,
  handleMoveConfig,
  createConfigDialog,
  createConfigFormRef,
  createConfigForm,
  createConfigRules,
  resetCreateConfigForm,
  submitCreateConfig,
  findConfigNode,
  updateNodeComponentType,
} = useTreeData({
  onConfigCreated: (configId) => {
    // 自动选中新建的配置
    selectedNodeKey.value = `config::${configId}`
    emit('select-config', configId)
  },
  onConfigDeleted: (configId) => {
    emit('config-deleted', configId)
  },
})

onMounted(() => init())

// ── 同步 ──────────────────────────────────────────────────────────
const {
  syncDialog,
  syncableSpaces,
  syncTargetSpaceName,
  openSyncDialog,
  resetSyncDialog,
  submitSync,
} = useSync({ spaces, currentSpaceId })

// ── 外部切换配置时同步树的高亮选中节点 ───────────────────────────
watch(
  () => props.selectedConfigId,
  (configId) => {
    if (configId) {
      selectedNodeKey.value = `config::${configId}`
    }
  },
)

// ── 树数据 & 搜索 ─────────────────────────────────────────────────
const {
  searchKeyword,
  hasActiveFilter,
  selectedNodeKey,
  defaultExpandedKeys,
  mixedTree,
  filteredTree,
} = useFolderTree({
  getTree: () => tree.value,
})

// ── 拖拽 ──────────────────────────────────────────────────────────
const { allowDrag: _allowDrag, allowDrop, handleDrop: _handleDrop } = useTreeDrag({
  onMoveFolder: (src, tgt) => handleMoveFolder(src, tgt as number),
  onMoveConfig: (id, folderId) => handleMoveConfig(id, folderId),
})

// 只读空间时禁止拖拽
const allowDrag = (node: DragNode) => {
  if (isReadonlySpace.value) return false
  return _allowDrag(node)
}

const handleDrop = (draggingNode: DragNode, dropNode: DragNode, dropType: DropType) => {
  _handleDrop(draggingNode, dropNode, dropType)
}

// ── 右键菜单 ─────────────────────────────────────────────────────
const {
  folderDropdownRef,
  configDropdownRef,
  contextMenuAnchor,
  handleContextMenu: _handleContextMenu,
  onFolderMenuCommand,
  onConfigMenuCommand,
} = useContextMenu({
  onSelectNode: (key) => { selectedNodeKey.value = key },
  onFolderCommand: handleFolderCommand,
  onConfigCommand: handleConfigCommand,
})

// 只读空间时仍允许弹出右键菜单（可执行同步），但写操作菜单项会被隐藏
const handleContextMenu = (event: MouseEvent, type: 'folder' | 'config', data: TreeNode) => {
  _handleContextMenu(event, type, data)
}

// ── 节点命令处理 ──────────────────────────────────────────────────

function handleFolderCommand(cmd: string, data: TreeNode) {
  if (cmd === 'create-config') {
    handleCreateConfig(data.id ?? 0)
  } else if (cmd === 'create-folder') {
    handleCreateFolder(data.id ?? 0)
  } else if (cmd === 'rename') {
    promptRenameFolder(data, (newName) => handleRenameFolder(data.id!, newName))
  } else if (cmd === 'sync') {
    openSyncDialog('folder', data.id!, data.name)
  } else if (cmd === 'delete') {
    confirmDeleteFolder(data, () => handleDeleteFolder(data.id!, props.selectedConfigId ?? null))
  }
}

function handleConfigCommand(cmd: string, data: TreeNode) {
  if (cmd === 'rename') {
    promptRenameConfig(data, (newName) => handleRenameConfig(data.configId!, newName))
  } else if (cmd === 'sync') {
    openSyncDialog('config', data.configId!, data.name)
  } else if (cmd === 'delete') {
    confirmDeleteConfig(data, () => handleDeleteConfig(data.configId!))
  }
}

// ── 节点点击 ─────────────────────────────────────────────────────
const handleNodeClick = (data: TreeNode) => {
  if (data.nodeType === 'folder') {
    selectedNodeKey.value = `folder::${data.id}`
  } else {
    selectedNodeKey.value = `config::${data.configId}`
    emit('select-config', data.configId!)
  }
}

// ── 点击空白区域取消选中 ──────────────────────────────────────────
const handleDeselect = () => {
  selectedNodeKey.value = null
}

/**
 * 当前选中节点对应的"目标文件夹 ID"：
 *   - 选中文件夹 → 该文件夹 ID（在其内部新建）
 *   - 选中配置   → 该配置所在的文件夹 ID（同级新建）
 *   - 未选中     → 0（根目录）
 */
const selectedFolderPath = computed(() => {
  const key = selectedNodeKey.value
  if (!key) return 0
  if (key.startsWith('folder::')) {
    return Number(key.replace('folder::', ''))
  }
  if (key.startsWith('config::')) {
    const configId = key.replace('config::', '')
    return findConfigFolderId(mixedTree.value, configId)
  }
  return 0
})

/** 递归在树中找 config 节点的父文件夹 ID */
function findConfigFolderId(nodes: TreeNode[], configId: string): number {
  for (const n of nodes) {
    if (n.nodeType === 'folder') {
      if (n.children?.some((c) => c.nodeType === 'config' && c.configId === configId)) {
        return n.id ?? 0
      }
      const found = findConfigFolderId(n.children ?? [], configId)
      if (found !== 0) return found
    }
  }
  return 0
}

/** 当前选中的文件夹名称，用于 Header 下拉菜单提示 */
const selectedFolderDisplayName = computed(() => {
  const folderId = selectedFolderPath.value
  if (!folderId) return null
  return findFolderName(mixedTree.value, folderId)
})

/** 递归在树中找文件夹名称 */
function findFolderName(nodes: TreeNode[], id: number): string | null {
  for (const n of nodes) {
    if (n.nodeType === 'folder') {
      if (n.id === id) return n.name
      const found = findFolderName(n.children ?? [], id)
      if (found !== null) return found
    }
  }
  return null
}

const handleHeaderCommand = (command: string) => {
  if (command === 'folder') {
    handleCreateFolder(selectedFolderPath.value)
  } else {
    handleCreateConfig(selectedFolderPath.value)
  }
}

// ── 展开 / 收起全部 ──────────────────────────────────────────────
const contentRef = ref()

const handleExpandAll = () => {
  const treeEl = contentRef.value?.treeRef
  if (!treeEl) return
  const expand = (nodes: TreeNode[]) => {
    nodes.forEach((n) => {
      treeEl.store?.nodesMap?.[n.__key]?.expand?.()
      if (n.children?.length) expand(n.children)
    })
  }
  expand(mixedTree.value)
}

const handleCollapseAll = () => {
  const treeEl = contentRef.value?.treeRef
  if (!treeEl) return
  const collapse = (nodes: TreeNode[]) => {
    nodes.forEach((n) => {
      treeEl.store?.nodesMap?.[n.__key]?.collapse?.()
      if (n.children?.length) collapse(n.children)
    })
  }
  collapse(mixedTree.value)
}

// ── Expose：供 ConfigCenter 通过 ref 访问必要状态 ─────────────────
defineExpose({
  /** 当前树数据（只读引用） */
  tree,
  /** 当前空间 ID */
  currentSpaceId,
  /** 当前空间是否为只读模式 */
  isReadonlySpace,
  /** 在树中按 configId 查找节点（ConfigCenter 更新 componentType 时使用） */
  findConfigNode: (configId: string): Node | null => findConfigNode(tree.value, configId),
  /** 原地更新节点 componentType，避免全量刷树 */
  updateNodeComponentType,
  /** 空间列表（供 ConfigCenter header 中 space-name 显示用） */
  spaces,
})
</script>

<style lang="less" scoped>
.folder-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
}

// 右键菜单删除项高亮为红色
:deep(.el-dropdown-menu .el-dropdown-menu__item--danger) {
  color: var(--el-color-danger);

  .el-icon {
    color: var(--el-color-danger);
  }

  &:hover {
    background-color: #fff2f0;
  }
}

.create-config-folder {
  font-size: 13px;
  color: #6b7280;
  background: #f3f4f6;
  border-radius: 4px;
  padding: 2px 8px;
  font-family: 'JetBrains Mono', monospace;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>

<!-- 右键菜单弹出动画关闭（popper teleport 到 body，必须用全局样式）-->
<style lang="less">
.context-menu--no-animation {
  transition: none !important;
  animation: none !important;

  .el-dropdown__popper,
  .el-popper,
  .el-tooltip__popper {
    transition: none !important;
    animation: none !important;
  }
}
</style>