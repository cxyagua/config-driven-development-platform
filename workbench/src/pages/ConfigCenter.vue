<template>
  <!-- 整页：左侧文件夹树 + 右侧工作台，全高无滚动 -->
  <div class="workbench-page">

    <!-- ===== 左侧：文件夹树 ===== -->
    <aside class="workbench-sidebar" :class="{ 'is-collapsed': sidebarCollapsed }">
      <FolderTree
        ref="folderTreeRef"
        :selected-config-id="activeConfigId"
        @select-config="handleSelectConfig"
        @config-deleted="handleConfigDeleted"
      />
    </aside>

    <!-- ===== 右侧：顶部 header + 工作台内容 ===== -->
    <div class="workbench-main">

      <!-- 顶部固定 header -->
      <div class="workbench-header">
        <!-- 侧边栏折叠/展开按钮：始终显示，统一控制 -->
        <el-button
          class="sidebar-toggle-btn"
          link
          size="small"
          @click="sidebarCollapsed = !sidebarCollapsed"
        >
          <el-icon size="16">
            <FolderOpened v-if="sidebarCollapsed" />
            <Folder v-else />
          </el-icon>
        </el-button>

        <div class="workbench-header__title">
          <span v-if="activeConfig" class="workbench-header__config-name">
            {{ activeConfig.name }}
          </span>
          <span v-if="activeConfig" class="workbench-header__config-badge">
            {{ activeConfig.configId }}
          </span>
          <!-- 组件类型切换下拉：只读时禁用 -->
          <el-select
            v-if="activeConfig"
            :model-value="activeConfig.componentType || 'others'"
            size="small"
            class="workbench-header__type-select"
            :loading="typeChanging"
            :disabled="isReadonlySpace"
            @change="handleChangeComponentType"
          >
            <el-option label="BiFilter（筛选器）" value="BiFilter" />
            <el-option label="BiTable（数据表格）" value="BiTable" />
            <el-option label="BiChart（图表）" value="BiChart" />
            <el-option label="Others（其他）" value="others" />
          </el-select>
          <!-- 只读空间提示 -->
          <span v-if="activeConfig && isReadonlySpace" class="workbench-header__readonly-tip">
            <el-icon size="13" style="color:#f59e0b; vertical-align: middle;">
              <Warning />
            </el-icon>
            只读模式
          </span>
          <span v-if="!activeConfig" class="workbench-header__placeholder">
            请从左侧选择或新建配置
          </span>
        </div>
        <div class="workbench-header__actions">
          <!-- 只读空间时隐藏重置/保存按钮 -->
          <template v-if="!isReadonlySpace">
            <!-- 重置：常驻，任何时候都可点击 -->
            <el-button
              plain
              @click="jsonEditorRef?.handleReset()"
            >
              重置
            </el-button>
            <!-- 保存：常驻，有脏数据时可点，否则 disabled -->
            <el-button
              type="primary"
              :loading="saving"
              :disabled="!jsonEditorRef?.isDirty"
              @click="jsonEditorRef?.handleSave()"
            >
              保存
            </el-button>
          </template>
        </div>
      </div>

      <!-- 工作台区域 -->
      <div class="workbench-content">

        <!-- 未选中配置时：空状态提示 -->
        <div v-if="!activeConfig" class="workbench-empty">
          <div class="workbench-empty__icon">
            <img :src="emptySvg" width="64" height="64" alt="" />
          </div>
          <p class="workbench-empty__text">请从左侧选择一个配置表开始编辑</p>
        </div>

        <!-- 已选中配置时：左右分栏 -->
        <div v-else class="workbench-editor-layout">

          <!-- 左侧：预览区（仅三大原子组件才显示） -->
          <PreviewPane
            v-if="isPreviewable"
            :content="activeJsonContent"
            :component-type="activeConfig.componentType"
            class="preview-pane-slot"
          />

          <!-- 可拖拽分隔条（仅预览区存在时显示） -->
          <div
            v-if="isPreviewable"
            class="editor-divider editor-divider--resizable"
            @mousedown="startResize"
          />

          <!-- 右侧：JSON 编辑器（用包装 div 承载宽度，避免组件内部 flex:1 覆盖） -->
          <div
            class="editor-pane-wrapper"
            :style="isPreviewable ? { width: editorWidth + 'px' } : { flex: '1' }"
          >
            <JsonEditorPane
              ref="jsonEditorRef"
              v-model="activeJsonContent"
              :config-name="activeConfig?.name"
              :space-name="folderTreeRef?.spaces.find((s) => s.id === folderTreeRef?.currentSpaceId)?.name"
              :saving="saving"
              :readonly="isReadonlySpace"
              @save="handleSaveConfig"
            />
          </div>

        </div>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { FolderOpened, Folder, Warning } from '@element-plus/icons-vue'
