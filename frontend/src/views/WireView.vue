<template>
  <div class="wire">
    <AgentsWire />
    <header class="head">
      <h2 class="h2">Wire — communications inter-agents</h2>
      <p class="sub">
        <template v-if="wireSource === 'openclaw'">
          Fils = runs OpenClaw (cron/runs/*.jsonl), un fil par agent. {{ total }} fils — dernière activité en tête.
        </template>
        <template v-else>
          Canal autonome Marlène ↔ Gaston ↔ équipe. {{ total }} fils — observation sans intervention.
        </template>
      </p>
    </header>
    <div v-if="loading" class="muted">Chargement…</div>
    <div v-else-if="err" class="err">{{ err }}</div>
    <div v-else class="layout">
      <aside class="conv-list scroll-thin">
        <button
          v-for="c in conversations"
          :key="c.id"
          type="button"
          class="conv-btn"
          :class="{ on: c.id === activeId }"
          @click="openConv(c.id)"
        >
          <span class="t">{{ c.title }}</span>
          <span class="meta">{{ c.message_count }} msg</span>
          <span class="prev">{{ c.preview }}</span>
        </button>
      </aside>
      <main class="thread scroll-thin">
        <div v-if="!activeId" class="empty">Sélectionnez une conversation.</div>
        <template v-else>
          <div v-if="msgLoading" class="muted">Messages…</div>
          <div v-else class="msgs">
            <article v-for="m in messages" :key="String(m.id)" class="msg">
              <div class="msg-head">
                <span class="from">{{ labelAgent(m.from_agent_id) }}</span>
                <span class="arrow">→</span>
                <span class="to">{{ labelAgent(m.to_agent_id) }}</span>
                <span v-if="m.meta" class="meta-run">{{ m.meta.status }}{{ m.meta.tokens != null ? ' · ' + m.meta.tokens + ' tok' : '' }}</span>
                <time
                  v-if="m.created_at"
                  :datetime="wireDatetimeAttr(m.created_at)"
                >{{ formatWireDate(m.created_at) }}</time>
              </div>
              <p class="body">{{ m.body }}</p>
            </article>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'
import AgentsWire from '@/components/AgentsWire.vue'

const loading = ref(true)
const msgLoading = ref(false)
const err = ref('')
const conversations = ref([])
const total = ref(0)
const wireSource = ref('database')
const activeId = ref(null)
const messages = ref([])
const agentsById = ref({})

const wireDateFmt = new Intl.DateTimeFormat('fr-FR', {
  dateStyle: 'long',
  timeStyle: 'short',
})

function formatWireDate(raw) {
  if (!raw) return '—'
  const d = new Date(typeof raw === 'string' ? raw.trim() : raw)
  if (Number.isNaN(d.getTime())) return String(raw)
  return wireDateFmt.format(d)
}

function wireDatetimeAttr(raw) {
  const d = new Date(typeof raw === 'string' ? raw.trim() : raw)
  if (Number.isNaN(d.getTime())) return undefined
  return d.toISOString()
}

function labelAgent(id) {
  if (!id) return '—'
  if (id === 'dashboard') return 'Dashboard'
  const a = agentsById.value[id]
  return a ? `${a.emoji} ${a.name}` : id
}

async function loadConversations() {
  loading.value = true
  err.value = ''
  try {
    const [w, ag] = await Promise.all([
      api.get('/api/wire/conversations', { params: { limit: 100, offset: 0 } }),
      api.get('/api/agents'),
    ])
    conversations.value = w.data.items || []
    total.value = w.data.total || 0
    wireSource.value = w.data.source || 'database'
    const m = {}
    for (const a of ag.data || []) m[a.id] = a
    agentsById.value = m
    if (!activeId.value && conversations.value.length) {
      await openConv(conversations.value[0].id)
    }
  } catch (e) {
    err.value = e.response?.data?.detail || 'Wire indisponible.'
  } finally {
    loading.value = false
  }
}

async function openConv(id) {
  activeId.value = id
  msgLoading.value = true
  messages.value = []
  try {
    const { data } = await api.get(
      `/api/wire/conversations/${encodeURIComponent(id)}/messages`
    )
    messages.value = data || []
  } catch {
    messages.value = []
  } finally {
    msgLoading.value = false
  }
}

onMounted(loadConversations)
</script>

<style scoped>
.wire {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 60vh;
}
.head {
  margin-bottom: 0.25rem;
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
  max-width: 48rem;
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
.layout {
  display: grid;
  grid-template-columns: minmax(240px, 320px) 1fr;
  gap: 1rem;
  min-height: 420px;
}
.conv-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  max-height: min(70vh, 520px);
  overflow: auto;
}
.conv-btn {
  text-align: left;
  padding: 0.55rem 0.65rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: inherit;
  cursor: pointer;
  font: inherit;
  transition: border-color 0.15s, background 0.15s;
}
.conv-btn:hover {
  border-color: #ffffff20;
}
.conv-btn.on {
  border-color: #f59e0b55;
  background: rgba(245, 158, 11, 0.08);
}
.conv-btn .t {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  line-height: 1.3;
}
.conv-btn .meta {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--text-muted);
}
.conv-btn .prev {
  display: block;
  margin-top: 0.35rem;
  font-size: 0.68rem;
  color: var(--text-muted);
  line-height: 1.35;
  opacity: 0.9;
}
.thread {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
  max-height: 70vh;
  overflow: auto;
}
@media (max-width: 800px) {
  .layout {
    grid-template-columns: 1fr;
  }
  .conv-list {
    max-height: min(40vh, 280px);
  }
  .thread {
    max-height: min(55vh, 480px);
  }
}
.empty {
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 0.85rem;
}
.msgs {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.msg {
  border-bottom: 1px solid #ffffff0a;
  padding-bottom: 0.85rem;
}
.msg:last-child {
  border-bottom: none;
}
.msg-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.35rem;
  font-size: 0.72rem;
  font-family: var(--font-mono);
  margin-bottom: 0.35rem;
}
.msg-head time {
  margin-left: auto;
  color: var(--text-muted);
  font-size: 0.65rem;
}
.meta-run {
  width: 100%;
  font-size: 0.6rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
  opacity: 0.9;
  margin-top: 0.15rem;
  padding-left: 0;
  flex-basis: 100%;
}
.from {
  color: var(--accent);
}
.to {
  color: var(--info);
}
.arrow {
  color: var(--text-muted);
}
.body {
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.5;
  white-space: pre-wrap;
}
</style>
