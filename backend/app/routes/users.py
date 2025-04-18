from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.dao import UserDAO, TournamentDAO, MatchDAO

# Création du Blueprint pour les routes utilisateurs
bp = Blueprint("users", __name__)
user_dao = UserDAO()
tournament_dao = TournamentDAO()
match_dao = MatchDAO()


# Route pour obtenir le profil de l'utilisateur
@bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    current_user_id = int(get_jwt_identity())
    user = user_dao.get_by_id(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user), 200


# Route pour mettre à jour le profil
@bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    current_user_id = int(get_jwt_identity())
    user = user_dao.get_by_id(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    update_data = {}

    if 'name' in data:
        update_data['name'] = data['name']
    if 'profile_picture' in data:
        update_data['profile_picture'] = data['profile_picture']
    if 'country' in data:
        update_data['country'] = data['country']
    if 'state' in data:
        update_data['state'] = data['state']

    try:
        updated_user = user_dao.update(current_user_id, update_data)
        return jsonify(updated_user), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Filtres
    search = request.args.get('search', '')

    users = user_dao.search(search, page=page, per_page=per_page)

    return jsonify({
        'users': users['items'],
        'total': users['total'],
        'pages': users['pages'],
        'current_page': page
    }), 200


@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = user_dao.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user), 200


@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    user = user_dao.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    if not user_dao.check_password(user_id, data.get('current_password')):
        return jsonify({
            'error': 'Mot de passe actuel incorrect'
        }), 400

    update_data = {}
    if 'name' in data:
        update_data['name'] = data['name']
    if 'profile_picture' in data:
        update_data['profile_picture'] = data['profile_picture']
    if 'country' in data:
        update_data['country'] = data['country']
    if 'state' in data:
        update_data['state'] = data['state']

    try:
        updated_user = user_dao.update(user_id, update_data)
        return jsonify(updated_user), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<int:user_id>/tournaments', methods=['GET'])
@jwt_required()
def get_user_tournaments(user_id):
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    tournaments = tournament_dao.get_by_participant(
        user_id,
        page=page,
        per_page=per_page
    )

    return jsonify({
        'tournaments': tournaments['items'],
        'total': tournaments['total'],
        'pages': tournaments['pages'],
        'current_page': page
    }), 200


@bp.route('/<int:user_id>/stats', methods=['GET'])
@jwt_required()
def get_user_stats(user_id):
    # Vérifier si l'utilisateur existe
    user = user_dao.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Récupérer les statistiques
    stats = user_dao.get_statistics(user_id)

    return jsonify(stats), 200


@bp.route('/<int:user_id>/matches', methods=['GET'])
@jwt_required()
def get_user_matches(user_id):
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    matches = match_dao.get_by_player(
        user_id,
        page=page,
        per_page=per_page
    )

    return jsonify({
        'matches': matches['items'],
        'total': matches['total'],
        'pages': matches['pages'],
        'current_page': page
    }), 200
