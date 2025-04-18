-- Index pour la table users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_name ON users(name);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Index pour la table tournaments
CREATE INDEX idx_tournaments_status ON tournaments(status);
CREATE INDEX idx_tournaments_start_date ON tournaments(start_date);
CREATE INDEX idx_tournaments_end_date ON tournaments(end_date);
CREATE INDEX idx_tournaments_organizer ON tournaments(organizer_id);

-- Index pour la table matches
CREATE INDEX idx_matches_tournament ON matches(tournament_id);
CREATE INDEX idx_matches_player1 ON matches(player1_id);
CREATE INDEX idx_matches_player2 ON matches(player2_id);
CREATE INDEX idx_matches_winner ON matches(winner_id);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_start_time ON matches(start_time);

-- Index pour la table registrations
CREATE INDEX idx_registrations_user ON registrations(user_id);
CREATE INDEX idx_registrations_tournament ON registrations(tournament_id);
CREATE INDEX idx_registrations_status ON registrations(status);

-- Index pour la table rankings
CREATE INDEX idx_rankings_user ON rankings(user_id);
CREATE INDEX idx_rankings_tournament ON rankings(tournament_id);
CREATE INDEX idx_rankings_points ON rankings(points);

-- Index pour la table match_characters
CREATE INDEX idx_match_characters_match ON match_characters(match_id);
CREATE INDEX idx_match_characters_player ON match_characters(player_id);
CREATE INDEX idx_match_characters_character ON match_characters(character_id);

-- Contraintes d'intégrité pour la table users
ALTER TABLE users
ADD CONSTRAINT chk_users_email CHECK (email LIKE '%@%.%'),
ADD CONSTRAINT chk_users_password CHECK (LENGTH(password) >= 8),
ADD CONSTRAINT chk_users_name CHECK (LENGTH(name) >= 2);

-- Contraintes d'intégrité pour la table tournaments
ALTER TABLE tournaments
ADD CONSTRAINT chk_tournaments_dates CHECK (start_date < end_date),
ADD CONSTRAINT chk_tournaments_participants CHECK (current_participants <= max_participants),
ADD CONSTRAINT chk_tournaments_status CHECK (status IN ('pending', 'active', 'completed', 'cancelled'));

-- Contraintes d'intégrité pour la table matches
ALTER TABLE matches
ADD CONSTRAINT chk_matches_players CHECK (player1_id != player2_id),
ADD CONSTRAINT chk_matches_winner CHECK (
    (winner_id IS NULL) OR
    (winner_id = player1_id OR winner_id = player2_id)
),
ADD CONSTRAINT chk_matches_status CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled'));

-- Contraintes d'intégrité pour la table registrations
ALTER TABLE registrations
ADD CONSTRAINT chk_registrations_status CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled')),
ADD CONSTRAINT chk_registrations_seed CHECK (seed > 0);

-- Contraintes d'intégrité pour la table rankings
ALTER TABLE rankings
ADD CONSTRAINT chk_rankings_points CHECK (points >= 0),
ADD CONSTRAINT chk_rankings_matches CHECK (matches_played >= matches_won + matches_lost);

-- Contraintes de clés étrangères
ALTER TABLE user_role
ADD CONSTRAINT fk_user_role_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_user_role_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE;

ALTER TABLE tournaments
ADD CONSTRAINT fk_tournaments_organizer FOREIGN KEY (organizer_id) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE matches
ADD CONSTRAINT fk_matches_tournament FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_matches_player1 FOREIGN KEY (player1_id) REFERENCES users(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_matches_player2 FOREIGN KEY (player2_id) REFERENCES users(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_matches_winner FOREIGN KEY (winner_id) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE registrations
ADD CONSTRAINT fk_registrations_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_registrations_tournament FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE;

ALTER TABLE rankings
ADD CONSTRAINT fk_rankings_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_rankings_tournament FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE;

ALTER TABLE match_characters
ADD CONSTRAINT fk_match_characters_match FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_match_characters_player FOREIGN KEY (player_id) REFERENCES users(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_match_characters_character FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE;