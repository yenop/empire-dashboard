<template>
  <div class="panel">
    <h2 class="h">Intel du jour <span class="sub">(Édith)</span></h2>
    <ul class="feed">
      <li v-for="item in items" :key="item.id" class="line">
        <div class="top">
          <span v-if="item.score != null" class="score">{{ item.score }}/10</span>
          <span class="title">{{ item.title }}</span>
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
defineProps({
  items: { type: Array, default: () => [] },
})
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
.feed {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  max-height: min(360px, 45vh);
  overflow: auto;
}
.line {
  padding: 0.6rem 0.45rem;
  border-left: 2px solid var(--info);
  background: #ffffff04;
  border-radius: 0 6px 6px 0;
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
.bot {
  display: flex;
  justify-content: space-between;
  margin-top: 0.35rem;
  font-size: 0.65rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.stat {
  text-transform: uppercase;
  font-size: 0.58rem;
}
.stat.implemented {
  color: var(--success);
}
.stat.pending {
  color: var(--warning);
}
.stat.borderline {
  color: var(--danger);
}
</style>
