<template>
  <div class="panel">
    <h2 class="h">Intel — veille &amp; décision <span class="sub">(Édith)</span></h2>

    <div v-if="intelKpis" class="kpi-strip">
      <div class="kpi" :class="{ alert: intelKpis.avg_days_alert }">
        <span class="kpi-l">Délai moy. → décision</span>
        <span class="kpi-v">
          {{ intelKpis.avg_days_new_to_decision != null ? `${Number(intelKpis.avg_days_new_to_decision).toFixed(1)} j` : '—' }}
        </span>
      </div>
      <div class="kpi" :class="{ alert: intelKpis.implementation_rate_alert }">
        <span class="kpi-l">Taux implémentation</span>
        <span class="kpi-v">
          {{
            intelKpis.implementation_rate_pct != null
              ? `${Math.round(intelKpis.implementation_rate_pct)} %`
              : '—'
          }}
        </span>
      </div>
      <div class="kpi" :class="{ alert: intelKpis.approved_without_task_alert }">
        <span class="kpi-l">Approved sans tâche</span>
        <span class="kpi-v">{{ intelKpis.approved_without_task }}</span>
      </div>
      <div class="kpi" :class="{ alert: intelKpis.implementing_stuck_alert }">
        <span class="kpi-l">Implementing &gt; 14 j</span>
        <span class="kpi-v">{{ intelKpis.implementing_stuck_over_14d }}</span>
      </div>
    </div>

    <ul class="feed">
      <li v-for="item in items" :key="item.id" class="line" :class="[`priority-${item.priority || 'normal'}`, { inbox: needsDecision(item) }]">
        <div class="top">
          <span v-if="item.score != null" class="score">{{ item.score }}/10</span>
          <span class="title">{{ item.title }}</span>
        </div>
        <div class="meta">
          <span v-if="item.agent_name" class="agent-badge">{{ item.agent_name }}</span>
          <span class="category-tag">{{ item.category || item.type }}</span>
        </div>
        <p v-if="item.note" class="yvon-note">{{ item.note }}</p>

        <div v-if="needsDecision(item)" class="decision-row">
          <select v-model="priorities[item.id]" class="prio-select">
            <option value="low">Basse</option>
            <option value="normal">Normale</option>
            <option value="high">Haute</option>
            <option value="critical">Critique</option>
          </select>
          <input v-model="notes[item.id]" class="note-input" type="text" placeholder="Note optionnelle…" />
          <button type="button" class="btn-approve" :disabled="busyId === item.id" @click="decide(item, 'approve')">
            Approuver + créer tâche
          </button>
          <button type="button" class="btn-reject" :disabled="busyId === item.id" @click="decide(item, 'reject')">
            Rejeter
          </button>
        </div>

        <div v-if="item.task_id" class="task-link">
          Tâche #{{ item.task_id }}
          <span v-if="item.task_status" class="task-st">— {{ item.task_status }}</span>
        </div>

        <div v-if="item.status === 'implemented'" class="verify-row">
          <button type="button" class="btn-verify" :disabled="busyId === item.id" @click="verify(item)">
            Marquer vérifié (prod)
          </button>
        </div>

        <div class="bot">
          <span class="src">{{ item.source }}</span>
          <span :class="['stat', item.status]">{{ item.status }}</span>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import api from '@/api'

const props = defineProps({
  items: { type: Array, default: () => [] },
  intelKpis: { type: Object, default: null },
})

const emit = defineEmits(['refresh'])

const priorities = reactive({})
const notes = reactive({})
const busyId = ref(null)

watch(
  () => props.items,
  (list) => {
    for (const it of list || []) {
      if (priorities[it.id] === undefined) priorities[it.id] = it.priority || 'normal'
      if (notes[it.id] === undefined) notes[it.id] = ''
    }
  },
  { immediate: true },
)

function needsDecision(item) {
  return ['new', 'reviewed', 'pending_decision'].includes(item.status)
}

