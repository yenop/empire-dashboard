# Déploiement VPS (App Empire Dashboard)

## Prérequis

- Docker et Docker Compose sur le serveur
- Un nom de domaine pointant vers le VPS (pour TLS)
- Ports **80** et **443** ouverts (reste du trafic en privé / firewall)

## Secrets

1. Copier [`.env.example`](.env.example) vers `.env` sur le serveur (permissions `chmod 600 .env`).
2. Générer un hash Argon2 pour le mot de passe admin (depuis un poste de confiance) :

   ```bash
   cd backend && pip install -r requirements.txt
   python ../scripts/hash_password.py 'votre_mot_de_passe_fort'
   ```

   Coller le résultat dans `EMPIRE_PASSWORD_HASH` (valeur entre quotes simples si le fichier `.env` est lu par Docker Compose, pour éviter l’interpolation des `$`).
3. Définir `EMPIRE_JWT_SECRET` (chaîne aléatoire d’au moins 32 caractères).
4. Choisir des mots de passe forts pour `DB_PASSWORD`, `MARIADB_ROOT_PASSWORD`, `MINIO_ROOT_PASSWORD`.

## Reverse proxy (Caddy ou Traefik)

Exposer uniquement le service **frontend** (port interne 80 du conteneur `frontend`) derrière HTTPS. Ne pas publier MariaDB (3306) ni MinIO (9000/9001) sur Internet ; les laisser sur le réseau Docker uniquement.

Par défaut, le compose mappe le front sur le port **3080** (`3080:80`) et l’API sur **8008** (`8008:8000`) pour limiter les collisions locales ; ajustez ces ports dans [`docker-compose.yml`](docker-compose.yml) selon votre VPS.

Exemple Caddy : `reverse_proxy localhost:3080`.

## OpenClaw

Sur la même machine ou un réseau privé, le gateway OpenClaw peut rester sur un port local (ex. 18789). Dans `.env` du dashboard :

- `OPENCLAW_GATEWAY_URL=http://host.docker.internal:18789` (Mac/Windows Docker Desktop) ou l’IP privée du host Linux.
- `OPENCLAW_GATEWAY_TOKEN` : le même jeton Bearer que celui configuré sur le gateway.

Le dashboard appelle `GET {OPENCLAW_GATEWAY_URL}/api/status` via la route agrégée `GET /api/supervision/openclaw` (authentification JWT requise).

### Nerve center ↔ fichiers OpenClaw sur disque

Par défaut, l’écran **Nerve** lit/écrit la table `nerve_files` (MariaDB). Pour utiliser les vrais `IDENTITY.md`, `SOUL.md`, `MEMORY.md`, etc. sous le répertoire monté en `OPENCLAW_DIR` :

1. Dans `.env` du serveur, définir **`OPENCLAW_HOST_PATH=/home/ubuntu/.openclaw`** (ou le chemin réel du répertoire OpenClaw sur l’hôte). Sans cette ligne, Compose utilise par défaut `./.docker-openclaw` dans le clone du dépôt, ce qui convient au dev local mais pas au VPS. Monter avec accès **lecture-écriture** (pas de `:ro`) pour l’enregistrement Nerve depuis l’UI.
2. Dans `.env` :
   - `NERVE_STORAGE=filesystem`
   - `OPENCLAW_NERVE_AGENT_PATHS` : JSON `{"<agent_id_dashboard>":"chemin/relatif/sous/openclaw"}`, par ex. `{"marlene":"workspace/marlene-cron"}`.
   - Optionnel : `OPENCLAW_NERVE_PATH_TEMPLATE=workspace/{agent_id}` pour les agents absents de la carte (chemins relatifs, sans `..`).

Sécurité : en mode `filesystem`, le conteneur **backend** peut modifier les fichiers sous ce volume ; ne montez que le périmètre OpenClaw nécessaire et gardez l’API derrière auth JWT comme aujourd’hui.

## Sauvegardes

Les données MariaDB et MinIO sont dans des **volumes Docker nommés** (`mariadb_data`, `minio_data`), préfixés par le nom du projet Compose (voir `docker volume ls`).

- **MariaDB** : `mysqldump` planifié (conteneur `mariadb` + réseau interne), ou sauvegarde du volume via un conteneur utilitaire (`docker run --rm -v <projet>_mariadb_data:/source ...`).
- **MinIO** : même principe pour le volume `<projet>_minio_data` si vous y stockez des fichiers non reproductibles.

## Mise à jour

```bash
git pull
docker compose build --no-cache
docker compose up -d
```

Vérifier les logs : `docker compose logs -f backend`.
