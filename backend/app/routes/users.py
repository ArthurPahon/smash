from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db
from app.models import User, Tournament, Match

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
        query = query.filter(User.nom.ilike(f'%{search}%'))

    pagination = query.paginate(page=page, per_page=per_page)
    users = pagination.items

    return jsonify({
        'users': [{
            'id': user.id,
            'nom': user.nom,
            'email': user.email,
            'photo_profil': user.photo_profil,
            'pays': user.pays,
            'province': user.province,
            'date_inscription': user.date_inscription.isoformat()
        } for user in users],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)

    return jsonify({
        'id': user.id,
        'nom': user.nom,
        'email': user.email,
        'photo_profil': user.photo_profil,
        'pays': user.pays,
        'province': user.province,
        'date_inscription': user.date_inscription.isoformat()
    }), 200

@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()

    # Vérification des permissions
    if current_user_id != user_id:
        return jsonify({'error': 'Non autorisé'}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    # Mise à jour des champs
    if 'nom' in data:
        user.nom = data['nom']
    if 'photo_profil' in data:
        user.photo_profil = data['photo_profil']
    if 'pays' in data:
        user.pays = data['pays']
    if 'province' in data:
        user.province = data['province']

    db.session.commit()

    return jsonify({
        'id': user.id,
        'nom': user.nom,
        'email': user.email,
        'photo_profil': user.photo_profil,
        'pays': user.pays,
        'province': user.province,
        'date_inscription': user.date_inscription.isoformat()
    }), 200

@bp.route('/<int:user_id>/tournaments', methods=['GET'])
@jwt_required()
def get_user_tournaments(user_id):
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Récupération des tournois via les inscriptions
    query = Tournament.query.join(Tournament.inscriptions).filter(
        Tournament.inscriptions.any(user_id=user_id)
    )

    pagination = query.paginate(page=page, per_page=per_page)
    tournaments = pagination.items

    return jsonify({
        'tournaments': [{
            'id': t.id,
            'nom': t.nom,
            'date_debut': t.date_debut.isoformat(),
            'date_fin': t.date_fin.isoformat(),
            'adresse': t.adresse,
            'description': t.description,
            'statut': t.statut
        } for t in tournaments],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@bp.route('/<int:user_id>/stats', methods=['GET'])
@jwt_required()
def get_user_stats(user_id):
    user = User.query.get_or_404(user_id)

    # Statistiques des matchs
    matchs_gagnes = Match.query.filter_by(winner_id=user_id).count()
    matchs_perdus = Match.query.filter_by(loser_id=user_id).count()
    total_matchs = matchs_gagnes + matchs_perdus
    win_rate = (matchs_gagnes / total_matchs * 100) if total_matchs > 0 else 0

    # Statistiques des tournois
    tournois_participes = Tournament.query.join(
        Tournament.inscriptions
    ).filter(
        Tournament.inscriptions.any(user_id=user_id)
    ).count()

    return jsonify({
        'matchs': {
            'total': total_matchs,
            'gagnes': matchs_gagnes,
            'perdus': matchs_perdus,
            'win_rate': round(win_rate, 2)
        },
        'tournois': {
            'participes': tournois_participes
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
        (Match.joueur1_id == user_id) | (Match.joueur2_id == user_id)
    ).order_by(Match.id.desc())

    pagination = query.paginate(page=page, per_page=per_page)
    matches = pagination.items

    return jsonify({
        'matches': [{
            'id': m.id,
            'tournament_id': m.tournament_id,
            'bracket_type': m.bracket_type,
            'round': m.round,
            'position': m.position,
            'joueur1': {
                'id': m.joueur1.id,
                'nom': m.joueur1.nom
            } if m.joueur1 else None,
            'joueur2': {
                'id': m.joueur2.id,
                'nom': m.joueur2.nom
            } if m.joueur2 else None,
            'score_joueur1': m.score_joueur1,
            'score_joueur2': m.score_joueur2,
            'winner': {
                'id': m.winner.id,
                'nom': m.winner.nom
            } if m.winner else None,
            'loser': {
                'id': m.loser.id,
                'nom': m.loser.nom
            } if m.loser else None
        } for m in matches],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200
