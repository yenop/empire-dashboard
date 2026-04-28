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
            <p v-if="statusErr" class="err status-err">{{ statusErr }}</p>
            <article v-for="m in messages" :key="String(m.id)" class="msg">
              <div class="msg-head">
                <span v-if="m.source === 'dashboard'" class="src-badge" title="Message depuis le dashboard"
                  >Dashboard</span
                >
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
              <div v-if="isDashboardHumanMsg(m)" class="feedback-controls">
                <button
                  v-if="(m.human_status || 'sent') === 'sent'"
                  type="button"
                  class="btn-approve"
                  @click="setMessageStatus(m, 'approved')"
                >
                  Approuver
                </button>
                <button
                  v-if="(m.human_status || 'sent') === 'sent'"
                  type="button"
                  class="btn-rework"
                  @click="setMessageStatus(m, 'rework')"
                >
                  À retravailler
                </button>
                <span
                  class="loop-status"
                  :class="m.human_status || 'sent'"
                >{{ loopLabel(m.human_status || 'sent') }}</span>
              </div>
            </article>
          </div>
          <footer v-if="!msgLoading" class="composer">
            <p v-if="sendErr" class="err">{{ sendErr }}</p>
            <div class="row">
              <label class="lab">
                <span class="lab-t">Destinataire</span>
                <select v-model="toAgentId" class="sel" :disabled="sending || !agentsList.length">
                  <option disabled value="">— Choisir un agent —</option>
                  <option v-for="a in agentsList" :key="a.id" :value="a.id">
                    {{ a.emoji }} {{ a.name }} ({{ a.id }})
                  </option>
                </select>
              </label>
              <label class="nerve-ck">
                <input v-model="pushNerve" type="checkbox" :disabled="sending" />
                <span>Ajouter la consigne au Nerve (HEARTBEAT)</span>
              </label>
            </div>
            <div class="row2">
              <textarea
                v-model="draft"
                class="ta"
                rows="3"
                placeholder="Message pour l’agent…"
                :disabled="sending"
              />
              <button
                type="button"
                class="send"
                :disabled="sending || !draft.trim() || !toAgentId"
                @click="sendMessage"
              >
                {{ sending ? 'Envoi…' : 'Envoyer' }}
              </button>
            </div>
          </footer>
        </template>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import AgentsWire from '@/components/AgentsWire.vue'

const route = useRoute()

const loading = ref(true)
const msgLoading = ref(false)
const err = ref('')
const conversations = ref([])
const total = ref(0)
const wireSource = ref('database')
const activeId = ref(null)
const messages = ref([])
const agentsById = ref({})
const agentsList = ref([])
const draft = ref('')
const toAgentId = ref('')
const pushNerve = ref(true)
const sending = ref(false)
const sendErr = ref('')
const statusErr = ref('')

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

function wireMessageNumericId(m) {
  if (typeof m.id === 'number') return m.id
  const s = String(m.id)
  if (s.startsWith('db-')) {
    const n = parseInt(s.slice(3), 10)
    return Number.isNaN(n) ? null : n
  }
  return null
}

function isDashboardHumanMsg(m) {
  return m.from_agent_id === 'dashboard' && wireMessageNumericId(m) != null
}

function loopLabel(status) {
  return (
    {
      sent: '— envoyé',
      approved: '✓ approuvé',
      rework: '↻ retravailler',
      ack: "○ vu par l'agent",
      applied: '✓ appliqué',
    }[status] ?? status
  )
}

async function setMessageStatus(m, st) {
  const numId = wireMessageNumericId(m)
  if (numId == null) return
  statusErr.value = ''
  try {
    await api.patch(`/api/wire/messages/${numId}/status`, { status: st, note: '' })
    await openConv(activeId.value)
  } catch (e) {
    statusErr.value = e.response?.data?.detail || 'Mise à jour impossible.'
  }
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
    agentsList.value = ag.data || []
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
  sendErr.value = ''
  statusErr.value = ''
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

function syncRecipientForActiveConv() {
  const id = activeId.value
  const c = conversations.value.find((x) => String(x.id) === String(id))
  if (c?.agent_key) {
    toAgentId.value = c.agent_key
  } else {
    toAgentId.value = ''
  }
}

watch(activeId, () => {
  syncRecipientForActiveConv()
})

watch(
  () => ({ agentQ: route.query.agent, agents: agentsById.value }),
  () => {
    const ag = route.query.agent
    if (typeof ag === 'string' && agentsById.value[ag]) {
      toAgentId.value = ag
    }
  },
  { immediate: true }
)

async function sendMessage() {
  if (!activeId.value || !toAgentId.value || !draft.value.trim()) return
  sending.value = true
  sendErr.value = ''
  try {
    await api.post('/api/wire/messages', {
      body: draft.value.trim(),
      to_agent_id: toAgentId.value,
      conversation_id: String(activeId.value),
      push_to_nerve: pushNerve.value,
    })
    draft.value = ''
    await openConv(activeId.value)
  } catch (e) {
    sendErr.value = e.response?.data?.detail || "Envoi impossible."
  } finally {
    sending.value = false
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
.src-badge {
  font-size: 0.58rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--warning, #f59e0b);
  margin-right: 0.35rem;
  font-family: var(--font-mono);
}
.composer {
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid #ffffff12;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.composer .row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.75rem 1rem;
}
.composer .row2 {
  display: flex;
  gap: 0.65rem;
  align-items: flex-end;
}
.lab {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 12rem;
  flex: 1;
}
.lab-t {
  font-size: 0.65rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.sel {
  font: inherit;
  padding: 0.4rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg, #0a0a0a);
  color: inherit;
}
.nerve-ck {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  color: var(--text-muted);
  cursor: pointer;
  user-select: none;
}
.ta {
  flex: 1;
  min-height: 4rem;
  font: inherit;
  padding: 0.5rem 0.65rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg, #0a0a0a);
  color: inherit;
  resize: vertical;
}
.send {
  flex-shrink: 0;
  padding: 0.55rem 1rem;
  border-radius: 8px;
  border: 1px solid #f59e0b55;
  background: rgba(245, 158, 11, 0.12);
  color: inherit;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
.send:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.status-err {
  margin: 0 0 0.75rem;
}
.feedback-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.btn-approve,
.btn-rework {
  font: inherit;
  font-size: 0.7rem;
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid var(--border);
  background: var(--bg, #0a0a0a);
  color: inherit;
}
.btn-approve {
  border-color: #22c55e55;
  background: rgba(34, 197, 94, 0.1);
}
.btn-rework {
  border-color: #f9731655;
  background: rgba(249, 115, 22, 0.1);
}
.loop-status {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--text-muted);
}
.loop-status.sent {
  opacity: 0.85;
}
.loop-status.approved,
.loop-status.applied {
  color: #4ade80;
}
.loop-status.rework {
  color: #fb923c;
}
.loop-status.ack {
  color: var(--info);
}
</style>
