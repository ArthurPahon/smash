import os
import sys
import bcrypt
from datetime import datetime, timedelta
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import (
    User, Tournament, Match, Bracket, Registration, Role, Character, Ranking
)


def init_db():
    app = create_app()
    with app.app_context():
        # Suppression de toutes les données existantes
        db.drop_all()
        db.create_all()

        # Création des rôles
        roles = {
            'admin': Role(
                name='admin',
                description='Administrateur du système'
            ),
            'organisateur': Role(
                name='organisateur',
                description='Organisateur de tournois'
            ),
            'joueur': Role(
                name='joueur',
                description='Joueur participant aux tournois'
            )
        }
        for role in roles.values():
            db.session.add(role)
        db.session.commit()

        # Création des utilisateurs
        users = []
        for i in range(1, 11):
            user = User(
                name=f"Joueur {i}",
                email=f"joueur{i}@example.com",
                password="password123"
            )
            user.country = "Canada"
            user.state = "Québec"
            users.append(user)
            db.session.add(user)
        db.session.commit()

        # Création des personnages
        characters = [
            Character(
                name="Mario",
                game="Super Smash Bros. Ultimate",
                image_url="https://example.com/mario.png"
            ),
            Character(
                name="Link",
                game="Super Smash Bros. Ultimate",
                image_url="https://example.com/link.png"
            ),
            Character(
                name="Samus",
                game="Super Smash Bros. Ultimate",
                image_url="https://example.com/samus.png"
            ),
            Character(
                name="Pikachu",
                game="Super Smash Bros. Ultimate",
                image_url="https://example.com/pikachu.png"
            ),
            Character(
                name="Donkey Kong",
                game="Super Smash Bros. Ultimate",
                image_url="https://example.com/dk.png"
            )
        ]
        for character in characters:
            db.session.add(character)
        db.session.commit()

        # Création des tournois
        tournaments = []
        for i in range(1, 6):
            start_date = datetime.now() + timedelta(days=i*7)
            tournament = Tournament(
                name=f"Tournoi {i}",
                description=f"Description du tournoi {i}",
                start_date=start_date,
                end_date=start_date + timedelta(days=2),
                registration_deadline=start_date - timedelta(days=2),
                max_participants=16,
                format="simple_elimination",
                rules="Règles standard du tournoi",
                prize_pool=1000 * i,
                status="upcoming",
                organizer_id=users[0].id
            )
            tournaments.append(tournament)
            db.session.add(tournament)
        db.session.commit()

        # Création des inscriptions
        for tournament in tournaments:
            for i, user in enumerate(users):
                registration = Registration(
                    user_id=user.id,
                    tournament_id=tournament.id,
                    status="registered",
                    registration_date=datetime.utcnow(),
                    seed=i+1
                )
                db.session.add(registration)
        db.session.commit()

        # Création des matchs
        for tournament in tournaments:
            for i in range(0, len(users)-1, 2):
                start_time = tournament.start_date + timedelta(hours=i)
                match = Match(
                    tournament_id=tournament.id,
                    player1_id=users[i].id,
                    player2_id=users[i+1].id,
                    round=1,
                    bracket_position=i//2 + 1,
                    status="scheduled",
                    start_time=start_time,
                    end_time=start_time + timedelta(hours=1)
                )
                db.session.add(match)
        db.session.commit()

        # Mise à jour de certains matchs comme terminés
        matches = Match.query.all()
        for match in matches[:5]:  # Marquer les 5 premiers matchs comme terminés
            match.status = "finished"
            match.winner_id = match.player1_id
            match.loser_id = match.player2_id
            match.end_time = match.start_time + timedelta(hours=1)

        # Création des classements
        for tournament in tournaments:
            for user in users:
                matches_played = random.randint(0, 5)
                matches_won = random.randint(0, matches_played)
                ranking = Ranking(
                    user_id=user.id,
                    tournament_id=tournament.id,
                    rank=random.randint(1, len(users)),
                    points=random.randint(0, 100),
                    matches_played=matches_played,
                    matches_won=matches_won,
                    matches_lost=matches_played - matches_won
                )
                db.session.add(ranking)
        db.session.commit()

        print("Base de données initialisée avec succès!")


if __name__ == '__main__':
    init_db()