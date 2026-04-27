from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    AgentModel,
    AgentStatus,
    ApiKeyRequestModel,
    ApiKeyRequestStatus,
    AppModel,
    AppStatus,
    ContentPipelineModel,
    ContentStage,
    IntelModel,
    IntelStatus,
    IntelType,
    NerveFileModel,
    NicheCandidateModel,
    NicheStatus,
    SeoRankModel,
    TaskModel,
    TaskPriority,
    TaskStatus,
    WorkflowStateModel,
)


def seed_if_empty(db: Session) -> None:
    if db.scalars(select(AgentModel).limit(1)).first():
        return

    agents = [
        ("yvon", "Yvon", "Chief of Staff", "direction", "⚡", "#f59e0b", AgentStatus.active, 42, 50, "Stratège", 12, 120),
        ("marlene", "Marlène", "Head of Research", "recherche", "🔍", "#ec4899", AgentStatus.active, 38, 50, "Expert", 8, 95),
        ("gaston", "Gaston", "ASO Analyst", "recherche", "📊", "#f59e0b", AgentStatus.active, 30, 50, "Analyste", 15, 88),
        ("colette", "Colette", "Head of Production", "production", "🎨", "#8b5cf6", AgentStatus.active, 35, 50, "Lead", 9, 72),
        ("theodore", "Théodore", "Production Manager", "production", "🏭", "#10b981", AgentStatus.setup, 10, 50, "Junior", 3, 40),
        ("hugo", "Hugo", "Content", "production", "✍️", "#06b6d4", AgentStatus.setup, 5, 50, "Recrue", 1, 22),
        ("simone", "Simone", "Quality Assurance", "production", "🔬", "#f43f5e", AgentStatus.recruit, 0, 50, "Recrue", 0, 0),
        ("edith", "Édith", "Head of Intelligence", "intelligence", "🧠", "#3b82f6", AgentStatus.active, 40, 50, "Expert", 20, 200),
        ("germaine", "Germaine", "Finance", "intelligence", "💹", "#10b981", AgentStatus.recruit, 0, 50, "Recrue", 0, 0),
        ("raymond", "Raymond", "Head of Support", "support", "🛡️", "#f59e0b", AgentStatus.setup, 8, 50, "Junior", 2, 18),
        ("lucien", "Lucien", "Customer Service", "support", "🎧", "#06b6d4", AgentStatus.recruit, 0, 50, "Recrue", 0, 0),
        ("baptiste", "Baptiste", "Head of Expansion", "expansion", "🚀", "#f43f5e", AgentStatus.recruit, 0, 50, "Recrue", 0, 0),
        ("marcel", "Marcel", "Marketing", "expansion", "📱", "#8b5cf6", AgentStatus.recruit, 0, 50, "Recrue", 0, 0),
        ("fernand", "Fernand", "Distribution", "expansion", "📦", "#10b981", AgentStatus.recruit, 0, 50, "Recrue", 0, 0),
    ]
    for row in agents:
        (
            aid, name, role, pole, emoji, color, status, xp, max_xp, rank,
            tasks_c, msg_c,
        ) = row
        db.add(
            AgentModel(
                id=aid,
                name=name,
                role=role,
                pole=pole,
                emoji=emoji,
                color=color,
                status=status,
                xp=xp,
                max_xp=max_xp,
                rank_label=rank,
                tasks_count=tasks_c,
                messages_count=msg_c,
            )
        )

    apps = [
        (
            "receipt2go",
            "Receipt2Go",
            "Quittances immobilier",
            "🧾",
            "#3b82f6",
            Decimal("8.5"),
            1200,
            Decimal("2.1"),
            Decimal("1.2"),
            62,
            AppStatus.live,
        ),
        (
            "playertrackr",
            "PlayerTrackr",
            "Stats basket",
            "🏀",
            "#f59e0b",
            Decimal("12.0"),
            4500,
            Decimal("3.4"),
            Decimal("0.8"),
            71,
            AppStatus.live,
        ),
        (
            "soia",
            "Soia",
            "Programme bien-être",
            "🌿",
            "#10b981",
            Decimal("6.0"),
            800,
            Decimal("1.8"),
            Decimal("2.0"),
            55,
            AppStatus.beta,
        ),
        (
            "lumina",
            "Lumina",
            "Affirmations positives",
            "✨",
            "#8b5cf6",
            Decimal("3.5"),
            600,
            Decimal("1.2"),
            Decimal("3.0"),
            48,
            AppStatus.dev,
        ),
    ]
    for row in apps:
        (
            aid, name, niche, icon, color, mrr, dl, conv, churn, aso, st,
        ) = row
        db.add(
            AppModel(
                id=aid,
                name=name,
                niche=niche,
                icon=icon,
                color=color,
                mrr=mrr,
                downloads=dl,
                conversion_rate=conv,
                churn_rate=churn,
                aso_score=aso,
                status=st,
            )
        )

    intel_rows = [
        (
            "Ajouter mots-clés quittance + bail dans ASO",
            "App Store Connect",
            IntelType.seo,
            8,
            IntelStatus.implemented,
            "Gaston",
        ),
        (
            "Intégrer webhook RevenueCat pour MRR live",
            "RevenueCat docs",
            IntelType.api,
            7,
            IntelStatus.pending,
            "Yvon",
        ),
        (
            "Tester modèle économy sur tâches simples",
            "OpenClaw",
            IntelType.model,
            6,
            IntelStatus.borderline,
            "Édith",
        ),
    ]
    for title, source, itype, score, ist, _agent in intel_rows:
        db.add(
            IntelModel(
                title=title,
                source=source,
                intel_type=itype,
                score=score,
                status=ist,
            )
        )

    tasks = [
        ("Publier build 1.2 Receipt2Go", "colette", "receipt2go", TaskStatus.inprogress, TaskPriority.high),
        ("Audit ASO PlayerTrackr", "gaston", "playertrackr", TaskStatus.todo, TaskPriority.medium),
        ("Script export intel quotidien", "edith", None, TaskStatus.todo, TaskPriority.low),
        ("Page onboarding Soia", "hugo", "soia", TaskStatus.done, TaskPriority.medium),
    ]
    for title, ag, ap, st, pr in tasks:
        db.add(
            TaskModel(
                title=title,
                agent_id=ag,
                app_id=ap,
                status=st,
                priority=pr,
            )
        )

    db.commit()


