<template>
  <section class="ops">
    <h2 class="h2">Modules agents — sorties câblées</h2>
    <p class="intro">
      Niches (Marlène + Gaston), Content Pipeline (Hugo), SEO Ranks (Gaston), demandes clés API (tous agents → toi).
    </p>
    <div v-if="loading" class="muted">Chargement modules…</div>
    <div v-else class="grid">
      <div class="card niches">
        <div class="accent" style="background: #ec4899" />
        <h3>Niches</h3>
        <ul>
          <li v-for="n in niches" :key="n.id">
            <span class="t">{{ n.title }}</span>
            <span v-if="n.score_seo != null" class="score">{{ n.score_seo }}</span>
            <span class="st">{{ n.status }}</span>
          </li>
        </ul>
      </div>
      <div class="card content">
        <div class="accent" style="background: #06b6d4" />
        <h3>Content pipeline</h3>
        <ul>
          <li v-for="c in content" :key="c.id">
            <span class="t">{{ c.title }}</span>
            <span class="st">{{ c.stage }}</span>
          </li>
        </ul>
      </div>
      <div class="card seo">
        <div class="accent" style="background: #f59e0b" />
        <h3>SEO ranks</h3>
        <ul>
          <li v-for="s in seo" :key="s.id">
            <span class="t">{{ s.keyword }}</span>
            <span class="pos">#{{ s.position }}</span>
            <span class="app">{{ s.app_id || '—' }}</span>
          </li>
        </ul>
      </div>
      <div class="card apis">
        <div class="accent" style="background: #8b5cf6" />
        <h3>Demandes API</h3>
        <ul>
          <li v-for="r in apiReq" :key="r.id">
            <div class="row">
              <span class="t">{{ r.service_name }}</span>
              <span class="st">{{ r.status }}</span>
            </div>
            <div class="agent">{{ r.agent_id }}</div>
            <div v-if="r.status === 'pending'" class="actions">
              <button type="button" class="btn" @click="fulfill(r.id)">Clé fournie</button>
              <button type="button" class="btn ghost" @click="reject(r.id)">Refuser</button>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'

const loading = ref(true)
const niches = ref([])
const content = ref([])
const seo = ref([])
const apiReq = ref([])

async function load() {
  loading.value = true
  try {
    const [n, c, s, a] = await Promise.all([
      api.get('/api/ops/niches'),
      api.get('/api/ops/content-pipeline'),
      api.get('/api/ops/seo-ranks'),
      api.get('/api/ops/api-requests'),
    ])
    niches.value = (n.data || []).slice(0, 6)
    content.value = (c.data || []).slice(0, 6)
    seo.value = (s.data || []).slice(0, 6)
    apiReq.value = (a.data || []).slice(0, 8)
  } finally {
    loading.value = false
  }
}

async function fulfill(id) {
  await api.patch(`/api/ops/api-requests/${id}`, { status: 'fulfilled' })
  await load()
}

async function reject(id) {
  await api.patch(`/api/ops/api-requests/${id}`, { status: 'rejected' })
  await load()
}

onMounted(load)
</script>

<style scoped>
.ops {
  margin-top: 1.5rem;
}
.h2 {
  margin: 0 0 0.35rem;
  font-family: var(--font-mono);
  font-size: 0.95rem;
  letter-spacing: 0.03em;
}
.intro {
  margin: 0 0 1rem;
  font-size: 0.8rem;
  color: var(--text-muted);
  line-height: 1.45;
  max-width: 48rem;
}
.muted {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text-muted);
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
.card {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.75rem 0.85rem 0.85rem;
  overflow: hidden;
}
.card .accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
}
.card h3 {
  margin: 0.5rem 0 0.5rem;
  font-size: 0.72rem;
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}
.card ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}
.card li {
  font-size: 0.78rem;
  line-height: 1.35;
  border-bottom: 1px solid #ffffff08;
  padding-bottom: 0.35rem;
}
.card li:last-child {
  border-bottom: none;
  padding-bottom: 0;
}
.t {
  display: inline;
  font-weight: 500;
}
.score,
.pos {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--accent);
  margin-left: 0.35rem;
}
.st {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--text-muted);
  margin-left: 0.35rem;
}
.app {
  font-size: 0.6rem;
  color: var(--cyan);
  margin-left: 0.35rem;
}
.row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
}
.agent {
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-top: 0.15rem;
}
.actions {
  margin-top: 0.35rem;
  display: flex;
  gap: 0.35rem;
}
.btn {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  padding: 0.2rem 0.45rem;
  border-radius: 4px;
  border: 1px solid #10b98155;
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
  cursor: pointer;
}
.btn.ghost {
  border-color: #f43f5e44;
  background: transparent;
  color: var(--danger);
}
</style>
