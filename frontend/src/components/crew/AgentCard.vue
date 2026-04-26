<template>
  <button
    type="button"
    class="card"
    :class="{ dimmed: phaseLit === false }"
    @click="$emit('open', agent)"
  >
    <div class="accent" :style="{ background: agent.color }" />
    <div class="head">
      <div class="avatar" :style="{ borderColor: agent.color, color: agent.color }">
        {{ agent.emoji }}
      </div>
      <div>
        <div class="name">{{ agent.name }}</div>
        <div class="role" :style="{ color: agent.color }">{{ agent.role }}</div>
      </div>
      <span
        class="status-dot"
        :class="agent.status"
        :style="dotGlow"
      />
    </div>
    <p class="desc">{{ shortDesc }}</p>
    <div class="xp-row">
      <div class="xp-bar" :style="{ '--c': agent.color }">
        <div class="xp-fill" :style="{ width: xpPct + '%' }" />
      </div>
      <span class="rank">{{ agent.rank_label }}</span>
    </div>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  agent: { type: Object, required: true },
  /** false = agent hors phase courante (Timeline) — grisé */
  phaseLit: { type: Boolean, default: true },
})

defineEmits(['open'])

const shortDesc = computed(
  () => `${props.agent.pole} · ${props.agent.tasks_count} tâches`
)

const xpPct = computed(() =>
  Math.min(100, (props.agent.xp / Math.max(1, props.agent.max_xp)) * 100)
)

const dotGlow = computed(() => {
  if (props.agent.status === 'active') {
    return { boxShadow: `0 0 6px ${props.agent.color}` }
  }
  return {}
})
</script>

<style scoped>
.card {
  position: relative;
  text-align: left;
  width: 100%;
  padding: 0 0.85rem 0.85rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  color: inherit;
  font: inherit;
  transition: transform 0.15s, border-color 0.15s;
  overflow: hidden;
}
.card:hover {
  transform: translateY(-2px);
  border-color: var(--border-hover);
}
.card.dimmed {
  opacity: 0.4;
  filter: grayscale(0.35);
}
.card.dimmed:hover {
  opacity: 0.55;
}
.accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
}
.head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
}
.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  border: 2px solid;
  background: #00000040;
  flex-shrink: 0;
}
.name {
  font-weight: 600;
  font-size: 0.9rem;
}
.role {
  font-size: 0.72rem;
  margin-top: 0.1rem;
}
.status-dot {
  margin-left: auto;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.active {
  background: #10b981;
  animation: pulse-dot 2s ease-in-out infinite;
}
.status-dot.setup {
  background: #f59e0b;
}
.status-dot.recruit {
  background: #444;
}
.desc {
  margin: 0.5rem 0 0.65rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.4;
}
.xp-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.xp-bar {
  flex: 1;
  height: 4px;
  background: #ffffff10;
  border-radius: 2px;
  overflow: hidden;
}
.xp-fill {
  height: 100%;
  background: var(--c, var(--accent));
  border-radius: 2px;
}
.rank {
  font-size: 0.65rem;
  font-family: var(--font-mono);
  color: var(--text-muted);
}
</style>
