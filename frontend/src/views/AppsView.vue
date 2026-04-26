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
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr));
  gap: 1rem;
}
</style>
