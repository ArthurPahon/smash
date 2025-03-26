from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

# Création du Blueprint pour les routes des matches
bp = Blueprint("matches", __name__)


# Route pour obtenir tous les matches d'un tournoi
@bp.route("/tournament/<int:tournament_id>", methods=["GET"])
def get_tournament_matches(tournament_id):
    # Pour l'instant, on renvoie des matches fictifs
    matches_data = [
        {
            "id": 1,
            "tournament_id": tournament_id,
            "player1": "player1",
            "player2": "player2",
            "winner": "player1",
            "score": "3-2",
            "round": 1,
        },
        {
            "id": 2,
            "tournament_id": tournament_id,
            "player1": "player3",
            "player2": "player4",
            "winner": "player3",
            "score": "3-1",
            "round": 1,
        },
    ]
    return jsonify(matches_data), 200


# Route pour obtenir un match spécifique
@bp.route("/<int:match_id>", methods=["GET"])
def get_match(match_id):
    # Pour l'instant, on renvoie un match fictif
    match_data = {
        "id": match_id,
        "tournament_id": 1,
        "player1": "player1",
        "player2": "player2",
        "winner": "player1",
        "score": "3-2",
        "round": 1,
        "details": {
            "character_player1": "Mario",
            "character_player2": "Link",
            "stage": "Final Destination",
        },
    }
    return jsonify(match_data), 200


# Route pour créer un nouveau match
@bp.route("", methods=["POST"])
@jwt_required()
def create_match():
    # Pour l'instant, on renvoie juste un message de succès
    return jsonify({"message": "Match créé avec succès", "id": 3}), 201


# Route pour mettre à jour le résultat d'un match
@bp.route("/<int:match_id>/result", methods=["PUT"])
@jwt_required()
def update_match_result(match_id):
    # Pour l'instant, on renvoie juste un message de succès
    return jsonify(
        {"message": f"Résultat du match {match_id} mis à jour"}
    ), 200
