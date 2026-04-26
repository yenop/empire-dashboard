<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="logo">APP EMPIRE</div>
      <div class="by">by Nicolas</div>
    </div>
    <div class="live-pill">
      <span class="dot pulse-mint" />
      LIVE
    </div>
    <nav class="nav">
      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="nav-link"
        active-class="active"
      >
        <span>{{ item.label }}</span>
        <span v-if="item.badge" class="badge">{{ item.badge }}</span>
      </RouterLink>
    </nav>
    <div class="mrr-widget">
      <div class="mrr-label">Objectif MRR</div>
      <div class="mrr-val"><span class="dollar">$</span>{{ mrrCurrent.toFixed(0) }} <span class="sep">/</span> $10K</div>
      <div class="bar"><div class="fill" :style="{ width: progress + '%' }" /></div>
    </div>
    <button type="button" class="logout" @click="logout">Déconnexion</button>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}

const items = [
  { to: '/', label: 'Dashboard', badge: null },
  { to: '/timeline', label: 'Timeline', badge: null },
  { to: '/wire', label: 'Wire', badge: null },
  { to: '/nerve', label: 'Nerve', badge: null },
  { to: '/crew', label: 'Crew', badge: '14' },
  { to: '/apps', label: 'Apps', badge: '4' },
  { to: '/tasks', label: 'Tasks', badge: null },
]

const mrrCurrent = 30
const progress = computed(() => Math.min(100, (mrrCurrent / 10000) * 100))
</script>

<style scoped>
.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 1.25rem 0.75rem;
  min-height: 100vh;
}
.brand {
  padding: 0 0.5rem 1rem;
}
.logo {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 0.95rem;
  letter-spacing: 0.04em;
  color: var(--text);
}
.by {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}
.live-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  margin: 0 0.5rem 1.25rem;
  padding: 0.2rem 0.5rem;
  font-size: 0.65rem;
  font-family: var(--font-mono);
  color: var(--success);
  background: rgba(16, 185, 129, 0.12);
  border-radius: 4px;
  width: fit-content;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--success);
}
.nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}
.nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.65rem;
  border-radius: 6px;
  color: var(--text-muted);
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}
.nav-link:hover {
  background: #ffffff08;
  color: var(--text);
}
.nav-link.active {
  background: #ffffff0d;
  color: var(--accent);
}
.badge {
  font-size: 0.65rem;
  font-family: var(--font-mono);
  color: var(--text-muted);
  background: #ffffff0a;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}
.mrr-widget {
  margin-top: auto;
  padding: 0.75rem 0.5rem 0;
  border-top: 1px solid var(--border);
}
.mrr-label {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  font-family: var(--font-mono);
  margin-bottom: 0.35rem;
}
.mrr-val {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--accent);
  margin-bottom: 0.4rem;
}
.sep {
  color: var(--text-muted);
  font-weight: 400;
}
.bar {
  height: 4px;
  background: #ffffff10;
  border-radius: 2px;
  overflow: hidden;
}
.fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), #d97706);
  border-radius: 2px;
  transition: width 0.4s ease;
}
.logout {
  margin-top: 0.75rem;
  padding: 0.45rem;
  width: 100%;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border: 1px solid #ffffff18;
  border-radius: 6px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}
.logout:hover {
  color: var(--danger);
  border-color: #f43f5e44;
}
</style>
