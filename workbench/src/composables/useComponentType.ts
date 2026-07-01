import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '@/http'
import type { Ref } from 'vue'
import type FolderTree from '@/components/FolderTree'

/**
 * 管理配置的组件类型切换（PATCH /configs/:id/type）。
 *
 * @param folderTreeRef  - FolderTree 组件实例 ref，用于原地更新节点
 * @param activeConfigId - 当前活跃配置的 ID ref
 */
export function useComponentType(
  folderTreeRef: Ref<InstanceType<typeof FolderTree> | null>,
  activeConfigId: Ref<string | null>,
) {
  const typeChanging = ref<boolean>(false)

  async function handleChangeComponentType(componentType: string) {
    const configId = activeConfigId.value
    if (!configId) return
    typeChanging.value = true
    try {
      const res = (await http.patch(`/configs/${configId}/type`, { componentType })) as any
      if (res?.code === 0) {
        // 通过 FolderTree expose 的方法原地更新节点，避免全量刷树
        folderTreeRef.value?.updateNodeComponentType(configId, componentType)
        ElMessage.success('组件类型已更新')
      } else {
        ElMessage.error(res?.message ?? '更新失败')
      }
    } catch {
      ElMessage.error('更新组件类型失败，请稍后重试')
    } finally {
      typeChanging.value = false
    }
  }

  return {
    typeChanging,
    handleChangeComponentType,
  }
}
