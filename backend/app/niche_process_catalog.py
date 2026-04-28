"""Static catalog for « Process recherche de niches » (M08) — Marlène, Gaston, décision humaine."""

from typing import Any

# Pipeline cards (phase 3 = human, no agent_id)
PIPELINE: list[dict[str, Any]] = [
    {
        "id": "marlene",
        "agent_key": "marlene",
        "label": "Marlène",
        "role": "Business",
        "subtitle": "Découverte & Scoring Business",
        "color": "#ec4899",
        "icon": "search",
    },
    {
        "id": "gaston",
        "agent_key": "gaston",
        "label": "Gaston",
        "role": "SEO",
        "subtitle": "Analyse SEO & Validation",
        "color": "#3b82f6",
        "icon": "chart",
    },
    {
        "id": "nicolas",
        "agent_key": None,
        "label": "Nicolas",
        "role": "Décision",
        "subtitle": "GO / NO-GO (humain)",
        "color": "#f59e0b",
        "icon": "target",
    },
]


def _step(
    key: str, title: str, items: list[str], highlight: bool = False
) -> dict[str, Any]:
    return {
        "key": key,
        "title": title,
        "highlight": highlight,
        "items": [{"key": f"{key}.{i}", "label": lab} for i, lab in enumerate(items)],
    }


MARLENE_STEPS: list[dict[str, Any]] = [
    _step(
        "marlene.fiche",
        "Fiche d’identité",
        [
            "Nom précis (pas générique)",
            "Emoji",
            "Description 2–3 phrases",
            "Marché cible (FR/EN)",
        ],
    ),
    _step(
        "marlene.scoring",
        "Scoring 7 critères business (/10)",
        [
            "Passion identitaire — « Je suis un… » source Reddit/FB",
            "Taille communauté — Chiffre + 2 sources min",
            "Propension à dépenser — CSP + budget estimé",
            "Répétabilité achat — Occasions listées",
            "Fit POD visuel — Types de designs identifiés",
            "Concurrence POD (inversé) — Recherche Google FR",
            "International — Universel ou culturel ?",
        ],
        highlight=True,
    ),
    _step(
        "marlene.keywords",
        "Mots-clés identitaires niche (filtre Gaston)",
        [
            "Liste des seeds pour la phase SEO",
            "Alignés avec la promesse identitaire",
            "Format exploitable (copier vers Gaston)",
            "Vérification non génériques",
        ],
    ),
    _step(
        "marlene.communaute",
        "Données communauté",
        [
            "Sources actives (où vit la niche)",
            "Signaux d’engagement",
            "Freins / friction observés",
        ],
    ),
    _step(
        "marlene.design",
        "Potentiel design",
        [
            "Hooks visuels probables",
            "Contraintes licence / IP",
            "Angle créatif principal",
        ],
    ),
    _step(
        "marlene.synthese",
        "Synthèse",
        [
            "Résumé décisionnel pour la suite",
            "Points de vigilance",
            "Prêt pour passation Gaston",
        ],
    ),
]


