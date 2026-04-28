<template>
  <div class="process">
    <div v-if="loading" class="muted">Chargement…</div>
    <div v-else-if="err" class="err">{{ err }}</div>
    <template v-else>
      <header class="head">
        <div>
          <h2 class="h2">Process recherche de niches</h2>
          <p class="sub">
            Ref : cours AFFISEO M08 — pipeline complet de la découverte à la décision.
            Les agents <strong>Marlène</strong> (business) et <strong>Gaston</strong> (SEO) préparent la
            matière ; la décision GO / NO-GO est tranchée par toi (Nicolas).
          </p>
        </div>
      </header>

      <ProcessPipeline :pipeline="payload.pipeline" />

      <p class="wire-auto-hint muted">
        Les fils Wire de Marlène et Gaston sont <strong>détectés automatiquement</strong> comme sur la page Wire
        (job OpenClaw par agent, ou conversation DB la plus récente qui les concerne). Les envois restent sur Wire.
      </p>

      <div class="pills" role="tablist" aria-label="Agent">
        <button
          type="button"
          role="tab"
          :aria-selected="tab === 'marlene'"
          class="pill tab-ml"
          :class="{ on: tab === 'marlene' }"
          @click="tab = 'marlene'"
        >
          Marlène — Business (7 critères)
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="tab === 'gaston'"
          class="pill tab-ga"
          :class="{ on: tab === 'gaston' }"
          @click="tab = 'gaston'"
        >
          Gaston — SEO (3 critères + données)
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="tab === 'decision'"
          class="pill tab-de"
          :class="{ on: tab === 'decision' }"
          @click="tab = 'decision'"
        >
          Décision — Nicolas
        </button>
      </div>

      <div v-show="tab === 'marlene'" class="panel">
        <p class="wire-row">
          <RouterLink class="wire-link" :to="{ name: 'wire', query: { agent: 'marlene' } }">
            Ouvrir le Wire — Marlène
          </RouterLink>
          <span class="wire-hint">Propositions, consignes, compte rendu vers l’agent.</span>
        </p>

        <ProcessWireFeed
          lane-filter="marlene"
          :items="wireFeed.items"
          :warnings="wireFeed.warnings"
          :configured="wireFeed.configured"
          :loading="wireFeed.loading"
          :err="wireFeed.err"
          @refresh="loadWireFeed"
        />

        <section class="handoff card">
          <h4 class="hand-title">Mots-clés identitaires niche → Gaston</h4>
          <p class="hand-desc">
            Saisie côté Marlène ; affichée en lecture sur l’onglet Gaston comme filtre pour les seeds SEO.
          </p>
          <textarea
            v-model="handoffText"
            class="ta"
            rows="4"
            placeholder="Liste de mots-clés identitaires (une ligne ou phrases séparées par virgule)…"
            @blur="saveHandoff"
          />
        </section>

        <ProcessChecklist
          title="Checklist Marlène"
          icon="🔍"
          :steps="payload.marlene.steps"
          :items-checked="state.items_checked"
          border-accent="#ec4899"
          @toggle-item="onToggleItem"
        />

        <label class="notes card">
          <span class="nl">Synthèse Marlène (notes)</span>
          <textarea
            v-model="notesLocal.marlene_synthese"
            class="ta"
            rows="3"
            @blur="saveNotes"
          />
        </label>
      </div>

      <div v-show="tab === 'gaston'" class="panel">
        <p class="wire-row">
          <RouterLink class="wire-link" :to="{ name: 'wire', query: { agent: 'gaston' } }">
            Ouvrir le Wire — Gaston
          </RouterLink>
          <span class="wire-hint">Collecte SEO, filtrage, verdict — dialogue avec l’agent.</span>
        </p>

        <ProcessWireFeed
          lane-filter="gaston"
          :items="wireFeed.items"
          :warnings="wireFeed.warnings"
          :configured="wireFeed.configured"
          :loading="wireFeed.loading"
          :err="wireFeed.err"
          @refresh="loadWireFeed"
        />

        <section class="handoff card readonly">
          <h4 class="hand-title">Mots-clés identitaires (depuis Marlène)</h4>
          <p v-if="!identityKwPreview" class="empty-hint">Renseigne le bloc Marlène pour voir le filtre ici.</p>
          <pre v-else class="kw-preview">{{ identityKwPreview }}</pre>
        </section>

        <ProcessChecklist
          title="Checklist Gaston"
          icon="📊"
          :steps="payload.gaston.steps"
          :items-checked="state.items_checked"
          border-accent="#3b82f6"
          @toggle-item="onToggleItem"
        />

        <label class="notes card">
          <span class="nl">Verdict Gaston (notes)</span>
          <textarea
            v-model="notesLocal.gaston_verdict"
            class="ta"
            rows="3"
            @blur="saveNotes"
          />
        </label>
      </div>

      <div v-show="tab === 'decision'" class="panel decision">
        <ProcessWireFeed
          lane-filter="all"
          :items="wireFeed.items"
          :warnings="wireFeed.warnings"
          :configured="wireFeed.configured"
          :loading="wireFeed.loading"
          :err="wireFeed.err"
          @refresh="loadWireFeed"
        />
        <ProcessScoringPanel
          :scores-business="state.scores_business"
          :scores-seo="state.scores_seo"
          :computed="computedScores"
          @update-business="onScoreBiz"
          @update-seo="onScoreSeo"
        />
        <ProcessRedFlags
          :definitions="payload.red_flags"
          :red-flags="state.red_flags"
          @toggle="onRedFlag"
        />
        <label class="notes card">
          <span class="nl">Décision Nicolas — synthèse GO / NO-GO</span>
          <textarea
            v-model="notesLocal.nicolas_decision"
            class="ta"
            rows="4"
            @blur="saveNotes"
          />
        </label>
      </div>

      <footer class="foot-meta">
        Process v1.0 — 28 avril 2026 — Ref : cours AFFISEO M08 (L01 + L02 + L03).
      </footer>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import api from '@/api'
