from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.dao import CharacterDAO

# Création du Blueprint pour les routes des personnages
bp = Blueprint("characters", __name__)
character_dao = CharacterDAO()


# Route pour obtenir tous les personnages
@bp.route("", methods=["GET"])
@jwt_required()
def get_all_characters():
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Filtres
    tier = request.args.get('tier')
    search = request.args.get('search', '')

    if search:
        characters = character_dao.search(
            search,
            page=page,
            per_page=per_page
        )
    elif tier:
        characters = character_dao.get_by_tier(
            tier,
            page=page,
            per_page=per_page
        )
    else:
        characters = character_dao.get_all(page=page, per_page=per_page)

    return jsonify({
        'characters': characters['items'],
        'total': characters['total'],
        'pages': characters['pages'],
        'current_page': page
    }), 200


# Route pour obtenir un personnage spécifique
@bp.route("/<int:character_id>", methods=["GET"])
@jwt_required()
def get_character(character_id):
    character = character_dao.get_by_id(character_id)
    if not character:
        return jsonify({'error': 'Character not found'}), 404

    return jsonify(character), 200


@bp.route("/stats", methods=["GET"])
@jwt_required()
def get_character_stats():
    # Statistiques d'utilisation des personnages
    usage_stats = character_dao.get_usage_statistics()
    tier_distribution = character_dao.get_tier_distribution()

    return jsonify({
        'usage_statistics': usage_stats,
        'tier_distribution': tier_distribution
    }), 200
