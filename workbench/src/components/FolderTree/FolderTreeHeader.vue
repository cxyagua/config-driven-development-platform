<template>
  <div class="folder-tree__header">
    <!-- 空间切换下拉 -->
    <el-dropdown
      trigger="click"
      class="folder-tree__space-switcher"
      @command="(id: string) => emit('switch-space', id)"
    >
      <div class="folder-tree__space-trigger">
        <span class="folder-tree__space-name">{{ currentSpaceName }}</span>
        <!-- 只读标识 -->
        <span v-if="props.readonly" class="folder-tree__readonly-badge">只读</span>
        <el-icon class="folder-tree__space-arrow" size="18"><ArrowDown /></el-icon>
      </div>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item
            v-for="space in spaces"
            :key="space.id"
            :command="space.id"
            :class="{ 'is-active-space': space.id === currentSpaceId }"
          >
            {{ space.name }}
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <div class="folder-tree__header-actions">
      <!-- 新建 dropdown：只读空间时隐藏 -->
      <el-dropdown v-if="!props.readonly" trigger="click" @command="(cmd: string) => emit('command', cmd)">
        <el-button type="primary" size="small" circle>
          <el-icon><Plus /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="folder">
              <el-icon><Folder /></el-icon>
              <span>新建文件夹</span>
              <span v-if="selectedFolderName" class="header-menu__context-hint">在「{{ selectedFolderName }}」中</span>
            </el-dropdown-item>
            <el-dropdown-item command="config">
              <el-icon><Document /></el-icon>
              <span>新建配置</span>
              <span v-if="selectedFolderName" class="header-menu__context-hint">在「{{ selectedFolderName }}」中</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Plus, Folder, Document, ArrowDown } from '@element-plus/icons-vue'
import type { SpaceItem } from './types'

interface Props {
  spaces: SpaceItem[]
  currentSpaceId: string | null
  /** 当前选中的文件夹名称（用于显示新建目标提示） */
  selectedFolderName?: string | null
  /** 当前空间是否只读，只读时隐藏新建按钮 */
  readonly?: boolean
}

interface Emits {
  (e: 'switch-space', spaceId: string): void
  (e: 'command', cmd: string): void
}

const props = withDefaults(defineProps<Props>(), {
  spaces: () => [],
  currentSpaceId: null,
  selectedFolderName: null,
  readonly: false,
})

const emit = defineEmits<Emits>()

const currentSpaceName = computed(() =>
  props.spaces.find((s) => s.id === props.currentSpaceId)?.name ?? '请选择空间'
)
</script>

<style lang="less" scoped>
.folder-tree__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
  height: 50px;
  box-sizing: border-box;
  padding: 0 12px;
}

.folder-tree__space-switcher {
  flex: 1;
  min-width: 0;
}

.folder-tree__space-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  cursor: pointer;
  max-width: 100%;
  height: 23px;
  padding: 0px 6px;
  border-radius: 6px;
  transition: background-color 0.15s;
  * {
    line-height: 1;
  }
  &:hover {
    background-color: #f3f4f6;
  }
}

.folder-tree__space-name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.folder-tree__space-arrow {
  font-size: 12px;
  color: #9ca3af;
  flex-shrink: 0;
  transition: transform 0.2s;
}

:deep(.el-dropdown-menu__item.is-active-space) {
  color: var(--el-color-primary);
  font-weight: 600;
}

.folder-tree__header-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}

.header-menu__context-hint {
  margin-left: 6px;
  font-size: 11px;
  color: #9ca3af;
  white-space: nowrap;
}

.folder-tree__readonly-badge {
  font-size: 12px;
  color: #9ca3af;
  background-color: #f3f4f6;
  border-radius: 4px;
  padding: 2px 4px;
  margin-left: 4px;
  font-weight: 500;
}
</style>