import ProcessPipeline from '@/components/process/ProcessPipeline.vue'
import ProcessChecklist from '@/components/process/ProcessChecklist.vue'
import ProcessScoringPanel from '@/components/process/ProcessScoringPanel.vue'
import ProcessRedFlags from '@/components/process/ProcessRedFlags.vue'
import ProcessWireFeed from '@/components/process/ProcessWireFeed.vue'

const loading = ref(true)
const err = ref('')
const tab = ref('marlene')

const payload = reactive({
  pipeline: [],
  marlene: { steps: [] },
  gaston: { steps: [] },
  red_flags: [],
})

const state = reactive({
  items_checked: {},
  handoff: { identity_keywords: '' },
  scores_business: {},
  scores_seo: {},
  red_flags: {},
  notes: {},
  wire: { marlene_conversation_id: null, gaston_conversation_id: null },
})

const wireFeed = reactive({
  items: [],
  warnings: [],
  configured: { marlene: false, gaston: false },
  loading: false,
  err: '',
})

let wirePollTimer = null

const computedScores = ref(null)

const notesLocal = reactive({
  marlene_synthese: '',
  gaston_verdict: '',
  nicolas_decision: '',
})

const handoffText = ref('')

const identityKwPreview = computed(() => (state.handoff?.identity_keywords || '').trim())

function assignPayload(data) {
  payload.pipeline = data.pipeline || []
  payload.marlene = data.marlene || { steps: [] }
  payload.gaston = data.gaston || { steps: [] }
  payload.red_flags = data.red_flags || []
  Object.assign(state, data.state || {})
  computedScores.value = data.computed || null
  const n = state.notes || {}
  notesLocal.marlene_synthese = n.marlene_synthese ?? ''
  notesLocal.gaston_verdict = n.gaston_verdict ?? ''
  notesLocal.nicolas_decision = n.nicolas_decision ?? ''
  handoffText.value = state.handoff?.identity_keywords ?? ''
}

async function load() {
  err.value = ''
  try {
    const { data } = await api.get('/api/niche-process')
    assignPayload(data)
    await loadWireFeed()
  } catch (e) {
    err.value = e.response?.data?.detail || 'Impossible de charger le process.'
  } finally {
    loading.value = false
  }
}

async function loadWireFeed() {
  wireFeed.loading = true
  wireFeed.err = ''
  try {
    const { data } = await api.get('/api/niche-process/wire-feed')
    wireFeed.items = data.items || []
    wireFeed.warnings = data.warnings || []
    wireFeed.configured = data.configured || { marlene: false, gaston: false }
  } catch (e) {
    wireFeed.err = e.response?.data?.detail || 'Flux Wire indisponible.'
    wireFeed.items = []
    wireFeed.warnings = []
  } finally {
    wireFeed.loading = false
  }
}

