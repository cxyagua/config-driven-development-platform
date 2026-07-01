<template>
  <div class="preview-pane">
    <!-- 面板 header -->
    <div class="pane-header">
      <div class="pane-header__meta">
        <span class="pane-title">预览</span>
      </div>
      <div class="pane-header__actions">
        <!-- 画布尺寸控制条 -->
        <div v-if="canPreview" class="canvas-toolbar">
          <!-- 模式下拉：全屏 / 自定义 -->
          <el-select
            v-model="canvasMode"
            size="small"
            class="canvas-toolbar__mode"
          >
            <el-option value="fullscreen" label="全屏" />
            <el-option value="custom" label="自定义" />
          </el-select>

          <!-- 自定义宽高输入（仅自定义模式显示） -->
          <template v-if="canvasMode === 'custom'">
            <span class="canvas-toolbar__divider" />
            <el-input-number
              v-model="canvasWidth"
              size="small"
              :min="100"
              :max="3840"
              :controls="false"
              class="canvas-toolbar__size-input"
            />
            <span class="canvas-toolbar__sep">×</span>
            <el-input-number
              v-model="canvasHeight"
              size="small"
              :min="100"
              :max="2160"
              :controls="false"
              class="canvas-toolbar__size-input"
            />
          </template>

          <span class="canvas-toolbar__divider" />

          <!-- 缩放比例下拉 -->
          <el-select
            v-model="zoomLevel"
            size="small"
            class="canvas-toolbar__zoom"
            >
            <el-option :value="0.5" label="50%" />
            <el-option :value="0.75" label="75%" />
            <el-option :value="1" label="100%" />
            <el-option :value="1.5" label="150%" />
            <el-option :value="2" label="200%" />
          </el-select>
        </div>

        <el-button v-if="canPreview" link size="small" @click="doRefresh">
          <el-icon><Refresh /></el-icon>
          <span>刷新</span>
        </el-button>
      </div>
    </div>

    <!-- 预览主体 -->
    <div class="pane-body">

      <!-- ① 配置 JSON 解析错误 -->
      <div v-if="parseError && canPreview" class="preview-error">
        <el-icon size="20" color="#f87171"><Warning /></el-icon>
        <span>配置解析失败：{{ parseError }}</span>
      </div>

      <!-- ③ 画布容器（全屏 / 自定义 + 缩放居中） -->
      <div v-else class="canvas-viewport">
        <div class="canvas-wrapper" v-if="canPreview">
          <div class="canvas-stage" :style="canvasStageStyle">

            <!-- 组件预览容器 -->
            <div class="preview-content">
              <!-- TODO: 组件预览逻辑 -->
            </div>

          </div>
          <!-- <div class="canvas-hint">注意：预览模式下组件不会发起正式请求，当前展示数据为mock数据。</div> -->
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Refresh, Warning } from '@element-plus/icons-vue'

// ── Props ─────────────────────────────────────────────────────────────────────
const props = defineProps<{
  /** 当前配置的 JSON 内容 */
  content?: unknown
  /** 组件类型，如 BiFilter / BiTable / BiChart */
  componentType?: string | null
}>()

// ── 刷新键（点击刷新时递增，强制重建组件） ────────────────────────────────────
const refreshKey = ref(0)
function doRefresh() { refreshKey.value++ }

// ── 解析 JSON 内容（computed 无副作用）────────────────────────────────────────
const parseError = ref<string | null>(null)
const parsedConfig = computed<Record<string, any>>(() => {
  if (!props.content) return {}
  if (typeof props.content === 'string') {
    try { return JSON.parse(props.content) } catch { return {} }
  }
  return props.content as Record<string, any>
})

// 单独 watch 处理解析错误，避免在 computed 里写 ref（副作用）
watch(() => props.content, (content) => {
  if (typeof content === 'string') {
    try { JSON.parse(content); parseError.value = null }
    catch (e) { parseError.value = e instanceof Error ? e.message : String(e) }
  } else {
    parseError.value = null
  }
  // 内容变化时刷新预览
  refreshKey.value++
}, { immediate: true })

