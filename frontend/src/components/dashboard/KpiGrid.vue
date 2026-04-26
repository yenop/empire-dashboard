<template>
  <div class="kpi-grid">
    <div v-for="k in items" :key="k.label" class="kpi">
      <div class="kpi-label">{{ k.label }}</div>
      <div class="kpi-value" :style="{ color: k.color || 'var(--text)' }">
        {{ k.value }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  items: { type: Array, default: () => [] },
})
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 130px), 1fr));
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}
.kpi {
  position: relative;
  padding: 1rem 1rem 0.85rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
}
.kpi::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--accent);
  opacity: 0.7;
}
.kpi-label {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  font-family: var(--font-mono);
  margin-bottom: 0.35rem;
}
.kpi-value {
  font-family: var(--font-mono);
  font-size: 1.15rem;
  font-weight: 700;
}
</style>
