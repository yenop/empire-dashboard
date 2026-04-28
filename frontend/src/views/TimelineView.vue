<template>
  <div v-if="loading" class="muted">Chargement…</div>
  <div v-else-if="err" class="err">{{ err }}</div>
  <div v-else class="timeline-page">
    <header class="head">
      <div>
        <h2 class="h2">Timeline — coordination par phases</h2>
        <p class="sub">
          Phase <strong>{{ wf.phase }}</strong> / 10 · seuls les agents de la phase courante sont « allumés » dans le Crew et la topbar.
          <span v-if="wf.last_validated_at" class="muted-inline">
            Dernière validation : {{ wf.last_validated_at }}
          </span>
        </p>
      </div>
      <div class="actions">
        <button
          type="button"
          class="btn-primary"
          :disabled="wf.phase >= 10 || busy || !canAdvance"
          :title="
            wf.phase >= 10 || canAdvance
              ? ''
              : 'Complète tous les livrables requis de la phase courante'
          "
          @click="advance"
        >
          Valider &amp; avancer →
        </button>
        <button type="button" class="btn-ghost" :disabled="busy" @click="resetWf">Réinitialiser phase 1</button>
      </div>
    </header>

    <div class="current-card" v-if="wf.current">
      <div class="accent" />
      <div class="cur-title">En cours — {{ wf.current.title }}</div>
      <p class="cur-sum">{{ wf.current.summary }}</p>

      <div class="deliverables-gate">
        <div class="gate-title">Livrables phase {{ wf.phase }}</div>
        <div
          v-for="item in deliverables"
          :key="item.key"
          class="deliverable-row"
        >
          <span
            class="check-icon"
            :class="item.checked_at ? 'done' : 'pending'"
          >
            {{ item.checked_at ? '✓' : '○' }}
          </span>
          <span class="deliverable-label">{{ item.label }}</span>
          <button
            v-if="!item.auto_check && !item.checked_at"
            type="button"
            class="check-btn"
            :disabled="busy"
            @click="checkDeliverable(item.key)"
          >
            Valider
          </button>
          <span v-if="item.checked_at" class="auto-label">
            {{ item.checked_by === 'auto' ? 'auto' : 'validé' }}
          </span>
        </div>
      </div>

      <div class="chips">
        <span
          v-for="aid in wf.current.agents"
          :key="aid"
          class="chip"
          :style="chipStyle(aid)"
        >
          {{ agentEmoji(aid) }} {{ agentName(aid) }}
        </span>
      </div>
    </div>

    <div class="phases-scroll scroll-thin">
      <div
        v-for="p in wf.phases"
        :key="p.index"
        class="phase-card"
        :class="{ active: p.index === wf.phase, done: p.index < wf.phase }"
      >
        <div class="phase-num">{{ p.index }}</div>
        <div class="phase-title">{{ p.title }}</div>
        <div class="phase-agents">{{ (p.agents || []).length }} agents</div>
      </div>
    </div>

    <section class="crons">
      <h3 class="h3">Crons du workflow</h3>
      <p class="cron-hint">
        Tâches planifiées (référence OpenClaw / orchestrateur) — Marlène / Gaston décalés, veille Marcel & Édith, fenêtre nocturne Yvon.
      </p>
      <ul class="cron-list">
        <li v-for="c in crons" :key="c.id">
          <code>{{ c.schedule }}</code>
          <span>{{ c.label }}</span>
          <span class="cron-phase">{{ c.phase }}</span>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '@/api'

const loading = ref(true)
const busy = ref(false)
const err = ref('')
const wf = ref({
  phase: 1,
  phases: [],
  current: null,
  lit_agent_ids: [],
  last_validated_at: null,
})
const agentsById = ref({})
const crons = ref([])
const deliverables = ref([])

const canAdvance = computed(() =>
  deliverables.value.filter((d) => d.required).every((d) => d.checked_at != null),
)

function agentEmoji(id) {
  return agentsById.value[id]?.emoji || '·'
}
function agentName(id) {
  return agentsById.value[id]?.name || id
}
function chipStyle(id) {
  const c = agentsById.value[id]?.color
  return c ? { borderColor: `${c}55`, color: c } : {}
}

async function fetchDeliverables() {
  try {
    const { data } = await api.get('/api/workflow/deliverables')
    deliverables.value = data || []
  } catch {
    deliverables.value = []
  }
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const [w, ag, cr] = await Promise.all([
      api.get('/api/workflow'),
      api.get('/api/agents'),
      api.get('/api/ops/crons'),
      fetchDeliverables(),
    ])
    wf.value = w.data
    crons.value = cr.data || []
    const m = {}
    for (const a of ag.data || []) m[a.id] = a
    agentsById.value = m
  } catch (e) {
    err.value = e.response?.data?.detail || 'Impossible de charger la timeline.'
  } finally {
    loading.value = false
  }
}

