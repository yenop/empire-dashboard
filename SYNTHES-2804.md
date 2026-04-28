Empire Dashboard — Fonctionnement, agents, OpenClaw et leviers pour la validation humaine
1. Rôle de l’application
Empire Dashboard (app-empire-dashboard) est une interface de pilotage : authentification JWT, données en MariaDB, fichiers optionnels en MinIO. Elle ne fait pas tourner les LLM elle-même : elle affiche l’état du « crew », des KPIs seedés, un workflow par phases, des modules ops (niches, contenu, SEO, demandes de clés API), le Wire (fil de messages / sorties agents), le Nerve center (fichiers de contrat / mémoire par agent), et une supervision des crons OpenClaw quand un volume de données OpenClaw est monté.
Les agents sont surtout des entités métier en base (agents, tâches, messages wire, etc.), alignées sur une fiction d’orchestration ; l’exécution réelle des jobs est supposée côté OpenClaw (crons) ou scripts externes.
2. Où vit la « logique workflow » aujourd’hui
2.1 Phases (métier)
Les 10 phases et les agents « actifs » par phase sont figés en Python dans workflow_phases.py (PHASES : index, titre, résumé, liste agents).
2.2 État persisté
Une seule ligne d’état (WorkflowStateModel, id fixe 1) contient au minimum :
phase (1 à 10)
last_validated_at (horodatage après une action humaine de validation)
Les endpoints GET/POST /api/workflow exposent la phase courante, la définition de phase, et lit_agent_ids (les ids agents de la phase en cours) pour l’UI (Timeline, Crew).
2.3 Action humaine actuelle sur le workflow
POST /api/workflow/advance : incrémente la phase (max 10), met à jour last_validated_at.
POST /api/workflow/reset : repasse à la phase 1.
Il n’y a pas de lien automatique avec l’activation / désactivation des crons OpenClaw dans ce code : la validation est uniquement un curseur de phase côté dashboard.
3. OpenClaw — comment le dashboard s’y branche
3.1 Données sur disque (OPENCLAW_DIR)
Le service openclaw_cron.py lit un répertoire (souvent monté en volume Docker, ex. /openclaw-data) :
cron/jobs.json — liste des jobs / crons
cron/runs/{jobId}.jsonl — une ligne JSON = un run (résumé, statut, usage tokens, etc.)
La table de correspondance AGENTS_MAP lie :
une clé métier (marlene, marcel_x, …)
un jobId UUID OpenClaw
un dashboard_agent_id (ex. marlene, marcel, edith, yvon)
Les jobs sans jobId (ex. Gaston dans la map actuelle) apparaissent comme « non configurés » côté agrégation OpenClaw.
3.2 Supervision API
GET /api/supervision/openclaw et GET /api/supervision/openclaw/agents lisent surtout jobs.json + runs sous openclaw_dir (variante « fichier » dans supervision.py).
Note : DEPLOY.md mentionne aussi un appel possible au gateway (OPENCLAW_GATEWAY_URL + /api/status). Les variables openclaw_gateway_* existent dans config.py, mais la route /api/supervision/openclaw telle qu’implémentée dans supervision.py s’appuie sur le filesystem ; le bandeau OpenClaw du dashboard (DashboardView.vue) attend des champs du type jobs_in_file / last_run_status_counts qui peuvent ne pas correspondre exactement au JSON renvoyé par cette route — à harmoniser si tu relies tout au gateway ou au fichier.
3.3 Wire (fil « équipe »)
GET /api/wire/conversations : si le volume OpenClaw est présent, les « conversations » sont dérivées des fichiers runs/{jobId}.jsonl (aperçu = dernier run). Sinon, fallback sur les conversations en base (WireConversationModel).
GET /api/wire/conversations/{id}/messages : si id est un UUID de job OpenClaw, les messages sont les lignes du jsonl (chacune traitée comme un message from_agent_id → dashboard), fusionnées avec d’éventuels messages DB rattachés au même openclaw_job_id.
POST /api/wire/messages : l’humain envoie un message vers un agent. En mode conversation OpenClaw, le message est stocké en DB et, si push_to_nerve est vrai, append_nerve_note ajoute un bloc daté dans le fichier / enregistrement HEARTBEAT de l’agent (wire_outbound.py) pour que les crons lisent le feedback dans la « couche nerveuse ».
3.4 Nerve center
Mode database (défaut) : contenu dans nerve_files.
Mode filesystem : lecture/écriture sous OPENCLAW_DIR selon OPENCLAW_NERVE_AGENT_PATHS / template (voir DEPLOY.md).
Les slugs sont définis dans workflow_phases.py (NERVE_SLUGS : identity, soul, memory, agents, heartbeat).
3.5 Crons affichés (Timeline)
GET /api/ops/crons renvoie une liste statique WORKFLOW_CRONS dans ops.py (documentation / alignement conceptuel avec OpenClaw), sans lecture live des UUID OpenClaw.
4. Interactions « agents » sans OpenClaw
POST /api/internal/tasks avec X-Empire-Internal-Key : création de tâches pour scripts / intégrations (ex. sortie d’un cron qui pousse une tâche dans le dashboard).
Ops : niches, pipeline contenu, SEO, demandes de clés API — données DB ; l’UI dashboard permet déjà une décision humaine partielle sur les demandes API (PATCH /api/ops/api-requests/{id}).
POST /api/wire/webhook : secret = empire_jwt_secret ; crée conversation du jour + message (utile pour pousser du contenu agent depuis l’extérieur sans passer par OpenClaw files).
5. Synthèse du flux actuel (schéma mental)
Empire Dashboard
OpenClaw hors dashboard
JWT
advance phase
Wire message + Nerve
FastAPI
MariaDB
Vue UI
Crons OpenClaw
jobs.json
runs jobId.jsonl
Fichiers Nerve workspace
Les agents « pensent » et s’exécutent hors de cette app ; le dashboard observe (runs, supervision), oriente (phase, nerve, wire → heartbeat), et enregistre des artefacts (tâches, wire, ops).
6. Pistes pour intégrer validation et visualisation humaine dans le workflow
Objectif typique : ne pas considérer une phase / une sortie comme « validée » tant qu’un humain n’a pas vu et approuvé, avec une UI claire sur ce qui attend une décision.
6.1 Niveau phase (Timeline)
Ajouter un état du type pending_review / human_approved_for_phase_N dans WorkflowStateModel (ou une table d’historique).
Remplacer ou compléter advance par : soumettre pour revue → approuver → alors seulement incrémenter la phase (ou notifier OpenClaw).
Option : ne pas faire confiance uniquement à advance : exposer GET des « livrables de phase » agrégés (derniers runs des jobs de la phase, niches, etc.).
6.2 Niveau run OpenClaw (jsonl)
Convention dans chaque ligne JSON : champs human_status, reviewed_at, ou file d’attente en DB indexée par (job_id, run_ts) pour ne pas réécrire les jsonl.
UI : file d’attente « Runs à valider » alimentée par webhook interne après chaque run, ou scan périodique du jsonl.
6.3 Niveau Wire / Nerve
Aujourd’hui le Wire sert surtout à lire les sorties et répondre (→ HEARTBEAT). On peut ajouter des réactions (approuvé / à retravailler) stockées en DB et réinjectées dans le prochain prompt (Nerve ou note dédiée).
6.4 Niveau données métier (ops)
Tables NicheCandidateModel, ContentPipelineModel, etc. : colonnes ou statuts awaiting_human, approved, avec vues dédiées dans AgentOpsPanel ou une nouvelle page « Inbox validation ».
6.5 Gouvernance OpenClaw réelle
Si tu veux bloquer l’automatisation tant que la phase dashboard n’est pas validée : soit désactiver les crons côté OpenClaw (CLI / API gateway) en fonction d’un signal (polling d’une route Empire, ou fichier indicateur sur le volume partagé), soit documenter un garde-fou dans les prompts agents (moins fiable seul).
6.6 Cohérence front / supervision
Aligner la réponse de GET /api/supervision/openclaw avec ce que consomme DashboardView.vue, ou implémenter l’appel gateway décrit dans DEPLOY.md et unifier les deux modes (fichier vs HTTP).
7. Fichiers clés à ouvrir pour modifier la logique
Sujet	Fichiers
Phases + nerve slugs	backend/app/workflow_phases.py
État workflow + advance	backend/app/routers/workflow.py, modèle WorkflowStateModel
Map OpenClaw ↔ agents	backend/app/services/openclaw_cron.py (AGENTS_MAP)
Wire + merge jsonl / DB	backend/app/routers/wire.py, openclaw_cron.py
Feedback humain → agents	backend/app/services/wire_outbound.py (HEARTBEAT)
Supervision jobs/runs	backend/app/routers/supervision.py
Crons affichés (statiques)	backend/app/routers/ops.py (WORKFLOW_CRONS)
Nerve read/write	backend/app/routers/nerve.py, services/nerve_files.py
Tâches externes	backend/app/routers/internal_tasks.py
UI Timeline / Crew / Dashboard	frontend/src/views/TimelineView.vue, CrewView.vue, DashboardView.vue
Ce document résume l’état du code au moment de l’analyse du dépôt. Pour que je génère un fichier (ex. docs/workflow-humain-openclaw.md) directement dans le projet, indique-le en mode Agent.