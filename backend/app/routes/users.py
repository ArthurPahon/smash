from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db
from app.models import User, Tournament, Match
from sqlalchemy import or_

# Création du Blueprint pour les routes utilisateurs
bp = Blueprint("users", __name__)


# Route pour obtenir le profil de l'utilisateur
@bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    return jsonify(user.to_dict()), 200


# Route pour mettre à jour le profil
@bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    data = request.get_json()

    if 'name' in data:
        user.name = data['name']
    if 'profile_picture' in data:
        user.profile_picture = data['profile_picture']
    if 'country' in data:
        user.country = data['country']
    if 'state' in data:
        user.state = data['state']

    db.session.commit()
    return jsonify(user.to_dict()), 200


@bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Filtres
    search = request.args.get('search', '')

    query = User.query
    if search:
        query = query.filter(User.name.ilike(f'%{search}%'))

    pagination = query.paginate(page=page, per_page=per_page)
    users = pagination.items

    return jsonify({
        'users': [user.to_dict() for user in users],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not user.check_password(data.get('current_password')):
        return jsonify({
            'error': ('Mot de passe actuel incorrect')
        }), 400

    # Mise à jour des champs
    if 'name' in data:
        user.name = data['name']
    if 'profile_picture' in data:
        user.profile_picture = data['profile_picture']
    if 'country' in data:
        user.country = data['country']
    if 'state' in data:
        user.state = data['state']

    db.session.commit()
    return jsonify(user.to_dict()), 200


@bp.route('/<int:user_id>/tournaments', methods=['GET'])
@jwt_required()
def get_user_tournaments(user_id):
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Récupération des tournois via les inscriptions
    query = Tournament.query.join(Tournament.registrations).filter(
        Tournament.registrations.any(user_id=user_id)
    )

    pagination = query.paginate(page=page, per_page=per_page)
    tournaments = pagination.items

    return jsonify({
        'tournaments': [t.to_dict() for t in tournaments],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@bp.route('/<int:user_id>/stats', methods=['GET'])
@jwt_required()
def get_user_stats(user_id):
    # Statistiques des matchs
    total_matches = Match.query.filter(
        or_(
            Match.player1_id == user_id,
            Match.player2_id == user_id
        ),
        Match.status == 'finished'
    ).count()

    victories = Match.query.filter(
        Match.winner_id == user_id,
        Match.status == 'finished'
    ).count()

    win_rate = (victories / total_matches * 100) if total_matches > 0 else 0

    # Statistiques des tournois
    tournaments_participated = Tournament.query.join(
        Tournament.registrations
    ).filter(
        Tournament.registrations.any(user_id=user_id)
    ).count()

    return jsonify({
        'matches': {
            'total': total_matches,
            'won': victories,
            'lost': total_matches - victories,
            'win_rate': round(win_rate, 2)
        },
        'tournaments': {
            'participated': tournaments_participated
        }
    }), 200


@bp.route('/<int:user_id>/matches', methods=['GET'])
@jwt_required()
def get_user_matches(user_id):
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Récupération des matchs où l'utilisateur est joueur1 ou joueur2
    query = Match.query.filter(
        (Match.player1_id == user_id) | (Match.player2_id == user_id)
    ).order_by(Match.id.desc())

    pagination = query.paginate(page=page, per_page=per_page)
    matches = pagination.items

    return jsonify({
        'matches': [m.to_dict() for m in matches],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200
