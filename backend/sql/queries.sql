-- Procédure pour créer un nouveau tournoi
DELIMITER //
CREATE PROCEDURE create_tournament(
    IN p_name VARCHAR(100),
    IN p_description TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME,
    IN p_registration_deadline DATETIME,
    IN p_max_participants INT,
    IN p_format VARCHAR(20),
    IN p_rules TEXT,
    IN p_prize_pool TEXT,
    IN p_organizer_id INT
)
BEGIN
    INSERT INTO tournaments (
        name, description, start_date, end_date, registration_deadline,
        max_participants, format, rules, prize_pool, organizer_id
    ) VALUES (
        p_name, p_description, p_start_date, p_end_date, p_registration_deadline,
        p_max_participants, p_format, p_rules, p_prize_pool, p_organizer_id
    );
END //
DELIMITER ;

-- Procédure pour inscrire un joueur à un tournoi
DELIMITER //
CREATE PROCEDURE register_player(
    IN p_user_id INT,
    IN p_tournament_id INT,
    IN p_seed INT
)
BEGIN
    DECLARE current_participants INT;

    -- Vérifier si le tournoi est plein
    SELECT current_participants INTO current_participants
    FROM tournaments
    WHERE id = p_tournament_id;

    IF current_participants < (
        SELECT max_participants
        FROM tournaments
        WHERE id = p_tournament_id
    ) THEN
        -- Ajouter l'inscription
        INSERT INTO registrations (user_id, tournament_id, seed)
        VALUES (p_user_id, p_tournament_id, p_seed);

        -- Mettre à jour le nombre de participants
        UPDATE tournaments
        SET current_participants = current_participants + 1
        WHERE id = p_tournament_id;
    END IF;
END //
DELIMITER ;

-- Procédure pour mettre à jour le résultat d'un match
DELIMITER //
CREATE PROCEDURE update_match_result(
    IN p_match_id INT,
    IN p_winner_id INT,
    IN p_score VARCHAR(50)
)
BEGIN
    DECLARE v_player1_id, v_player2_id INT;

    -- Récupérer les joueurs du match
    SELECT player1_id, player2_id INTO v_player1_id, v_player2_id
    FROM matches
    WHERE id = p_match_id;

    -- Mettre à jour le match
    UPDATE matches
    SET winner_id = p_winner_id,
        loser_id = CASE
            WHEN p_winner_id = player1_id THEN player2_id
            ELSE player1_id
        END,
        score = p_score,
        status = 'completed',
        end_time = CURRENT_TIMESTAMP
    WHERE id = p_match_id;

    -- Mettre à jour les statistiques des joueurs
    UPDATE rankings
    SET matches_played = matches_played + 1,
        matches_won = matches_won + 1
    WHERE user_id = p_winner_id
    AND tournament_id = (SELECT tournament_id FROM matches WHERE id = p_match_id);

    UPDATE rankings
    SET matches_played = matches_played + 1,
        matches_lost = matches_lost + 1
    WHERE user_id = CASE
        WHEN p_winner_id = v_player1_id THEN v_player2_id
        ELSE v_player1_id
    END
    AND tournament_id = (SELECT tournament_id FROM matches WHERE id = p_match_id);
END //
DELIMITER ;

-- Fonction pour calculer le classement d'un tournoi
DELIMITER //
CREATE FUNCTION calculate_tournament_ranking(p_tournament_id INT)
RETURNS TABLE (
    user_id INT,
    rank INT,
    points INT,
    matches_played INT,
    matches_won INT,
    matches_lost INT
)
BEGIN
    RETURN (
        SELECT
            r.user_id,
            RANK() OVER (ORDER BY r.points DESC, r.matches_won DESC) as rank,
            r.points,
            r.matches_played,
            r.matches_won,
            r.matches_lost
        FROM rankings r
        WHERE r.tournament_id = p_tournament_id
        ORDER BY r.points DESC, r.matches_won DESC
    );
END //
DELIMITER ;

-- Requête pour obtenir les détails d'un tournoi avec statistiques
SELECT
    t.*,
    COUNT(DISTINCT r.user_id) as total_registrations,
    COUNT(DISTINCT m.id) as total_matches,
    COUNT(DISTINCT CASE WHEN m.status = 'completed' THEN m.id END) as completed_matches,
    u.name as organizer_name
FROM tournaments t
LEFT JOIN registrations r ON t.id = r.tournament_id
LEFT JOIN matches m ON t.id = m.tournament_id
LEFT JOIN users u ON t.organizer_id = u.id
WHERE t.id = ?
GROUP BY t.id;

-- Requête pour obtenir le classement global des joueurs
SELECT
    u.id,
    u.name,
    COUNT(DISTINCT m.id) as total_matches,
    COUNT(DISTINCT CASE WHEN m.winner_id = u.id THEN m.id END) as matches_won,
    COUNT(DISTINCT CASE WHEN m.loser_id = u.id THEN m.id END) as matches_lost,
    COUNT(DISTINCT t.id) as tournaments_played,
    COUNT(DISTINCT CASE WHEN m.winner_id = u.id AND t.status = 'completed' THEN t.id END) as tournaments_won
FROM users u
LEFT JOIN matches m ON u.id IN (m.player1_id, m.player2_id)
LEFT JOIN tournaments t ON m.tournament_id = t.id
GROUP BY u.id, u.name
ORDER BY matches_won DESC, total_matches DESC;

-- Requête pour obtenir les matchs à venir d'un joueur
SELECT
    m.*,
    t.name as tournament_name,
    p1.name as player1_name,
    p2.name as player2_name,
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
WHERE (m.player1_id = ? OR m.player2_id = ?)
AND m.status = 'pending'
AND m.start_time > CURRENT_TIMESTAMP
ORDER BY m.start_time ASC;