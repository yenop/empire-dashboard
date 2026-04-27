# App Empire Dashboard

Petit guide de configuration et de test local. Pour le déploiement sur serveur, voir [DEPLOY.md](DEPLOY.md).

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) et [Docker Compose](https://docs.docker.com/compose/) (v2 : `docker compose …`)
- Python 3, uniquement si tu dois **générer le hash** du mot de passe admin (voir plus bas)

## 1. Fichier d’environnement

1. Copie le modèle vers un fichier local **non versionné** :

   ```bash
   cp .env.example .env
   ```

2. Ajuste les valeurs. Ne commite jamais `.env`.

## 2. Compte d’authentification (admin)

L’appli n’enregistre **pas** le mot de passe en clair. Elle stocke un **hash Argon2** dans `EMPIRE_PASSWORD_HASH` ; c’est le résultat du script `scripts/hash_password.py` appliqué au mot de passe que **tu** choisis.

- **`EMPIRE_AUTH_USERNAME`** : identifiant affiché à l’écran (souvent `admin`).
- **`EMPIRE_PASSWORD_HASH`** : une seule ligne générée par le script (ci-dessous).
- **`EMPIRE_JWT_SECRET`** : secret pour signer les jetons d’API — une chaîne aléatoire **longue** (32 caractères ou plus), **indépendante** du mot de passe de connexion.

### Générer le hash

Depuis le dossier `backend` (après installation des dépendances Python) :

```bash
cd backend
pip install -r requirements.txt
python ../scripts/hash_password.py 'votre_mot_de_passe_ici'
```

- Tu peux lancer le script **sans** argument : il te demande le mot de passe sans l’afficher.
- Colle la **ligne** imprimée (commençant par `$argon2id$…`) dans `.env` :

  ```env
  EMPIRE_PASSWORD_HASH='$argon2id$v=19$...'
  ```

  Les **guillemets simples** entoure la valeur sont recommandés : le hash contient des caractères `$` que Docker Compose interpréterait sinon.

### Ce que tu saisis pour te connecter

Sur l’écran de login, tu utilises `EMPIRE_AUTH_USERNAME` et le **même** mot de passe en clair que tu as passé à `hash_password.py`. Aucun mot de passe n’est prédéfini dans le dépôt : tant que le hash n’est pas correctement rempli, la connexion ne pourra pas fonctionner.

## 3. Autres mots de passe dans `.env`

Ce sont de **vrais** mots de passe que tu choisis, en clair, dans le fichier (usage interne base de données / MinIO) :

- `DB_PASSWORD` / `MARIADB_ROOT_PASSWORD` — base MariaDB
- `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` — stockage objet MinIO

Le fichier [docker-compose.yml](docker-compose.yml) relie ces variables aux services ; en local, les valeurs par défaut d’exemple du `.env.example` suffisent souvent, à condition d’être cohérentes d’un démarrage à l’autre (les volumes gardent les données existantes).

## 4. Lancer la stack en local (Docker)

À la racine de ce dépôt (`app-empire-dashboard`) :

```bash
docker compose up -d --build
```

Ports exposés par défaut :

| Service | URL hôte        |
|--------|------------------|
| Front  | http://localhost:3080 |
| API    | http://localhost:8008  |

Arrêt :

```bash
docker compose down
```

Vérification des conteneurs : `docker compose ps` ; logs : `docker compose logs -f` (ou le nom d’un service).

## 5. Lancer depuis Cursor / VS Code (ce repo parent)

Si tu ouvres le dossier parent `nico-empire` dans l’IDE, un [launch.json](https://code.visualstudio.com/docs/editor/debugging) et des tâches à la racine lancent le même `docker compose` (voir le dossier `.vscode` à la racine du monorepo).

## 6. OpenClaw (optionnel)

Pour l’intégration avec un gateway OpenClaw, définis `OPENCLAW_GATEWAY_URL` et `OPENCLAW_GATEWAY_TOKEN` dans `.env` (détails dans [DEPLOY.md](DEPLOY.md)).

---

En cas de doute, commence par : `.env` complet, hash Argon2 valide, puis `docker compose up -d --build` et accès à http://localhost:3080.



nextly.ovh (51.178.52.121)
│
├── nextly.ovh / www.nextly.ovh
│   └── ✅ Hub statique → /var/www/hub (fichier local dans nginx)
│
├── orchestrator.nextly.ovh
│   └── ✅ OTT Dashboard Angular → /var/www/dashboard (local)
│       └── /api/ → http://app:3000 (container Docker OTT)
│
├── app.nextly.ovh
│   └── ✅ même config qu'orchestrator (doublon OTT)
│
├── cryptobot.nextly.ovh
│   └── ✅ Frontend → /var/www/cryptobot (local)
│       └── /api/ → http://172.21.0.1:8092 (host gateway Docker)
│
├── communityradar.nextly.ovh
│   └── ✅ → http://51.178.52.121:8090 (IP publique VPS)
│
├── capcut-replicate.nextly.ovh
│   └── ⚠️ → http://51.178.52.121:8086 (cert archive, pas live)
│
├── appmagictracker.nextly.ovh
│   └── ⚠️ → http://appmagic-frontend:80 (nom container OTT ?)
│
└── empire-dash.nextly.ovh
    └── ❌ 502 → http://localhost:8008 + :3080


    # 1. Rebuild empire-dashboard
cd /home/ubuntu/.openclaw/workspace/empire-dashboard
docker compose down && docker compose up -d --build

# 2. Rebuild orchestrator_nginx
cd /home/ubuntu/.openclaw/workspace/orchestratorTrendTiktok
docker compose up -d --build nginx