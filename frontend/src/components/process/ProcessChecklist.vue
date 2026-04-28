<template>
  <section class="checklist card" :style="{ '--step-hl': borderAccent }">
    <header class="head">
      <h3 class="title">
        <span class="icon" aria-hidden="true">{{ icon }}</span>
        {{ title }}
      </h3>
      <span class="meta">{{ steps.length }} étapes · {{ totalItems }} items</span>
    </header>
    <div class="steps">
      <div
        v-for="st in steps"
        :key="st.key"
        class="step"
        :class="{ open: expanded[st.key], highlight: st.highlight }"
      >
        <button
          type="button"
          class="step-head"
          :aria-expanded="expanded[st.key]"
          @click="toggle(st.key)"
        >
          <span class="prog" :class="stepDoneClass(st)">{{ stepDoneIcon(st) }}</span>
          <span class="step-title">{{ st.title }}</span>
          <span class="n">{{ st.items?.length || 0 }} items</span>
        </button>
        <div v-show="expanded[st.key]" class="step-body">
          <label
            v-for="it in st.items"
            :key="it.key"
            class="item-row"
          >
            <input
              type="checkbox"
              :checked="!!itemsChecked[it.key]"
              @change="onToggle(it.key, $event.target.checked)"
            />
            <span>{{ it.label }}</span>
          </label>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  icon: { type: String, default: '✓' },
  steps: { type: Array, required: true },
  itemsChecked: { type: Object, required: true },
  borderAccent: { type: String, default: '#ec4899' },
})

const emit = defineEmits(['toggle-item'])

const expanded = reactive({})

function toggle(key) {
  expanded[key] = !expanded[key]
}

const totalItems = computed(() =>
  props.steps.reduce((n, s) => n + (s.items?.length || 0), 0)
)

function stepDoneIcon(st) {
  const items = st.items || []
  if (!items.length) return '○'
  const done = items.filter((i) => props.itemsChecked[i.key]).length
  if (done === items.length) return '✓'
  if (done > 0) return '◐'
  return '○'
}

function stepDoneClass(st) {
  const items = st.items || []
  const done = items.filter((i) => props.itemsChecked[i.key]).length
  if (items.length && done === items.length) return 'done'
  if (done > 0) return 'partial'
  return ''
}

function onToggle(key, checked) {
  emit('toggle-item', key, checked)
}

watch(
  () => props.steps,
  (steps) => {
    for (const st of steps || []) {
      if (st.highlight && expanded[st.key] === undefined) {
        expanded[st.key] = true
      }
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1.1rem;
}
.head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.icon {
  opacity: 0.85;
}
.meta {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.steps {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.step {
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.02);
}
.step.highlight {
  border-color: color-mix(in srgb, var(--step-hl, #ec4899) 42%, transparent);
}
.step-head {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.65rem;
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  text-align: left;
  font: inherit;
}
.step-head:hover {
  background: rgba(255, 255, 255, 0.04);
}
.prog {
  width: 1.25rem;
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-muted);
}
.prog.done {
  color: #3b82f6;
}
.prog.partial {
  color: var(--warning);
}
.step-title {
  flex: 1;
  font-size: 0.88rem;
}
.n {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.step-body {
  padding: 0.35rem 0.65rem 0.75rem 2.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}
.item-row {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  font-size: 0.82rem;
  line-height: 1.4;
  color: var(--text-muted);
  cursor: pointer;
}
.item-row input {
  margin-top: 0.2rem;
  accent-color: #3b82f6;
}
</style>
