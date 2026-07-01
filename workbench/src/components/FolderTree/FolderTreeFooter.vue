<template>
  <!-- ── 底部工具栏 ── -->
  <div class="folder-tree__footer">
    <div class="folder-tree__footer-left">
      <el-tooltip content="展开全部" effect="light" placement="top">
        <el-button link size="small" @click="emit('expand-all')">
          <el-icon><FolderOpened /></el-icon>
        </el-button>
      </el-tooltip>
      <el-tooltip content="收起全部" effect="light" placement="top">
        <el-button link size="small" @click="emit('collapse-all')">
          <el-icon><Folder /></el-icon>
        </el-button>
      </el-tooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Folder, FolderOpened } from '@element-plus/icons-vue'

interface Emits {
  (e: 'expand-all'): void
  (e: 'collapse-all'): void
}

const emit = defineEmits<Emits>()
</script>

<style lang="less" scoped>
.folder-tree__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2px;
  padding: 6px 10px;
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;

  .el-button {
    color: #6b7280;
    &:hover {
      color: var(--el-color-primary);
      background-color: #f0f4ff;
    }
  }
}

.folder-tree__footer-left {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
