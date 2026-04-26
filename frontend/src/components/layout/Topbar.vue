<template>
  <header class="topbar">
    <h1 class="title">{{ pageTitle }}</h1>
    <div class="right">
      <div class="pills" v-if="activeAgents.length">
        <div v-for="a in activeAgents" :key="a.id" class="pill" :title="a.name">
          <span class="emoji">{{ a.emoji }}</span>
          <span class="dot" :style="dotStyle" />
        </div>
      </div>
      <button type="button" class="btn-new" @click="noop">+ Nouvelle app</button>
    </div>
  </header>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const pageTitle = computed(
  () => route.meta.title || 'Dashboard'
)
const activeAgents = ref([])

const dotStyle = {
  background: 'var(--success)',
  boxShadow: '0 0 6px #10b981',
}

function noop() {}

async function loadAgents() {
  try {
    const [agentsRes, wfRes] = await Promise.all([
      api.get('/api/agents'),
      api.get('/api/workflow').catch(() => ({ data: null })),
    ])
    const all = agentsRes.data || []
    const lit = wfRes.data?.lit_agent_ids
    if (Array.isArray(lit) && lit.length) {
      const map = new Map(all.map((a) => [a.id, a]))
      activeAgents.value = lit.map((id) => map.get(id)).filter(Boolean)
    } else {
      activeAgents.value = all.filter((a) => a.status === 'active').slice(0, 8)
    }
  } catch {
    activeAgents.value = []
  }
}

onMounted(loadAgents)
watch(
  () => route.path,
  () => loadAgents()
)
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 1.5rem;
  border-bottom: 1px solid var(--border);
  background: rgba(5, 5, 15, 0.5);
  backdrop-filter: blur(6px);
}
.title {
  font-family: var(--font-mono);
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  margin: 0;
  color: var(--text);
}
.right {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.pills {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
  max-width: 280px;
  justify-content: flex-end;
}
.pill {
  position: relative;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
}
.pill .emoji {
  font-size: 0.9rem;
}
.pill .dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  animation: pulse-dot 2s ease-in-out infinite;
}
.btn-new {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  border: 1px solid #f59e0b44;
  background: rgba(245, 158, 11, 0.1);
  color: var(--accent);
  cursor: pointer;
  white-space: nowrap;
}
.btn-new:hover {
  background: rgba(245, 158, 11, 0.2);
  border-color: #f59e0b88;
}
</style>