GASTON_STEPS: list[dict[str, Any]] = [
    _step(
        "gaston.seeds",
        "Keywords seeds (25 min)",
        [
            "Brainstorm initial aligné mots-clés Marlène",
            "Volume de seeds minimal atteint",
            "Segments FR prioritaires",
            "Exclusions notées",
        ],
    ),
    _step(
        "gaston.collecte",
        "Collecte données par keyword",
        [
            "Volume / intention par seed",
            "Serp features notées",
            "Saisonnalité si visible",
            "Concurrents type par requête",
            "Coût cognitif collecte",
            "Tableau ou export à jour",
        ],
    ),
    _step(
        "gaston.filtrage",
        "Quadruple filtrage (CRITIQUE)",
        [
            "Filtre 1 — intention transactionnelle",
            "Filtre 2 — alignement niche",
            "Filtre 3 — faisabilité contenu",
            "Filtre 4 — cohérence avec seeds Marlène",
            "Décision garde / écart",
        ],
    ),
    _step(
        "gaston.kgr",
        "Classification KGR",
        [
            "Calcul ou estimation KGR par keyword vert",
            "Seuil vert documenté",
            "Liste des verts",
            "Justification borderline",
        ],
    ),
    _step(
        "gaston.serp",
        "Analyse SERP (top 3 verts)",
        [
            "Brave Search pour chaque keyword vert",
            "Identifier : blogs / marketplaces / boutiques POD / e-com",
            "Forces et faiblesses de chaque résultat",
            "Nombre de boutiques POD FR en page 1",
        ],
        highlight=True,
    ),
    _step(
        "gaston.concurrents",
        "Concurrents POD",
        [
            "Recherche « t-shirt [niche] », « poster [niche] » Google FR",
            "Pour chaque concurrent : domaine, plateforme, nb produits, style, battable ?",
            "Etsy FR — relevé synthétique",
        ],
    ),
    _step(
        "gaston.gaps",
        "Gaps & Opportunités",
        [
            "Besoin non couvert clairement",
            "Angle de différenciation",
            "Risque copie / commodité",
            "Quick wins SEO listés",
            "Angles longue traîne",
            "Synthèse opportunités vs risques",
        ],
    ),
    _step(
        "gaston.scoring_seo",
        "Scoring SEO (3 critères /10) — données SPÉCIFIQUES",
        [
            "Volume transactionnel — preuve chiffrée",
            "KGR verts — preuve liste / ratio",
            "SERP battable — preuve top 3",
        ],
    ),
    _step(
        "gaston.verdict",
        "Verdict Gaston",
        [
            "Recommandation SEO structurée pour Nicolas",
        ],
    ),
]


RED_FLAG_DEFS: list[dict[str, str]] = [
    {"key": "copyright", "label": "Marques déposées / copyright problématique ?"},
    {"key": "saisonnalite", "label": "Saisonnalité extrême (ex. volume uniquement Noël) ?"},
    {"key": "diversite_produit", "label": "Diversité produit — au moins 3 types POD ?"},
    {"key": "scalabilite", "label": "Scalabilité — 20+ designs différents possibles ?"},
    {"key": "trends_declin", "label": "Déclin Google Trends sur 5 ans ?"},
    {"key": "concurrent_pod", "label": "Concurrent POD dominant (ex. Shopify FR leader) ?"},
    {"key": "faux_volume", "label": "Faux volume — keywords vraiment transactionnels ?"},
]


SCORE_BUSINESS_KEYS: list[str] = [
    "passion",
    "communaute",
    "depenses",
    "repetabilite",
    "fit_visuel",
    "concurrence_pod",
    "international",
]

SCORE_SEO_KEYS: list[str] = [
    "volume_trans",
    "kgr_verts",
    "serp_battable",
]


def checklist_item_keys(steps: list[dict[str, Any]]) -> list[str]:
    keys: list[str] = []
    for st in steps:
        for it in st.get("items", []):
            keys.append(it["key"])
    return keys


def all_catalog_item_keys() -> list[str]:
    return checklist_item_keys(MARLENE_STEPS) + checklist_item_keys(GASTON_STEPS)


def default_state_payload() -> dict[str, Any]:
    """Initial JSON document for `niche_process_state.payload`."""
    return {
        "items_checked": {},
        "handoff": {"identity_keywords": ""},
        "scores_business": {k: None for k in SCORE_BUSINESS_KEYS},
        "scores_seo": {k: None for k in SCORE_SEO_KEYS},
        "red_flags": {d["key"]: False for d in RED_FLAG_DEFS},
        "notes": {
            "marlene_synthese": "",
            "gaston_verdict": "",
            "nicolas_decision": "",
        },
    }


def catalog_payload() -> dict[str, Any]:
    return {
        "pipeline": PIPELINE,
        "marlene": {"agent_key": "marlene", "steps": MARLENE_STEPS},
        "gaston": {"agent_key": "gaston", "steps": GASTON_STEPS},
        "red_flags": RED_FLAG_DEFS,
        "score_keys": {
            "business": SCORE_BUSINESS_KEYS,
            "seo": SCORE_SEO_KEYS,
        },
    }
