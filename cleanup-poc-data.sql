-- ============================================================
-- EMPIRE DASHBOARD — Nettoyage données POC
-- Garde : apps (structure réelle), agents (structure)
-- Vide : tout ce qui est généré par le POC
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Tables à vider complètement (données 100% POC)
DELETE FROM wire_messages;
DELETE FROM wire_conversations;
DELETE FROM tasks;
DELETE FROM intel;
DELETE FROM niche_candidates;
DELETE FROM content_pipeline;
DELETE FROM seo_ranks;
DELETE FROM api_key_requests;

-- 2. Reset workflow à phase 1
DELETE FROM workflow_state;
INSERT INTO workflow_state (id, phase) VALUES (1, 1);

-- 3. Reset nerve files MEMORY (garder IDENTITY, SOUL, AGENTS, HEARTBEAT)
UPDATE nerve_files SET content = CONCAT('# MEMORY — ', agent_id, '\n\n## État\n- Aucune donnée encore.\n')
WHERE slug = 'memory';

-- 4. Reset métriques apps (garder les apps mais remettre les stats à 0)
UPDATE apps SET
    mrr = 0.00,
    downloads = 0,
    conversion_rate = 0.00,
    churn_rate = 0.00,
    aso_score = 0;

-- Mettre à jour les statuts réels des apps
UPDATE apps SET status = 'dev'  WHERE id = 'lumina';
UPDATE apps SET status = 'dev'  WHERE id = 'soia';
UPDATE apps SET status = 'dev'  WHERE id = 'playertrackr';
UPDATE apps SET status = 'dev'  WHERE id = 'receipt2go';

-- 5. Reset agents XP / counts (garder la structure)
UPDATE agents SET xp = 0, tasks_count = 0, messages_count = 0, rank_label = 'Recrue';
-- Remettre Yvon actif
UPDATE agents SET status = 'active' WHERE id = 'yvon';

-- 6. Reset auto-increment des tables vidées
ALTER TABLE wire_messages AUTO_INCREMENT = 1;
ALTER TABLE wire_conversations AUTO_INCREMENT = 1;
ALTER TABLE tasks AUTO_INCREMENT = 1;
ALTER TABLE intel AUTO_INCREMENT = 1;
ALTER TABLE niche_candidates AUTO_INCREMENT = 1;
ALTER TABLE content_pipeline AUTO_INCREMENT = 1;
ALTER TABLE seo_ranks AUTO_INCREMENT = 1;
ALTER TABLE api_key_requests AUTO_INCREMENT = 1;

SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Nettoyage POC terminé ✓' AS result;