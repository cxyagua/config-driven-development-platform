import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import http from '@/http'
import type { Ref } from 'vue'
import type { SpaceItem } from './types'

interface SyncState {
  visible: boolean
  nodeType: 'folder' | 'config'
  nodeId: number | string   // folder → number, config → string (configId)
  nodeName: string
  targetSpaceId: string
  loading: boolean
}

/**
 * 同步功能 composable
 *
 * 封装同步对话框状态、API 调用与成功/失败提示。
 *
 * @param spaces          空间列表（响应式）
 * @param currentSpaceId  当前空间 ID（响应式）
 */
export function useSync(options: {
  spaces: Ref<SpaceItem[]>
  currentSpaceId: Ref<string>
}) {
  const { spaces, currentSpaceId } = options

  // ── 对话框状态 ────────────────────────────────────────────────
  const syncDialog = ref<SyncState>({
    visible: false,
    nodeType: 'folder',
    nodeId: 0,
    nodeName: '',
    targetSpaceId: '',
    loading: false,
  })

  /** 可同步的目标空间：排除当前空间 */
  const syncableSpaces = computed(() =>
    spaces.value.filter((s) => s.id !== currentSpaceId.value)
  )

  /** 目标空间名称（用于提示文案） */
  const syncTargetSpaceName = computed(() =>
    spaces.value.find((s) => s.id === syncDialog.value.targetSpaceId)?.name ?? ''
  )

  // ── 打开 / 重置 ───────────────────────────────────────────────
  function openSyncDialog(nodeType: 'folder' | 'config', nodeId: number | string, nodeName: string) {
    syncDialog.value = {
      visible: true,
      nodeType,
      nodeId,
      nodeName,
      targetSpaceId: syncableSpaces.value[0]?.id ?? '',
      loading: false,
    }
  }

  function resetSyncDialog() {
    syncDialog.value.targetSpaceId = ''
  }

  // ── API 调用 ──────────────────────────────────────────────────
  async function syncFolder(folderId: number, targetSpaceId: string): Promise<void> {
    const res = await http.post(
      `/spaces/${currentSpaceId.value}/folders/${folderId}/sync`,
      { targetSpaceId }
    ) as any
    if (res?.code !== 0) throw new Error(res?.message ?? '同步失败')
  }

  async function syncConfig(configId: string, targetSpaceId: string): Promise<void> {
    const res = await http.post(`/configs/${configId}/sync`, { targetSpaceId }) as any
    if (res?.code !== 0) throw new Error(res?.message ?? '同步失败')
  }

  // ── 提交（含 loading 控制和成功/失败提示） ────────────────────
  async function submitSync() {
    const { nodeType, nodeId, targetSpaceId } = syncDialog.value
    if (!targetSpaceId) return

    syncDialog.value.loading = true
    try {
      if (nodeType === 'folder') {
        await syncFolder(nodeId as number, targetSpaceId)
      } else {
        await syncConfig(nodeId as string, targetSpaceId)
      }
      const spaceName = syncTargetSpaceName.value
      syncDialog.value.visible = false
      ElMessage.success(`已同步成功，请切换到「${spaceName}」查看`)
    } catch (err: any) {
      ElMessage.error(err?.message ?? '同步失败，请稍后重试')
    } finally {
      syncDialog.value.loading = false
    }
  }

  return {
    syncDialog,
    syncableSpaces,
    syncTargetSpaceName,
    openSyncDialog,
    resetSyncDialog,
    submitSync,
  }
}
