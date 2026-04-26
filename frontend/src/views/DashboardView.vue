<template>
  <div v-if="loading" class="loading">Chargement…</div>
  <div v-else-if="err" class="err">{{ err }}</div>
  <div v-else class="dashboard">
    <div class="human">
      <strong>Ton pilotage</strong> — trois leviers : valider une phase (Timeline), fournir une clé API
      (module ci-dessous), feedback stratégique (Wire / Crew). Le reste est autonome entre agents.
    </div>
    <KpiGrid :items="kpiItems" />
    <div class="openclaw" v-if="oc">
      <span class="oc-label">OpenClaw</span>
      <span v-if="!oc.configured" class="oc-off">Non configuré</span>
      <span v-else class="oc-on">Gateway connecté</span>
    </div>
    <div class="row-panels">
      <AppList :apps="data.apps" />
      <IntelFeed :items="data.intel" />
    </div>
    <AgentOpsPanel />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '@/api'
import KpiGrid from '@/components/dashboard/KpiGrid.vue'
import AppList from '@/components/dashboard/AppList.vue'
import IntelFeed from '@/components/dashboard/IntelFeed.vue'
import AgentOpsPanel from '@/components/dashboard/AgentOpsPanel.vue'

const data = ref({ kpis: null, apps: [], intel: [] })
const loading = ref(true)
const err = ref('')
const oc = ref(null)

const kpiItems = computed(() => {
  const k = data.value.kpis
  if (!k) return []
  return [
    { label: 'MRR total', value: `$${Number(k.mrr_total).toFixed(0)}`, color: 'var(--accent)' },
    { label: 'Apps live', value: String(k.apps_live), color: 'var(--success)' },
    { label: 'Agents actifs', value: String(k.agents_active), color: 'var(--success)' },
    { label: 'Churn moy.', value: `${Number(k.churn_avg).toFixed(1)}%` },
    { label: 'Downloads / mois', value: String(k.downloads_month) },
    { label: 'ASO moyen', value: Number(k.aso_score_avg).toFixed(0) },
  ]
})

onMounted(async () => {
  try {
    const [dash, sup] = await Promise.all([
      api.get('/api/dashboard'),
      api.get('/api/supervision/openclaw').catch(() => ({ data: null })),
    ])
    data.value = dash.data
    oc.value = sup.data
  } catch (e) {
    err.value = e.response?.data?.detail || 'Impossible de charger le dashboard.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.loading,
.err {
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 0.9rem;
}
.err {
  color: var(--danger);
}
.human {
  font-size: 0.78rem;
  color: var(--text-muted);
  line-height: 1.5;
  margin-bottom: 1rem;
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  border: 1px solid #ffffff10;
  background: rgba(59, 130, 246, 0.06);
}
.human strong {
  color: var(--info);
  font-weight: 600;
}
.row-panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  align-items: start;
}
@media (max-width: 960px) {
  .row-panels {
    grid-template-columns: 1fr;
  }
}
.openclaw {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: -0.5rem 0 1rem;
  font-size: 0.75rem;
  font-family: var(--font-mono);
}
.oc-label {
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.oc-off {
  color: var(--text-muted);
}
.oc-on {
  color: var(--success);
}
</style>
