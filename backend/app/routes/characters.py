from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models.character import Character

# Création du Blueprint pour les routes des personnages
bp = Blueprint("characters", __name__)


# Route pour obtenir tous les personnages
@bp.route("", methods=["GET"])
@jwt_required()
def get_all_characters():
    characters = Character.query.all()
    return jsonify([character.to_dict() for character in characters]), 200


# Route pour obtenir un personnage spécifique
@bp.route("/<int:character_id>", methods=["GET"])
@jwt_required()
def get_character(character_id):
    try:
        character = Character.query.get_or_404(character_id)
        return jsonify({
            'id': character.id,
            'name': character.name,
            'image_url': character.image_url,
            'description': character.description
        })
    except ValueError:
        return jsonify({
            'error': 'ID de personnage invalide'
        }), 400
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la récupération du personnage: {str(e)}'
        }), 500
