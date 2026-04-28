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

      <section class="wire-setup card">
        <h4 class="wire-setup-title">Fils Wire (IDs conversation)</h4>
        <p class="wire-setup-desc">
          Tu dialogues d’abord avec <strong>Marlène</strong> sur Wire, puis tu enchaînes avec <strong>Gaston</strong>
          (deux fils distincts). Copie chaque identifiant depuis la page Wire (numéro ou UUID OpenClaw), enregistre
          au blur : cette page fusionne la <strong>lecture</strong> des deux fils pour suivre l’historique. Les
          envois se font depuis Wire ou les liens « Ouvrir le Wire » ci-dessous — pas d’envoi groupé ici.
        </p>
        <div class="wire-setup-row">
          <label class="wire-lab">
            <span class="wire-lab-t">Fil Marlène</span>
            <input
              v-model="wireIdsLocal.marlene"
              type="text"
              class="wire-inp"
              placeholder="ex. 12 ou uuid du job"
              maxlength="120"
              @blur="saveWireIds"
            />
          </label>
          <label class="wire-lab">
            <span class="wire-lab-t">Fil Gaston</span>
            <input
              v-model="wireIdsLocal.gaston"
              type="text"
              class="wire-inp"
              placeholder="ex. 13 ou uuid du job"
              maxlength="120"
              @blur="saveWireIds"
            />
          </label>
        </div>
      </section>

      <ProcessWireFeed
        :items="wireFeed.items"
        :warnings="wireFeed.warnings"
        :configured="wireFeed.configured"
        :loading="wireFeed.loading"
        :err="wireFeed.err"
        @refresh="loadWireFeed"
      />

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

const computedScores = ref(null)

const notesLocal = reactive({
  marlene_synthese: '',
  gaston_verdict: '',
  nicolas_decision: '',
})

const handoffText = ref('')

const wireIdsLocal = reactive({
  marlene: '',
  gaston: '',
})

const wireFeed = reactive({
  items: [],
  warnings: [],
  configured: { marlene: false, gaston: false },
  loading: false,
  err: '',
})

let wirePollTimer = null

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
  const w = state.wire || {}
  wireIdsLocal.marlene = w.marlene_conversation_id ?? ''
  wireIdsLocal.gaston = w.gaston_conversation_id ?? ''
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

async function saveWireIds() {
  const sw = state.wire || {}
  const prevM = (sw.marlene_conversation_id ?? '').trim()
  const prevG = (sw.gaston_conversation_id ?? '').trim()
  const m = wireIdsLocal.marlene.trim()
  const g = wireIdsLocal.gaston.trim()
  if (m === prevM && g === prevG) return
  await patch({
    wire: {
      marlene_conversation_id: m || null,
      gaston_conversation_id: g || null,
    },
  })
  await loadWireFeed()
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
})

onMounted(() => {
  load()
  wirePollTimer = setInterval(loadWireFeed, 20_000)
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
.wire-setup-title {
  margin: 0 0 0.35rem;
  font-size: 0.95rem;
}
.wire-setup-desc {
  margin: 0 0 0.75rem;
  font-size: 0.78rem;
  color: var(--text-muted);
  line-height: 1.45;
}
.wire-setup-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
@media (max-width: 640px) {
  .wire-setup-row {
    grid-template-columns: 1fr;
  }
}
.wire-lab {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.wire-lab-t {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.wire-inp {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.45rem 0.55rem;
  color: var(--text);
  font: inherit;
  font-size: 0.85rem;
}
</style>
