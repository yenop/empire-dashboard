<template>
  <div class="pipeline">
    <div class="pipe-label">Pipeline</div>
    <div class="pipe-row">
      <template v-for="(card, i) in pipeline" :key="card.id">
        <article
          class="pipe-card"
          :style="{ '--card-accent': card.color }"
        >
          <div class="phase-idx">{{ i + 1 }}</div>
          <div class="pipe-accent" />
          <div class="pipe-body">
            <span class="pill" :style="{ background: card.color + '22', color: card.color }">
              {{ card.label }}
            </span>
            <span class="role">{{ card.role }}</span>
            <p class="sub">{{ card.subtitle }}</p>
          </div>
        </article>
        <span v-if="i < pipeline.length - 1" class="arrow" aria-hidden="true">→</span>
      </template>
    </div>
  </div>
</template>

<script setup>
defineProps({
  pipeline: {
    type: Array,
    required: true,
  },
})
</script>

<style scoped>
.pipeline {
  margin-bottom: 1.25rem;
}
.pipe-label {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}
.pipe-row {
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
  gap: 0.5rem 0.35rem;
}
.pipe-card {
  position: relative;
  flex: 1 1 160px;
  min-width: 140px;
  max-width: 280px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.85rem 0.85rem 0.85rem 1.15rem;
  overflow: hidden;
}
.phase-idx {
  position: absolute;
  top: 0.5rem;
  right: 0.55rem;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--text-muted);
}
.pipe-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--card-accent, var(--accent));
  border-radius: 10px 0 0 10px;
}
.pipe-body {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.pill {
  display: inline-block;
  align-self: flex-start;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
}
.role {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.sub {
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.35;
  color: var(--text);
  opacity: 0.92;
}
.arrow {
  align-self: center;
  color: var(--text-muted);
  font-size: 1.1rem;
  padding: 0 0.15rem;
}
@media (max-width: 720px) {
  .arrow {
    display: none;
  }
}
</style>
