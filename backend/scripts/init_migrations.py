import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_migrate import init, migrate, upgrade
from app import create_app


def init_migrations():
    app = create_app()
    with app.app_context():
        # Initialiser les migrations
        init()

        # Créer la migration initiale
        migrate()

        # Appliquer les migrations
        upgrade()

        print("Migrations initialisées avec succès!")


if __name__ == '__main__':
    init_migrations()