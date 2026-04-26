<template>
  <article class="card" :style="{ '--line': app.color }">
    <div class="accent" />
    <div class="top">
      <span class="icon">{{ app.icon }}</span>
      <div>
        <h3>{{ app.name }}</h3>
        <p class="niche">{{ app.niche }}</p>
      </div>
      <span :class="['badge', app.status]">{{ app.status }}</span>
    </div>
    <div class="metrics">
      <div>
        <span class="lab">MRR</span>
        <span class="val">${{ mrr }}</span>
      </div>
      <div>
        <span class="lab">DL</span>
        <span class="val">{{ app.downloads }}</span>
      </div>
      <div>
        <span class="lab">Conv</span>
        <span class="val">{{ app.conversion_rate }}%</span>
      </div>
      <div>
        <span class="lab">Churn</span>
        <span class="val">{{ app.churn_rate }}%</span>
      </div>
    </div>
    <div class="aso">
      <span>ASO</span>
      <div class="bar"><div :style="{ width: app.aso_score + '%' }" /></div>
      <span class="n">{{ app.aso_score }}</span>
    </div>
    <div class="actions">
      <button type="button" class="btn">ASO →</button>
      <button type="button" class="btn">Analytics →</button>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  app: { type: Object, required: true },
})
const mrr = computed(() => Number(props.app.mrr).toFixed(0))
</script>

<style scoped>
.card {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
  transition: transform 0.15s, border-color 0.15s;
  overflow: hidden;
}
.card:hover {
  transform: translateY(-2px);
  border-color: var(--border-hover);
}
.accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--line, var(--accent));
}
.top {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  margin-bottom: 0.75rem;
}
.icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  background: #ffffff0a;
  border-radius: 8px;
}
h3 {
  margin: 0;
  font-size: 1rem;
}
.niche {
  margin: 0.15rem 0 0;
  font-size: 0.75rem;
  color: var(--text-muted);
}
.badge {
  margin-left: auto;
  font-size: 0.6rem;
  text-transform: uppercase;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-family: var(--font-mono);
}
.badge.live {
  color: var(--success);
  background: rgba(16, 185, 129, 0.12);
}
.badge.beta {
  color: var(--info);
  background: rgba(59, 130, 246, 0.12);
}
.badge.dev {
  color: var(--text-muted);
  background: #ffffff0a;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.35rem;
  margin-bottom: 0.75rem;
  font-size: 0.7rem;
  font-family: var(--font-mono);
}
@media (max-width: 420px) {
  .metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}
.lab {
  display: block;
  color: var(--text-muted);
  font-size: 0.6rem;
  text-transform: uppercase;
  margin-bottom: 0.1rem;
}
.val {
  color: var(--text);
  font-weight: 600;
}
.aso {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.7rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
  margin-bottom: 0.75rem;
}
.aso .bar {
  flex: 1;
  height: 4px;
  background: #ffffff10;
  border-radius: 2px;
  overflow: hidden;
}
.aso .bar > div {
  height: 100%;
  background: var(--violet);
  border-radius: 2px;
}
.n {
  min-width: 2rem;
  text-align: right;
  color: var(--violet);
}
.actions {
  display: flex;
  gap: 0.5rem;
}
.btn {
  flex: 1;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  padding: 0.4rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: #ffffff08;
  color: var(--text-muted);
  cursor: pointer;
}
.btn:hover {
  color: var(--accent);
  border-color: #f59e0b44;
}
</style>
