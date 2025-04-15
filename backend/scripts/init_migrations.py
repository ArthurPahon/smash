import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Tournament, Match, Registration, Ranking, Character


def init_migrations():
    app = create_app()
    with app.app_context():
        # Initialisation de Flask-Migrate
        migrate = Migrate(app, db)

        # Création du dossier migrations s'il n'existe pas
        if not os.path.exists('migrations'):
            os.makedirs('migrations')

        # Initialisation des migrations
        from flask_migrate import init, migrate, upgrade
        init()
        migrate()
        upgrade()

        print("Migrations initialisées avec succès!")


if __name__ == '__main__':
    init_migrations()