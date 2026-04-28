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
      { path: 'crew', name: 'crew', component: () => import('@/views/CrewView.vue'), meta: { title: 'Crew' } },
      { path: 'apps', name: 'apps', component: () => import('@/views/AppsView.vue'), meta: { title: 'Apps' } },
      { path: 'tasks', name: 'tasks', component: () => import('@/views/TasksView.vue'), meta: { title: 'Tasks' } },
      { path: 'timeline', name: 'timeline', component: () => import('@/views/TimelineView.vue'), meta: { title: 'Timeline' } },
      { path: 'wire', name: 'wire', component: () => import('@/views/WireView.vue'), meta: { title: 'Wire' } },
      { path: 'nerve', name: 'nerve', component: () => import('@/views/NerveView.vue'), meta: { title: 'Agent Files' } },
      { path: 'store-factory', name: 'store-factory', component: placeholder, meta: { title: 'Store Factory' } },
      { path: 'branding', name: 'branding', component: placeholder, meta: { title: 'Branding' } },
      { path: 'phase-3', name: 'phase-3', component: placeholder, meta: { title: 'Phase 3' } },
      { path: 'site-docs', name: 'site-docs', component: placeholder, meta: { title: 'Site 1 Docs' } },
      { path: 'revenue', name: 'revenue', component: placeholder, meta: { title: 'Revenue' } },
      { path: 'profit-sim', name: 'profit-sim', component: placeholder, meta: { title: 'Profit Sim' } },
      { path: 'analytics', name: 'analytics', component: placeholder, meta: { title: 'Analytics' } },
      { path: 'content', name: 'content', component: placeholder, meta: { title: 'Content' } },
      { path: 'products-db', name: 'products-db', component: placeholder, meta: { title: 'Products DB' } },
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
