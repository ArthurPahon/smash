-- Création de la base de données
CREATE DATABASE IF NOT EXISTS smash;
USE smash;

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    profile_picture VARCHAR(255),
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    country VARCHAR(100),
    state VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE
);

-- Table des rôles
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);

-- Table d'association user_role
CREATE TABLE IF NOT EXISTS user_role (
    user_id INT,
    role_id INT,
    tournament_id INT,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE
);

-- Table des tournois
CREATE TABLE IF NOT EXISTS tournaments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    registration_deadline DATETIME,
    max_participants INT,
    current_participants INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    format VARCHAR(20) DEFAULT 'single_elimination',
    rules TEXT,
    prize_pool TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    organizer_id INT NOT NULL,
    FOREIGN KEY (organizer_id) REFERENCES users(id)
);

-- Table d'association user_tournaments
CREATE TABLE IF NOT EXISTS user_tournaments (
    user_id INT,
    tournament_id INT,
    PRIMARY KEY (user_id, tournament_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE
);

-- Table des personnages
CREATE TABLE IF NOT EXISTS characters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    game VARCHAR(100) NOT NULL,
    image_url VARCHAR(255)
);

-- Table d'association user_characters
CREATE TABLE IF NOT EXISTS user_characters (
    user_id INT,
    character_id INT,
    PRIMARY KEY (user_id, character_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- Table des matchs
CREATE TABLE IF NOT EXISTS matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT NOT NULL,
    player1_id INT NOT NULL,
    player2_id INT NOT NULL,
    winner_id INT,
    loser_id INT,
    score VARCHAR(50),
    round INT,
    bracket_position INT,
    status VARCHAR(20) DEFAULT 'pending',
    start_time DATETIME,
    end_time DATETIME,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
    FOREIGN KEY (player1_id) REFERENCES users(id),
    FOREIGN KEY (player2_id) REFERENCES users(id),
    FOREIGN KEY (winner_id) REFERENCES users(id),
    FOREIGN KEY (loser_id) REFERENCES users(id)
);

-- Table d'association match_characters
CREATE TABLE IF NOT EXISTS match_characters (
    match_id INT,
    character_id INT,
    player_id INT NOT NULL,
    PRIMARY KEY (match_id, character_id),
    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES users(id)
);

-- Table des brackets
CREATE TABLE IF NOT EXISTS brackets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT NOT NULL,
    type VARCHAR(50),
    round_count INT,
    current_round INT DEFAULT 1,
    status VARCHAR(20) DEFAULT 'preparation',
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
);

-- Table des inscriptions
CREATE TABLE IF NOT EXISTS registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tournament_id INT NOT NULL,
    registration_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'registered',
    seed INT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
);

-- Table des classements
CREATE TABLE IF NOT EXISTS rankings (
    user_id INT,
    tournament_id INT,
    rank INT,
    points INT DEFAULT 0,
    matches_played INT DEFAULT 0,
    matches_won INT DEFAULT 0,
    matches_lost INT DEFAULT 0,
    PRIMARY KEY (user_id, tournament_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
);

-- Index pour optimiser les performances
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_tournaments_status ON tournaments(status);
CREATE INDEX idx_tournaments_dates ON tournaments(start_date, end_date);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_tournament ON matches(tournament_id);
CREATE INDEX idx_registrations_tournament ON registrations(tournament_id);
CREATE INDEX idx_rankings_tournament ON rankings(tournament_id);