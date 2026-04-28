/**
 * Sidebar navigation: App / niche, Empire, Système.
 * `routeName` must match a named route in `router/index.js`.
 */
export const NAV_SECTIONS = [
  {
    id: 'app',
    label: 'App / niche',
    accent: 'default',
    defaultOpen: false,
    items: [
      { routeName: 'store-factory', label: 'Store Factory', icon: '🏭', placeholder: true },
      { routeName: 'branding', label: 'Branding', icon: '⭐', placeholder: true },
      { routeName: 'phase-3', label: 'Phase 3', icon: '🚀', placeholder: true },
      { routeName: 'site-docs', label: 'Site 1 Docs', icon: '📄', placeholder: true },
      { routeName: 'revenue', label: 'Revenue', icon: '📈', placeholder: true },
      { routeName: 'profit-sim', label: 'Profit Sim', icon: '💲', placeholder: true },
      { routeName: 'analytics', label: 'Analytics', icon: '📊', placeholder: true },
      { routeName: 'content', label: 'Content', icon: '📝', placeholder: true },
      { routeName: 'products-db', label: 'Products DB', icon: '📦', placeholder: true },
    ],
  },
  {
    id: 'empire',
    label: 'Empire',
    accent: 'default',
    defaultOpen: true,
    items: [
      { routeName: 'dashboard', label: 'Dashboard', icon: '🏠', placeholder: false },
      { routeName: 'crew', label: 'Crew', icon: '👥', placeholder: false },
      { routeName: 'apps', label: 'Apps', icon: '📱', placeholder: false },
      { routeName: 'tasks', label: 'Tasks', icon: '✅', placeholder: false },
      { routeName: 'openclaw-intel', label: 'OpenClaw Intel', icon: '⚡', placeholder: true },
      { routeName: 'ecom-intel', label: 'Ecom Intel', icon: '⚡', placeholder: true },
      { routeName: 'newsletter', label: 'Newsletter', icon: '✉️', placeholder: true },
      { routeName: 'memory', label: 'Memory', icon: '🧠', placeholder: true },
    ],
  },
  {
    id: 'system',
    label: 'Système',
    accent: 'system',
    defaultOpen: true,
    items: [
      { routeName: 'wire', label: 'Wire', icon: '💬', placeholder: false },
      { routeName: 'timeline', label: 'Timeline', icon: '🕐', placeholder: false },
      { routeName: 'apis', label: 'APIs', icon: '🔗', placeholder: true },
      { routeName: 'nerve', label: 'Agent Files', icon: '📎', placeholder: false },
    ],
  },
]
