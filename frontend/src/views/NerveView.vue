<template>
  <div class="nerve">
    <header class="head">
      <h2 class="h2">Nerve center — fichiers .md des agents</h2>
      <p class="sub">
        IDENTITY, SOUL, MEMORY, AGENTS, HEARTBEAT : mémoire et contrat éditable en direct (couche nerveuse OpenClaw).
      </p>
    </header>
    <div v-if="loading" class="muted">Chargement…</div>
    <div v-else-if="err" class="err">{{ err }}</div>
    <div v-else class="editor-layout">
      <aside class="agents scroll-thin">
        <button
          v-for="a in agents"
          :key="a.id"
          type="button"
          class="ag-btn"
          :class="{ on: a.id === agentId }"
          @click="selectAgent(a.id)"
        >
          <span class="e">{{ a.emoji }}</span>
          {{ a.name }}
        </button>
      </aside>
      <div class="main">
        <div class="tabs">
          <button
            v-for="s in slugs"
            :key="s.slug"
            type="button"
            class="tab"
            :class="{ on: slug === s.slug }"
            @click="selectSlug(s.slug)"
          >
            {{ s.label }}
          </button>
        </div>
        <textarea v-model="content" class="ta scroll-thin" spellcheck="false" />
        <div class="bar">
          <span v-if="savedOk" class="ok">Enregistré.</span>
          <button type="button" class="save" :disabled="saving" @click="save">Enregistrer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'

const loading = ref(true)
const saving = ref(false)
const err = ref('')
const agents = ref([])
const slugs = ref([])
const agentId = ref('')
const slug = ref('identity')
const content = ref('')
const savedOk = ref(false)

async function loadMeta() {
  const [ag, sg] = await Promise.all([
    api.get('/api/nerve/agents'),
    api.get('/api/nerve/slugs'),
  ])
  agents.value = ag.data || []
  slugs.value = sg.data || []
  if (!agentId.value && agents.value.length) {
    agentId.value = agents.value[0].id
  }
}

async function loadFile() {
  if (!agentId.value || !slug.value) return
  savedOk.value = false
  try {
    const { data } = await api.get(`/api/nerve/${agentId.value}/${slug.value}`)
    content.value = data.content ?? ''
  } catch {
    content.value = ''
  }
}

async function selectAgent(id) {
  agentId.value = id
  await loadFile()
}

async function selectSlug(s) {
  slug.value = s
  await loadFile()
}

async function save() {
  saving.value = true
  savedOk.value = false
  err.value = ''
  try {
    await api.put(`/api/nerve/${agentId.value}/${slug.value}`, { content: content.value })
    savedOk.value = true
    setTimeout(() => {
      savedOk.value = false
    }, 2500)
  } catch (e) {
    err.value = e.response?.data?.detail || 'Sauvegarde impossible.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    await loadMeta()
    await loadFile()
  } catch (e) {
    err.value = e.response?.data?.detail || 'Nerve center indisponible.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.nerve {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.h2 {
  margin: 0 0 0.35rem;
  font-family: var(--font-mono);
  font-size: 1rem;
}
.sub {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-muted);
  max-width: 44rem;
  line-height: 1.45;
}
.muted,
.err {
  font-family: var(--font-mono);
  font-size: 0.85rem;
}
.err {
  color: var(--danger);
}
.editor-layout {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 1rem;
  min-height: 480px;
}
@media (max-width: 720px) {
  .editor-layout {
    grid-template-columns: 1fr;
  }
}
.agents {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  max-height: 70vh;
  overflow: auto;
}
@media (max-width: 720px) {
  .agents {
    flex-direction: row;
    flex-wrap: nowrap;
    overflow-x: auto;
    overflow-y: hidden;
    max-height: none;
    padding-bottom: 0.35rem;
    gap: 0.35rem;
    -webkit-overflow-scrolling: touch;
    scroll-snap-type: x proximity;
  }
  .ag-btn {
    flex: 0 0 auto;
    white-space: nowrap;
    scroll-snap-align: start;
  }
  .ta {
    min-height: 220px;
  }
}
.ag-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  text-align: left;
  padding: 0.45rem 0.5rem;
  border-radius: 6px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-muted);
  font: inherit;
  cursor: pointer;
  font-size: 0.85rem;
}
.ag-btn:hover {
  background: #ffffff08;
  color: var(--text);
}
.ag-btn.on {
  border-color: #f59e0b44;
  color: var(--accent);
  background: rgba(245, 158, 11, 0.06);
}
.e {
  font-size: 1rem;
}
.main {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
}
.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.tab {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  padding: 0.35rem 0.55rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-muted);
  cursor: pointer;
}
.tab.on {
  border-color: #f59e0b55;
  color: var(--accent);
}
.ta {
  flex: 1;
  min-height: 360px;
  width: 100%;
  resize: vertical;
  padding: 0.85rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: #06060f;
  color: var(--text);
  font-family: var(--font-mono);
  font-size: 0.78rem;
  line-height: 1.45;
}
.bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}
.save {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  padding: 0.45rem 0.9rem;
  border-radius: 6px;
  border: 1px solid #10b98155;
  background: rgba(16, 185, 129, 0.12);
  color: var(--success);
  cursor: pointer;
}
.save:disabled {
  opacity: 0.5;
}
.ok {
  font-size: 0.75rem;
  color: var(--success);
  font-family: var(--font-mono);
}
</style>
