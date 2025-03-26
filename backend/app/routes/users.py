from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

# Création du Blueprint pour les routes utilisateurs
bp = Blueprint("users", __name__)


# Route pour obtenir le profil de l'utilisateur
@bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    # Pour l'instant, on renvoie juste un utilisateur fictif
    user_data = {
        "id": 1,
        "username": current_user,
        "email": "user@example.com",
        "created_at": "2023-01-01",
    }
    return jsonify(user_data), 200


# Route pour mettre à jour le profil
@bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    # Pour l'instant, on renvoie juste un message de succès
    return jsonify({"message": "Profil mis à jour avec succès"}), 200
