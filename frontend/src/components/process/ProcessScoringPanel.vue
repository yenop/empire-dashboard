<template>
  <section class="score card">
    <h3 class="h">Formule de scoring final</h3>

    <div class="formula-visual" aria-label="Formules de calcul">
      <div class="formula-card formula-marlene">
        <div class="formula-head">
          <span class="dot" aria-hidden="true" />
          score<sub class="sub">marlène</sub>
        </div>
        <pre class="formula-code" tabindex="-1">
<span class="kw">score_marlene</span> = (
  passion + communaute + depenses + repetabilite
  + fit_visuel + concurrence_pod + international
) / <span class="n">7</span></pre>
        <p class="formula-legend">Moyenne des 7 critères business (/10 chacun).</p>
      </div>

      <div class="formula-card formula-gaston">
        <div class="formula-head">
          <span class="dot dot-b" aria-hidden="true" />
          score<sub class="sub">gaston</sub>
        </div>
        <pre class="formula-code"><span class="kw">score_gaston</span> = (
  volume_trans + kgr_verts + serp_battable
) / <span class="n">3</span></pre>
        <p class="formula-legend">Moyenne des 3 critères SEO (/10 chacun).</p>
      </div>

      <div class="formula-final-wrap">
        <div class="formula-card formula-final">
          <div class="formula-head">
            <span class="dot dot-g" aria-hidden="true" />
            score<sub class="sub">final</sub>
          </div>
          <pre class="formula-code formula-final-code"><span class="kw">score_final</span> =
  <span class="w60">score_marlene × 0,6</span>
  + <span class="w40">score_gaston × 0,4</span></pre>
          <p class="formula-legend">
            Business <strong>60&nbsp;%</strong> · SEO <strong>40&nbsp;%</strong>
          </p>
        </div>
      </div>
    </div>

    <div class="verdict-strip" aria-label="Seuils de verdict">
      <div class="tier tier-go">
        <span class="tier-label">GO</span>
        <span class="tier-range">≥ 8,0</span>
      </div>
      <div class="tier tier-border">
        <span class="tier-label">BORDERLINE</span>
        <span class="tier-range">6,0 — 7,9</span>
      </div>
      <div class="tier tier-nogo">
        <span class="tier-label">NO-GO</span>
        <span class="tier-range">&lt; 6,0</span>
      </div>
    </div>

    <p class="hint hint-after">
      Saisis les notes ci-dessous : les moyennes et le score final se calculent automatiquement.
    </p>

    <div class="grid biz">
      <h4 class="subh">Score Marlène (business)</h4>
      <label v-for="entry in businessFields" :key="entry.key" class="field">
        <span class="lab">{{ entry.label }}</span>
        <input
          type="number"
          min="0"
          max="10"
          step="0.1"
          :value="numOrEmpty(modelBiz[entry.key])"
          placeholder="—"
          @input="onBiz(entry.key, $event.target.value)"
        />
      </label>
    </div>

    <div class="grid seo">
      <h4 class="subh">Score Gaston (SEO)</h4>
      <label v-for="entry in seoFields" :key="entry.key" class="field">
        <span class="lab">{{ entry.label }}</span>
        <input
          type="number"
          min="0"
          max="10"
          step="0.1"
          :value="numOrEmpty(modelSeo[entry.key])"
          placeholder="—"
          @input="onSeo(entry.key, $event.target.value)"
        />
      </label>
    </div>

    <div class="out">
      <div class="row">
        <span>Moyenne Marlène</span>
        <strong>{{ fmt(computed?.score_marlene) }}</strong>
      </div>
      <div class="row">
        <span>Moyenne Gaston</span>
        <strong>{{ fmt(computed?.score_gaston) }}</strong>
      </div>
      <div class="row final">
        <span>Score final</span>
        <strong>{{ fmt(computed?.score_final) }}</strong>
      </div>
      <div class="verdict" :class="verdictClass">
        {{ verdictLabel }}
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const businessFields = [
  { key: 'passion', label: 'Passion' },
  { key: 'communaute', label: 'Communauté' },
  { key: 'depenses', label: 'Dépenses' },
  { key: 'repetabilite', label: 'Répétabilité' },
  { key: 'fit_visuel', label: 'Fit visuel' },
  { key: 'concurrence_pod', label: 'Concurrence POD' },
  { key: 'international', label: 'International' },
]

const seoFields = [
  { key: 'volume_trans', label: 'Volume transactionnel' },
  { key: 'kgr_verts', label: 'KGR verts' },
  { key: 'serp_battable', label: 'SERP battable' },
]

const props = defineProps({
  scoresBusiness: { type: Object, required: true },
  scoresSeo: { type: Object, required: true },
  computed: { type: Object, default: null },
})

const emit = defineEmits(['update-business', 'update-seo'])

const modelBiz = computed(() => props.scoresBusiness || {})
const modelSeo = computed(() => props.scoresSeo || {})

function onBiz(key, raw) {
  const t = String(raw).trim()
  if (t === '') {
    emit('update-business', key, null)
    return
  }
  const n = Number(t)
  emit('update-business', key, Number.isFinite(n) ? n : null)
}

function onSeo(key, raw) {
  const t = String(raw).trim()
  if (t === '') {
    emit('update-seo', key, null)
    return
  }
  const n = Number(t)
  emit('update-seo', key, Number.isFinite(n) ? n : null)
}

