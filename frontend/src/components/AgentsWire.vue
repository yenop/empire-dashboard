<template>
  <section class="ow">
    <header class="ow-head">
      <h2 class="ow-h2">OpenClaw — agents (crons)</h2>
      <p class="ow-sub">
        Lectures locales des fichiers cron. Rafraîchissement automatique 30s.
        <span v-if="!meta.configured" class="warn">Volume OpenClaw non monté.</span>
      </p>
    </header>
    <div v-if="loading" class="muted">Chargement des agents…</div>
    <div v-else-if="err" class="err">{{ err }}</div>
    <div v-else class="ow-body">
      <div v-for="g in byPole" :key="g.pole" class="pole">
        <h3 class="pole-t">{{ g.label }}</h3>
        <ul class="agents">
          <li
            v-for="a in g.items"
            :key="a.key"
            :class="['acard', a.status, { 'has-err': (a.consecutiveErrors || 0) > 0 }]"
          >
            <button
              type="button"
              class="acard-btn"
              :disabled="!a.jobId"
              @click="open(a)"
            >
              <span :class="['dot', statusDot(a)]" aria-hidden="true" />
              <span class="aname">{{ a.name }} — {{ a.label }}</span>
              <span v-if="(a.consecutiveErrors || 0) > 0" class="badge-err" title="Erreurs consécutives (jobs.json)">
                +{{ a.consecutiveErrors }} erreur(s) suite
              </span>
            </button>
            <p v-if="a.lastRun?.summary" class="excerpt">
              {{ truncate(a.lastRun.summary) }}
            </p>
            <p v-else-if="!a.jobId" class="excerpt muted2">Cron non créé — remplir jobId côté backend (Gaston)</p>
          </li>
        </ul>
      </div>
    </div>
    <Teleport to="body">
      <div v-if="drawer" class="drawer-back" @click.self="drawer = null">
        <aside class="drawer">
          <button type="button" class="x" @click="drawer = null" aria-label="Fermer">×</button>
          <h3 v-if="drawer" class="d-name">{{ drawer.name }} — {{ drawer.label }}</h3>
          <div v-if="repLoad" class="muted">Rapport…</div>
          <template v-else-if="drawerData">
            <p v-if="drawerData.latest" class="d-stat">
              Dernier run
              <span v-if="drawerData.latest.tokens != null" class="tok">
                · {{ drawerData.latest.tokens }} tokens
              </span>
              <time v-if="drawerData.latest.ts"> · {{ drawerData.latest.ts }}</time>
            </p>
            <pre v-if="drawerData.latest?.summary" class="d-summary">{{ drawerData.latest.summary }}</pre>
            <h4 class="d-h4">Historique des runs</h4>
            <ul class="runs">
              <li v-for="(r, i) in drawerData.runs" :key="i" class="run">
                <span :class="['r-dot', r.status]" />
                <div class="r-text">
                  <div class="r-line">
                    <time>{{ r.ts || '—' }}</time>
                    <span v-if="r.tokens != null" class="tok"> · {{ r.tokens }} tok.</span>
                    <span v-if="r.model" class="m"> · {{ r.model }}</span>
                  </div>
                  <p v-if="r.summary" class="r-sum">{{ truncate(r.summary, 200) }}</p>
                </div>
              </li>
            </ul>
            <p v-if="!drawerData.runs.length" class="muted">Aucun run enregistré dans le .jsonl.</p>
          </template>
        </aside>
      </div>
    </Teleport>
  </section>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import api from '@/api'

const OPENCLAW_API = '/api/supervision'
const POLE_ORDER = [
  { key: 'recherche', label: 'Recherche' },
  { key: 'intelligence', label: 'Intelligence' },
  { key: 'production', label: 'Production' },
  { key: 'support', label: 'Support' },
  { key: 'expansion', label: 'Expansion' },
  { key: 'orchestration', label: 'Orchestration' },
]

const loading = ref(true)
const err = ref('')
const agents = ref([])
const meta = ref({ configured: true })
const drawer = ref(null)
const drawerData = ref(null)
const repLoad = ref(false)
let timer

function statusDot(a) {
  if (!a.jobId) return 'idle'
  if (a.status === 'not_configured' || a.status === 'disabled') return 'idle'
  if (a.status === 'error' || a.status === 'err') return 'err'
  if (a.status === 'ok' || a.status === 'success') return 'ok'
  return 'idle'
}

const byPole = computed(() => {
  const m = new Map(POLE_ORDER.map((p) => [p.key, { ...p, items: [] }]))
  for (const a of agents.value) {
    const p = a.pole || 'orchestration'
    if (!m.has(p)) m.set(p, { key: p, label: p, items: [] })
    m.get(p).items.push(a)
  }
  const oi = (k) => {
    const i = POLE_ORDER.findIndex((x) => x.key === k)
    return i === -1 ? 200 : i
  }
  return Array.from(m.values())
    .filter((g) => g.items && g.items.length)
    .sort((a, b) => oi(a.key) - oi(b.key) || a.label.localeCompare(b.label))
})

function truncate(s, n = 120) {
  if (!s || typeof s !== 'string') return ''
  const t = s.replace(/\s+/g, ' ').trim()
  if (t.length <= n) return t
  return t.slice(0, n) + '…'
}

async function load() {
  err.value = ''
  try {
    const { data } = await api.get(`${OPENCLAW_API}/openclaw/agents`)
    meta.value = { configured: data.configured !== false, message: data.message }
    agents.value = data.agents || []
  } catch (e) {
    err.value = e.response?.data?.detail || 'Supervision OpenClaw indisponible.'
  } finally {
    loading.value = false
  }
}

