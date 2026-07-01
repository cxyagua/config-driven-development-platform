import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '@/http'
import type { Ref } from 'vue'
import type FolderTree from '@/components/FolderTree'
import type { Node } from '@/components/FolderTree/types'

/**
 * 管理当前活跃配置的选中状态、JSON 内容加载与保存。
 *
 * @param folderTreeRef - FolderTree 组件实例 ref，用于查找配置节点
 */
export function useActiveConfig(folderTreeRef: Ref<InstanceType<typeof FolderTree> | null>) {
  const activeConfigId = ref<string | null>(null)
  const saving = ref<boolean>(false)
  const activeJsonContent = ref<unknown>({})

  /** 从 FolderTree 内部树中查找当前活跃配置节点 */
  const activeConfig = computed((): Node | null => {
    if (!activeConfigId.value || !folderTreeRef.value) return null
    return folderTreeRef.value.findConfigNode(activeConfigId.value)
  })

  /** 仅三大原子组件才展示预览区 */
  // const PREVIEWABLE_TYPES = new Set(['BiFilter', 'BiTable', 'BiChart'])
  // const isPreviewable = computed(
  //   () =>
  //     !!activeConfig.value?.componentType &&
  //     PREVIEWABLE_TYPES.has(activeConfig.value.componentType),
  // )
  const isPreviewable = ref<boolean>(false)

  // 切换配置时自动加载 JSON 内容，使用序号防止竞态
  let fetchSeq = 0
  watch(
    activeConfigId,
    async (configId, oldConfigId) => {
      if (configId === oldConfigId) return
      activeJsonContent.value = {}
      if (!configId) return
      const seq = ++fetchSeq
      try {
        const res = (await http.get(`/configs/${configId}/content`)) as any
        if (seq === fetchSeq) {
          activeJsonContent.value = res?.data ?? {}
        }
      } catch {
        if (seq === fetchSeq) activeJsonContent.value = {}
      }
    },
    { immediate: true },
  )

  /** 保存当前配置内容 */
  async function handleSaveConfig(content: unknown) {
    if (!activeConfig.value) return
    saving.value = true
    try {
      await http.put(`/configs/${activeConfig.value.configId}/content`, content)
      ElMessage.success('保存成功')
    } catch {
      ElMessage.error('保存失败，请稍后重试')
    } finally {
      saving.value = false
    }
  }

  /** FolderTree @select-config 事件处理 */
  function handleSelectConfig(configId: string) {
    activeConfigId.value = configId
  }

  /** FolderTree @config-deleted 事件处理 */
  function handleConfigDeleted(configId: string) {
    if (activeConfigId.value === configId) activeConfigId.value = null
  }

  return {
    activeConfigId,
    activeConfig,
    activeJsonContent,
    isPreviewable,
    saving,
    handleSaveConfig,
    handleSelectConfig,
    handleConfigDeleted,
  }
}
