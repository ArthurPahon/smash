from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Match, Tournament, User

# Création du Blueprint pour les routes des matches
bp = Blueprint("matches", __name__)


# Route pour obtenir tous les matches d'un tournoi
@bp.route("/tournaments/<int:tournament_id>/matches", methods=["GET"])
@jwt_required()
def get_tournament_matches(tournament_id):
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Filtres
    bracket_type = request.args.get('bracket_type', '')
    round = request.args.get('round', type=int)

    query = Match.query.filter_by(tournament_id=tournament_id)
    if bracket_type:
        query = query.filter_by(bracket_type=bracket_type)
    if round is not None:
        query = query.filter_by(round=round)

    pagination = query.paginate(page=page, per_page=per_page)
    matches = pagination.items

    return jsonify({
        'matches': [{
            'id': m.id,
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


# Route pour obtenir un match spécifique
@bp.route("/matches/<int:match_id>", methods=["GET"])
@jwt_required()
def get_match(match_id):
    match = Match.query.get_or_404(match_id)

    return jsonify({
        'id': match.id,
        'tournament_id': match.tournament_id,
        'bracket_type': match.bracket_type,
        'round': match.round,
        'position': match.position,
        'joueur1': {
            'id': match.joueur1.id,
            'nom': match.joueur1.nom
        } if match.joueur1 else None,
        'joueur2': {
            'id': match.joueur2.id,
            'nom': match.joueur2.nom
        } if match.joueur2 else None,
        'score_joueur1': match.score_joueur1,
        'score_joueur2': match.score_joueur2,
        'winner': {
            'id': match.winner.id,
            'nom': match.winner.nom
        } if match.winner else None,
        'loser': {
            'id': match.loser.id,
            'nom': match.loser.nom
        } if match.loser else None
    }), 200


# Route pour créer un nouveau match
@bp.route("", methods=["POST"])
@jwt_required()
def create_match():
    # Pour l'instant, on renvoie juste un message de succès
    return jsonify({"message": "Match créé avec succès", "id": 3}), 201


# Route pour mettre à jour le résultat d'un match
@bp.route("/matches/<int:match_id>", methods=["PUT"])
@jwt_required()
def update_match(match_id):
    current_user_id = get_jwt_identity()
    match = Match.query.get_or_404(match_id)

    # Vérification des permissions
    # TODO: Implémenter la vérification des rôles
    # Pour l'instant, on vérifie juste si l'utilisateur est un des joueurs
    if match.joueur1_id != current_user_id and match.joueur2_id != current_user_id:
        return jsonify({'error': 'Non autorisé'}), 403

    data = request.get_json()

    # Mise à jour des champs
    if 'score_joueur1' in data:
        match.score_joueur1 = data['score_joueur1']
    if 'score_joueur2' in data:
        match.score_joueur2 = data['score_joueur2']

    # Mise à jour du winner/loser
    if match.score_joueur1 > match.score_joueur2:
        match.winner_id = match.joueur1_id
        match.loser_id = match.joueur2_id
    elif match.score_joueur2 > match.score_joueur1:
        match.winner_id = match.joueur2_id
        match.loser_id = match.joueur1_id

    db.session.commit()

    return jsonify({
        'id': match.id,
        'tournament_id': match.tournament_id,
        'bracket_type': match.bracket_type,
        'round': match.round,
        'position': match.position,
        'joueur1': {
            'id': match.joueur1.id,
            'nom': match.joueur1.nom
        } if match.joueur1 else None,
        'joueur2': {
            'id': match.joueur2.id,
            'nom': match.joueur2.nom
        } if match.joueur2 else None,
        'score_joueur1': match.score_joueur1,
        'score_joueur2': match.score_joueur2,
        'winner': {
            'id': match.winner.id,
            'nom': match.winner.nom
        } if match.winner else None,
        'loser': {
            'id': match.loser.id,
            'nom': match.loser.nom
        } if match.loser else None
    }), 200


# Route pour mettre à jour le score d'un match
@bp.route("/matches/<int:match_id>/score", methods=["PUT"])
@jwt_required()
def update_match_score(match_id):
    current_user_id = get_jwt_identity()
    match = Match.query.get_or_404(match_id)

    # Vérification des permissions
    # TODO: Implémenter la vérification des rôles
    # Pour l'instant, on vérifie juste si l'utilisateur est un des joueurs
    if match.joueur1_id != current_user_id and match.joueur2_id != current_user_id:
        return jsonify({'error': 'Non autorisé'}), 403

    data = request.get_json()

    if 'score_joueur1' not in data or 'score_joueur2' not in data:
        return jsonify({'error': 'Les scores des deux joueurs sont requis'}), 400

    match.score_joueur1 = data['score_joueur1']
    match.score_joueur2 = data['score_joueur2']

    # Mise à jour du winner/loser
    if match.score_joueur1 > match.score_joueur2:
        match.winner_id = match.joueur1_id
        match.loser_id = match.joueur2_id
    elif match.score_joueur2 > match.score_joueur1:
        match.winner_id = match.joueur2_id
        match.loser_id = match.joueur1_id

    db.session.commit()

    return jsonify({
        'id': match.id,
        'score_joueur1': match.score_joueur1,
        'score_joueur2': match.score_joueur2,
        'winner': {
            'id': match.winner.id,
            'nom': match.winner.nom
        } if match.winner else None,
        'loser': {
            'id': match.loser.id,
            'nom': match.loser.nom
        } if match.loser else None
    }), 200