// ── 是否可以预览 ───────────────────────────────────────────────────────────────
const canPreview = computed(() =>
  !!props.content &&
  !!parsedConfig.value.id
)

// ── 画布尺寸控制 ───────────────────────────────────────────────────────────────
/** 模式：fullscreen = 填满预览区；custom = 指定宽高 */
const canvasMode = ref<'fullscreen' | 'custom'>('custom')
const canvasWidth = ref(960)
const canvasHeight = ref(500)
/** 缩放比例，默认 100% */
const zoomLevel = ref(1)

/** 画布 stage 的内联样式 */
const canvasStageStyle = computed(() => {
  if (canvasMode.value === 'fullscreen') {
    return {
      width: '100%',
      height: '100%',
      transform: `scale(${zoomLevel.value})`,
      transformOrigin: 'top center',
    }
  }
  // 自定义模式：固定宽高，居中，缩放
  return {
    width: `${canvasWidth.value}px`,
    height: `${canvasHeight.value}px`,
    flexShrink: '0',
    transform: `scale(${zoomLevel.value})`,
    transformOrigin: 'top center',
  }
})


</script>

<style lang="less" scoped>
.preview-pane {
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
  * {
    line-height: 1;
  }
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
  gap: 8px;
}

.pane-badge {
  font-size: 11px;
  color: #6b7280;
  background-color: #f3f4f6;
  padding: 1px 7px;
  border-radius: 10px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

/* ── 画布尺寸控制条 ── */
.canvas-toolbar {
  display: flex;
  align-items: center;
  gap: 6px;

  &__mode {
    width: 80px;
  }

  &__size-input {
    width: 68px;
  }

  &__sep {
    font-size: 13px;
    color: #9ca3af;
    padding: 0 1px;
  }

  &__divider {
    display: inline-block;
    width: 1px;
    height: 14px;
    background-color: #e5e7eb;
    margin: 0 4px;
  }

  &__zoom {
    width: 74px;
  }
}

/* ── 预览主体 ── */
.pane-body {
  flex: 1;
  overflow: auto;
  box-sizing: border-box;
}

/* ── 画布视口：负责居中 ── */
.canvas-viewport {
  width: 100%;
  height: 100%;
  overflow: auto;
  padding: 16px;
  box-sizing: border-box;
  background: #f5f5f5;
  // 让 inline-flex 的 canvas-wrapper 水平居中
  text-align: center;
}

/* ── canvas-wrapper：包裹 stage + hint，inline-flex 列方向，左边缘天然对齐 ── */
.canvas-wrapper {
  display: inline-flex;
  flex-direction: column;
  text-align: left; // 重置 viewport 的 text-align 继承
  width: 100%;
}

.canvas-stage {
  border-radius: 8px;
  box-shadow: 0 1px 50px 0 rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
  padding: 20px;
  // 缩放时保留物理尺寸，不影响布局流
  will-change: transform;
  background: white;
  overflow: auto;
  margin: 0 auto;
}

/* ── 占位 / 错误提示 ── */
.preview-placeholder {
  height: 100%;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #9ca3af;
  font-size: 13px;

  &__label { color: #6b7280; }
  &__sub {
    font-size: 11px;
    color: #d1d5db;
    background-color: #f9fafb;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px dashed #e5e7eb;
  }
}

.preview-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fff2f0;
  border: 1px solid #ffa39e;
  border-radius: 6px;
  color: #cf1322;
  font-size: 13px;
  margin: 16px;
}

/* ── 预览内容区：宽度占满画布，高度自然撑开（不强制 100% 避免分页贴底） */
.preview-content {
  width: 100%;
}

/* ── canvas-hint：预览模式提示小字，位于 canvas-stage 内部底部 ── */
.canvas-hint {
  margin-top: 12px;
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.5;
  text-align: center;
}
</style>