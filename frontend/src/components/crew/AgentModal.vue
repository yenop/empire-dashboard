<template>
  <Teleport to="body">
    <div v-if="open && agent" class="backdrop" @click.self="emit('close')">
      <div class="modal">
        <header class="hd">
          <div class="avatar" :style="{ borderColor: agent.color }">{{ agent.emoji }}</div>
          <div>
            <h2>{{ agent.name }}</h2>
            <div class="role" :style="{ color: agent.color }">{{ agent.role }}</div>
            <div class="status">{{ agent.status }}</div>
          </div>
          <button type="button" class="close" @click="emit('close')">×</button>
        </header>
        <p class="blurb">{{ agent.pole }} — XP {{ agent.xp }}/{{ agent.max_xp }}</p>
        <h3>Compétences</h3>
        <ul class="skills">
          <li v-for="(v, k) in skillMap" :key="k">
            <span>{{ k }}</span>
            <div class="bar"><div :style="{ width: v + '%' }" /></div>
            <span class="n">{{ v }}</span>
          </li>
        </ul>
        <div class="stats">
          <div><strong>{{ agent.tasks_count }}</strong><span>Tâches</span></div>
          <div><strong>{{ agent.messages_count }}</strong><span>Messages</span></div>
          <div><strong>{{ agent.xp }}</strong><span>XP</span></div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  open: Boolean,
  agent: { type: Object, default: null },
})

const emit = defineEmits(['close'])

const skillMap = computed(() => {
  if (props.agent?.skills && typeof props.agent.skills === 'object') {
    return props.agent.skills
  }
  return { Stratégie: 50, Exécution: 50, Rigueur: 50 }
})
</script>

<style scoped>
.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.modal {
  width: 100%;
  max-width: 420px;
  max-height: 90vh;
  overflow: auto;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem;
}
.hd {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}
.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: 2px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  background: #00000040;
}
.hd h2 {
  margin: 0;
  font-size: 1.1rem;
}
.role {
  font-size: 0.8rem;
  margin-top: 0.15rem;
}
.status {
  font-size: 0.65rem;
  text-transform: uppercase;
  color: var(--text-muted);
  font-family: var(--font-mono);
  margin-top: 0.25rem;
}
.close {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}
.blurb {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 1rem 0;
}
h3 {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  font-family: var(--font-mono);
  margin: 0 0 0.5rem;
}
.skills {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.skills li {
  display: grid;
  grid-template-columns: 100px 1fr 32px;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}
.bar {
  height: 4px;
  background: #ffffff10;
  border-radius: 2px;
  overflow: hidden;
}
.bar > div {
  height: 100%;
  background: var(--info);
  border-radius: 2px;
}
.n {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-muted);
  text-align: right;
}
.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
  text-align: center;
}
.stats strong {
  display: block;
  font-size: 1.1rem;
  font-family: var(--font-mono);
  color: var(--accent);
}
.stats span {
  font-size: 0.65rem;
  color: var(--text-muted);
  text-transform: uppercase;
}
</style>
