import os
import sys
import bcrypt
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import (
    User, Tournament, Match, Bracket, Registration, Role, Character
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
            password = f'password{i}'
            hashed = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            user = User(
                name=f'Joueur {i}',
                email=f'joueur{i}@example.com',
                password=hashed,
                profile_picture=(
                    f'https://api.dicebear.com/7.x/avataaars/svg?'
                    f'seed=joueur{i}'
                )
            )
            user.country = 'France'
            user.state = 'Québec'
            users.append(user)
            db.session.add(user)
        db.session.commit()

        # Création des personnages
        characters = [
            Character(
                name='Mario',
                game='Super Smash Bros. Ultimate',
                image_url='https://example.com/mario.png'
            ),
            Character(
                name='Link',
                game='Super Smash Bros. Ultimate',
                image_url='https://example.com/link.png'
            ),
            Character(
                name='Pikachu',
                game='Super Smash Bros. Ultimate',
                image_url='https://example.com/pikachu.png'
            )
        ]
        for character in characters:
            db.session.add(character)
        db.session.commit()

        # Création des tournois
        tournaments = []
        for i in range(1, 4):
            start_date = datetime.now() + timedelta(days=i*7)
            tournament = Tournament(
                name=f'Tournoi {i}',
                start_date=start_date,
                end_date=start_date + timedelta(days=1),
                address=f'Adresse du tournoi {i}',
                description=f'Description du tournoi {i}',
                format='double_elimination',
                nb_places_max=8,
                status='preparation'
            )
            tournaments.append(tournament)
            db.session.add(tournament)
        db.session.commit()

        # Création des inscriptions
        for tournament in tournaments:
            for user in users[:8]:  # 8 joueurs par tournoi
                registration = Registration(
                    user_id=user.id,
                    tournament_id=tournament.id,
                    status='confirmed',
                    seed=users.index(user) + 1
                )
                db.session.add(registration)
        db.session.commit()

        # Création des brackets
        brackets = []
        for tournament in tournaments:
            bracket = Bracket(
                tournament_id=tournament.id,
                name='Principal',
                order=1,
                format='double_elimination'
            )
            brackets.append(bracket)
            db.session.add(bracket)
        db.session.commit()

        # Simuler quelques matchs terminés
        for tournament in tournaments[:1]:  # Seulement pour le premier tournoi
            bracket = Bracket.query.filter_by(tournament_id=tournament.id).first()
            # Simuler les matchs du premier tour
            for i in range(0, 8, 2):
                match = Match(
                    tournament_id=tournament.id,
                    bracket_id=bracket.id,
                    round=1,
                    match_number=i//2 + 1,
                    player1_id=users[i].id,
                    player2_id=users[i+1].id,
                    score='2-1',
                    status='completed',
                    winner_id=users[i].id,
                    loser_id=users[i+1].id,
                    character1_id=characters[0].id,
                    character2_id=characters[1].id
                )
                db.session.add(match)
        db.session.commit()

        print("Base de données initialisée avec succès!")


if __name__ == '__main__':
    init_db()