def _nerve_md(agent_id: str, name: str, role: str, pole: str) -> dict[str, str]:
    return {
        "identity": (
            f"# {name}\n\n"
            f"- **ID** : `{agent_id}`\n"
            f"- **Rôle** : {role}\n"
            f"- **Pôle** : {pole}\n"
            f"- Équipe Podpire / Empire — niche apps & dropshipping pilotés par timeline.\n"
        ),
        "soul": (
            f"# Comment {name} travaille\n\n"
            "- Réponses courtes, livrables structurés.\n"
            "- Priorité au Wire pour les handoffs inter-agents.\n"
            "- MEMORY mis à jour après chaque tâche significative.\n"
        ),
        "memory": (
            f"# MEMORY — {name}\n\n"
            "## État projet\n"
            "- Phase courante suivie via dashboard Timeline.\n"
            "- Pas de blocage API signalé.\n\n"
            "## Dernières notes\n"
            "- Sync initiale depuis le dashboard Empire.\n"
        ),
        "agents": (
            "# AGENTS.md (vue locale)\n\n"
            "| Agent | Rôle |\n"
            "|-------|------|\n"
            "| Yvon | Chef d’orchestre |\n"
            "| Marlène | Niches |\n"
            "| Gaston | SEO / ASO |\n"
            "| Colette | Production |\n"
            "| Hugo | Contenu |\n"
            "| Simone | QA |\n"
            "| Édith | Intelligence |\n"
            "| + équipe support / expansion |\n\n"
            "Coordination : **Timeline** (phases) + **Wire** (messages).\n"
        ),
        "heartbeat": (
            f"# HEARTBEAT — {name}\n\n"
            "```\n"
            "status: OK\n"
            "last_tick: dashboard_seed\n"
            "next: suivre phase active + crons\n"
            "```\n"
        ),
    }


