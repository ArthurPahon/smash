from datetime import timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

# Création du Blueprint pour les routes d'authentification
bp = Blueprint("auth", __name__)


# Route pour l'inscription d'un utilisateur
@bp.route("/register", methods=["POST"])
def register():
    try:
        # Pour l'instant, on renvoie juste un message de succès
        return jsonify({"message": "Inscription réussie!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Route pour la connexion d'un utilisateur
@bp.route("/login", methods=["POST"])
def login():
    try:
        # Pour l'instant, on crée juste un token fictif
        access_token = create_access_token(
            identity="test_user", expires_delta=timedelta(days=1)
        )
        return jsonify({"access_token": access_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Route pour vérifier si l'utilisateur est connecté
@bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    current_user = get_jwt_identity()
    return jsonify({"user": current_user}), 200