async function open(a) {
  if (!a.jobId) return
  drawer.value = a
  drawerData.value = null
  repLoad.value = true
  try {
    const { data } = await api.get(
      `${OPENCLAW_API}/openclaw/agents/${a.jobId}/report`
    )
    drawerData.value = data
  } catch (e) {
    drawerData.value = {
      latest: a.lastRun ? { ...a.lastRun, summary: a.lastRun.summary } : null,
      runs: [],
    }
  } finally {
    repLoad.value = false
  }
}

onMounted(() => {
  load()
  timer = setInterval(load, 30_000)
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.ow {
  margin-bottom: 1.5rem;
  padding: 0 0 0.5rem;
  border-bottom: 1px solid #ffffff12;
}
.ow-h2 {
  margin: 0 0 0.35rem;
  font-family: var(--font-mono);
  font-size: 0.95rem;
  font-weight: 600;
}
.ow-sub {
  margin: 0 0 0.75rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.4;
  max-width: 52rem;
}
.warn {
  color: #f59e0b;
  margin-left: 0.35rem;
}
.muted,
.muted2 {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.muted2 {
  font-style: italic;
}
.err {
  color: var(--danger);
  font-family: var(--font-mono);
  font-size: 0.85rem;
}
.ow-body {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.pole-t {
  margin: 0 0 0.5rem;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  font-weight: 600;
}
.agents {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.acard {
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  overflow: hidden;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.acard.has-err {
  border-color: #ef4444aa;
  box-shadow: 0 0 0 1px #ef444433 inset;
}
.acard-btn {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem 0.5rem;
  width: 100%;
  text-align: left;
  padding: 0.55rem 0.65rem;
  border: none;
  background: transparent;
  color: inherit;
  font: inherit;
  cursor: pointer;
}
.acard-btn:disabled {
  cursor: default;
  opacity: 0.9;
}
.aname {
  font-size: 0.8rem;
  font-weight: 500;
  flex: 1;
  min-width: 0;
}
.badge-err {
  font-size: 0.58rem;
  font-family: var(--font-mono);
  color: #f87171;
  white-space: nowrap;
}
.excerpt {
  margin: 0 0.65rem 0.55rem;
  font-size: 0.68rem;
  color: var(--text-muted);
  line-height: 1.4;
}
.dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  flex-shrink: 0;
  background: #6b7280;
}
.dot.ok {
  background: #22c55e;
  box-shadow: 0 0 6px #22c55e99;
  animation: opulse 1.4s ease-in-out infinite;
}
.dot.err {
  background: #ef4444;
  box-shadow: 0 0 4px #ef444499;
  animation: epulse 1.2s ease-in-out infinite;
}
.dot.idle {
  background: #6b7280;
}
@keyframes opulse {
  0%,
  100% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
}
@keyframes epulse {
  0%,
  100% {
    opacity: 0.85;
  }
  50% {
    opacity: 0.4;
  }
}
.drawer-back {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: #0009;
  display: flex;
  justify-content: flex-end;
  align-items: stretch;
  animation: fade 0.15s;
}
.drawer {
  width: min(32rem, 100vw);
  max-height: 100vh;
  overflow: auto;
  background: var(--bg-card);
  border-left: 1px solid var(--border);
  padding: 1rem 1.1rem 1.5rem;
  position: relative;
  box-shadow: -8px 0 32px #0004;
  animation: slide 0.2s ease;
}
@keyframes fade {
  from {
    opacity: 0;
  }
}
@keyframes slide {
  from {
    transform: translateX(0.5rem);
  }
}
.d-name {
  margin: 0 0 0.75rem;
  font-size: 0.9rem;
  line-height: 1.3;
  padding-right: 2rem;
  font-weight: 600;
}
.d-stat,
.d-h4 {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.d-stat {
  margin: 0 0 0.5rem;
  text-transform: none;
  letter-spacing: 0;
}
.tok,
.m {
  color: var(--text-muted);
}
.d-summary {
  margin: 0 0 1rem;
  font-size: 0.8rem;
  line-height: 1.5;
  white-space: pre-wrap;
  background: #0002;
  padding: 0.6rem 0.65rem;
  border-radius: 8px;
  max-height: min(40vh, 320px);
  overflow: auto;
}
.d-h4 {
  margin: 0 0 0.4rem;
}
.runs {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.run {
  display: flex;
  gap: 0.45rem;
  font-size: 0.75rem;
  line-height: 1.4;
  border-bottom: 1px solid #ffffff0a;
  padding-bottom: 0.4rem;
}
.r-dot {
  width: 0.35rem;
  height: 0.35rem;
  border-radius: 50%;
  margin-top: 0.35rem;
  flex-shrink: 0;
  background: #6b7280;
}
.r-dot.ok {
  background: #22c55e;
}
.r-dot.error,
.r-dot.err {
  background: #ef4444;
}
.r-line {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--text-muted);
}
.r-sum {
  margin: 0.2rem 0 0;
  color: #cbd5e1;
  white-space: pre-wrap;
  word-break: break-word;
}
.x {
  position: absolute;
  right: 0.65rem;
  top: 0.55rem;
  width: 1.8rem;
  height: 1.8rem;
  border: none;
  background: #ffffff0d;
  color: inherit;
  font-size: 1.1rem;
  line-height: 1;
  border-radius: 6px;
  cursor: pointer;
}
</style>