function fmt(v) {
  if (v == null || Number.isNaN(v)) return '—'
  return Number(v).toFixed(2)
}

function numOrEmpty(v) {
  if (v === null || v === undefined || v === '') return ''
  return v
}

const verdictLabel = computed(() => {
  const v = props.computed?.verdict
  if (v === 'go') return 'GO — score ≥ 8,0'
  if (v === 'borderline') return 'BORDERLINE — 6,0 à 7,9'
  if (v === 'nogo') return 'NO-GO — score < 6,0'
  return 'Complétez les 7 + 3 critères pour le verdict'
})

const verdictClass = computed(() => {
  const v = props.computed?.verdict
  if (v === 'go') return 'go'
  if (v === 'borderline') return 'borderline'
  if (v === 'nogo') return 'nogo'
  return 'pending'
})
</script>

<style scoped>
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1.1rem;
}
.h {
  margin: 0 0 0.5rem;
  font-size: 1rem;
}
.hint-after {
  margin: 0 0 1rem;
  font-size: 0.8rem;
  color: var(--text-muted);
  line-height: 1.45;
}

.formula-visual {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

@media (max-width: 720px) {
  .formula-visual {
    grid-template-columns: 1fr;
  }
}

.formula-card {
  border-radius: 10px;
  padding: 0.75rem 0.85rem;
  border: 1px solid var(--border);
  background: linear-gradient(
    165deg,
    rgba(255, 255, 255, 0.04) 0%,
    rgba(255, 255, 255, 0) 60%
  );
}

.formula-marlene {
  border-color: rgba(236, 72, 153, 0.35);
  box-shadow: 0 0 0 1px rgba(236, 72, 153, 0.08) inset;
}

.formula-gaston {
  border-color: rgba(59, 130, 246, 0.35);
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.08) inset;
}

.formula-final {
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.1) inset;
  background: linear-gradient(
    180deg,
    rgba(245, 158, 11, 0.07) 0%,
    rgba(255, 255, 255, 0.02) 100%
  );
}

.formula-final-wrap {
  grid-column: 1 / -1;
}

.formula-head {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 0.5rem;
}

.sub {
  font-size: 0.7em;
  font-weight: 600;
  opacity: 0.9;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ec4899;
  flex-shrink: 0;
}

.dot-b {
  background: #3b82f6;
}

.dot-g {
  background: #f59e0b;
}

.formula-code {
  margin: 0;
  padding: 0.55rem 0.6rem;
  background: rgba(0, 0, 0, 0.35);
  border-radius: 6px;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  line-height: 1.5;
  color: #c4c4d4;
  overflow-x: auto;
  white-space: pre;
  border: 1px solid var(--border);
}

.formula-code .kw {
  color: #f472b6;
}

.formula-gaston .formula-code .kw {
  color: #60a5fa;
}

.formula-final .formula-code .kw {
  color: #fbbf24;
}

.formula-code .n {
  color: #a5b4fc;
  font-weight: 700;
}

.formula-final-code .w60 {
  color: #f472b6;
}

.formula-final-code .w40 {
  color: #60a5fa;
}

.formula-legend {
  margin: 0.45rem 0 0;
  font-size: 0.72rem;
  color: var(--text-muted);
  line-height: 1.4;
}

.verdict-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin-bottom: 1rem;
}

@media (max-width: 560px) {
  .verdict-strip {
    grid-template-columns: 1fr;
  }
}

.tier {
  text-align: center;
  padding: 0.55rem 0.5rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  font-size: 0.78rem;
}

.tier-label {
  display: block;
  font-weight: 700;
  font-family: var(--font-mono);
  letter-spacing: 0.04em;
  font-size: 0.72rem;
  margin-bottom: 0.2rem;
}

.tier-range {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.tier-go {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.35);
}

.tier-go .tier-label {
  color: var(--success);
}

.tier-border {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.35);
}

.tier-border .tier-label {
  color: var(--warning);
}

.tier-nogo {
  background: rgba(244, 63, 94, 0.1);
  border-color: rgba(244, 63, 94, 0.35);
}

.tier-nogo .tier-label {
  color: var(--danger);
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 0.65rem;
  margin-bottom: 1.25rem;
}
.subh {
  grid-column: 1 / -1;
  margin: 0;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.lab {
  font-size: 0.75rem;
  color: var(--text-muted);
}
.field input {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.35rem 0.5rem;
  color: var(--text);
  font-family: var(--font-mono);
  font-size: 0.85rem;
}
.out {
  border-top: 1px solid var(--border);
  padding-top: 0.85rem;
}
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.88rem;
  margin-bottom: 0.35rem;
}
.row.final {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed var(--border);
  font-size: 1rem;
}
.verdict {
  margin-top: 0.75rem;
  padding: 0.55rem 0.65rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
}
.verdict.pending {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-muted);
}
.verdict.go {
  background: rgba(16, 185, 129, 0.12);
  color: var(--success);
}
.verdict.borderline {
  background: rgba(245, 158, 11, 0.12);
  color: var(--warning);
}
.verdict.nogo {
  background: rgba(244, 63, 94, 0.12);
  color: var(--danger);
}
</style>
