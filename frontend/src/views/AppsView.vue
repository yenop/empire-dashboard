<template>
  <div v-if="loading" class="muted">Chargement…</div>
  <div v-else class="grid">
    <AppCard v-for="a in apps" :key="a.id" :app="a" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'
import AppCard from '@/components/apps/AppCard.vue'

const loading = ref(true)
const apps = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/api/apps')
    apps.value = data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.muted {
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}
@media (max-width: 800px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
