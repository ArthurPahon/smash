-- Vue pour les statistiques des tournois
CREATE OR REPLACE VIEW tournament_statistics AS
SELECT
    t.id,
    t.name,
    t.status,
    t.start_date,
    t.end_date,
    t.current_participants,
    t.max_participants,
    COUNT(DISTINCT m.id) as total_matches,
    COUNT(DISTINCT CASE WHEN m.status = 'completed' THEN m.id END) as completed_matches,
    COUNT(DISTINCT CASE WHEN m.status = 'pending' THEN m.id END) as pending_matches,
    COUNT(DISTINCT r.user_id) as total_registrations,
    u.name as organizer_name
FROM tournaments t
LEFT JOIN matches m ON t.id = m.tournament_id
LEFT JOIN registrations r ON t.id = r.tournament_id
LEFT JOIN users u ON t.organizer_id = u.id
GROUP BY t.id, t.name, t.status, t.start_date, t.end_date, t.current_participants, t.max_participants, u.name;

-- Vue pour les classements des joueurs
CREATE OR REPLACE VIEW player_rankings AS
SELECT
    u.id,
    u.name,
    u.country,
    u.state,
    COUNT(DISTINCT m.id) as total_matches,
    COUNT(DISTINCT CASE WHEN m.winner_id = u.id THEN m.id END) as matches_won,
    COUNT(DISTINCT CASE WHEN m.loser_id = u.id THEN m.id END) as matches_lost,
    COUNT(DISTINCT t.id) as tournaments_played,
    COUNT(DISTINCT CASE WHEN m.winner_id = u.id AND t.status = 'completed' THEN t.id END) as tournaments_won,
    RANK() OVER (ORDER BY COUNT(DISTINCT CASE WHEN m.winner_id = u.id THEN m.id END) DESC) as global_rank
FROM users u
LEFT JOIN matches m ON u.id IN (m.player1_id, m.player2_id)
LEFT JOIN tournaments t ON m.tournament_id = t.id
GROUP BY u.id, u.name, u.country, u.state;

-- Vue pour les matchs en cours
CREATE OR REPLACE VIEW active_matches AS
SELECT
    m.id,
    m.tournament_id,
    t.name as tournament_name,
    m.player1_id,
    p1.name as player1_name,
    m.player2_id,
    p2.name as player2_name,
    m.status,
    m.start_time,
    m.end_time,
    c1.name as player1_character,
    c2.name as player2_character
FROM matches m
JOIN tournaments t ON m.tournament_id = t.id
JOIN users p1 ON m.player1_id = p1.id
JOIN users p2 ON m.player2_id = p2.id
LEFT JOIN match_characters mc1 ON m.id = mc1.match_id AND m.player1_id = mc1.player_id
LEFT JOIN match_characters mc2 ON m.id = mc2.match_id AND m.player2_id = mc2.player_id
LEFT JOIN characters c1 ON mc1.character_id = c1.id
LEFT JOIN characters c2 ON mc2.character_id = c2.id
WHERE m.status IN ('pending', 'in_progress')
AND m.start_time <= NOW()
AND (m.end_time IS NULL OR m.end_time > NOW());

-- Vue pour les inscriptions en attente
CREATE OR REPLACE VIEW pending_registrations AS
SELECT
    r.id,
    r.user_id,
    u.name as user_name,
    r.tournament_id,
    t.name as tournament_name,
    r.registration_date,
    r.status,
    r.seed,
    t.registration_deadline,
    t.max_participants,
    t.current_participants
FROM registrations r
JOIN users u ON r.user_id = u.id
JOIN tournaments t ON r.tournament_id = t.id
WHERE r.status = 'pending'
AND t.registration_deadline > NOW()
AND t.current_participants < t.max_participants;

-- Vues pour simplifier les requêtes complexes

-- Vue des détails des tournois avec statistiques
CREATE OR REPLACE VIEW tournament_details AS
SELECT
    t.*,
    u.name AS organizer_name,
    COUNT(DISTINCT r.id) AS total_registrations,
    COUNT(DISTINCT m.id) AS total_matches,
    COUNT(DISTINCT CASE WHEN m.status = 'completed' THEN m.id END) AS completed_matches,
    COUNT(DISTINCT CASE WHEN m.status = 'pending' THEN m.id END) AS pending_matches
FROM tournaments t
LEFT JOIN users u ON t.organizer_id = u.id
LEFT JOIN registrations r ON t.id = r.tournament_id
LEFT JOIN matches m ON t.id = m.tournament_id
GROUP BY t.id, t.name, t.description, t.start_date, t.end_date,
         t.registration_deadline, t.max_participants, t.format, t.rules,
         t.prize_pool, t.status, t.organizer_id, u.name;

