<template>
  <section class="wire-feed card">
    <div class="wire-feed-head">
      <h4 class="wire-feed-title">{{ title }}</h4>
      <button
        type="button"
        class="btn-refresh"
        :disabled="loading"
        @click="$emit('refresh')"
      >
        {{ loading ? '…' : 'Rafraîchir' }}
      </button>
    </div>
    <p v-if="err" class="err">{{ err }}</p>
    <p v-else-if="!hasAnyLane" class="hint">
      Aucun fil détecté pour cet agent : vérifie le <strong>jobId</strong> OpenClaw dans la carte agent (AGENTS_MAP),
      ou qu’une conversation Wire en base mentionne bien cet agent dans le dernier message.
    </p>
    <p v-else-if="!latestSlots.length && !loading" class="feed-empty muted">{{ emptyHint }}</p>
    <div v-else class="latest-root" :class="{ dual: laneFilter === 'all' && latestSlots.length > 1 }">
      <article
        v-for="slot in latestSlots"
        :key="slotKey(slot)"
        class="latest-article"
        :class="laneClass(slot.agent)"
      >
        <header class="latest-head">
          <span class="lane-badge" :class="laneClass(slot.agent)">{{ laneLabel(slot.agent) }}</span>
          <span class="meta">
            <span class="who">{{ formatWho(slot.message) }}</span>
            <time v-if="slot.message.created_at" class="ts" :datetime="slot.message.created_at">{{
              slot.message.created_at
            }}</time>
          </span>
        </header>
        <div class="rich-root">
          <template v-for="(block, bi) in blocksFor(slot.message.body)" :key="bi">
            <div v-if="block.isNiche" class="niche-card">
              <div class="niche-card-top">
                <h5 class="niche-title">{{ block.title }}</h5>
                <span v-if="block.score" class="niche-score">Score {{ block.score }}/10</span>
              </div>
              <p v-for="(line, li) in trimLines(block.lines, 12)" :key="li" class="niche-line">
                <template v-for="(seg, si) in inlineSegments(line)" :key="si">
                  <strong v-if="seg.b">{{ seg.t }}</strong>
                  <template v-else>{{ seg.t }}</template>
                </template>
              </p>
            </div>
            <div v-else class="text-block" :class="{ preamble: block.preamble }">
              <h4 v-if="!block.preamble" class="block-title">{{ block.title }}</h4>
              <p v-for="(line, li) in trimLines(block.lines, 24)" :key="li" class="md-line">
                <template v-for="(seg, si) in inlineSegments(line)" :key="si">
                  <strong v-if="seg.b">{{ seg.t }}</strong>
                  <template v-else>{{ seg.t }}</template>
                </template>
              </p>
            </div>
          </template>
        </div>
      </article>
    </div>
    <ul v-if="filteredWarnings.length" class="warn-list">
      <li v-for="(w, i) in filteredWarnings" :key="i" class="warn">{{ w }}</li>
    </ul>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { parseReportBlocks, pickLatestAgentReplyAfterHuman } from '@/utils/processWireParse'

const props = defineProps({
  items: { type: Array, default: () => [] },
  warnings: { type: Array, default: () => [] },
  configured: {
    type: Object,
    default: () => ({ marlene: false, gaston: false }),
  },
  laneFilter: {
    type: String,
    default: 'all',
    validator: (v) => ['marlene', 'gaston', 'all'].includes(v),
  },
  loading: { type: Boolean, default: false },
  err: { type: String, default: '' },
})

defineEmits(['refresh'])

const title = computed(() => {
  if (props.laneFilter === 'marlene') return 'Dernière synthèse — Marlène'
  if (props.laneFilter === 'gaston') return 'Dernière synthèse — Gaston'
  return 'Dernières synthèses — fils Wire'
})

const hasAnyLane = computed(() => {
  if (props.laneFilter === 'marlene') return props.configured.marlene
  if (props.laneFilter === 'gaston') return props.configured.gaston
  return props.configured.marlene || props.configured.gaston
})

const latestSlots = computed(() => {
  const items = props.items || []
  if (props.laneFilter === 'marlene') {
    const m = pickLatestAgentReplyAfterHuman(
      items.filter((i) => i.lane === 'marlene'),
      'marlene'
    )
    return m ? [{ message: m, agent: 'marlene' }] : []
  }
  if (props.laneFilter === 'gaston') {
    const m = pickLatestAgentReplyAfterHuman(
      items.filter((i) => i.lane === 'gaston'),
      'gaston'
    )
    return m ? [{ message: m, agent: 'gaston' }] : []
  }
  const slots = []
  const ml = pickLatestAgentReplyAfterHuman(
    items.filter((i) => i.lane === 'marlene'),
    'marlene'
  )
  const ga = pickLatestAgentReplyAfterHuman(
    items.filter((i) => i.lane === 'gaston'),
    'gaston'
  )
  if (ml) slots.push({ message: ml, agent: 'marlene' })
  if (ga) slots.push({ message: ga, agent: 'gaston' })
  return slots
})

function laneItems(lane) {
  return (props.items || []).filter((i) => i.lane === lane)
}

function hintForLane(lane, label) {
  const ix = laneItems(lane)
  if (!ix.length) {
    return `${label} : pas encore de messages sur ce fil.`
  }
  if (!ix.some((m) => m.from_agent_id === 'dashboard')) {
    return `${label} : aucun message envoyé par vous depuis le dashboard sur ce fil — écrivez d’abord depuis Wire.`
  }
  return `${label} : en attente de la réponse de l’agent après votre dernier message.`
}

