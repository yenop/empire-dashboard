<template>
  <div class="board">
    <div v-for="col in columns" :key="col.key" class="col">
      <h2 class="col-h">{{ col.label }} <span class="n">({{ byStatus[col.key].length }})</span></h2>
      <div class="list">
        <div v-for="t in byStatus[col.key]" :key="t.id" class="card">
          <p class="title">{{ t.title }}</p>
          <div class="sub" v-if="t.agent_id">
            <span>{{ t.agent_emoji }} {{ t.agent_name }}</span>
            <span v-if="t.app_id" :style="{ color: t.app_color }">{{ t.app_name }}</span>
          </div>
          <div class="move" v-if="t.status !== 'done'">
            <button
              v-for="(target, k) in nextMap[t.status] || []"
              :key="k"
              type="button"
              @click="emit('move', t, target)"
            >
              →
              {{ colLabel(target) }}
            </button>
          </div>
        </div>
        <p v-if="!byStatus[col.key].length" class="empty">Aucune tâche</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tasks: { type: Array, default: () => [] },
})

const emit = defineEmits(['move'])

const columns = [
  { key: 'todo', label: 'À faire' },
  { key: 'inprogress', label: 'En cours' },
  { key: 'done', label: 'Terminé' },
]

const nextMap = {
  todo: ['inprogress', 'done'],
  inprogress: ['todo', 'done'],
  done: [],
}

const byStatus = computed(() => {
  const m = { todo: [], inprogress: [], done: [] }
  for (const t of props.tasks) {
    const s = t.status
    if (m[s]) m[s].push(t)
  }
  return m
})

const colMap = { todo: 'À faire', inprogress: 'En cours', done: 'Terminé' }
function colLabel(k) {
  return colMap[k] || k
}
</script>

<style scoped>
.board {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  align-items: start;
}
@media (max-width: 1024px) and (min-width: 561px) {
  .board {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 560px) {
  .board {
    grid-template-columns: 1fr;
  }
}
.col {
  background: #ffffff04;
  border: 1px solid var(--border);
  border-radius: 10px;
  min-height: 200px;
}
.col-h {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin: 0;
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid var(--border);
}
.n {
  color: var(--text-muted);
  font-weight: 400;
}
.list {
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: min(60vh, 520px);
  overflow: auto;
}
@media (max-width: 560px) {
  .list {
    max-height: min(50vh, 400px);
  }
}
.card {
  padding: 0.65rem 0.5rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  border-top: 2px solid var(--accent);
}
.title {
  margin: 0 0 0.4rem;
  font-size: 0.85rem;
  line-height: 1.3;
  font-weight: 500;
}
.sub {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 0.5rem;
  font-size: 0.7rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.move {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.5rem;
}
.move button {
  font-size: 0.6rem;
  font-family: var(--font-mono);
  padding: 0.2rem 0.35rem;
  border-radius: 4px;
  border: 1px solid #ffffff20;
  background: #ffffff08;
  color: var(--text-muted);
  cursor: pointer;
}
.move button:hover {
  color: var(--accent);
  border-color: #f59e0b44;
}
.empty {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: center;
  margin: 0.5rem 0;
  font-style: italic;
}
</style>
