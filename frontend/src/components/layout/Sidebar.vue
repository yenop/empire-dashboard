<template>
  <aside class="sidebar" :class="{ open: navOpen }">
    <div class="brand">
      <div class="logo">APP EMPIRE</div>
      <div class="by">by Nicolas</div>
    </div>
    <div class="live-pill">
      <span class="dot pulse-mint" />
      LIVE
    </div>
    <nav class="nav-scroll scroll-thin" aria-label="Navigation principale">
      <div
        v-for="section in NAV_SECTIONS"
        :key="section.id"
        class="nav-section"
      >
        <button
          type="button"
          class="section-head"
          :class="{ 'section-head--system': section.accent === 'system' }"
          :aria-expanded="sectionOpen[section.id]"
          :aria-controls="`nav-section-${section.id}`"
          @click="toggleSection(section.id)"
        >
          <span class="section-label">{{ section.label }}</span>
          <span class="chevron" :class="{ collapsed: !sectionOpen[section.id] }" aria-hidden="true" />
        </button>
        <div
          :id="`nav-section-${section.id}`"
          v-show="sectionOpen[section.id]"
          class="section-items"
        >
          <template v-for="item in section.items" :key="item.routeName">
            <RouterLink
              v-if="item.routeName !== 'dashboard'"
              :to="{ name: item.routeName }"
              class="nav-link"
              active-class="active"
              @click="onNavClick"
            >
              <span class="nav-link-main">
                <span class="icon" aria-hidden="true">{{ item.icon }}</span>
                <span class="nav-text">{{ item.label }}</span>
              </span>
              <span v-if="item.placeholder" class="pill-soon">bientôt</span>
            </RouterLink>
            <RouterLink
              v-else
              :to="{ name: 'dashboard' }"
              class="nav-link"
              custom
              v-slot="{ href, navigate, isExactActive }"
            >
              <a
                :href="href"
                class="nav-link"
                :class="{ active: isExactActive }"
                @click="(e) => { navigate(e); onNavClick() }"
              >
                <span class="nav-link-main">
                  <span class="icon" aria-hidden="true">{{ item.icon }}</span>
                  <span class="nav-text">{{ item.label }}</span>
                </span>
              </a>
            </RouterLink>
          </template>
        </div>
      </div>
    </nav>
    <div class="status-footer">
      <p class="status-line">
        {{ onlineAgents }}/{{ totalAgents }} agents en ligne
      </p>
      <p class="status-line status-conn">
        <span class="conn-dot" :class="{ ok: apiOk }" aria-hidden="true" />
        <span>{{ apiOk ? 'Dashboard connecté' : 'API indisponible' }}</span>
      </p>
    </div>
    <div class="mrr-widget">
      <div class="mrr-label">Objectif MRR</div>
      <div class="mrr-val"><span class="dollar">$</span>{{ mrrCurrent.toFixed(0) }} <span class="sep">/</span> $10K</div>
      <div class="bar"><div class="fill" :style="{ width: progress + '%' }" /></div>
    </div>
    <button type="button" class="logout" @click="logout">Déconnexion</button>
  </aside>
</template>