async function decide(item, action) {
  busyId.value = item.id
  try {
    await api.patch(`/api/ops/intel/${item.id}/decide`, {
      action,
      note: notes[item.id] || null,
      priority: priorities[item.id] || 'normal',
    })
    emit('refresh')
  } catch (e) {
    console.error(e)
    alert(e.response?.data?.detail || 'Décision impossible.')
  } finally {
    busyId.value = null
  }
}

async function verify(item) {
  busyId.value = item.id
  try {
    await api.patch(`/api/ops/intel/${item.id}/verify`)
    emit('refresh')
  } catch (e) {
    console.error(e)
    alert(e.response?.data?.detail || 'Vérification impossible.')
  } finally {
    busyId.value = null
  }
}
</script>

<style scoped>
.panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem 0.85rem;
  min-height: 200px;
}
.h {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin: 0 0 0.75rem 0.25rem;
  font-weight: 700;
}
.sub {
  text-transform: none;
  font-weight: 400;
  color: var(--info);
  letter-spacing: 0;
}
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.45rem 0.65rem;
  margin-bottom: 0.85rem;
  font-family: var(--font-mono);
  font-size: 0.62rem;
}
@media (min-width: 640px) {
  .kpi-strip {
    grid-template-columns: repeat(4, 1fr);
  }
}
.kpi {
  padding: 0.35rem 0.45rem;
  border-radius: 6px;
  background: #ffffff06;
  border: 1px solid #ffffff10;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.kpi.alert {
  border-color: rgba(248, 113, 113, 0.45);
  background: rgba(248, 113, 113, 0.08);
}
.kpi-l {
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.kpi-v {
  color: var(--text);
  font-size: 0.75rem;
  font-weight: 600;
}
.feed {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  max-height: min(420px, 52vh);
  overflow: auto;
}
.line {
  padding: 0.6rem 0.45rem;
  border-left: 2px solid var(--info);
  background: #ffffff04;
  border-radius: 0 6px 6px 0;
}
.line.inbox {
  border-left-color: var(--accent);
  background: rgba(245, 158, 11, 0.06);
}
.line.priority-critical {
  border-left-color: #f87171;
}
.top {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}
.score {
  flex-shrink: 0;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--accent);
  padding: 0.1rem 0.35rem;
  background: rgba(245, 158, 11, 0.12);
  border-radius: 4px;
}
.title {
  font-size: 0.82rem;
  line-height: 1.35;
}
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.35rem;
  font-size: 0.62rem;
  font-family: var(--font-mono);
}
.agent-badge {
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  background: rgba(59, 130, 246, 0.15);
  color: var(--info);
}
.category-tag {
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.yvon-note {
  margin: 0.4rem 0 0;
  font-size: 0.72rem;
  color: var(--text-muted);
  line-height: 1.4;
  font-style: italic;
}
.decision-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.55rem;
}
.prio-select,
.note-input {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  padding: 0.25rem 0.35rem;
  border-radius: 4px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
}
.note-input {
  flex: 1;
  min-width: 120px;
}
.btn-approve,
.btn-reject,
.btn-verify {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.35rem 0.55rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}
.btn-approve {
  background: rgba(16, 185, 129, 0.25);
  color: var(--success);
}
.btn-reject {
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
}
.btn-verify {
  background: rgba(59, 130, 246, 0.2);
  color: var(--info);
}
.btn-approve:disabled,
.btn-reject:disabled,
.btn-verify:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.task-link {
  margin-top: 0.4rem;
  font-size: 0.68rem;
  font-family: var(--font-mono);
  color: var(--success);
}
.task-st {
  color: var(--text-muted);
}
.verify-row {
  margin-top: 0.45rem;
}
.bot {
  display: flex;
  justify-content: space-between;
  margin-top: 0.45rem;
  font-size: 0.65rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.stat {
  text-transform: uppercase;
  font-size: 0.58rem;
}
.stat.implemented,
.stat.verified {
  color: var(--success);
}
.stat.pending_decision,
.stat.new,
.stat.reviewed {
  color: var(--warning);
}
.stat.borderline {
  color: var(--danger);
}
.stat.approved {
  color: var(--info);
}
.stat.implementing {
  color: #a78bfa;
}
.stat.rejected {
  color: var(--danger);
}
</style>
