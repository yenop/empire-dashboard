"""10-phase Timeline: only listed agents are 'lit' for coordination (dropship / niche app)."""

PHASES: list[dict[str, object]] = [
    {
        "index": 1,
        "title": "Recherche niche & SEO",
        "summary": "Marlène prospecte, Gaston score SEO, Édith cadre l’intel.",
        "agents": ["marlene", "gaston", "edith"],
    },
    {
        "index": 2,
        "title": "Stratégie & arbitrage",
        "summary": "Yvon tranche, Marlène défend ou retire les niches.",
        "agents": ["yvon", "marlene"],
    },
    {
        "index": 3,
        "title": "Branding & naming",
        "summary": "Identité boutique / app, promesse, tonalité.",
        "agents": ["colette", "yvon"],
    },
    {
        "index": 4,
        "title": "Setup Shopify / shell app",
        "summary": "Structure technique, thème, navigation.",
        "agents": ["theodore", "colette"],
    },
    {
        "index": 5,
        "title": "Contenu & catalogue",
        "summary": "Fiches produit, pages, copy conversion.",
        "agents": ["hugo", "colette"],
    },
    {
        "index": 6,
        "title": "QA & ASO",
        "summary": "Contrôle qualité, métadonnées stores, corrections.",
        "agents": ["simone", "gaston"],
    },
    {
        "index": 7,
        "title": "Veille & amplification",
        "summary": "Intel marché, social, angles marketing.",
        "agents": ["edith", "marcel"],
    },
    {
        "index": 8,
        "title": "Support & documentation",
        "summary": "FAQ, politiques, prise en charge utilisateur.",
        "agents": ["raymond", "lucien"],
    },
    {
        "index": 9,
        "title": "Lancement & distribution",
        "summary": "Go-live, canaux, logistique / rollout.",
        "agents": ["baptiste", "fernand"],
    },
    {
        "index": 10,
        "title": "Finance & scale",
        "summary": "Unit economics, réinvestissement, priorisation.",
        "agents": ["germaine", "yvon"],
    },
]

NERVE_SLUGS = ("identity", "soul", "memory", "agents", "heartbeat")
NERVE_LABELS = {
    "identity": "IDENTITY.md",
    "soul": "SOUL.md",
    "memory": "MEMORY.md",
    "agents": "AGENTS.md",
    "heartbeat": "HEARTBEAT.md",
}
