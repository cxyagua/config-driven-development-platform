import { ref, onBeforeUnmount } from 'vue'

const EDITOR_DEFAULT_WIDTH = 500
const EDITOR_MIN_WIDTH = 350

/**
 * 管理右侧 JSON 编辑器面板的可拖拽宽度。
 *
 * 用法：将 `startResize` 绑定到分隔条的 `@mousedown` 事件，
 * 将 `editorWidth` 作为编辑器容器的内联宽度样式。
 */
export function useEditorResize() {
  const editorWidth = ref(EDITOR_DEFAULT_WIDTH)

  function startResize(e: MouseEvent) {
    e.preventDefault()
    const startX = e.clientX
    const startWidth = editorWidth.value

    function onMove(ev: MouseEvent) {
      const delta = startX - ev.clientX
      editorWidth.value = Math.max(EDITOR_MIN_WIDTH, startWidth + delta)
    }

    function onUp() {
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }

    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }

  // 组件卸载时恢复 body 样式，防止异常退出后样式残留
  onBeforeUnmount(() => {
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  })

  return {
    editorWidth,
    startResize,
  }
}
