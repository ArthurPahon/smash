from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.dao import RankingDAO, TournamentDAO, UserDAO


bp = Blueprint('rankings', __name__)
ranking_dao = RankingDAO()
tournament_dao = TournamentDAO()
user_dao = UserDAO()

# Configuration des points
POINTS_CONFIG = {
    'victory': 3,
    'defeat': 0,
    'bye': 1
}


@bp.route('', methods=['GET'])
@jwt_required()
def get_global_rankings():
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    rankings = ranking_dao.get_global_ranking(page=page, per_page=per_page)

    return jsonify({
        'rankings': rankings,
        'current_page': page
    }), 200


@bp.route('/tournaments/<int:tournament_id>/ranking', methods=['GET'])
@jwt_required()
def get_tournament_ranking(tournament_id):
    """Récupérer le classement d'un tournoi"""
    try:
        # Vérifier si le tournoi existe
        tournament = tournament_dao.get_by_id(tournament_id)
        if not tournament:
            return jsonify({'error': 'Tournoi non trouvé'}), 404

        # Récupérer le classement
        ranking = ranking_dao.get_by_tournament(tournament_id)
        return jsonify(ranking), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_rankings(user_id):
    # Vérification si l'utilisateur existe
    user = user_dao.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Récupération des classements de l'utilisateur
    rankings = ranking_dao.get_by_user(user_id)

    return jsonify({
        'user': {
            'id': user['id'],
            'name': user['name'],
            'profile_picture': user['profile_picture']
        },
        'rankings': rankings
    }), 200


@bp.route('/tournaments/<int:tournament_id>/calculate', methods=['POST'])
def calculate_tournament_rankings(tournament_id):
    # Vérification si le tournoi existe
    tournament = tournament_dao.get_by_id(tournament_id)
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404

    # Vérification si le tournoi est terminé
    if tournament['status'] != 'finished':
        return jsonify({
            'error': ('Le classement ne peut être calculé que pour un '
                     'tournoi terminé')
        }), 400

    try:
        # Calcul du classement
        rankings = ranking_dao.calculate_tournament_ranking(tournament_id)
        return jsonify({
            'message': 'Classement calculé avec succès',
            'rankings': rankings
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400