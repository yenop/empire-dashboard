import { onMounted, ref } from 'vue'
import api from '@/api'

/**
 * Agent counts and API reachability for the sidebar footer (same data sources as Topbar).
 */
export function useSidebarStatus() {
  const totalAgents = ref(0)
  const onlineAgents = ref(0)
  const apiOk = ref(true)

  async function load() {
    try {
      const [agentsRes, wfRes] = await Promise.all([
        api.get('/api/agents'),
        api.get('/api/workflow').catch(() => ({ data: null })),
      ])
      const all = agentsRes.data || []
      totalAgents.value = all.length
      const lit = wfRes.data?.lit_agent_ids
      if (Array.isArray(lit) && lit.length) {
        const map = new Map(all.map((a) => [a.id, a]))
        onlineAgents.value = lit.map((id) => map.get(id)).filter(Boolean).length
      } else {
        onlineAgents.value = all.filter((a) => a.status === 'active').length
      }
      apiOk.value = true
    } catch {
      totalAgents.value = 0
      onlineAgents.value = 0
      apiOk.value = false
    }
  }

  onMounted(load)

  return {
    totalAgents,
    onlineAgents,
    apiOk,
    refresh: load,
  }
}
