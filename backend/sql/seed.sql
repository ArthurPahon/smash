-- Insertion des rôles de base
INSERT INTO roles (name, description) VALUES
('admin', 'Administrateur du système avec tous les droits'),
('organizer', 'Organisateur de tournois'),
('player', 'Joueur participant aux tournois');

-- Création d'un utilisateur administrateur par défaut
-- Le mot de passe est 'admin123' (à changer en production)
INSERT INTO users (name, email, password, country, state, is_active) VALUES
('Administrateur', 'admin@smash.com', '$2a$10$rPQcHhQ8QZ9QZ9QZ9QZ9QOQZ9QZ9QZ9QZ9QZ9QZ9QZ9QZ9QZ9QZ9', 'Canada', 'Québec', TRUE);

-- Attribution du rôle admin à l'administrateur
INSERT INTO user_role (user_id, role_id)
SELECT u.id, r.id
FROM users u, roles r
WHERE u.email = 'admin@smash.com' AND r.name = 'admin';

-- Insertion des personnages de base de Super Smash Bros.
INSERT INTO characters (name, game, image_url) VALUES
('Mario', 'Super Smash Bros.', '/images/characters/mario.png'),
('Link', 'Super Smash Bros.', '/images/characters/link.png'),
('Samus', 'Super Smash Bros.', '/images/characters/samus.png'),
('Donkey Kong', 'Super Smash Bros.', '/images/characters/donkey_kong.png'),
('Yoshi', 'Super Smash Bros.', '/images/characters/yoshi.png'),
('Kirby', 'Super Smash Bros.', '/images/characters/kirby.png'),
('Fox', 'Super Smash Bros.', '/images/characters/fox.png'),
('Pikachu', 'Super Smash Bros.', '/images/characters/pikachu.png'),
('Luigi', 'Super Smash Bros.', '/images/characters/luigi.png'),
('Ness', 'Super Smash Bros.', '/images/characters/ness.png'),
('Captain Falcon', 'Super Smash Bros.', '/images/characters/captain_falcon.png'),
('Jigglypuff', 'Super Smash Bros.', '/images/characters/jigglypuff.png');

-- Création d'un tournoi exemple
INSERT INTO tournaments (
    name,
    description,
    start_date,
    end_date,
    registration_deadline,
    max_participants,
    format,
    rules,
    prize_pool,
    organizer_id
) VALUES (
    'Tournoi d''été 2023',
    'Grand tournoi estival de Super Smash Bros.',
    DATE_ADD(NOW(), INTERVAL 7 DAY),
    DATE_ADD(NOW(), INTERVAL 14 DAY),
    DATE_ADD(NOW(), INTERVAL 5 DAY),
    32,
    'double_elimination',
    'Règles standard de tournoi. Format en double élimination. Matchs en 3 stocks, 8 minutes.',
    '1er prix: 500$, 2ème prix: 250$, 3ème prix: 100$',
    (SELECT id FROM users WHERE email = 'admin@smash.com')
);

-- Insertion des utilisateurs
INSERT INTO users (name, email, password_hash, role) VALUES
('Admin', 'admin@smash.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vYBxLri', 'admin'),
('John Doe', 'john@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vYBxLri', 'player'),
('Jane Smith', 'jane@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vYBxLri', 'player'),
('Bob Wilson', 'bob@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vYBxLri', 'player'),
('Alice Brown', 'alice@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vYBxLri', 'player'),
('Charlie Davis', 'charlie@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vYBxLri', 'player'),
('Eve Johnson', 'eve@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vYBxLri', 'player'),
('Frank Miller', 'frank@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vYBxLri', 'player');

