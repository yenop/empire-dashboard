import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
      { path: 'nerve', name: 'nerve', component: () => import('@/views/NerveView.vue'), meta: { title: 'Nerve center' } },
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
