<template>
  <div v-if="loading" class="muted">Chargement…</div>
  <div v-else>
    <div class="filters">
      <button
        v-for="f in filterOptions"
        :key="f.value || 'all'"
        type="button"
        :class="{ on: filter === f.value }"
        @click="filter = f.value"
      >
        {{ f.label }}
      </button>
    </div>
    <div class="grid">
      <AgentCard
        v-for="a in filtered"
        :key="a.id"
        :agent="a"
        :phase-lit="isPhaseLit(a.id)"
        @open="openDetail"
      />
    </div>
    <AgentModal :open="!!selected" :agent="selected" @close="selected = null" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '@/api'
import AgentCard from '@/components/crew/AgentCard.vue'
import AgentModal from '@/components/crew/AgentModal.vue'

const loading = ref(true)
const agents = ref([])
const litAgentIds = ref(new Set())
const filter = ref(null)
const selected = ref(null)

function isPhaseLit(id) {
  if (!litAgentIds.value.size) return true
  return litAgentIds.value.has(id)
}

const filterOptions = [
  { label: 'Tous', value: null },
  { label: 'Direction', value: 'direction' },
  { label: 'Recherche', value: 'recherche' },
  { label: 'Production', value: 'production' },
  { label: 'Intelligence', value: 'intelligence' },
  { label: 'Support', value: 'support' },
  { label: 'Expansion', value: 'expansion' },
]

const filtered = computed(() => {
  if (!filter.value) return agents.value
  return agents.value.filter((a) => a.pole === filter.value)
})

onMounted(async () => {
  try {
    const [agentsRes, wfRes] = await Promise.all([
      api.get('/api/agents'),
      api.get('/api/workflow').catch(() => ({ data: null })),
    ])
    agents.value = agentsRes.data
    const ids = wfRes.data?.lit_agent_ids
    litAgentIds.value = Array.isArray(ids) ? new Set(ids) : new Set()
  } finally {
    loading.value = false
  }
})

async function openDetail(a) {
  const { data } = await api.get(`/api/agents/${a.id}`)
  selected.value = data
}
</script>

<style scoped>
.muted {
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1rem;
}
.filters button {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: #ffffff06;
  color: var(--text-muted);
  cursor: pointer;
}
.filters button.on {
  border-color: #f59e0b55;
  color: var(--accent);
  background: rgba(245, 158, 11, 0.1);
}
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}
@media (max-width: 1100px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 640px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
