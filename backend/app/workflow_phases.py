"""10-phase Timeline: only listed agents are 'lit' for coordination (dropship / niche app)."""

# Each deliverable: key, label, optional auto_check rule (see deliverable_checker), optional required (default True).
PHASES: list[dict[str, object]] = [
    {
        "index": 1,
        "title": "Recherche niche & SEO",
        "summary": "Marlène prospecte, Gaston score SEO, Édith cadre l’intel.",
        "agents": ["marlene", "gaston", "edith"],
        "deliverables": [
            {
                "key": "niches_candidates",
                "label": "≥5 niches candidates listées",
                "auto_check": "niches_count>=5",
            },
            {
                "key": "niche_scored",
                "label": "≥1 niche avec score ≥7.5",
                "auto_check": "niches_score>=7.5",
            },
            {
                "key": "niche_validated",
                "label": "Niche finale choisie par Romain",
                "auto_check": None,
            },
        ],
    },
    {
        "index": 2,
        "title": "Stratégie & arbitrage",
        "summary": "Yvon tranche, Marlène défend ou retire les niches.",
        "agents": ["yvon", "marlene"],
        "deliverables": [
            {
                "key": "arbitrage_doc",
                "label": "Arbitrage niche / concurrence documenté",
                "auto_check": None,
            },
            {
                "key": "go_nogo",
                "label": "Décision GO / NO-GO validée",
                "auto_check": None,
            },
        ],
    },
    {
        "index": 3,
        "title": "Branding & naming",
        "summary": "Identité boutique / app, promesse, tonalité.",
        "agents": ["colette", "yvon"],
        "deliverables": [
            {
                "key": "naming_shortlist",
                "label": "Shortlist naming + contrôle disponibilité",
                "auto_check": None,
            },
            {
                "key": "brand_brief",
                "label": "Brief marque (promesse, tonalité, visuels)",
                "auto_check": None,
            },
        ],
    },
    {
        "index": 4,
        "title": "Setup Shopify / shell app",
        "summary": "Structure technique, thème, navigation.",
        "agents": ["theodore", "colette"],
        "deliverables": [
            {
                "key": "store_or_app_shell",
                "label": "Boutique ou shell app déployé (staging)",
                "auto_check": None,
            },
            {
                "key": "nav_theme",
                "label": "Navigation + thème validés",
                "auto_check": None,
            },
        ],
    },
    {
        "index": 5,
        "title": "Contenu & catalogue",
        "summary": "Fiches produit, pages, copy conversion.",
        "agents": ["hugo", "colette"],
        "deliverables": [
            {
                "key": "catalog_min",
                "label": "Catalogue minimal publiable (SKUs / pages clefs)",
                "auto_check": None,
            },
            {
                "key": "copy_conversion",
                "label": "Copy conversion revue (above the fold)",
                "auto_check": None,
            },
        ],
    },
    {
        "index": 6,
        "title": "QA & ASO",
        "summary": "Contrôle qualité, métadonnées stores, corrections.",
        "agents": ["simone", "gaston"],
        "deliverables": [
            {
                "key": "qa_pass",
                "label": "Pass QA bloquants résolus",
                "auto_check": None,
            },
            {
                "key": "aso_metadata",
                "label": "Métadonnées ASO prêtes (titres, keywords)",
                "auto_check": None,
            },
        ],
    },
    {
        "index": 7,
        "title": "Veille & amplification",
        "summary": "Intel marché, social, angles marketing.",
        "agents": ["edith", "marcel"],
        "deliverables": [
            {
                "key": "intel_snapshot",
                "label": "Snapshot veille + angles prioritaires",
                "auto_check": None,
            },
            {
                "key": "amplification_plan",
                "label": "Plan amplification validé",
                "auto_check": None,
            },
        ],
    },
    {
        "index": 8,
        "title": "Support & documentation",
        "summary": "FAQ, politiques, prise en charge utilisateur.",
        "agents": ["raymond", "lucien"],
        "deliverables": [
            {
                "key": "faq_policies",
                "label": "FAQ + politiques publiées",
                "auto_check": None,
            },
            {
                "key": "support_playbook",
                "label": "Playbook support (SLA, escalade)",
                "auto_check": None,
            },
        ],
    },
    {
        "index": 9,
        "title": "Lancement & distribution",
        "summary": "Go-live, canaux, logistique / rollout.",
        "agents": ["baptiste", "fernand"],
        "deliverables": [
            {
                "key": "golive_checklist",
                "label": "Checklist go-live cochée",
                "auto_check": None,
            },
            {
                "key": "distribution_channels",
                "label": "Canaux distribution activés",
                "auto_check": None,
            },
        ],
    },
    {
        "index": 10,
        "title": "Finance & scale",
        "summary": "Unit economics, réinvestissement, priorisation.",
        "agents": ["germaine", "yvon"],
        "deliverables": [
            {
                "key": "unit_economics",
                "label": "Unit economics revus",
                "auto_check": None,
            },
            {
                "key": "scale_priorities",
                "label": "Priorités scale trimestre",
                "auto_check": None,
            },
        ],
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
