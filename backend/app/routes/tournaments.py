from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

# Création du Blueprint pour les routes des tournois
bp = Blueprint("tournaments", __name__)


# Route pour obtenir tous les tournois
@bp.route("", methods=["GET"])
def get_all_tournaments():
    # Pour l'instant, on renvoie des tournois fictifs
    tournaments_data = [
        {
            "id": 1,
            "name": "Tournoi de Paris",
            "date": "2023-06-15",
            "location": "Paris, France",
            "max_participants": 32,
            "current_participants": 12,
        },
        {
            "id": 2,
            "name": "Smash Bros Ultimate Championship",
            "date": "2023-07-20",
            "location": "New York, USA",
            "max_participants": 64,
            "current_participants": 45,
        },
    ]
    return jsonify(tournaments_data), 200


# Route pour obtenir un tournoi spécifique
@bp.route("/<int:tournament_id>", methods=["GET"])
def get_tournament(tournament_id):
    # Pour l'instant, on renvoie un tournoi fictif
    tournament_data = {
        "id": tournament_id,
        "name": "Tournoi de Paris",
        "date": "2023-06-15",
        "location": "Paris, France",
        "max_participants": 32,
        "current_participants": 12,
        "participants": [
            {"id": 1, "username": "player1"},
            {"id": 2, "username": "player2"},
        ],
        "matches": [
            {
                "id": 1,
                "player1": "player1",
                "player2": "player2",
                "winner": "player1",
                "score": "3-2",
            }
        ],
    }
    return jsonify(tournament_data), 200


# Route pour créer un nouveau tournoi
@bp.route("", methods=["POST"])
@jwt_required()
def create_tournament():
    # Pour l'instant, on renvoie juste un message de succès
    return jsonify({"message": "Tournoi créé avec succès", "id": 3}), 201


# Route pour s'inscrire à un tournoi
@bp.route("/<int:tournament_id>/register", methods=["POST"])
@jwt_required()
def register_to_tournament(tournament_id):
    # Pour l'instant, on renvoie juste un message de succès
    return jsonify(
        {"message": f"Inscription au tournoi {tournament_id} réussie"}
    ), 200
