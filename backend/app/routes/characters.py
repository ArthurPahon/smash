from flask import Blueprint, jsonify

# Création du Blueprint pour les routes des personnages
bp = Blueprint("characters", __name__)


# Route pour obtenir tous les personnages
@bp.route("", methods=["GET"])
def get_all_characters():
    # Pour l'instant, on renvoie des personnages fictifs
    characters_data = [
        {
            "id": 1,
            "name": "Mario",
            "series": "Super Mario",
            "image_url": "https://example.com/mario.png",
        },
        {
            "id": 2,
            "name": "Link",
            "series": "The Legend of Zelda",
            "image_url": "https://example.com/link.png",
        },
        {
            "id": 3,
            "name": "Pikachu",
            "series": "Pokémon",
            "image_url": "https://example.com/pikachu.png",
        },
    ]
    return jsonify(characters_data), 200


# Route pour obtenir un personnage spécifique
@bp.route("/<int:character_id>", methods=["GET"])
def get_character(character_id):
    # Pour l'instant, on renvoie un personnage fictif
    character_data = {
        "id": character_id,
        "name": "Mario",
        "series": "Super Mario",
        "image_url": "https://example.com/mario.png",
        "stats": {
            "weight": "Medium",
            "speed": "Medium",
            "recovery": "Good",
            "combo_potential": "High",
        },
        "moves": [
            {"name": "Fireball", "type": "Special"},
            {"name": "Cape", "type": "Special"},
            {"name": "Super Jump Punch", "type": "Special"},
            {"name": "F.L.U.D.D.", "type": "Special"},
        ],
    }
    return jsonify(character_data), 200
