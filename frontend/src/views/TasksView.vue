<template>
  <div v-if="loading" class="muted">Chargement…</div>
  <KanbanBoard v-else :tasks="tasks" @move="onMove" />
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'
import KanbanBoard from '@/components/tasks/KanbanBoard.vue'

const loading = ref(true)
const tasks = ref([])

async function load() {
  const { data } = await api.get('/api/tasks')
  tasks.value = data
}

onMounted(async () => {
  try {
    await load()
  } finally {
    loading.value = false
  }
})

async function onMove(t, newStatus) {
  await api.put(`/api/tasks/${t.id}`, { status: newStatus })
  await load()
}
</script>

<style scoped>
.muted {
  color: var(--text-muted);
  font-family: var(--font-mono);
}
</style>
