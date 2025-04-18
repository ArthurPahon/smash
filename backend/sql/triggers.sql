DELIMITER //

-- Trigger pour mettre à jour le nombre de participants lors d'une inscription
CREATE TRIGGER after_registration_insert
AFTER INSERT ON registrations
FOR EACH ROW
BEGIN
    UPDATE tournaments
    SET current_participants = current_participants + 1
    WHERE id = NEW.tournament_id;
END //

-- Trigger pour mettre à jour le nombre de participants lors d'une désinscription
CREATE TRIGGER after_registration_delete
AFTER DELETE ON registrations
FOR EACH ROW
BEGIN
    UPDATE tournaments
    SET current_participants = current_participants - 1
    WHERE id = OLD.tournament_id;
END //

-- Trigger pour vérifier les dates des tournois
CREATE TRIGGER before_tournament_insert
BEFORE INSERT ON tournaments
FOR EACH ROW
BEGIN
    IF NEW.start_date >= NEW.end_date THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La date de début doit être antérieure à la date de fin';
    END IF;

    IF NEW.registration_deadline >= NEW.start_date THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La date limite d''inscription doit être antérieure à la date de début';
    END IF;
END //

-- Trigger pour mettre à jour les classements après un match
CREATE TRIGGER after_match_update
AFTER UPDATE ON matches
FOR EACH ROW
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        -- Mise à jour du classement du gagnant
        INSERT INTO rankings (user_id, tournament_id, points, matches_played, matches_won, matches_lost)
        VALUES (NEW.winner_id, NEW.tournament_id, 3, 1, 1, 0)
        ON DUPLICATE KEY UPDATE
            points = points + 3,
            matches_played = matches_played + 1,
            matches_won = matches_won + 1;

        -- Mise à jour du classement du perdant
        INSERT INTO rankings (user_id, tournament_id, points, matches_played, matches_won, matches_lost)
        VALUES (NEW.loser_id, NEW.tournament_id, 0, 1, 0, 1)
        ON DUPLICATE KEY UPDATE
            matches_played = matches_played + 1,
            matches_lost = matches_lost + 1;
    END IF;
END //

-- Trigger pour vérifier la validité des inscriptions
CREATE TRIGGER before_registration_insert
BEFORE INSERT ON registrations
FOR EACH ROW
BEGIN
    DECLARE v_current_participants INT;
    DECLARE v_max_participants INT;
    DECLARE v_registration_deadline DATETIME;

    -- Vérifier si le tournoi est plein
    SELECT current_participants, max_participants, registration_deadline
    INTO v_current_participants, v_max_participants, v_registration_deadline
    FROM tournaments
    WHERE id = NEW.tournament_id;

    IF v_current_participants >= v_max_participants THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Le tournoi est déjà complet';
    END IF;

    IF NOW() > v_registration_deadline THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La date limite d''inscription est dépassée';
    END IF;

    -- Vérifier si l'utilisateur n'est pas déjà inscrit
    IF EXISTS (
        SELECT 1 FROM registrations
        WHERE user_id = NEW.user_id
        AND tournament_id = NEW.tournament_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'L''utilisateur est déjà inscrit à ce tournoi';
    END IF;
END //

DELIMITER ;