import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const placeholder = () => import('@/views/PlaceholderView.vue')

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/views/ShellView.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: () => import('@/views/DashboardView.vue'), meta: { title: 'Dashboard' } },
      { path: 'crew', name: 'crew', component: () => import('@/views/CrewView.vue'), meta: { title: 'Team' } },
      { path: 'apps', name: 'apps', component: () => import('@/views/AppsView.vue'), meta: { title: 'Apps' } },
      { path: 'tasks', name: 'tasks', component: () => import('@/views/TasksView.vue'), meta: { title: 'Tasks' } },
      { path: 'timeline', name: 'timeline', component: () => import('@/views/TimelineView.vue'), meta: { title: 'Timeline' } },
      { path: 'wire', name: 'wire', component: () => import('@/views/WireView.vue'), meta: { title: 'Wire' } },
      { path: 'nerve', name: 'nerve', component: () => import('@/views/NerveView.vue'), meta: { title: 'Agent Files' } },
      { path: 'briefing', name: 'briefing', component: placeholder, meta: { title: 'Briefing' } },
      { path: 'war-room', name: 'war-room', component: placeholder, meta: { title: 'War Room' } },
      { path: 'decision', name: 'decision', component: placeholder, meta: { title: 'Décision' } },
      { path: 'process', name: 'process', component: placeholder, meta: { title: 'Process' } },
      { path: 'niches', name: 'niches', component: placeholder, meta: { title: 'Niches' } },
      { path: 'niche-galaxy', name: 'niche-galaxy', component: placeholder, meta: { title: 'Niche Galaxy' } },
      { path: 'comparator', name: 'comparator', component: placeholder, meta: { title: 'Comparator' } },
      { path: 'launchpad', name: 'launchpad', component: placeholder, meta: { title: 'Launchpad' } },
      { path: 'seo-ranks', name: 'seo-ranks', component: placeholder, meta: { title: 'SEO Ranks' } },
      { path: 'seo-spy', name: 'seo-spy', component: placeholder, meta: { title: 'SEO Spy' } },
      { path: 'openclaw-intel', name: 'openclaw-intel', component: placeholder, meta: { title: 'OpenClaw Intel' } },
      { path: 'ecom-intel', name: 'ecom-intel', component: placeholder, meta: { title: 'Ecom Intel' } },
      { path: 'newsletter', name: 'newsletter', component: placeholder, meta: { title: 'Newsletter' } },
      { path: 'memory', name: 'memory', component: placeholder, meta: { title: 'Memory' } },
      { path: 'apis', name: 'apis', component: placeholder, meta: { title: 'APIs' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    if (auth.isAuthenticated && to.name === 'login') return next({ name: 'dashboard' })
    return next()
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }
  next()
})

export default router
