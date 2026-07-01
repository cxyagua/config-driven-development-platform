import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import http from '@/http'
import type { Node, SpaceItem } from './types'

// ── 新建配置表单类型 ──────────────────────────────
interface CreateConfigForm {
  name: string
  configId: string
  componentType: string
}

/**
 * 管理 FolderTree 自身的数据层：
 * - 空间列表 + 当前空间
 * - 树数据加载 / 刷新
 * - 文件夹 / 配置的 CRUD（含弹窗交互）
 *
 * @param onConfigCreated  新建配置成功后的回调（通知外部自动打开该配置）
 * @param onConfigDeleted  删除配置成功后的回调（通知外部清空右侧面板）
 * @param onConfigSelected 点击选中配置节点时的回调（通知外部加载 JSON）
 */
export function useTreeData(options: {
  onConfigCreated?: (configId: string) => void
  onConfigDeleted?: (configId: string) => void
  onConfigSelected?: (configId: string) => void
} = {}) {
  const { onConfigCreated, onConfigDeleted, onConfigSelected } = options

  // ── 空间 ──────────────────────────────────────────────────────
  const spaces = ref<SpaceItem[]>([])
  const currentSpaceId = ref<string>('uat')

  // ── 树数据 ────────────────────────────────────────────────────
  const tree = ref<Node[]>([])
  const treeLoading = ref(false)

  const loadTreeData = async (spaceId: string) => {
    treeLoading.value = true
    tree.value = []
    try {
      const res = await http.get(`/spaces/${spaceId}/nodes`) as any
      tree.value = res?.data ?? []
    } catch {
      console.error('加载树数据失败')
    } finally {
      treeLoading.value = false
    }
  }

  // ── 初始化：加载空间列表 ──────────────────────────────────────
  const init = async () => {
    try {
      const res = await http.get('/spaces') as any
      spaces.value = res?.data ?? []
      if (spaces.value.length && !spaces.value.find((s) => s.id === currentSpaceId.value)) {
        currentSpaceId.value = spaces.value[0].id
      }
    } catch {
      // 降级兜底
      spaces.value = [
        { id: 'uat', name: 'UAT 环境' },
        { id: 'prod', name: '生产环境', readonly: true },
        { id: 'dev', name: '开发环境' },
      ]
    }
    await loadTreeData(currentSpaceId.value)
  }

  // ── 切换空间 ──────────────────────────────────────────────────
  const handleSwitchSpace = (spaceId: string) => {
    if (spaceId === currentSpaceId.value) return
    currentSpaceId.value = spaceId
    loadTreeData(spaceId)
  }

  // ── 工具：递归查找 config 节点 ───────────────────────────────
  function findConfigNode(nodes: Node[], configId: string): Node | null {
    for (const n of nodes) {
      if (n.nodeType === 'config' && n.configId === configId) return n
      if (n.children?.length) {
        const found = findConfigNode(n.children, configId)
        if (found) return found
      }
    }
    return null
  }

  /**
   * 工具：收集某父节点下的直接子节点
   * tree.value 是嵌套结构，需要先找到目标父文件夹再取其 children；
   * parentId === 0 表示根目录，直接返回顶层节点。
   */
  function collectSiblings(nodes: Node[], parentId: number): Node[] {
    if (parentId === 0) return nodes
    // 递归找到 id === parentId 的文件夹，返回其 children
    function findChildren(list: Node[]): Node[] | null {
      for (const n of list) {
        if (n.nodeType === 'folder' && n.id === parentId) return n.children ?? []
        if (n.children?.length) {
          const found = findChildren(n.children)
          if (found !== null) return found
        }
      }
      return null
    }
    return findChildren(nodes) ?? []
  }

  /**
   * 工具：在嵌套节点树中找某个节点（folder 或 config）的 parentId
   * 通过递归遍历 children 实现。
   */
  function findParentId(nodes: Node[], nodeType: 'folder' | 'config', id: number | string, parentId = 0): number {
    for (const n of nodes) {
      if (nodeType === 'folder' && n.nodeType === 'folder' && n.id === id) return parentId
      if (nodeType === 'config' && n.nodeType === 'config' && n.configId === id) return parentId
      if (n.children?.length) {
        const found = findParentId(n.children, nodeType, id, n.id ?? 0)
        if (found !== -1) return found
      }
    }
    return -1
  }

  // ── 新建文件夹 ────────────────────────────────────────────────
  const handleCreateFolder = (parentId: number | null | undefined) => {
    ElMessageBox.prompt('请输入文件夹名称', '新建文件夹', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValidator: (val) => {
        if (!val || !val.trim()) return '文件夹名称不能为空'
        // 同名守卫：同一父节点下不能有同名文件夹（允许与配置同名）
        const pid = parentId ?? 0
        const siblings = collectSiblings(tree.value, pid)
        if (siblings.some((n) => n.nodeType === 'folder' && n.name === val.trim())) {
          return `同级已存在同名文件夹「${val.trim()}」，请换一个名称`
        }
        return true
      },
    }).then(async ({ value }) => {
      const name = value.trim()
      try {
        const res = await http.post(`/spaces/${currentSpaceId.value}/folders`, {
          name,
          parentId: parentId ?? 0,
        }) as any
        if (res?.code === 0) {
          tree.value = res.data
          ElMessage.success('文件夹创建成功')
        } else if (res?.code === 409) {
          ElMessage.warning('文件夹已存在')
        } else {
          ElMessage.error(res?.message ?? '创建失败')
        }
      } catch {
        ElMessage.error('创建文件夹失败，请稍后重试')
      }
    }).catch(() => {})
  }

  // ── 新建配置（弹窗状态） ──────────────────────────────────────
  const createConfigDialog = ref<{ visible: boolean; folderId: number; loading: boolean }>({
    visible: false,
    folderId: 0,
    loading: false,
  })
  const createConfigFormRef = ref<FormInstance | null>(null)
  const createConfigForm = ref<CreateConfigForm>({
    name: '',
    configId: '',
    componentType: 'BiFilter',
  })
  const createConfigRules: FormRules = {
    name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
    configId: [
      { required: true, message: '请输入配置 ID', trigger: 'blur' },
      {
        pattern: /^[a-zA-Z0-9-_]+$/,
        message: '只允许英文、数字、连字符和下划线',
        trigger: 'blur',
      },
    ],
  }

  const handleCreateConfig = (folderId: number | null | undefined) => {
    createConfigDialog.value.folderId = folderId ?? 0
    createConfigDialog.value.visible = true
  }

  const resetCreateConfigForm = () => {
    createConfigForm.value = { name: '', configId: '', componentType: 'BiFilter' }
    createConfigFormRef.value?.resetFields()
  }

  const submitCreateConfig = async () => {
    const valid = await createConfigFormRef.value?.validate().catch(() => false)
    if (!valid) return

    // 同名守卫：同一父节点下不能有同名配置（允许与文件夹同名）
    const folderId = createConfigDialog.value.folderId
    const siblings = collectSiblings(tree.value, folderId)
    if (siblings.some((n) => n.nodeType === 'config' && n.name === createConfigForm.value.name.trim())) {
      ElMessage.warning(`同级已存在同名配置「${createConfigForm.value.name.trim()}」，请换一个名称`)
      return
    }

    createConfigDialog.value.loading = true
    try {
      const { name, configId, componentType } = createConfigForm.value
      const res = await http.post(`/spaces/${currentSpaceId.value}/configs`, {
        configId,
        name,
        componentType: componentType === 'others' ? null : componentType || null,
        folderId: createConfigDialog.value.folderId,
      }) as any

      if (res?.code === 0) {
        tree.value = res.data
        ElMessage.success('配置创建成功')
        createConfigDialog.value.visible = false
        onConfigCreated?.(configId)
      } else if (res?.code === 409) {
        ElMessage.error(`配置 ID "${configId}" 已存在，请更换`)
      } else {
        ElMessage.error(res?.message ?? '创建失败')
      }
    } catch {
      ElMessage.error('创建配置失败，请稍后重试')
    } finally {
      createConfigDialog.value.loading = false
    }
  }

  // ── 重命名文件夹 ──────────────────────────────────────────────
  const handleRenameFolder = async (id: number, newName: string) => {
    // 同名守卫：同一父节点下不能有同名文件夹（允许与配置同名）
    const parentId = findParentId(tree.value, 'folder', id)
    const siblings = collectSiblings(tree.value, parentId).filter((n) => !(n.nodeType === 'folder' && n.id === id))
    if (siblings.some((n) => n.nodeType === 'folder' && n.name === newName)) {
      ElMessage.warning(`同级已存在同名文件夹「${newName}」，无法重命名`)
      return
    }
    try {
      const res = await http.patch(`/spaces/${currentSpaceId.value}/folders/rename`, {
        id,
        newName,
      }) as any
      if (res?.code === 0) {
        tree.value = res.data
        ElMessage.success('重命名成功')
      } else {
        ElMessage.error(res?.message ?? '重命名失败')
      }
    } catch {
      ElMessage.error('重命名失败，请稍后重试')
    }
  }

  // ── 删除文件夹 ────────────────────────────────────────────────
  const handleDeleteFolder = async (id: number, currentConfigId: string | null) => {
    try {
      const res = await http.delete(`/spaces/${currentSpaceId.value}/folders/delete`, {
        data: { id },
      }) as any
      if (res?.code === 0) {
        tree.value = res.data
        // 如果当前打开的配置在被删文件夹下，通知外部清空
        if (currentConfigId) {
          const stillExists = findConfigNode(tree.value, currentConfigId)
          if (!stillExists) onConfigDeleted?.(currentConfigId)
        }
        ElMessage.success('删除成功')
      } else {
        ElMessage.error(res?.message ?? '删除失败')
      }
    } catch {
      ElMessage.error('删除失败，请稍后重试')
    }
  }

  // ── 移动文件夹 ────────────────────────────────────────────────
  const handleMoveFolder = async (sourceId: number, targetParentId: number) => {
    // 同名守卫：目标目录下不能有同名文件夹（允许与配置同名）
    const folder = tree.value.find((n) => n.nodeType === 'folder' && n.id === sourceId)
    if (folder) {
      const siblings = collectSiblings(tree.value, targetParentId).filter(
        (n) => !(n.nodeType === 'folder' && n.id === sourceId)
      )
      if (siblings.some((n) => n.nodeType === 'folder' && n.name === folder.name)) {
        // 强制重置树：el-tree 在 @node-drop 时已更新 DOM，需要重新赋值让 Vue 还原
        tree.value = JSON.parse(JSON.stringify(tree.value))
        ElMessage.warning(`目标目录下已存在同名文件夹「${folder.name}」，无法移动`)
        return
      }
    }
    try {
      const res = await http.patch(`/spaces/${currentSpaceId.value}/folders/move`, {
        sourceId,
        targetParentId,
      }) as any
      if (res?.code === 0) {
        tree.value = res.data
      } else {
        ElMessage.error(res?.message ?? '移动失败')
      }
    } catch {
      ElMessage.error('移动失败，请稍后重试')
    }
  }

  // ── 重命名配置 ────────────────────────────────────────────────
  const handleRenameConfig = async (configId: string, newName: string) => {
    // 同名守卫：同一父节点下不能有同名配置（允许与文件夹同名）
    const parentId = findParentId(tree.value, 'config', configId)
    const siblings = collectSiblings(tree.value, parentId).filter(
      (n) => !(n.nodeType === 'config' && n.configId === configId)
    )
    if (siblings.some((n) => n.nodeType === 'config' && n.name === newName)) {
      ElMessage.warning(`同级已存在同名配置「${newName}」，无法重命名`)
      return
    }
    try {
      const res = await http.patch(`/configs/${configId}/rename`, { newName }) as any
      if (res?.code === 0) {
        tree.value = res.data
        ElMessage.success('重命名成功')
      } else {
        ElMessage.error(res?.message ?? '重命名失败')
      }
    } catch {
      ElMessage.error('重命名失败，请稍后重试')
    }
  }

  // ── 删除配置 ──────────────────────────────────────────────────
  const handleDeleteConfig = async (configId: string) => {
    try {
      const res = await http.delete(`/configs/${configId}`) as any
      if (res?.code === 0) {
        tree.value = res.data
        onConfigDeleted?.(configId)
        ElMessage.success('删除成功')
      } else {
        ElMessage.error(res?.message ?? '删除失败')
      }
    } catch {
      ElMessage.error('删除失败，请稍后重试')
    }
  }

  // ── 移动配置 ──────────────────────────────────────────────────
  const handleMoveConfig = async (configId: string, targetFolderId: number) => {
    // 同名守卫：目标目录下不能有同名配置（允许与文件夹同名）
    const config = tree.value.find((n) => n.nodeType === 'config' && n.configId === configId)
    if (config) {
      const siblings = collectSiblings(tree.value, targetFolderId).filter(
        (n) => !(n.nodeType === 'config' && n.configId === configId)
      )
      if (siblings.some((n) => n.nodeType === 'config' && n.name === config.name)) {
        // 强制重置树：el-tree 在 @node-drop 时已更新 DOM，需要重新赋值让 Vue 还原
        tree.value = JSON.parse(JSON.stringify(tree.value))
        ElMessage.warning(`目标目录下已存在同名配置「${config.name}」，无法移动`)
        return
      }
    }
    try {
      const res = await http.patch(`/configs/${configId}/move`, { targetFolderId }) as any
      if (res?.code === 0) {
        tree.value = res.data
      } else {
        ElMessage.error(res?.message ?? '移动失败')
      }
    } catch {
      ElMessage.error('移动失败，请稍后重试')
    }
  }

  // ── 原地更新节点 componentType（避免全量刷树） ───────────────
  const updateNodeComponentType = (configId: string, componentType: string): boolean => {
    function walk(nodes: Node[]): boolean {
      for (const n of nodes) {
        if (n.nodeType === 'config' && n.configId === configId) {
          n.componentType = componentType
          return true
        }
        if (n.children?.length && walk(n.children)) return true
      }
      return false
    }
    return walk(tree.value)
  }

  // ── 当前空间是否只读 ─────────────────────────────────────────
  const isReadonlySpace = computed(
    () => !!spaces.value.find((s) => s.id === currentSpaceId.value)?.readonly,
  )

  return {
    // 状态
    spaces,
    currentSpaceId,
    tree,
    treeLoading,
    /** 当前空间是否为只读模式 */
    isReadonlySpace,
    // 初始化
    init,
    // 空间
    handleSwitchSpace,
    // 文件夹
    handleCreateFolder,
    handleRenameFolder,
    handleDeleteFolder,
    handleMoveFolder,
    // 配置
    handleCreateConfig,
    handleRenameConfig,
    handleDeleteConfig,
    handleMoveConfig,
    // 新建配置弹窗状态（需挂载到模板）
    createConfigDialog,
    createConfigFormRef,
    createConfigForm,
    createConfigRules,
    resetCreateConfigForm,
    submitCreateConfig,
    // 工具
    findConfigNode,
    updateNodeComponentType,
  }
}