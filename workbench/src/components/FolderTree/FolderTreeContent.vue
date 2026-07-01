<template>
  <!-- ── 搜索栏 ── -->
  <div class="folder-tree__filter-bar">
    <el-input
      :model-value="searchKeyword"
      placeholder="搜索名称"
      clearable
      class="folder-tree__search-input"
      @update:model-value="(v: string) => emit('update:searchKeyword', v)"
    >
      <template #prefix>
        <el-icon style="font-size: 14px"><Search /></el-icon>
      </template>
    </el-input>
  </div>

  <!-- ── 树内容 ── -->
  <div class="folder-tree__content" @contextmenu.prevent @click.self="emit('deselect')">
    <el-tree
      ref="treeRef"
      :key="hasActiveFilter ? 'filtered' : 'normal'"
      :data="filteredTree"
      :props="treeProps"
      node-key="__key"
      :current-node-key="selectedNodeKey"
      highlight-current
      :default-expand-all="hasActiveFilter"
      :default-expanded-keys="defaultExpandedKeys"
      :expand-on-click-node="false"
      :indent="10"
      draggable
      :allow-drag="allowDrag"
      :allow-drop="allowDrop"
      class="folder-tree__tree"
      @node-click="handleNodeClick"
      @node-drop="handleDrop"
    >
      <template #default="{ node, data }">
        <!-- ── 文件夹节点 ── -->
        <div
          v-if="data.nodeType === 'folder'"
          class="tree-node tree-node--folder"
          @contextmenu.stop="emit('contextmenu', $event, 'folder', data)"
        >
          <el-icon class="tree-node__icon tree-node__icon--folder">
            <FolderOpened v-if="node.expanded" />
            <Folder v-else />
          </el-icon>
          <span class="tree-node__label">{{ data.name }}</span>
        </div>

        <!-- ── 配置文件节点 ── -->
        <div
          v-else
          class="tree-node tree-node--config"
          @contextmenu.stop="emit('contextmenu', $event, 'config', data)"
        >
          <el-icon class="tree-node__icon tree-node__icon--config">
            <Document />
          </el-icon>
          <span class="tree-node__label tree-node__label--config">{{ data.name }}</span>
          <span
            class="tree-node__type-tag"
            :class="`tree-node__type-tag--${(data.componentType ?? 'others').toLowerCase()}`"
          >{{ data.componentType === 'others' ? '其他' : data.componentType }}</span>
        </div>
      </template>

      <template #empty>
        <div class="folder-tree__empty">
          <el-icon><Plus /></el-icon>
          <p>暂无配置，点击右上角 + 创建</p>
        </div>
      </template>
    </el-tree>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus, Folder, FolderOpened, Document, Search } from '@element-plus/icons-vue'
import type { TreeNode, DragNode, AllowDropType, DropType } from './types'

interface Props {
  filteredTree: TreeNode[]
  selectedNodeKey: string | null
  hasActiveFilter: boolean
  defaultExpandedKeys: string[]
  allowDrag: (node: DragNode) => boolean
  allowDrop: (draggingNode: DragNode, dropNode: DragNode, type: AllowDropType) => boolean
  searchKeyword: string
}

interface Emits {
  (e: 'node-click', data: TreeNode): void
  (e: 'node-drop', draggingNode: DragNode, dropNode: DragNode, dropType: DropType): void
  (e: 'contextmenu', event: MouseEvent, type: 'folder' | 'config', data: TreeNode): void
  (e: 'update:searchKeyword', value: string): void
  (e: 'deselect'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const treeRef = ref()

const treeProps = {
  children: 'children',
  label: 'name',
}

const handleNodeClick = (data: TreeNode) => {
  emit('node-click', data)
}

const handleDrop = (draggingNode: DragNode, dropNode: DragNode, dropType: DropType) => {
  emit('node-drop', draggingNode, dropNode, dropType)
}

/** 暴露 treeRef 给父组件用于展开/收起 */
defineExpose({ treeRef })
</script>

<style lang="less" scoped>
// ── 搜索栏 ──
.folder-tree__filter-bar {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  flex-shrink: 0;
  height: 40px;
  :deep(.el-input) {
    .el-input__wrapper {
      background: #f5f5f5;
      border: none;
      box-shadow: none;
      width: 100%;
      padding: 4px 8px;
    }
    .el-input__inner {
      line-height: 24px;
      height: 24px;
    }
  }
}

.folder-tree__search-input {
  flex: 1;
  min-width: 0;
}

// ── 滚动内容区 ──
.folder-tree__content {
  flex: 1;
  overflow-y: auto;
  padding: 6px 10px;

  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: #d1d5db;
    border-radius: 2px;
  }
}

// ── 空状态 ──
.folder-tree__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 16px;
  color: #9ca3af;
  font-size: 12px;

  .el-icon {
    font-size: 28px;
  }
  p { margin: 0; }
}

// ── el-tree 全局覆盖 ──
.folder-tree__tree {
  :deep(.el-tree-node__content) {
    height: 30px;
    border-radius: 0;
    padding-right: 4px;

    &:hover {
      background-color: #f3f4f6;

      .tree-node__actions {
        opacity: 1;
      }
      .tree-node__count {
        display: none;
      }
    }
  }

  :deep(.el-tree-node.is-current > .el-tree-node__content) {
    background-color: #eff6ff;
    color: var(--el-color-primary);
  }

  :deep(.el-tree-node__expand-icon) {
    font-size: 12px;
    color: #9ca3af;
  }

  :deep(.el-tree-node__expand-icon.is-leaf) {
    visibility: hidden;
    margin-right: -10px;
  }

  :deep(.el-tree-node.is-dragging > .el-tree-node__content) {
    opacity: 0.45;
    background-color: #f3f4f6 !important;
  }

  :deep(.el-tree-node.is-drop-inner > .el-tree-node__content) {
    background-color: #dbeafe !important;
    outline: 1px dashed var(--el-color-primary);
    outline-offset: -1px;
  }
}

// ── 通用节点行 ──
.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 5px;
  overflow: hidden;
  min-width: 0;
  * {
    line-height: 1;
  }
}

.tree-node__icon {
  font-size: 14px;
  flex-shrink: 0;

  &--folder {
    color: #f59e0b;
  }
  &--config {
    color: #60a5fa;
  }
}

.tree-node__label {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #374151;

  &--config {
    color: #4b5563;
    font-size: 12px;
  }
}

.tree-node__count {
  font-size: 11px;
  color: #9ca3af;
  background: #f3f4f6;
  padding: 1px 5px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  flex-shrink: 0;
}

.tree-node__actions {
  display: flex;
  gap: 1px;
  opacity: 0;
  transition: opacity 0.15s;
  flex-shrink: 0;
}

.tree-node__type-tag {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 3px;
  flex-shrink: 0;
  font-weight: 500;

  &--bifilter {
    background: #dbeafe;
    color: #2563eb;
  }
  &--bitable {
    background: #d1fae5;
    color: #059669;
  }
  &--bichart {
    background: #fef3c7;
    color: #d97706;
  }
  &--others {
    background: #f3f4f6;
    color: #6b7280;
  }
}
</style>
