# Empire Dashboard — Actions restantes pour mise en prod

> Généré par Yvon (carte blanche nuit) — 2026-04-26 23:00 UTC

## État actuel
- ✅ Docker stack up (9/9 containers healthy)
- ✅ DNS `empire-dash.nextly.ovh` → 51.178.52.121 créé
- ✅ `.env` configuré (passwords changés)
- ❌ Nginx vhost non configuré → pas d'accès public
- ❌ SSL/HTTPS absent
- ❌ JWT_SECRET = dev secret (à changer pour prod)
- ❌ OPENCLAW_GATEWAY_URL vide → pas d'intégration OpenClaw

## Étape 1 — Nginx (depuis SSH ubuntu@51.178.52.121)

```bash
sudo tee /etc/nginx/sites-available/empire-dash.nextly.ovh > /dev/null << 'NGINX'
server {
    listen 80;
    server_name empire-dash.nextly.ovh;

    location /api/ {
        proxy_pass http://localhost:8008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://localhost:3080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/empire-dash.nextly.ovh /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## Étape 2 — SSL Certbot

```bash
sudo certbot --nginx -d empire-dash.nextly.ovh --non-interactive --agree-tos -m admin@nextly.ovh
```

## Étape 3 — Sécurisation JWT (optionnel mais recommandé)

Dans `/home/ubuntu/.openclaw/workspace/empire-dashboard/.env` :
```
EMPIRE_JWT_SECRET=<générer avec: openssl rand -hex 32>
```
Puis redémarrer : `cd /home/ubuntu/.openclaw/workspace/empire-dashboard && docker compose restart backend`

## Étape 4 — Connecter OpenClaw

Dans `.env` :
```
OPENCLAW_GATEWAY_URL=http://localhost:18789
OPENCLAW_GATEWAY_TOKEN=<token du gateway OpenClaw>
```

## Credentials dashboard
- URL : https://empire-dash.nextly.ovh
- Login : admin
- Pass : (celui utilisé pour générer le hash Argon2 le 26/04)