<script setup>
import { computed, inject, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { NAV_SECTIONS } from '@/config/navSections'
import { useSidebarStatus } from '@/composables/useSidebarStatus'

const LS_PREFIX = 'empire-nav-open-'

function readStoredOpen(id, defaultOpen) {
  if (typeof localStorage === 'undefined') return defaultOpen
  try {
    const v = localStorage.getItem(`${LS_PREFIX}${id}`)
    if (v === '1') return true
    if (v === '0') return false
  } catch {
    /* ignore */
  }
  return defaultOpen
}

function writeStoredOpen(id, open) {
  if (typeof localStorage === 'undefined') return
  try {
    localStorage.setItem(`${LS_PREFIX}${id}`, open ? '1' : '0')
  } catch {
    /* ignore */
  }
}

const shellNav = inject('shellNav', null)
const navOpen = computed(() => Boolean(shellNav?.navOpen?.value))

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { totalAgents, onlineAgents, apiOk, refresh } = useSidebarStatus()

const sectionOpen = reactive({})
for (const s of NAV_SECTIONS) {
  sectionOpen[s.id] = readStoredOpen(s.id, s.defaultOpen)
}

function toggleSection(id) {
  sectionOpen[id] = !sectionOpen[id]
  writeStoredOpen(id, sectionOpen[id])
}

function onNavClick() {
  shellNav?.closeNav?.()
}

function logout() {
  shellNav?.closeNav?.()
  auth.logout()
  router.push({ name: 'login' })
}

watch(
  () => route.fullPath,
  () => {
    refresh()
  }
)

const mrrCurrent = 30
const progress = computed(() => Math.min(100, (mrrCurrent / 10000) * 100))
</script>

<style scoped>
.sidebar {
  width: 248px;
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
  flex-shrink: 0;
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
  margin: 0 0.5rem 1rem;
  padding: 0.2rem 0.5rem;
  font-size: 0.65rem;
  font-family: var(--font-mono);
  color: var(--success);
  background: rgba(16, 185, 129, 0.12);
  border-radius: 4px;
  width: fit-content;
  flex-shrink: 0;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--success);
}
.nav-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 0.15rem;
  margin-right: -0.15rem;
}
.nav-section {
  margin-bottom: 1rem;
}
.nav-section:last-of-type {
  margin-bottom: 0.5rem;
}
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.35rem 0.5rem 0.5rem;
  margin: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  text-align: left;
  border-radius: 6px;
  color: var(--text-muted);
  transition: color 0.15s, background 0.15s;
}
.section-head:hover {
  color: var(--text);
  background: #ffffff06;
}
.section-label {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.section-head--system .section-label {
  color: var(--warning);
}
.section-head:not(.section-head--system) .section-label {
  color: var(--text-muted);
}
.chevron {
  width: 0.45rem;
  height: 0.45rem;
  border-right: 1.5px solid currentColor;
  border-bottom: 1.5px solid currentColor;
  transform: rotate(45deg);
  margin-top: -0.2rem;
  opacity: 0.7;
  transition: transform 0.2s ease;
}
.chevron.collapsed {
  transform: rotate(-45deg);
  margin-top: 0.1rem;
}
.section-items {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding-top: 0.15rem;
}
.nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.35rem;
  padding: 0.5rem 0.65rem;
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 0.875rem;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}
.nav-link:hover {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text);
}
.nav-link.active {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text);
}
.nav-link-main {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  min-width: 0;
}
.icon {
  font-size: 0.95rem;
  line-height: 1;
  flex-shrink: 0;
}
.nav-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pill-soon {
  flex-shrink: 0;
  font-size: 0.6rem;
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  opacity: 0.75;
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
  background: #ffffff08;
}
.status-footer {
  flex-shrink: 0;
  padding: 0.65rem 0.5rem 0.75rem;
  margin-top: 0.25rem;
  border-top: 1px solid var(--border);
}
.status-line {
  margin: 0;
  font-size: 0.68rem;
  font-family: var(--font-mono);
  color: var(--text-muted);
  line-height: 1.45;
}
.status-conn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.35rem;
}
.conn-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
  background: var(--danger);
  opacity: 0.85;
}
.conn-dot.ok {
  background: var(--success);
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.45);
}
.mrr-widget {
  flex-shrink: 0;
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
  flex-shrink: 0;
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

@media (max-width: 900px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: min(288px, 88vw);
    z-index: 101;
    min-height: 100dvh;
    padding-top: max(1.25rem, env(safe-area-inset-top));
    padding-bottom: max(0.75rem, env(safe-area-inset-bottom));
    box-shadow: 8px 0 32px rgba(0, 0, 0, 0.45);
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    border-right: 1px solid var(--border);
  }
  .sidebar.open {
    transform: translateX(0);
  }
}
</style>
