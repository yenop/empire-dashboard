<template>
  <div class="placeholder">
    <h2 class="heading">{{ title }}</h2>
    <p class="lead">Cette section sera branchée prochainement.</p>
    <p class="hint">Écran réservé dans la navigation App / niche ou Empire.</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => route.meta.title || 'À venir')
</script>

<style scoped>
.placeholder {
  max-width: 32rem;
  padding: 1.5rem 0;
}
.heading {
  margin: 0 0 0.75rem;
  font-family: var(--font-mono);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.02em;
}
.lead {
  margin: 0 0 0.5rem;
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
}
.hint {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-muted);
  opacity: 0.85;
}
</style>
