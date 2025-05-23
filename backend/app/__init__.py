import os
from dotenv import load_dotenv

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Chargement des variables d'environnement
load_dotenv()

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Configuration de l'application
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_key")
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY",
                                                  "jwt_dev_key")

    # Configuration des logs
    import logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    # Mode de développement sans base de données
    if os.environ.get("FLASK_ENV") == "development_no_db":
        app.logger.info("Running in development mode without database")
    else:
        # Configuration de la base de données
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "DATABASE_URL", "sqlite:///test.db"
        )
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        # Initialisation de la base de données
        db.init_app(app)
        migrate.init_app(app, db)

    # Initialisation de JWT et CORS
    jwt.init_app(app)

    # Gestionnaires d'erreurs JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        app.logger.error(f"Token expiré - Header: {jwt_header}, Payload: {jwt_payload}")
        return {"error": "Le token a expiré"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        app.logger.error(f"Token invalide - Erreur: {error}")
        return {"error": "Token invalide"}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        app.logger.error(f"Token manquant - Erreur: {error}")
        return {"error": "Token manquant"}, 401

    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Enregistrement des blueprints
    with app.app_context():
        try:
            # Importation des routes
            from .routes import (
                auth,
                characters,
                matches,
                tournaments,
                users,
                rankings
            )

            # Enregistrement des blueprints
            app.register_blueprint(auth.bp, url_prefix="/api/auth")
            app.register_blueprint(users.bp, url_prefix="/api/users")
            app.register_blueprint(
                tournaments.bp,
                url_prefix="/api/tournaments"
            )
            app.register_blueprint(matches.bp, url_prefix="/api/matches")
            app.register_blueprint(
                characters.bp,
                url_prefix="/api/characters"
            )
            app.register_blueprint(rankings.bp, url_prefix="/api/rankings")

            app.logger.info("All blueprints registered successfully")
        except ImportError as e:
            app.logger.error(f"Error importing routes: {e}")

            # Création d'une route de base pour le mode de développement
            @app.route("/")
            def home():
                return {"message": "API is running in development mode"}, 200

    return app
