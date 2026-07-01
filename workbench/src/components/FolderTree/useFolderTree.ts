import { ref, computed } from 'vue'
import type { Node, TreeNode } from './types'

/**
 * 给每个节点递归补充 __key（接口返回的树没有 __key，这里统一加上）
 */
function injectKeys(nodes: Node[]): TreeNode[] {
  return nodes.map((n) => {
    const keyed: TreeNode = {
      ...n,
      __key: n.nodeType === 'folder' ? `folder::${n.id}` : `config::${n.configId}`,
    } as TreeNode
    if (n.children?.length) {
      keyed.children = injectKeys(n.children)
    }
    return keyed
  })
}

export function useFolderTree(options: {
  getTree: () => Node[]
}) {
  const { getTree } = options

  // ── 搜索关键词 ────────────────────────────────
  const searchKeyword = ref('')
  const hasActiveFilter = computed(() => !!searchKeyword.value.trim())

  // ── 当前选中节点 key ──────────────────────────
  const selectedNodeKey = ref<string | null>(null)

  // ── 为接口树补充 __key，得到可渲染树 ─────────
  const mixedTree = computed((): TreeNode[] => injectKeys(getTree()))

  // ── 默认展开第一层文件夹 ─────────────────────
  const defaultExpandedKeys = computed(() =>
    mixedTree.value
      .filter((n) => n.nodeType === 'folder')
      .map((n) => n.__key)
  )

  // ── 递归过滤树：保留匹配的配置节点及其祖先文件夹 ──
  const filterNodes = (nodes: TreeNode[]): TreeNode[] => {
    const keyword = searchKeyword.value.trim().toLowerCase()
    return nodes.reduce<TreeNode[]>((acc, node) => {
      if (node.nodeType === 'config') {
        if (!keyword || node.name.toLowerCase().includes(keyword)) acc.push(node)
      } else {
        const filteredChildren = filterNodes(node.children || [])
        if (filteredChildren.length > 0) {
          acc.push({ ...node, children: filteredChildren })
        } else if (!keyword) {
          acc.push(node)
        }
      }
      return acc
    }, [])
  }

  const filteredTree = computed(() => {
    if (!hasActiveFilter.value) return mixedTree.value
    return filterNodes(mixedTree.value)
  })

  return {
    searchKeyword,
    hasActiveFilter,
    selectedNodeKey,
    defaultExpandedKeys,
    mixedTree,
    filteredTree,
  }
}