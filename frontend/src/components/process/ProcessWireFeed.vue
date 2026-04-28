<template>
  <section class="wire-feed card">
    <div class="wire-feed-head">
      <h4 class="wire-feed-title">Activité Wire (Marlène + Gaston)</h4>
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
    <p v-else-if="!configured.marlene && !configured.gaston" class="hint">
      Renseigne les IDs de fil ci-dessus pour agréger les messages des deux agents.
    </p>
    <ul v-else-if="!items.length && !loading" class="feed-empty muted">
      Aucun message sur les fils configurés (ou fils vides).
    </ul>
    <ul v-else class="feed-list scroll-thin" role="list">
      <li
        v-for="(m, idx) in items"
        :key="feedKey(m, idx)"
        class="feed-row"
        :class="laneClass(m.lane)"
      >
        <span class="lane-badge" :class="laneClass(m.lane)">{{ laneLabel(m.lane) }}</span>
        <span class="meta">
          <span class="who">{{ formatWho(m) }}</span>
          <time v-if="m.created_at" class="ts" :datetime="m.created_at">{{ m.created_at }}</time>
        </span>
        <pre class="body">{{ m.body }}</pre>
      </li>
    </ul>
    <ul v-if="warnings.length" class="warn-list">
      <li v-for="(w, i) in warnings" :key="i" class="warn">{{ w }}</li>
    </ul>
  </section>
</template>

<script setup>
const props = defineProps({
  items: { type: Array, default: () => [] },
  warnings: { type: Array, default: () => [] },
  configured: {
    type: Object,
    default: () => ({ marlene: false, gaston: false }),
  },
  loading: { type: Boolean, default: false },
  err: { type: String, default: '' },
})

defineEmits(['refresh'])

function laneClass(lane) {
  if (lane === 'gaston') return 'lane-ga'
  if (lane === 'marlene') return 'lane-ml'
  return 'lane-unk'
}

function laneLabel(lane) {
  if (lane === 'gaston') return 'Gaston'
  if (lane === 'marlene') return 'Marlène'
  return lane || '—'
}

function formatWho(m) {
  const fr = m.from_agent_id || '—'
  const to = m.to_agent_id || '—'
  return `${fr} → ${to}`
}

function feedKey(m, idx) {
  const id = m.id != null ? String(m.id) : ''
  const lane = m.lane || ''
  const t = m.created_at || ''
  return `${lane}-${id}-${t}-${idx}`
}
</script>

<style scoped>
.wire-feed {
  margin-top: 0.25rem;
}
.wire-feed-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.65rem;
}
.wire-feed-title {
  margin: 0;
  font-size: 0.95rem;
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
.feed-list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 280px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.feed-row {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.55rem 0.65rem;
  background: rgba(0, 0, 0, 0.2);
}
.feed-row.lane-ml {
  border-color: rgba(236, 72, 153, 0.35);
}
.feed-row.lane-ga {
  border-color: rgba(59, 130, 246, 0.35);
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
  background: rgba(236, 72, 153, 0.15);
  color: #f9a8d4;
}
.lane-badge.lane-ga {
  background: rgba(59, 130, 246, 0.15);
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
  margin-bottom: 0.35rem;
}
.who {
  word-break: break-all;
}
.ts {
  opacity: 0.85;
}
.body {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 0.84rem;
  line-height: 1.45;
  color: var(--text);
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
.scroll-thin {
  scrollbar-width: thin;
}
</style>
