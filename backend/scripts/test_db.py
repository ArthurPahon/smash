import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Tournament

def test_db():
    app = create_app()
    with app.app_context():
        try:
            tournaments = Tournament.query.all()
            print("Tournois trouvés :", len(tournaments))
            for t in tournaments:
                print(f"- {t.name} ({t.status})")
        except Exception as e:
            print("Erreur :", str(e))

if __name__ == '__main__':
    test_db()