async function patch(body) {
  try {
    const { data } = await api.patch('/api/niche-process', body)
    assignPayload(data)
  } catch (e) {
    err.value = e.response?.data?.detail || 'Enregistrement impossible.'
  }
}

function onToggleItem(key, checked) {
  patch({ items_checked: { [key]: checked } })
}

async function saveHandoff() {
  const v = handoffText.value
  if (v === (state.handoff?.identity_keywords ?? '')) return
  await patch({ handoff: { identity_keywords: v } })
}

async function saveNotes() {
  await patch({
    notes: {
      marlene_synthese: notesLocal.marlene_synthese,
      gaston_verdict: notesLocal.gaston_verdict,
      nicolas_decision: notesLocal.nicolas_decision,
    },
  })
}

function onScoreBiz(key, value) {
  patch({
    scores_business: {
      ...state.scores_business,
      [key]: value,
    },
  })
}

function onScoreSeo(key, value) {
  patch({
    scores_seo: {
      ...state.scores_seo,
      [key]: value,
    },
  })
}

function onRedFlag(key, checked) {
  patch({
    red_flags: {
      ...state.red_flags,
      [key]: checked,
    },
  })
}

watch(tab, () => {
  err.value = ''
  loadWireFeed()
})

onMounted(() => {
  load()
  wirePollTimer = setInterval(loadWireFeed, 25_000)
})

onUnmounted(() => {
  if (wirePollTimer) clearInterval(wirePollTimer)
})
</script>

<style scoped>
.process {
  max-width: 960px;
}
.head {
  margin-bottom: 1.25rem;
}
.h2 {
  margin: 0 0 0.5rem;
  font-family: var(--font-mono);
  font-size: 1.2rem;
  letter-spacing: 0.02em;
}
.sub {
  margin: 0;
  font-size: 0.88rem;
  color: var(--text-muted);
  line-height: 1.55;
}
.muted {
  color: var(--text-muted);
}
.wire-auto-hint {
  margin: 0 0 1rem;
  font-size: 0.8rem;
  line-height: 1.5;
  max-width: 52rem;
}
.err {
  color: var(--danger);
  font-size: 0.9rem;
}
.pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.pill {
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-muted);
  padding: 0.45rem 0.75rem;
  border-radius: 999px;
  font-size: 0.82rem;
  cursor: pointer;
  font-family: inherit;
}
.pill.tab-ml.on {
  border-color: rgba(236, 72, 153, 0.45);
  color: var(--text);
  background: rgba(236, 72, 153, 0.08);
}
.pill.tab-ga.on {
  border-color: rgba(59, 130, 246, 0.45);
  color: var(--text);
  background: rgba(59, 130, 246, 0.08);
}
.pill.tab-de.on {
  border-color: rgba(245, 158, 11, 0.45);
  color: var(--text);
  background: rgba(245, 158, 11, 0.08);
}
.panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.wire-row {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.5rem 1rem;
  font-size: 0.85rem;
}
.wire-link {
  color: var(--info);
  text-decoration: underline;
  text-underline-offset: 3px;
}
.wire-hint {
  color: var(--text-muted);
  font-size: 0.8rem;
}
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1.1rem;
}
.hand-title {
  margin: 0 0 0.35rem;
  font-size: 0.95rem;
}
.hand-desc {
  margin: 0 0 0.65rem;
  font-size: 0.78rem;
  color: var(--text-muted);
  line-height: 1.45;
}
.ta {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.55rem 0.65rem;
  color: var(--text);
  font: inherit;
  font-size: 0.88rem;
  line-height: 1.45;
  resize: vertical;
}
.notes {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.nl {
  font-size: 0.78rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.readonly .kw-preview {
  margin: 0;
  white-space: pre-wrap;
  font-size: 0.88rem;
  line-height: 1.45;
  color: var(--text);
}
.empty-hint {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-muted);
  font-style: italic;
}
.decision {
  gap: 0;
}
.foot-meta {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
  font-size: 0.72rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.decision .wire-feed {
  margin-bottom: 1rem;
}
</style>
