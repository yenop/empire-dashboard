# Empire Dashboard — Synthèse application, OpenClaw et flux de création

Document de synthèse : rôle de l’application, branchements OpenClaw, lacunes actuelles, et pistes pour amorcer un flux de création. Pour le détail technique du workflow humain, voir [workflow-humain-openclaw.md](workflow-humain-openclaw.md).

---

## 1. Rôle global de l’application

**Empire Dashboard** est une **console de pilotage** (frontend Vue, API FastAPI, MariaDB, MinIO optionnel pour les fichiers).

- Elle **n’exécute pas** les modèles de langage ni les jobs planifiés : elle **affiche** et **persiste** l’état opérationnel.
- **Authentification** JWT ; données métier en base.
- **Fonctionnalités principales** :
  - État du **crew** et KPI (souvent issus du seed).
  - **Workflow en 10 phases** (définition métier + curseur de phase persisté).
  - **Modules ops** : niches, pipeline contenu, SEO, demandes de clés API.
  - **Wire** : fil de messages / sorties agents (DB et/ou fichiers OpenClaw).
  - **Nerve center** : fichiers de contrat / mémoire par agent (`identity`, `soul`, `memory`, `agents`, `heartbeat`).
  - **Supervision OpenClaw** lorsque les données cron OpenClaw sont montées sur disque.

Les **agents** sont surtout des **entités métier en base** (`agents`, tâches, conversations wire, etc.), alignées sur une logique d’orchestration. L’**exécution réelle** des automatisations est supposée **hors application** : OpenClaw (crons), scripts, ou autres intégrations.

---

## 2. Connecteurs avec OpenClaw

| Mécanisme | Rôle |
|-----------|------|
| **`OPENCLAW_DIR`** | Répertoire partagé (souvent volume Docker, ex. `/openclaw-data`). Contient notamment `cron/jobs.json` et `cron/runs/{jobId}.jsonl`. |
| **`AGENTS_MAP`** (`backend/app/services/openclaw_cron.py`) | Correspondance **clé métier** → **`jobId`** (UUID OpenClaw) → **`dashboard_agent_id`**. Sans `jobId` valide ou sans mapping cohérent, l’agrégation et le Wire peuvent être incomplets. |
| **Supervision API** | `GET /api/supervision/openclaw` et `GET /api/supervision/openclaw/agents` lisent **jobs.json** et les **runs** sous `OPENCLAW_DIR` (mode **fichiers**). |
| **Wire** | Si le volume est présent, les « conversations » peuvent être dérivées des **runs** ; les messages humains peuvent aller en DB et, avec **`push_to_nerve`**, dans le **HEARTBEAT** pour lecture par les crons (`wire_outbound.py`). |
| **Nerve** | Mode **base de données** (défaut) ou **fichiers** sous `OPENCLAW_DIR` selon la configuration (voir `DEPLOY.md`). |
| **`OPENCLAW_GATEWAY_URL` / `OPENCLAW_GATEWAY_TOKEN`** | Variables prévues dans la config et documentées pour un **gateway** HTTP (ex. `GET …/api/status`). L’implémentation actuelle de **`/api/supervision/openclaw`** s’appuie sur le **filesystem**, pas sur ce gateway. Le bandeau OpenClaw du dashboard peut attendre des champs à **harmoniser** avec la réponse réelle. |

En résumé : le **connecteur opérationnel principal** aujourd’hui est le **dossier partagé** (jobs + runs + nerve fichiers). Le **gateway** est une extension documentée, pas le cœur du code de supervision actuel.

---

## 3. Ce qui n’est pas (ou pas complètement) implémenté

