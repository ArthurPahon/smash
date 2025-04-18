DELIMITER //

-- Fonction pour calculer les points d'un joueur dans un tournoi
CREATE FUNCTION calculate_player_points(
    p_user_id INT,
    p_tournament_id INT
) RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_points INT;

    SELECT COALESCE(SUM(
        CASE
            WHEN m.winner_id = p_user_id THEN 3
            WHEN m.loser_id = p_user_id THEN 0
            ELSE 1
        END
    ), 0)
    INTO v_points
    FROM matches m
    WHERE m.tournament_id = p_tournament_id
    AND (m.player1_id = p_user_id OR m.player2_id = p_user_id)
    AND m.status = 'completed';

    RETURN v_points;
END //

-- Fonction pour vérifier l'éligibilité d'un joueur à un tournoi
CREATE FUNCTION is_player_eligible(
    p_user_id INT,
    p_tournament_id INT
) RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE v_is_eligible BOOLEAN;
    DECLARE v_registration_deadline DATETIME;
    DECLARE v_current_participants INT;
    DECLARE v_max_participants INT;

    -- Vérifier si le tournoi existe et n'est pas plein
    SELECT
        registration_deadline,
        current_participants,
        max_participants
    INTO
        v_registration_deadline,
        v_current_participants,
        v_max_participants
    FROM tournaments
    WHERE id = p_tournament_id;

    -- Vérifier les conditions d'éligibilité
    SET v_is_eligible = (
        NOW() <= v_registration_deadline AND
        v_current_participants < v_max_participants AND
        NOT EXISTS (
            SELECT 1 FROM registrations
            WHERE user_id = p_user_id
            AND tournament_id = p_tournament_id
        )
    );

    RETURN v_is_eligible;
END //

-- Fonction pour générer les brackets d'un tournoi
CREATE PROCEDURE generate_tournament_brackets(
    IN p_tournament_id INT
)
BEGIN
    DECLARE v_player_count INT;
    DECLARE v_round_count INT;
    DECLARE v_current_round INT DEFAULT 1;
    DECLARE v_match_count INT;
    DECLARE v_player1_id INT;
    DECLARE v_player2_id INT;

    -- Obtenir le nombre de joueurs inscrits
    SELECT COUNT(*) INTO v_player_count
    FROM registrations
    WHERE tournament_id = p_tournament_id
    AND status = 'approved';

    -- Calculer le nombre de rounds nécessaires
    SET v_round_count = CEIL(LOG2(v_player_count));

    -- Créer les matchs du premier round
    SET v_match_count = POWER(2, v_round_count - 1);

    -- Insérer les matchs initiaux
    INSERT INTO matches (
        tournament_id,
        round,
        bracket_position,
        status
    )
    SELECT
        p_tournament_id,
        1,
        n,
        'pending'
    FROM (
        SELECT a.N + b.N * 10 + 1 as n
        FROM (SELECT 0 as N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
             (SELECT 0 as N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) b
        WHERE a.N + b.N * 10 < v_match_count
    ) numbers;
END //

-- Fonction pour valider un match
CREATE FUNCTION validate_match_result(
    p_match_id INT,
    p_winner_id INT,
    p_score VARCHAR(50)
) RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE v_is_valid BOOLEAN;
    DECLARE v_player1_id INT;
    DECLARE v_player2_id INT;

    -- Récupérer les joueurs du match
    SELECT player1_id, player2_id
    INTO v_player1_id, v_player2_id
    FROM matches
    WHERE id = p_match_id;

    -- Vérifier si le gagnant est l'un des joueurs du match
    SET v_is_valid = (
        p_winner_id IN (v_player1_id, v_player2_id) AND
        p_score IS NOT NULL AND
        p_score != ''
    );

    RETURN v_is_valid;
END //

-- Fonction pour obtenir le prochain match d'un joueur
CREATE FUNCTION get_next_match(
    p_user_id INT,
    p_tournament_id INT
) RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_next_match_id INT;

    SELECT m.id
    INTO v_next_match_id
    FROM matches m
    WHERE m.tournament_id = p_tournament_id
    AND (m.player1_id = p_user_id OR m.player2_id = p_user_id)
    AND m.status = 'pending'
    AND m.start_time > NOW()
    ORDER BY m.start_time ASC
    LIMIT 1;

    RETURN v_next_match_id;
END //

DELIMITER ;