-- Insertion des personnages
INSERT INTO characters (name, description, image_url, tier) VALUES
('Mario', 'Le plombier le plus célèbre du monde des jeux vidéo', 'mario.jpg', 'S'),
('Link', 'Le héros du temps de la série Zelda', 'link.jpg', 'S'),
('Samus', 'La chasseuse de prime en armure', 'samus.jpg', 'A'),
('Pikachu', 'La mascotte de Pokémon', 'pikachu.jpg', 'A'),
('Donkey Kong', 'Le roi de la jungle', 'donkey_kong.jpg', 'B'),
('Sonic', 'Le hérisson le plus rapide du monde', 'sonic.jpg', 'B'),
('Mega Man', 'Le robot bleu combattant', 'mega_man.jpg', 'C'),
('Pac-Man', 'Le mangeur de points jaune', 'pac_man.jpg', 'C');

-- Insertion des tournois
INSERT INTO tournaments (name, description, start_date, end_date, registration_deadline, max_participants, format, rules, prize_pool, organizer_id, status) VALUES
('Tournoi d''été 2024', 'Le plus grand tournoi de l''été', '2024-07-01 10:00:00', '2024-07-01 18:00:00', '2024-06-30 23:59:59', 32, 'double_elimination', 'Règles standard Smash Bros', '1000€', 1, 'pending'),
('Championnat régional', 'Qualifications pour le championnat national', '2024-08-15 09:00:00', '2024-08-15 20:00:00', '2024-08-14 23:59:59', 64, 'single_elimination', 'Règles officielles', '2000€', 1, 'pending'),
('Tournoi amical', 'Tournoi pour s''amuser et progresser', '2024-06-01 14:00:00', '2024-06-01 22:00:00', '2024-05-31 23:59:59', 16, 'round_robin', 'Règles simplifiées', '500€', 1, 'completed');

-- Insertion des inscriptions
INSERT INTO registrations (tournament_id, user_id, character_id, registration_date, status) VALUES
(1, 2, 1, NOW(), 'confirmed'),
(1, 3, 2, NOW(), 'confirmed'),
(1, 4, 3, NOW(), 'confirmed'),
(1, 5, 4, NOW(), 'confirmed'),
(2, 2, 1, NOW(), 'confirmed'),
(2, 3, 2, NOW(), 'confirmed'),
(2, 6, 5, NOW(), 'confirmed'),
(2, 7, 6, NOW(), 'confirmed'),
(3, 2, 1, NOW(), 'confirmed'),
(3, 3, 2, NOW(), 'confirmed'),
(3, 4, 3, NOW(), 'confirmed'),
(3, 5, 4, NOW(), 'confirmed');

-- Insertion des matchs
INSERT INTO matches (tournament_id, player1_id, player2_id, round, scheduled_time, status) VALUES
(3, 2, 3, 1, '2024-06-01 14:00:00', 'completed'),
(3, 4, 5, 1, '2024-06-01 14:30:00', 'completed'),
(3, 2, 4, 2, '2024-06-01 15:00:00', 'completed'),
(3, 3, 5, 2, '2024-06-01 15:30:00', 'completed'),
(3, 2, 5, 3, '2024-06-01 16:00:00', 'completed'),
(3, 3, 4, 3, '2024-06-01 16:30:00', 'completed');

-- Mise à jour des résultats des matchs
UPDATE matches SET winner_id = 2, loser_id = 3, score = '3-1' WHERE id = 1;
UPDATE matches SET winner_id = 4, loser_id = 5, score = '3-2' WHERE id = 2;
UPDATE matches SET winner_id = 2, loser_id = 4, score = '3-0' WHERE id = 3;
UPDATE matches SET winner_id = 3, loser_id = 5, score = '3-1' WHERE id = 4;
UPDATE matches SET winner_id = 2, loser_id = 5, score = '3-2' WHERE id = 5;
UPDATE matches SET winner_id = 3, loser_id = 4, score = '3-1' WHERE id = 6;

-- Insertion des classements
INSERT INTO rankings (user_id, tournament_id, points, matches_played, matches_won, matches_lost) VALUES
(2, 3, 9, 3, 3, 0),
(3, 3, 6, 3, 2, 1),
(4, 3, 3, 3, 1, 2),
(5, 3, 0, 3, 0, 3);