- **Lien automatique phase ↔ crons OpenClaw** : `POST /api/workflow/advance` met à jour uniquement le curseur de phase en base ; **aucune** activation ou désactivation des crons OpenClaw depuis le dashboard.
- **Gateway HTTP** : variables présentes ; les routes de supervision utilisent les **fichiers**. L’alignement avec `DEPLOY.md` (appel agrégé au gateway) peut nécessiter du code supplémentaire ou une mise à jour de la doc si l’on reste 100 % fichier.
- **Crons sur la Timeline** : `GET /api/ops/crons` renvoie une liste **statique** (`WORKFLOW_CRONS`), pas une lecture live des UUID depuis `jobs.json`.
- **Validation métier structurée** : pas de file d’attente type `pending_review` par phase, pas de statut humain standard sur chaque ligne de run jsonl (pistes décrites dans `workflow-humain-openclaw.md`).
- **Déploiement** (cf. `SETUP-REMAINING.md` à l’époque de sa rédaction) : vhost nginx, SSL, secret JWT de production, **`OPENCLAW_GATEWAY_URL` vide** sur le VPS = pas d’intégration gateway côté serveur.
- **Carte agents** : vérifier que chaque entrée utile a un **`dashboard_agent_id`** cohérent (ex. agents « production » comme Colette) pour le Wire et le crew.

---

## 4. Programmer un début de flux de création

L’application ne fournit pas un moteur de « workflow BPM » bout-en-bout ; on **compose** des briques existantes.

### 4.1 Cadrage métier

1. Positionner la **phase** du workflow (`GET` / `POST` `/api/workflow`, éventuellement `reset` puis progression) pour que l’UI et `lit_agent_ids` reflètent les agents de la phase courante (définition dans `backend/app/workflow_phases.py`).

### 4.2 Déclencher ou nourrir le travail des agents

Choisir un ou plusieurs canaux :

| Canal | Usage typique |
|-------|----------------|
| **Wire** (`POST /api/wire/messages`) | Message humain vers un agent ; avec **`push_to_nerve`**, ajout d’une note datée dans **HEARTBEAT** pour que les **crons OpenClaw** lisent la consigne ou le feedback. |
| **`POST /api/internal/tasks`** | Création de tâches depuis un script ou un job externe (header `X-Empire-Internal-Key` si `EMPIRE_INTERNAL_API_KEY` est défini). |
| **`POST /api/wire/webhook`** | Push d’un message depuis l’extérieur (authentification par secret configuré) sans passer par l’UI. |

### 4.3 Côté OpenClaw

Les crons utilisent le **workspace** et les **fichiers** : un « début de flux » efficace combine **Nerve / HEARTBEAT à jour** + éventuellement **tâches** visibles dans le dashboard pour le suivi humain. Les UUID des jobs sont ceux référencés dans `AGENTS_MAP` et dans la configuration OpenClaw.

### 4.4 Gouvernance (bloquer / débloquer l’automatisation)

Tant qu’il n’y a pas d’appel programmatique au gateway ou à la CLI OpenClaw depuis le backend :

- **Manuel** : activer / désactiver les crons via la CLI OpenClaw (ex. `openclaw cron enable|disable <uuid>`).
- **Fichier drapeau** : convention sur le volume partagé lue par les prompts ou scripts avant d’exécuter une étape coûteuse.
- **Évolution** : polling d’une route Empire ou fichier indicateur + automation côté OpenClaw pour refléter une validation humaine dans le dashboard.

### 4.5 Évolution vers un flux « soumission → revue → approbation »

Pistes détaillées (modèle d’état workflow, table des runs à valider, statuts ops, alignement front / supervision) : **[workflow-humain-openclaw.md](workflow-humain-openclaw.md)** sections 6 et 7.

---

## 5. Fichiers et références utiles

| Sujet | Fichiers |
|--------|----------|
| Phases + slugs Nerve | `backend/app/workflow_phases.py` |
| État workflow | `backend/app/routers/workflow.py`, `WorkflowStateModel` dans `backend/app/models.py` |
| Map OpenClaw ↔ agents | `backend/app/services/openclaw_cron.py` |
| Wire | `backend/app/routers/wire.py` |
| Feedback → HEARTBEAT | `backend/app/services/wire_outbound.py` |
| Supervision | `backend/app/routers/supervision.py` |
| Crons affichés (statique) | `backend/app/routers/ops.py` |
| Tâches machine | `backend/app/routers/internal_tasks.py` |
| Config | `backend/app/config.py` |
| Setup local | [README.md](../README.md) |
| Déploiement / gateway / Nerve FS | [DEPLOY.md](../DEPLOY.md) |

---

*Document généré pour faciliter l’onboarding et la planification produit ; à tenir à jour si la supervision passe au mode gateway HTTP ou si le modèle de validation workflow évolue.*
