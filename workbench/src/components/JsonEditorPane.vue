<template>
  <div class="json-editor-pane">
    <!-- 面板 header -->
    <div class="pane-header">
      <span class="pane-title">JSON 配置</span>
      <div class="pane-header__actions">
        <el-button
          link
          size="small"
          :loading="downloading"
          @click="handleDownload"
        >
          <el-icon><Download /></el-icon>
          <span>下载配置</span>
        </el-button>
      </div>
    </div>

    <!-- JSON 编辑器主体 -->
    <div class="pane-body">
      <!-- 只读模式遮罩提示 -->
      <div v-if="props.readonly" class="pane-readonly-overlay">
        <span>⚠ 当前空间为只读模式，不可编辑</span>
      </div>
      <JsonEditorVue
        v-model="localContent"
        class="json-editor-instance"
        mode="text"
        :navigation-bar="false"
        :status-bar="true"
        :ask-to-format="false"
        :read-only="props.readonly"
        :on-render-menu="filterModeMenu"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import JsonEditorVue from 'vue3-ts-jsoneditor'
import { Download } from '@element-plus/icons-vue'
import { ElNotification } from 'element-plus'

// ── Props ─────────────────────────────────────
const props = defineProps<{
  /** 当前编辑的 JSON 内容（由父组件传入） */
  modelValue: unknown
  /** 当前打开的配置文件名称 */
  configName?: string
  /** 当前空间名称 */
  spaceName?: string
  /** 是否正在保存 */
  saving?: boolean
  /** 是否只读模式（只读时禁止编辑） */
  readonly?: boolean
}>()

// ── Emits ─────────────────────────────────────
const emit = defineEmits<{
  /** 内容变更（实时双向绑定） */
  (e: 'update:modelValue', value: unknown): void
  /** 用户点击"保存"按钮，携带当前编辑内容 */
  (e: 'save', value: unknown): void
}>()

// ── 本地副本（用于脏检测） ──────────────────────
const localContent = ref<unknown>(props.modelValue ?? {})
/** 初始值快照，用于脏检测 */
const originalContent = ref<string>(JSON.stringify(props.modelValue ?? {}))
/** 标记本次 props.modelValue 变化是由自身 emit 引起的回流，非外部切换 */
let isSelfUpdate = false

/** 内容是否已被修改（脏状态） */
const isDirty = computed(() => {
  try {
    return JSON.stringify(localContent.value) !== originalContent.value
  } catch {
    return false
  }
})

// ── 监听 props.modelValue 变化（外部切换配置）──
watch(
  () => props.modelValue,
  (val) => {
    if (isSelfUpdate) {
      // 本次变化是自身 emit 回流，不重置快照，否则 isDirty 永远为 false
      isSelfUpdate = false
      return
    }
    // 外部切换了配置，同步本地内容并刷新快照
    localContent.value = val ?? {}
    originalContent.value = JSON.stringify(val ?? {})
  },
)

// ── 监听本地编辑，同步给父组件 ─────────────────
watch(localContent, (val) => {
  isSelfUpdate = true
  emit('update:modelValue', val)
})

// ── 保存 ─────────────────────────────────────
const handleSave = () => {
  emit('save', localContent.value)
}

// ── 重置 ─────────────────────────────────────
const handleReset = () => {
  try {
    localContent.value = JSON.parse(originalContent.value)
  } catch {
    localContent.value = {}
  }
}

// ── 过滤 JSON 编辑器顶部模式切换按钮 ─────────
function filterModeMenu(items: any[]) {
  return items.slice(4)
}

// ── 下载配置 ──────────────────────────────────
const downloading = ref(false)

const handleDownload = async () => {
  if (downloading.value) return
  downloading.value = true
  try {
    const json = JSON.stringify(localContent.value, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const configName = props.configName || 'config'
    const spaceName = props.spaceName || 'unknown'
    // TODO: 版本号暂用时间戳代替，后续迭代替换为真实版本号
    const version = Date.now()
    a.download = `${configName}_${spaceName}_${version}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElNotification({
      type: 'success',
      title: '下载成功',
      message: '请在下载目录中查看文件',
    })
  } finally {
    downloading.value = false
  }
}

// ── 向父组件暴露接口 ──────────────────────────
defineExpose({
  isDirty,
  handleReset,
  handleSave,
  handleDownload,
})
</script>

<style lang="less" scoped>
.json-editor-pane {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  overflow: hidden;
}

/* ── 面板 header ── */
.pane-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 40px;
  padding: 0 16px;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.pane-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.pane-header__meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pane-header__actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ── 编辑器主体 ── */
.pane-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;

  // 覆盖 jsoneditor 内部默认样式，撑满容器
  :deep(.jse-main) {
    flex: 1;
    min-height: 0;
  }
}

/* json editor 撑满父容器 */
.json-editor-instance {
  flex: 1;
  min-height: 0;
  height: 100%;
  border: none;
  border-radius: 0;
}

/* 只读遮罩提示条 */
.pane-readonly-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 2;
  background-color: #fffbeb;
  border-bottom: 1px solid #fcd34d;
  color: #92400e;
  font-size: 12px;
  text-align: center;
  padding: 6px 16px;
  pointer-events: none;
}
</style>