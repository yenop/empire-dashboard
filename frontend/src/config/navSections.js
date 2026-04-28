/**
 * Sidebar: COMMAND (pilotage), NICHES & SEO (app / niche), EMPIRE.
 * `icon` = id rendu par NavIcon.vue ; `routeName` = nom de route Vue Router.
 */
export const NAV_SECTIONS = [
  {
    id: 'command',
    label: 'COMMAND',
    accent: 'system',
    defaultOpen: true,
    items: [
      { routeName: 'briefing', label: 'Briefing', icon: 'briefing', placeholder: true },
      { routeName: 'dashboard', label: 'Dashboard', icon: 'home', placeholder: false },
      { routeName: 'war-room', label: 'War Room', icon: 'monitor', placeholder: true },
      { routeName: 'crew', label: 'Team', icon: 'team', placeholder: false },
      { routeName: 'tasks', label: 'Tasks', icon: 'tasks', placeholder: false },
      { routeName: 'wire', label: 'Wire', icon: 'bubble', placeholder: false },
      { routeName: 'timeline', label: 'Timeline', icon: 'clock', placeholder: false },
      { routeName: 'apis', label: 'APIs', icon: 'link', placeholder: true },
      { routeName: 'nerve', label: 'Agent Files', icon: 'document', placeholder: false },
    ],
  },
  {
    id: 'niches-seo',
    label: 'NICHES & SEO',
    accent: 'default',
    defaultOpen: true,
    items: [
      { routeName: 'decision', label: 'Décision', icon: 'star', labelEmoji: '🏆', placeholder: true },
      { routeName: 'process', label: 'Process', icon: 'book', placeholder: false },
      { routeName: 'niches', label: 'Niches', icon: 'target', placeholder: true },
      { routeName: 'niche-galaxy', label: 'Niche Galaxy', icon: 'globe', placeholder: true },
      { routeName: 'comparator', label: 'Comparator', icon: 'balance', placeholder: true },
      { routeName: 'launchpad', label: 'Launchpad', icon: 'rocket', placeholder: true },
      { routeName: 'seo-ranks', label: 'SEO Ranks', icon: 'search', placeholder: true },
      { routeName: 'seo-spy', label: 'SEO Spy', icon: 'searchSpy', placeholder: true },
    ],
  },
  {
    id: 'empire',
    label: 'EMPIRE',
    accent: 'default',
    defaultOpen: true,
    items: [
      { routeName: 'apps', label: 'Apps', icon: 'apps', placeholder: false },
      { routeName: 'openclaw-intel', label: 'OpenClaw Intel', icon: 'bolt', placeholder: true },
      { routeName: 'ecom-intel', label: 'Ecom Intel', icon: 'bolt', placeholder: true },
      { routeName: 'newsletter', label: 'Newsletter', icon: 'mail', placeholder: true },
      { routeName: 'memory', label: 'Memory', icon: 'brain', placeholder: true },
    ],
  },
]