const emptyHint = computed(() => {
  if (props.laneFilter === 'marlene') {
    return hintForLane('marlene', 'Marlène')
  }
  if (props.laneFilter === 'gaston') {
    return hintForLane('gaston', 'Gaston')
  }
  const parts = [hintForLane('marlene', 'Marlène'), hintForLane('gaston', 'Gaston')].filter(Boolean)
  return parts.length ? parts.join(' ') : 'Pas de réponse agent après un message dashboard sur ces fils.'
})

const filteredWarnings = computed(() => {
  const w = props.warnings || []
  if (props.laneFilter === 'all') return w
  const prefix = `${props.laneFilter}:`
  return w.filter((line) => line.toLowerCase().startsWith(prefix))
})

function blocksFor(body) {
  const blocks = parseReportBlocks(body)
  return blocks.length ? blocks : [{ title: 'Message', lines: (body || '').split('\n'), isNiche: false, score: null, preamble: false }]
}

function trimLines(lines, max) {
  const arr = (lines || []).map((l) => l.trimEnd()).filter((l) => l.trim().length > 0)
  return arr.slice(0, max)
}

function inlineSegments(line) {
  const s = line || ''
  const parts = []
  const re = /\*\*(.+?)\*\*/g
  let last = 0
  let m
  while ((m = re.exec(s))) {
    if (m.index > last) parts.push({ t: s.slice(last, m.index), b: false })
    parts.push({ t: m[1], b: true })
    last = m.index + m[0].length
  }
  if (last < s.length) parts.push({ t: s.slice(last), b: false })
  if (!parts.length) parts.push({ t: s, b: false })
  return parts
}

function laneClass(agent) {
  if (agent === 'gaston') return 'lane-ga'
  if (agent === 'marlene') return 'lane-ml'
  return 'lane-unk'
}

function laneLabel(agent) {
  if (agent === 'gaston') return 'Gaston'
  if (agent === 'marlene') return 'Marlène'
  return agent || '—'
}

function formatWho(m) {
  const fr = m.from_agent_id || '—'
  const to = m.to_agent_id || '—'
  return `${fr} → ${to}`
}

function slotKey(slot) {
  const id = slot.message?.id != null ? String(slot.message.id) : ''
  const t = slot.message?.created_at || ''
  return `${slot.agent}-${id}-${t}`
}
</script>

<style scoped>
.wire-feed {
  margin-top: 0;
}
.wire-feed-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}
.wire-feed-title {
  margin: 0;
  font-size: 0.92rem;
}
.btn-refresh {
  font: inherit;
  font-size: 0.78rem;
  padding: 0.35rem 0.65rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-muted);
  cursor: pointer;
}
.btn-refresh:hover:not(:disabled) {
  color: var(--text);
}
.btn-refresh:disabled {
  opacity: 0.5;
  cursor: default;
}
.err {
  color: var(--danger);
  font-size: 0.85rem;
  margin: 0 0 0.5rem;
}
.hint,
.feed-empty {
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.45;
}
.latest-root {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.latest-root.dual {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
@media (max-width: 720px) {
  .latest-root.dual {
    grid-template-columns: 1fr;
  }
}
.latest-article {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.75rem 0.85rem;
  background: rgba(0, 0, 0, 0.22);
}
.latest-article.lane-ml {
  border-color: rgba(236, 72, 153, 0.4);
}
.latest-article.lane-ga {
  border-color: rgba(59, 130, 246, 0.4);
}
.latest-head {
  margin-bottom: 0.65rem;
}
.lane-badge {
  display: inline-block;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.12rem 0.4rem;
  border-radius: 4px;
  margin-bottom: 0.35rem;
}
.lane-badge.lane-ml {
  background: rgba(236, 72, 153, 0.18);
  color: #f9a8d4;
}
.lane-badge.lane-ga {
  background: rgba(59, 130, 246, 0.18);
  color: #93c5fd;
}
.lane-badge.lane-unk {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-muted);
}
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 0.75rem;
  font-size: 0.72rem;
  color: var(--text-muted);
  font-family: var(--font-mono, monospace);
}
.rich-root {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.niche-card {
  border-radius: 10px;
  padding: 0.55rem 0.65rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.niche-card-top {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
}
.niche-title {
  margin: 0;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text);
  line-height: 1.35;
}
.niche-score {
  font-size: 0.78rem;
  font-family: var(--font-mono, monospace);
  color: #fbbf24;
  white-space: nowrap;
}
.niche-line {
  margin: 0.15rem 0 0;
  font-size: 0.8rem;
  line-height: 1.45;
  color: var(--text-muted);
}
.text-block {
  padding: 0.15rem 0;
}
.text-block.preamble {
  opacity: 0.88;
  font-size: 0.8rem;
  color: var(--text-muted);
}
.block-title {
  margin: 0 0 0.35rem;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text);
}
.md-line {
  margin: 0.2rem 0 0;
  font-size: 0.82rem;
  line-height: 1.5;
  color: var(--text);
  white-space: pre-wrap;
}
.warn-list {
  margin: 0.65rem 0 0;
  padding-left: 1.1rem;
  font-size: 0.78rem;
  color: var(--danger, #f87171);
}
.warn {
  margin: 0.15rem 0;
}
</style>
