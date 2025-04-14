import os

from app import create_app

# Configuration de l'environnement
os.environ["FLASK_ENV"] = "development"

# Création de l'application
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
