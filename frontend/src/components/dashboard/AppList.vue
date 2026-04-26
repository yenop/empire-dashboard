<template>
  <div class="panel">
    <h2 class="h">Apps</h2>
    <ul class="list">
      <li v-for="a in apps" :key="a.id" class="row" :style="{ '--accent': a.color }">
        <div class="row-top">
          <span class="icon">{{ a.icon }}</span>
          <div>
            <div class="name">{{ a.name }}</div>
            <div class="niche">{{ a.niche }}</div>
          </div>
        </div>
        <div class="meta">
          <span class="mrr"><span class="d">$</span>{{ mrr(a) }}</span>
          <span class="conv">conv. {{ a.conversion_rate }}%</span>
          <span :class="['st', a.status]">{{ a.status }}</span>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
defineProps({
  apps: { type: Array, default: () => [] },
})
function mrr(a) {
  return Number(a.mrr).toFixed(0)
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
.list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.row {
  position: relative;
  padding: 0.65rem 0.5rem 0.65rem 0.5rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #ffffff04;
  transition: transform 0.15s, border-color 0.15s;
  border-top: 2px solid var(--accent, var(--info));
}
.row:hover {
  transform: translateY(-2px);
  border-color: var(--border-hover);
}
.row-top {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}
.icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  background: #ffffff0a;
  border-radius: 8px;
}
.name {
  font-size: 0.9rem;
  font-weight: 600;
}
.niche {
  font-size: 0.7rem;
  color: var(--text-muted);
}
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 0.75rem;
  margin-top: 0.5rem;
  font-size: 0.7rem;
  font-family: var(--font-mono);
  color: var(--text-muted);
}
.mrr {
  color: var(--accent);
}
.st {
  text-transform: uppercase;
  font-size: 0.6rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}
.st.live {
  color: var(--success);
  background: rgba(16, 185, 129, 0.12);
}
.st.beta {
  color: var(--info);
  background: rgba(59, 130, 246, 0.12);
}
.st.dev {
  color: var(--text-muted);
  background: #ffffff0a;
}
</style>
