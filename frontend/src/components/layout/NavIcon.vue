<template>
  <svg
    class="nav-icon"
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.65"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <!-- Briefing: satellite / dish -->
    <g v-if="name === 'briefing'">
      <path d="M4 10c2-4 6-6 10-6" />
      <path d="M8 14c1.5-2 4-3 6-3" />
      <path d="M12 18h.01" />
      <path d="M18 8l2 2" />
      <path d="M20 6l-1 1" />
    </g>
    <!-- Dashboard: home -->
    <g v-else-if="name === 'home'">
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5 10v10h14V10" />
    </g>
    <!-- War room: monitor -->
    <g v-else-if="name === 'monitor'">
      <rect x="3" y="4" width="18" height="12" rx="1.5" />
      <path d="M8 21h8" />
      <path d="M12 17v4" />
    </g>
    <!-- Team -->
    <g v-else-if="name === 'team'">
      <circle cx="9" cy="8" r="3" />
      <circle cx="16" cy="9" r="2.5" />
      <path d="M4 20c0-3 3.5-5 7-5s7 2 7 5" />
      <path d="M14 20c0-2 1.8-3.5 4-3.5" />
    </g>
    <!-- Tasks: list + checks -->
    <g v-else-if="name === 'tasks'">
      <path d="M9 6h11" />
      <path d="M9 12h11" />
      <path d="M9 18h7" />
      <path d="M5 6l1 1 2-2" />
      <path d="M5 12l1 1 2-2" />
    </g>
    <!-- Wire: bubble -->
    <g v-else-if="name === 'bubble'">
      <path d="M21 12a7 7 0 0 1-7 7H8l-5 3v-3a7 7 0 1 1 18-7z" />
    </g>
    <!-- Timeline: clock -->
    <g v-else-if="name === 'clock'">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v6l4 2" />
    </g>
    <!-- APIs: link -->
    <g v-else-if="name === 'link'">
      <path d="M10 13a5 5 0 0 1 0-7l1-1a5 5 0 0 1 7 7l-1 1" />
      <path d="M14 11a5 5 0 0 1 0 7l-1 1a5 5 0 0 1-7-7l1-1" />
    </g>
    <!-- Agent files: document -->
    <g v-else-if="name === 'document'">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <path d="M14 2v6h6" />
      <path d="M9 15h6" />
      <path d="M9 11h2" />
    </g>
    <!-- Book: process -->
    <g v-else-if="name === 'book'">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
    </g>
    <!-- Target: niches -->
    <g v-else-if="name === 'target'">
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="5" />
      <circle cx="12" cy="12" r="1.5" />
    </g>
    <!-- Globe -->
    <g v-else-if="name === 'globe'">
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18" />
      <path d="M12 3a14 14 0 0 0 0 18 14 14 0 0 0 0-18" />
    </g>
    <!-- Comparator: balance -->
    <g v-else-if="name === 'balance'">
      <path d="M12 3v18" />
      <path d="M5 7h14" />
      <path d="M7 7 5 12h4L7 7" />
      <path d="M17 7l2 5h-4l2-5" />
    </g>
    <!-- Rocket -->
    <g v-else-if="name === 'rocket'">
      <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
      <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
      <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
      <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
    </g>
    <!-- Search -->
    <g v-else-if="name === 'search'">
      <circle cx="11" cy="11" r="6" />
      <path d="m21 21-4.3-4.3" />
    </g>
    <!-- Search spy: search + small dot -->
    <g v-else-if="name === 'searchSpy'">
      <circle cx="10.5" cy="10.5" r="5.5" />
      <path d="M20 20l-3.5-3.5" />
      <circle cx="17" cy="7" r="1.2" fill="currentColor" stroke="none" />
    </g>
    <!-- Star outline: décision -->
    <g v-else-if="name === 'star'">
      <path d="M12 2l2.4 7.4h7.6l-6 4.6 2.3 7-6.3-4.6-6.3 4.6 2.3-7-6-4.6h7.6z" />
    </g>
    <!-- Apps grid -->
    <g v-else-if="name === 'apps'">
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </g>
    <!-- Lightning -->
    <g v-else-if="name === 'bolt'">
      <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z" />
    </g>
    <!-- Mail -->
    <g v-else-if="name === 'mail'">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <path d="m22 6-10 7L2 6" />
    </g>
    <!-- Memory: chip / stack -->
    <g v-else-if="name === 'brain'">
      <rect x="5" y="7" width="14" height="10" rx="1.5" />
      <path d="M9 11h6M9 14h4" />
      <circle cx="8" cy="10" r="0.75" fill="currentColor" stroke="none" />
    </g>
    <!-- Fallback: circle -->
    <circle v-else cx="12" cy="12" r="4" />
  </svg>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    default: 'home',
  },
})
</script>

<style scoped>
.nav-icon {
  display: block;
  flex-shrink: 0;
  color: inherit;
  opacity: 0.88;
}
</style>