async function checkDeliverable(key) {
  busy.value = true
  try {
    await api.patch(`/api/workflow/deliverables/${encodeURIComponent(key)}/check`)
    await fetchDeliverables()
    err.value = ''
  } catch (e) {
    err.value = e.response?.data?.detail || e.message
  } finally {
    busy.value = false
  }
}

async function advance() {
  busy.value = true
  try {
    const { data } = await api.post('/api/workflow/advance')
    wf.value = data
    await fetchDeliverables()
    err.value = ''
  } catch (e) {
    err.value = e.response?.data?.detail || e.message
  } finally {
    busy.value = false
  }
}

async function resetWf() {
  if (!confirm('Revenir à la phase 1 ?')) return
  busy.value = true
  try {
    const { data } = await api.post('/api/workflow/reset')
    wf.value = data
    await fetchDeliverables()
    err.value = ''
  } catch (e) {
    err.value = e.response?.data?.detail || e.message
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.muted,
.err {
  font-family: var(--font-mono);
  font-size: 0.9rem;
}
.err {
  color: var(--danger);
}
.timeline-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}
.h2 {
  margin: 0 0 0.35rem;
  font-family: var(--font-mono);
  font-size: 1rem;
  letter-spacing: 0.04em;
}
.sub {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-muted);
  max-width: 52rem;
  line-height: 1.5;
}
.muted-inline {
  display: block;
  margin-top: 0.35rem;
  opacity: 0.85;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.btn-primary {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  padding: 0.55rem 1rem;
  border-radius: 8px;
  border: 1px solid #f59e0b66;
  background: linear-gradient(180deg, rgba(245, 158, 11, 0.25), rgba(245, 158, 11, 0.08));
  color: var(--accent);
  cursor: pointer;
}
.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.btn-ghost {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}
.current-card {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem 1rem 1rem;
  overflow: hidden;
}
.current-card .accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--violet));
}
.cur-title {
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 0.35rem;
}
.cur-sum {
  margin: 0 0 0.75rem;
  font-size: 0.8rem;
  color: var(--text-muted);
  line-height: 1.45;
}
.deliverables-gate {
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid #ffffff12;
  background: #00000018;
}
.gate-title {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}
.deliverable-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 0.5rem;
  align-items: center;
  font-size: 0.78rem;
  padding: 0.35rem 0;
  border-bottom: 1px solid #ffffff08;
}
.deliverable-row:last-child {
  border-bottom: none;
}
.check-icon {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  width: 1.25rem;
  text-align: center;
}
.check-icon.done {
  color: var(--cyan);
}
.check-icon.pending {
  color: var(--text-muted);
  opacity: 0.7;
}
.deliverable-label {
  line-height: 1.35;
}
.check-btn {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--accent);
  cursor: pointer;
}
.check-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.auto-label {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--text-muted);
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.chip {
  font-size: 0.72rem;
  font-family: var(--font-mono);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: #ffffff06;
}
.phases-scroll {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
}
.phase-card {
  flex: 0 0 140px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.65rem 0.5rem;
  opacity: 0.55;
}
.phase-card.active {
  opacity: 1;
  border-color: #f59e0b55;
  box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.15);
}
.phase-card.done {
  opacity: 0.75;
}
.phase-num {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--accent);
  margin-bottom: 0.25rem;
}
.phase-title {
  font-size: 0.72rem;
  font-weight: 600;
  line-height: 1.3;
  margin-bottom: 0.2rem;
}
.phase-agents {
  font-size: 0.6rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.crons {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
}
.h3 {
  margin: 0 0 0.5rem;
  font-family: var(--font-mono);
  font-size: 0.85rem;
}
.cron-hint {
  margin: 0 0 0.75rem;
  font-size: 0.78rem;
  color: var(--text-muted);
  line-height: 1.45;
}
.cron-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.cron-list li {
  display: grid;
  grid-template-columns: minmax(0, 8.5rem) minmax(0, 1fr) auto;
  gap: 0.5rem;
  align-items: baseline;
  font-size: 0.75rem;
  border-bottom: 1px solid #ffffff08;
  padding-bottom: 0.35rem;
}
@media (max-width: 560px) {
  .cron-list li {
    grid-template-columns: 1fr;
    align-items: start;
    gap: 0.25rem;
  }
  .cron-list code {
    word-break: break-word;
  }
  .cron-phase {
    justify-self: start;
  }
}
.cron-list code {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--cyan);
}
.cron-phase {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--text-muted);
}
</style>