import FolderTree from '@/components/FolderTree'
import JsonEditorPane from '@/components/JsonEditorPane.vue'
import PreviewPane from '@/components/PreviewPane.vue'
import { useActiveConfig } from '@/composables/useActiveConfig'
import { useComponentType } from '@/composables/useComponentType'
import { useEditorResize } from '@/composables/useEditorResize'
import emptySvg from '@/assets/empty.svg'

// ── FolderTree ref（通过 expose 访问内部状态） ────
const folderTreeRef = ref<InstanceType<typeof FolderTree> | null>(null)

// JSON 编辑器 ref
const jsonEditorRef = ref<InstanceType<typeof JsonEditorPane> | null>(null)

// ── 侧边栏折叠状态 ────────────────────────────────
const sidebarCollapsed = ref<boolean>(false)

// ── 活跃配置：选中、加载、保存 ───────────────────
const {
  activeConfigId,
  activeConfig,
  activeJsonContent,
  isPreviewable,
  saving,
  handleSaveConfig,
  handleSelectConfig,
  handleConfigDeleted,
} = useActiveConfig(folderTreeRef)

// ── 组件类型切换 ──────────────────────────────────
const { typeChanging, handleChangeComponentType } = useComponentType(folderTreeRef, activeConfigId)

// ── 编辑器面板可拖拽宽度 ──────────────────────────
const { editorWidth, startResize } = useEditorResize()

// ── 当前空间是否只读 ──────────────────────────────
const isReadonlySpace = computed(() => folderTreeRef.value?.isReadonlySpace ?? false)
</script>

<style lang="less" scoped>
/* ── 整页：左右分栏，占满 app-main 剩余空间 ── */
.workbench-page {
  display: flex;
  height: 100%;
  overflow: hidden;
  background-color: #f5f7fa;
}

/* ── 左侧文件夹树 ── */
.workbench-sidebar {
  width: 260px;
  flex-shrink: 0;
  height: 100%;
  overflow: hidden;
  background-color: #ffffff;
  border-right: 1px solid #e5e7eb;
  transition: transform 0.3s ease, margin-right 0.3s ease;
  transform: translateX(0);
}

.workbench-sidebar.is-collapsed {
  transform: translateX(-100%);
  margin-right: -260px;
}

/* ── 右侧主区域 ── */
.workbench-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  position: relative;
}

/* ── 顶部 header ── */
.workbench-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 50px;
  padding: 0 20px;
  gap: 8px;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
  box-sizing: border-box;
}

.workbench-header__title {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.workbench-header__config-name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.workbench-header__config-badge {
  font-size: 11px;
  color: #6b7280;
  background-color: #f3f4f6;
  padding: 2px 8px;
  border-radius: 10px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  flex-shrink: 0;
  white-space: nowrap;
}

.workbench-header__placeholder {
  font-size: 14px;
  color: #9ca3af;
}

/* ── 顶栏类型下拉 ── */
.workbench-header__type-select {
  width: 160px;
  flex-shrink: 0;
}

.workbench-header__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* ── 折叠时 header 内的展开按钮 ── */
.sidebar-toggle-btn {
  width: 28px;
  height: 28px;
  color: #6b7280;
}

/* ── 工作台内容区 ── */
.workbench-content {
  flex: 1;
  overflow: hidden;
  display: flex;
}

/* ── 空状态 ── */
.workbench-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #9ca3af;
}

.workbench-empty__icon {
  opacity: 0.6;
}

.workbench-empty__text {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* ── 编辑器左右布局 ── */
.workbench-editor-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 预览区自动占满剩余宽度 */
.preview-pane-slot {
  flex: 1;
  min-width: 800px;
  overflow: hidden;
}

/* ── 中间分隔线 ── */
.editor-divider {
  width: 1px;
  background-color: #e5e7eb;
  flex-shrink: 0;
}

/* ── 可拖拽分隔条 ── */
.editor-divider--resizable {
  width: 5px;
  cursor: col-resize;
  user-select: none;
  background-color: #e5e7eb;
  transition: background-color 0.15s ease;
  position: relative;
  flex-shrink: 0;

  &::after {
    content: '';
    position: absolute;
    inset: 0 -3px; /* 扩大热区，方便拖拽 */
  }

  &:hover {
    background-color: #4f86f7;
  }
}

/* ── JSON 编辑器包装容器 ── */
.editor-pane-wrapper {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 350px;
}

/* ── 只读模式提示标签 ── */
.workbench-header__readonly-tip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #f59e0b;
  background-color: #fffbeb;
  border: 1px solid #fcd34d;
  border-radius: 10px;
  padding: 2px 8px;
  flex-shrink: 0;
  white-space: nowrap;
}</style>