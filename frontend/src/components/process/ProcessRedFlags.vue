<template>
  <section class="flags card">
    <h3 class="h">Red flags — checklist obligatoire</h3>
    <p class="warn">
      À cocher même si le score final ≥ 8 — tout signal positif = risque à investiguer.
    </p>
    <ul class="list">
      <li v-for="def in definitions" :key="def.key">
        <label class="row">
          <input
            type="checkbox"
            :checked="!!model[def.key]"
            @change="emit('toggle', def.key, $event.target.checked)"
          />
          <span>{{ def.label }}</span>
        </label>
      </li>
    </ul>
    <p class="foot">
      Si une case est cochée : traiter comme alerte (investigation), pas comme veto automatique dans l’app.
    </p>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  definitions: { type: Array, required: true },
  redFlags: { type: Object, required: true },
})

const emit = defineEmits(['toggle'])

const model = computed(() => props.redFlags || {})
</script>

<style scoped>
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1.1rem;
  margin-top: 1rem;
}
.h {
  margin: 0 0 0.5rem;
  font-size: 1rem;
}
.warn {
  margin: 0 0 0.85rem;
  font-size: 0.8rem;
  color: var(--warning);
  line-height: 1.45;
}
.list {
  margin: 0;
  padding: 0;
  list-style: none;
}
.row {
  display: flex;
  gap: 0.55rem;
  align-items: flex-start;
  padding: 0.45rem 0;
  font-size: 0.85rem;
  line-height: 1.4;
  cursor: pointer;
  color: var(--text-muted);
}
.row input {
  margin-top: 0.2rem;
  accent-color: var(--danger);
}
.foot {
  margin: 0.75rem 0 0;
  font-size: 0.72rem;
  color: var(--text-muted);
  line-height: 1.4;
}
</style>