def seed_empire_extensions(db: Session) -> None:
    """Idempotent : complète workflow, nerve, wire, modules ops si absents."""
    if not db.scalars(select(AgentModel).limit(1)).first():
        return

    if db.get(WorkflowStateModel, 1) is None:
        db.add(WorkflowStateModel(id=1, phase=1))
        db.commit()

    n_nerve = db.scalar(select(func.count()).select_from(NerveFileModel)) or 0
    if n_nerve == 0:
        for ag in db.scalars(select(AgentModel)).all():
            for slug, content in _nerve_md(ag.id, ag.name, ag.role, ag.pole).items():
                db.add(NerveFileModel(agent_id=ag.id, slug=slug, content=content))
        db.commit()

    if not db.scalars(select(NicheCandidateModel).limit(1)).first():
        niches = [
            ("Gourde isotherme trail premium", "Accessoire sport outdoor, marge élevée, saison printemps.", 78, NicheStatus.in_review, "marlene+gaston"),
            ("Journal vocal mood + widget", "App bien-être, LTV via abonnement.", 71, NicheStatus.draft, "marlene"),
            ("POD humor bureau (safe)", "Print mugs / posters angle bureau SFW.", 64, NicheStatus.draft, "edith"),
            ("Mini-app quittance locataire", "Rappels + PDF conformes.", 82, NicheStatus.validated, "gaston+marlene"),
            ("Tracker perf basket amateur", "Social + stats locales.", 69, NicheStatus.draft, "marlene"),
        ]
        for title, summ, score, st, src in niches:
            db.add(
                NicheCandidateModel(
                    title=title,
                    summary=summ,
                    score_seo=score,
                    status=st,
                    source_agents=src,
                )
            )
        db.commit()

    if not db.scalars(select(ContentPipelineModel).limit(1)).first():
        rows = [
            ("Hero Soia — headline + preuve", "hugo", "soia", ContentStage.review, "Version 2 : CTA raccourci, badge confiance."),
            ("Fiches 5 SKU gourde trail", "hugo", None, ContentStage.draft, "Bullets + FAQ retours."),
            ("Post mortem ASO Receipt2Go", "gaston", "receipt2go", ContentStage.published, "Publié dans module SEO."),
        ]
        for title, aid, apid, st, ex in rows:
            db.add(
                ContentPipelineModel(
                    title=title, agent_id=aid, app_id=apid, stage=st, excerpt=ex
                )
            )
        db.commit()

    if not db.scalars(select(SeoRankModel).limit(1)).first():
        seo = [
            ("quittance loyer pdf", "receipt2go", 14),
            ("basket stats local", "playertrackr", 22),
            ("programme bien être 7 jours", "soia", 31),
            ("affirmations matin", "lumina", 18),
        ]
        for kw, app_id, pos in seo:
            db.add(SeoRankModel(keyword=kw, app_id=app_id, position=pos))
        db.commit()

    if not db.scalars(select(ApiKeyRequestModel).limit(1)).first():
        reqs = [
            ("gaston", "Google Trends API", "Scoring niches phase 1 — besoin quota hourly."),
            ("marlene", "Brave Search API", "Prospection SERP sans friction navigateur."),
            ("edith", "X API Pro", "Veille threads e-com 20h."),
        ]
        for aid, svc, reason in reqs:
            db.add(
                ApiKeyRequestModel(
                    agent_id=aid,
                    service_name=svc,
                    reason=reason,
                    status=ApiKeyRequestStatus.pending,
                )
            )
        db.commit()
