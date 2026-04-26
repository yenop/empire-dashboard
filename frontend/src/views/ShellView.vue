<template>
  <div class="shell">
    <div
      v-show="navOpen"
      class="nav-backdrop"
      aria-hidden="true"
      @click="closeNav"
    />
    <Sidebar />
    <div class="main">
      <Topbar />
      <main class="content scroll-thin">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, provide, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from '@/components/layout/Sidebar.vue'
import Topbar from '@/components/layout/Topbar.vue'

const route = useRoute()
const navOpen = ref(false)

function toggleNav() {
  navOpen.value = !navOpen.value
}
function closeNav() {
  navOpen.value = false
}

provide('shellNav', { navOpen, toggleNav, closeNav })

watch(
  () => route.fullPath,
  () => {
    closeNav()
  }
)

watch(navOpen, (open) => {
  if (typeof document === 'undefined') return
  document.body.classList.toggle('drawer-open', open)
})

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', onResize)
  }
})
onUnmounted(() => {
  if (typeof document !== 'undefined') {
    document.body.classList.remove('drawer-open')
  }
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', onResize)
  }
})

function onResize() {
  if (typeof window === 'undefined') return
  if (window.matchMedia('(min-width: 901px)').matches) {
    closeNav()
  }
}
</script>

<style scoped>
.shell {
  display: flex;
  min-height: 100vh;
  background: var(--bg);
}
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.content {
  flex: 1;
  padding: 1.25rem 1.5rem 2rem;
  padding-left: max(1.5rem, env(safe-area-inset-left));
  padding-right: max(1.5rem, env(safe-area-inset-right));
  padding-bottom: max(2rem, env(safe-area-inset-bottom));
  overflow: auto;
}
@media (max-width: 640px) {
  .content {
    padding: 1rem 1rem 1.5rem;
    padding-left: max(1rem, env(safe-area-inset-left));
    padding-right: max(1rem, env(safe-area-inset-right));
  }
}
.nav-backdrop {
  display: none;
}
@media (max-width: 900px) {
  .nav-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 100;
    background: rgba(0, 0, 0, 0.55);
    backdrop-filter: blur(2px);
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.12s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