-- Vue des statistiques des joueurs
CREATE OR REPLACE VIEW player_statistics AS
SELECT
    u.id AS user_id,
    u.name AS user_name,
    COUNT(DISTINCT r.tournament_id) AS tournaments_played,
    COUNT(DISTINCT CASE WHEN m.winner_id = u.id THEN m.id END) AS matches_won,
    COUNT(DISTINCT CASE WHEN m.loser_id = u.id THEN m.id END) AS matches_lost,
    COUNT(DISTINCT CASE WHEN m.winner_id IS NULL AND (m.player1_id = u.id OR m.player2_id = u.id) THEN m.id END) AS matches_pending,
    COUNT(DISTINCT CASE WHEN r.character_id IS NOT NULL THEN r.character_id END) AS characters_used
FROM users u
LEFT JOIN registrations r ON u.id = r.user_id
LEFT JOIN matches m ON (m.player1_id = u.id OR m.player2_id = u.id)
GROUP BY u.id, u.name;

-- Vue des classements des tournois
CREATE OR REPLACE VIEW tournament_rankings AS
SELECT
    r.tournament_id,
    t.name AS tournament_name,
    r.user_id,
    u.name AS user_name,
    COALESCE(SUM(
        CASE
            WHEN m.winner_id = r.user_id THEN 3
            WHEN m.loser_id = r.user_id THEN 0
            ELSE 1
        END
    ), 0) AS points,
    ROW_NUMBER() OVER (
        PARTITION BY r.tournament_id
        ORDER BY COALESCE(SUM(
            CASE
                WHEN m.winner_id = r.user_id THEN 3
                WHEN m.loser_id = r.user_id THEN 0
                ELSE 1
            END
        ), 0) DESC
    ) AS position
FROM registrations r
JOIN tournaments t ON r.tournament_id = t.id
JOIN users u ON r.user_id = u.id
LEFT JOIN matches m ON (
    m.tournament_id = r.tournament_id AND
    (m.player1_id = r.user_id OR m.player2_id = r.user_id)
)
GROUP BY r.tournament_id, t.name, r.user_id, u.name;

-- Vue des statistiques des personnages
CREATE OR REPLACE VIEW character_statistics AS
SELECT
    c.id AS character_id,
    c.name AS character_name,
    c.tier,
    COUNT(DISTINCT r.id) AS total_uses,
    COUNT(DISTINCT r.tournament_id) AS tournaments_used,
    COUNT(DISTINCT r.user_id) AS unique_users,
    COUNT(DISTINCT CASE WHEN m.winner_id = r.user_id THEN m.id END) AS matches_won,
    COUNT(DISTINCT CASE WHEN m.loser_id = r.user_id THEN m.id END) AS matches_lost
FROM characters c
LEFT JOIN registrations r ON c.id = r.character_id
LEFT JOIN matches m ON (
    m.tournament_id = r.tournament_id AND
    (m.player1_id = r.user_id OR m.player2_id = r.user_id)
)
GROUP BY c.id, c.name, c.tier;

-- Vue des prochains matchs
CREATE OR REPLACE VIEW upcoming_matches AS
SELECT
    m.id AS match_id,
    m.tournament_id,
    t.name AS tournament_name,
    m.round,
    m.player1_id,
    u1.name AS player1_name,
    c1.name AS player1_character,
    m.player2_id,
    u2.name AS player2_name,
    c2.name AS player2_character,
    m.scheduled_time,
    m.status
FROM matches m
JOIN tournaments t ON m.tournament_id = t.id
JOIN users u1 ON m.player1_id = u1.id
LEFT JOIN users u2 ON m.player2_id = u2.id
LEFT JOIN registrations r1 ON m.tournament_id = r1.tournament_id AND m.player1_id = r1.user_id
LEFT JOIN registrations r2 ON m.tournament_id = r2.tournament_id AND m.player2_id = r2.user_id
LEFT JOIN characters c1 ON r1.character_id = c1.id
LEFT JOIN characters c2 ON r2.character_id = c2.id
WHERE m.status = 'pending'
ORDER BY m.scheduled_time ASC;

-- Vue des inscriptions aux tournois
CREATE OR REPLACE VIEW tournament_registrations AS
SELECT
    r.id AS registration_id,
    r.tournament_id,
    t.name AS tournament_name,
    r.user_id,
    u.name AS user_name,
    r.character_id,
    c.name AS character_name,
    r.registration_date,
    t.start_date,
    t.end_date,
    t.status AS tournament_status
FROM registrations r
JOIN tournaments t ON r.tournament_id = t.id
JOIN users u ON r.user_id = u.id
LEFT JOIN characters c ON r.character_id = c.id
ORDER BY r.registration_date DESC;