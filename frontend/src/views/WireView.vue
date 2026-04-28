<template>
  <div class="wire">
    <details class="ow-details">
      <summary class="ow-summary">OpenClaw — agents &amp; crons (déplier)</summary>
      <div class="ow-inset">
        <AgentsWire />
      </div>
    </details>
    <header class="head">
      <div class="head-top">
        <h2 class="h2">Wire</h2>
        <button
          v-if="wireStats && !loading"
          type="button"
          class="btn-refresh head-refresh"
          :disabled="loading"
          @click="loadConversations"
        >
          Rafraîchir
        </button>
      </div>
      <p v-if="wireStats" class="stats-bullets">
        <span>{{ wireStats.messages }} messages</span>
        <span class="stats-dot" aria-hidden="true">·</span>
        <span>{{ wireStats.broadcasts }} broadcasts</span>
        <span class="stats-dot" aria-hidden="true">·</span>
        <span>{{ wireStats.conversations }} conversations</span>
        <span v-if="wireStats.threads != null">
          <span class="stats-dot" aria-hidden="true">·</span>
          <span>{{ wireStats.threads }} threads</span>
        </span>
      </p>
      <p v-else class="sub">
        <template v-if="wireSource === 'openclaw'">
          Fils = runs OpenClaw (cron/runs/*.jsonl) — {{ total }} fils.
        </template>
        <template v-else> Fil de messages — {{ total }} conversations.</template>
      </p>
    </header>
    <div v-if="loading" class="muted">Chargement…</div>
    <div v-else-if="err" class="err">{{ err }}</div>
    <div v-else class="stack">
      <div v-if="wireSource === 'database'" class="new-conv">
        <p v-if="createErr" class="err create-err">{{ createErr }}</p>
        <div class="new-conv-row">
          <label class="new-conv-lab">
            <span class="new-conv-t">Nouvelle conversation (par vous)</span>
            <input
              v-model="newTitle"
              type="text"
              class="new-conv-inp"
              placeholder="Titre du fil…"
              maxlength="300"
              :disabled="createLoading"
              @keydown.enter.prevent="createConversation"
            />
          </label>
          <button
            type="button"
            class="new-conv-btn"
            :disabled="createLoading || !newTitle.trim()"
            @click="createConversation"
          >
            {{ createLoading ? 'Création…' : 'Créer' }}
          </button>
        </div>
      </div>
      <div class="filter-bar">
        <div class="filter-tabs" role="tablist" aria-label="Type de fil">
          <button
            v-for="tab in kindTabs"
            :key="tab.id"
            type="button"
            class="filter-tab"
            :class="{ on: filterKind === tab.id }"
            role="tab"
            :aria-selected="filterKind === tab.id"
            @click="filterKind = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>
        <div class="filter-poles" role="group" aria-label="Pôle">
          <button
            v-for="p in poleTabs"
            :key="p.key"
            type="button"
            class="filter-pole"
            :class="{ on: filterPole === p.key }"
            @click="filterPole = p.key"
          >
            {{ p.label }}
          </button>
        </div>
      </div>
      <div v-if="!filteredConversations.length" class="empty filter-empty">Aucune conversation ne correspond aux filtres.</div>
    <div v-else class="wire-board">
      <section class="feed scroll-thin">
        <div class="feed-head">
          <h3 class="feed-title">Conversations ({{ filteredConversations.length }})</h3>
        </div>
        <ul class="feed-list" role="list">
          <li v-for="c in filteredConversations" :key="c.id" class="feed-item">
            <button
              type="button"
              class="feed-row"
              :class="{ on: String(c.id) === String(activeId) }"
              @click="openConv(c.id)"
            >
              <div class="feed-avatars" aria-hidden="true">
                <span class="feed-av" :title="(c.last_from_agent_id) || '—'">
                  {{ avatarEmoji(c.last_from_agent_id) }}
                </span>
                <span class="feed-av feed-av2" :title="(c.last_to_agent_id) || '—'">
                  {{ avatarEmoji(c.last_to_agent_id) }}
                </span>
              </div>
              <div class="feed-center">
                <div class="feed-line">{{ rowExchangeText(c) }}</div>
                <p class="feed-preview">{{ c.title }} — {{ c.preview }}</p>
              </div>
              <div class="feed-right">
                <span class="feed-dept" :class="{ cross: rowDeptBadge(c) === 'Cross-dept' }">{{
                  rowDeptBadge(c)
                }}</span>
                <time
                  v-if="c.last_message_at"
                  class="feed-when"
                  :datetime="wireDatetimeAttr(c.last_message_at)"
                >{{ formatRowTime(c.last_message_at) }}</time>
                <span v-else class="feed-when">—</span>
                <span class="feed-count" :title="String(c.message_count) + ' message(s)'">{{
                  c.message_count
                }}</span>
              </div>
            </button>
          </li>
        </ul>
      </section>
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
                <template v-for="line in [exchangeLine(m)]" :key="line.mode + '-' + m.id">
                  <span class="ex-pair">
                    <span :class="line.a === 'all' ? 'all-low' : 'from'">{{ line.a }}</span>
                    <span class="arrow" aria-hidden="true">→</span>
                    <span :class="line.b === 'all' ? 'all-low' : 'to'">{{ line.b }}</span>
                  </span>
                </template>
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
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import AgentsWire from '@/components/AgentsWire.vue'

const route = useRoute()

const BROADCAST_TOS = new Set(['', 'all', '*', 'everyone'])

const kindTabs = [
  { id: 'all', label: 'Tout' },
  { id: 'conversations', label: 'Conversations' },
  { id: 'broadcasts', label: 'Broadcasts' },
]

const POLE_TABS = [
  { key: 'all', label: 'Tous les pôles' },
  { key: 'recherche', label: 'Recherche' },
  { key: 'production', label: 'Production' },
  { key: 'support', label: 'Support' },
  { key: 'intelligence', label: 'Intelligence' },
  { key: 'expansion', label: 'Expansion' },
  { key: 'orchestration', label: 'Orchestration' },
]

const poleTabs = POLE_TABS
const filterKind = ref('all')
const filterPole = ref('all')
const newTitle = ref('')
const createLoading = ref(false)
const createErr = ref('')
const wireStats = ref(null)

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

const filteredConversations = computed(() => {
  let list = conversations.value
  if (filterKind.value === 'broadcasts') {
    list = list.filter((c) => c.last_is_broadcast)
  } else if (filterKind.value === 'conversations') {
    list = list.filter((c) => !c.last_is_broadcast)
  }
  if (filterPole.value !== 'all') {
    list = list.filter((c) => (c.last_pole || 'orchestration') === filterPole.value)
  }
  return list
})

const wireDateFmt = new Intl.DateTimeFormat('fr-FR', {
  dateStyle: 'long',
  timeStyle: 'short',
})

const rowTimeFmt = new Intl.DateTimeFormat('fr-FR', {
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
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

function formatRowTime(raw) {
  if (!raw) return '—'
  const d = new Date(typeof raw === 'string' ? raw.trim() : raw)
  if (Number.isNaN(d.getTime())) return '—'
  return rowTimeFmt.format(d)
}

function labelAgent(id) {
  if (!id) return '—'
  if (id === 'dashboard') return 'Dashboard'
  const a = agentsById.value[id]
  return a ? `${a.emoji} ${a.name}` : id
}

function isBroadcastTo(toId) {
  if (toId == null) return true
  return BROADCAST_TOS.has(String(toId).trim().toLowerCase())
}

function isGlobalFromId(id) {
  if (id == null || id === '') return true
  return ['all', 'everyone', 'broadcast', 'everybody', 'tous'].includes(
    String(id).trim().toLowerCase()
  )
}

function firstNameFromId(id) {
  if (id == null) return '—'
  if (id === 'dashboard') return 'Dashboard'
  if (isGlobalFromId(id)) return 'all'
  const a = agentsById.value[id]
  if (!a?.name) return id
  const w = a.name.trim().split(/\s+/)
  return w[0] || a.name
}

/**
 * Ligne de fil (message) : all → prénom, prénom → all, prénom → prénom.
 */
function exchangeLine(m) {
  const fr = m.from_agent_id
  const to = m.to_agent_id
  if (isGlobalFromId(fr) && to && !isBroadcastTo(to)) {
    return { mode: 'fromall', a: 'all', b: firstNameFromId(to) }
  }
  if (isBroadcastTo(to)) {
    return { mode: 'toall', a: firstNameFromId(fr), b: 'all' }
  }
  return { mode: 'pair', a: firstNameFromId(fr), b: firstNameFromId(to) }
}

function avatarEmoji(id) {
  if (isGlobalFromId(id)) return '⬤'
  if (id == null) return '·'
  if (isBroadcastTo(id)) return '⬤'
  if (id === 'dashboard') return '◆'
  return agentsById.value[id]?.emoji || '•'
}

function rowExchangeText(c) {
  const fa = c.last_from_agent_id
  const ta = c.last_to_agent_id
  if (isGlobalFromId(fa) && ta && !isBroadcastTo(ta)) {
    return `all → ${firstNameFromId(ta)}`
  }
  if (isBroadcastTo(ta)) {
    return `${firstNameFromId(fa)} → all`
  }
  return `${firstNameFromId(fa)} → ${firstNameFromId(ta)}`
}

function rowDeptBadge(c) {
  const fa = c.last_from_agent_id
  const ta = c.last_to_agent_id
  const poleOf = (id) => {
    if (id == null || id === 'dashboard' || isGlobalFromId(id)) return null
    if (isBroadcastTo(id)) return null
    return agentsById.value[id]?.pole || null
  }
  const pFrom = poleOf(fa)
  const pTo = poleOf(ta)
  if (pFrom && pTo && pFrom !== pTo) return 'Cross-dept'
  if (pFrom) return formatPoleLabel(pFrom)
  if (pTo) return formatPoleLabel(pTo)
  if (c.last_pole) return formatPoleLabel(c.last_pole)
  return '—'
}

function formatPoleLabel(key) {
  const t = POLE_TABS.find((p) => p.key === (key || '').toLowerCase())
  return t ? t.label : key
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
    wireStats.value = w.data.stats || null
    if (!w.data.stats && conversations.value.length) {
      const mc = w.data.items.reduce(
        (acc, c) => acc + (c.message_count || 0),
        0
      )
      wireStats.value = {
        messages: mc,
        broadcasts: 0,
        conversations: 0,
        threads: conversations.value.length,
      }
    }
    const m = {}
    for (const a of ag.data || []) m[a.id] = a
    agentsById.value = m
    agentsList.value = ag.data || []
    await nextTick()
    if (!filteredConversations.value.length) {
      activeId.value = null
    } else if (
      !activeId.value ||
      !filteredConversations.value.some(
        (c) => String(c.id) === String(activeId.value)
      )
    ) {
      await openConv(filteredConversations.value[0].id)
    } else {
      await openConv(activeId.value)
    }
  } catch (e) {
    err.value = e.response?.data?.detail || 'Wire indisponible.'
  } finally {
    loading.value = false
  }
}

async function createConversation() {
  const t = newTitle.value.trim()
  if (!t) return
  createLoading.value = true
  createErr.value = ''
  try {
    const { data } = await api.post('/api/wire/conversations', { title: t })
    newTitle.value = ''
    activeId.value = data.id
    await loadConversations()
  } catch (e) {
    createErr.value = e.response?.data?.detail || 'Création impossible.'
  } finally {
    createLoading.value = false
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

watch([filterKind, filterPole], async () => {
  if (loading.value) return
  await nextTick()
  if (!filteredConversations.value.length) {
    activeId.value = null
    return
  }
  if (!filteredConversations.value.some((c) => String(c.id) === String(activeId.value))) {
    await openConv(filteredConversations.value[0].id)
  }
})

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
.ow-details {
  border: 1px solid #ffffff12;
  border-radius: 8px;
  background: #0002;
  margin-bottom: 0.25rem;
}
.ow-summary {
  cursor: pointer;
  padding: 0.5rem 0.65rem;
  font-size: 0.72rem;
  font-family: var(--font-mono);
  color: var(--text-muted);
  list-style: none;
}
.ow-details[open] .ow-summary {
  color: #cbd5e1;
  border-bottom: 1px solid #ffffff0d;
}
.ow-inset {
  padding: 0 0.5rem 0.5rem;
  max-height: 60vh;
  overflow: auto;
}
.head {
  margin-bottom: 0.25rem;
}
.head-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 0.35rem;
}
.h2 {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 1.15rem;
  font-weight: 600;
  letter-spacing: -0.02em;
}
.sub {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-muted);
  max-width: 48rem;
  line-height: 1.45;
}
.stats-bullets {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem 0.15rem;
  margin: 0 0 0.25rem;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: #94a3b8;
  max-width: 100%;
}
.stats-dot {
  margin: 0 0.2rem;
  color: #64748b;
  user-select: none;
}
.btn-refresh {
  font: inherit;
  font-size: 0.7rem;
  font-family: var(--font-mono);
  padding: 0.35rem 0.7rem;
  border-radius: 6px;
  border: 1px solid #ffffff1a;
  background: #ffffff08;
  color: #e2e8f0;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.btn-refresh:hover:not(:disabled) {
  background: #ffffff12;
  border-color: #22c55e55;
  color: #86efac;
}
.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.head-refresh {
  flex-shrink: 0;
}
.stack {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.new-conv {
  padding: 0.75rem 0.85rem;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--bg-card);
}
.create-err {
  margin: 0 0 0.5rem;
}
.new-conv-row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.65rem;
}
.new-conv-lab {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
  min-width: 12rem;
}
.new-conv-t {
  font-size: 0.65rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.new-conv-inp {
  font: inherit;
  padding: 0.5rem 0.65rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg, #0a0a0a);
  color: inherit;
}
.new-conv-btn {
  padding: 0.5rem 0.9rem;
  border-radius: 8px;
  border: 1px solid #f59e0b55;
  background: rgba(245, 158, 11, 0.12);
  color: inherit;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}
.new-conv-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.filter-bar {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.filter-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.filter-tab {
  font: inherit;
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0.45rem 1rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-muted);
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}
.filter-tab.on,
.filter-tab:hover {
  color: #e2e8f0;
  border-color: #f59e0b55;
  background: rgba(245, 158, 11, 0.1);
}
.filter-poles {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem 0.45rem;
}
.filter-pole {
  font: inherit;
  font-size: 0.65rem;
  font-family: var(--font-mono);
  padding: 0.28rem 0.5rem;
  border-radius: 6px;
  border: 1px solid #ffffff12;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.filter-pole.on {
  border-color: #38bdf855;
  color: #7dd3fc;
  background: #0c4a6e22;
}
.filter-empty {
  margin: 0.25rem 0;
  padding: 0.5rem 0;
}
.wire-board {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(300px, 0.9fr);
  gap: 1rem;
  align-items: start;
  min-height: 420px;
}
.feed {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
  max-height: min(78vh, 720px);
  border: 1px solid var(--border);
  border-radius: 10px;
  background: #0003;
  padding: 0.5rem 0.35rem 0.65rem;
}
.feed-head {
  padding: 0.2rem 0.5rem 0.4rem;
  border-bottom: 1px solid #ffffff0d;
  margin-bottom: 0.25rem;
}
.feed-title {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 600;
  color: #e2e8f0;
  font-family: var(--font-mono);
}
.feed-list {
  list-style: none;
  margin: 0;
  padding: 0 0.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  overflow: auto;
  max-height: min(68vh, 640px);
}
.feed-item {
  margin: 0;
}
.feed-row {
  display: flex;
  align-items: center;
  gap: 0.65rem 0.75rem;
  width: 100%;
  text-align: left;
  padding: 0.55rem 0.5rem 0.55rem 0.4rem;
  border-radius: 8px;
  border: 1px solid #ffffff0d;
  background: var(--bg-card);
  color: inherit;
  font: inherit;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
  flex-wrap: wrap;
}
@media (min-width: 700px) {
  .feed-row {
    flex-wrap: nowrap;
  }
}
.feed-row:hover {
  border-color: #ffffff1a;
  background: #ffffff04;
}
.feed-row.on {
  border-color: #3b82f666;
  box-shadow: 0 0 0 1px #3b82f633 inset;
  background: #1e3a5c18;
}
.feed-avatars {
  position: relative;
  width: 2.5rem;
  height: 1.6rem;
  flex-shrink: 0;
}
.feed-av {
  position: absolute;
  left: 0;
  top: 0;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  background: #1e293b;
  border: 2px solid #0f172a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6rem;
  line-height: 1;
  z-index: 1;
}
.feed-av2 {
  left: 0.85rem;
  top: 0.2rem;
  z-index: 0;
  opacity: 0.95;
}
.feed-center {
  min-width: 0;
  flex: 1;
}
.feed-line {
  font-size: 0.8rem;
  font-weight: 500;
  color: #e2e8f0;
  line-height: 1.3;
  margin-bottom: 0.2rem;
}
.feed-preview {
  margin: 0;
  font-size: 0.7rem;
  line-height: 1.4;
  color: var(--text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.feed-right {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 0.45rem 0.65rem;
  flex-shrink: 0;
  font-size: 0.65rem;
  font-family: var(--font-mono);
  color: var(--text-muted);
}
@media (min-width: 700px) {
  .feed-right {
    flex-direction: column;
    align-items: flex-end;
  }
}
.feed-dept {
  display: inline-block;
  font-size: 0.6rem;
  text-transform: none;
  padding: 0.2rem 0.45rem;
  border-radius: 4px;
  background: #1d4ed820;
  color: #7dd3fc;
  border: 1px solid #38bdf833;
  max-width: 6rem;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.feed-dept.cross {
  background: #3b82f61a;
  color: #93c5fd;
  border-color: #60a5fa44;
}
.feed-when {
  color: #94a3b8;
  font-size: 0.64rem;
  white-space: nowrap;
}
.feed-count {
  min-width: 1.4rem;
  height: 1.4rem;
  padding: 0 0.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: #0f172a;
  color: #cbd5e1;
  font-size: 0.62rem;
  font-weight: 600;
  border: 1px solid #334155;
}
.muted,
.err {
  font-family: var(--font-mono);
  font-size: 0.85rem;
}
.err {
  color: var(--danger);
}
.thread {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
  max-height: min(78vh, 720px);
  overflow: auto;
}
.ex-pair {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.2rem 0.35rem;
}
.all-low {
  color: #94a3b8;
  font-size: 0.85em;
  font-weight: 500;
  letter-spacing: 0.03em;
  text-transform: none;
}
@media (max-width: 900px) {
  .wire-board {
    grid-template-columns: 1fr;
  }
  .feed {
    max-height: min(50vh, 420px);
  }
  .thread {
    max-height: min(50vh, 400px);
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
