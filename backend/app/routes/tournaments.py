from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Tournament, User, Registration, Bracket, Match

# Création du Blueprint pour les routes des tournois
bp = Blueprint("tournaments", __name__)


# Route pour obtenir tous les tournois
@bp.route("", methods=["GET"])
@jwt_required()
def get_tournaments():
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Filtres
    search = request.args.get('search', '')
    statut = request.args.get('statut', '')

    query = Tournament.query
    if search:
        query = query.filter(Tournament.nom.ilike(f'%{search}%'))
    if statut:
        query = query.filter(Tournament.statut == statut)

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


# Route pour obtenir un tournoi spécifique
@bp.route("/<int:tournament_id>", methods=["GET"])
@jwt_required()
def get_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    return jsonify({
        'id': tournament.id,
        'nom': tournament.nom,
        'date_debut': tournament.date_debut.isoformat(),
        'date_fin': tournament.date_fin.isoformat(),
        'adresse': tournament.adresse,
        'description': tournament.description,
        'statut': tournament.statut
    }), 200


# Route pour créer un nouveau tournoi
@bp.route("", methods=["POST"])
@jwt_required()
def create_tournament():
    data = request.get_json()

    # Vérification des champs requis
    required_fields = ['nom', 'date_debut', 'date_fin']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Le champ {field} est requis'}), 400

    # Création du tournoi
    tournament = Tournament(
        nom=data['nom'],
        date_debut=datetime.fromisoformat(data['date_debut']),
        date_fin=datetime.fromisoformat(data['date_fin']),
        adresse=data.get('adresse'),
        description=data.get('description'),
        statut='préparation'
    )

    db.session.add(tournament)
    db.session.commit()

    return jsonify({
        'id': tournament.id,
        'nom': tournament.nom,
        'date_debut': tournament.date_debut.isoformat(),
        'date_fin': tournament.date_fin.isoformat(),
        'adresse': tournament.adresse,
        'description': tournament.description,
        'statut': tournament.statut
    }), 201


# Route pour s'inscrire à un tournoi
@bp.route("/<int:tournament_id>/register", methods=["POST"])
@jwt_required()
def register_to_tournament(tournament_id):
    # Pour l'instant, on renvoie juste un message de succès
    return jsonify(
        {"message": f"Inscription au tournoi {tournament_id} réussie"}
    ), 200


@bp.route('/<int:tournament_id>', methods=['PUT'])
@jwt_required()
def update_tournament(tournament_id):
    current_user_id = get_jwt_identity()
    tournament = Tournament.query.get_or_404(tournament_id)

    # Vérification des permissions (TODO: implémenter la vérification des rôles)
    # Pour l'instant, on permet à n'importe qui de modifier
    data = request.get_json()

    # Mise à jour des champs
    if 'nom' in data:
        tournament.nom = data['nom']
    if 'date_debut' in data:
        tournament.date_debut = datetime.fromisoformat(data['date_debut'])
    if 'date_fin' in data:
        tournament.date_fin = datetime.fromisoformat(data['date_fin'])
    if 'adresse' in data:
        tournament.adresse = data['adresse']
    if 'description' in data:
        tournament.description = data['description']

    db.session.commit()

    return jsonify({
        'id': tournament.id,
        'nom': tournament.nom,
        'date_debut': tournament.date_debut.isoformat(),
        'date_fin': tournament.date_fin.isoformat(),
        'adresse': tournament.adresse,
        'description': tournament.description,
        'statut': tournament.statut
    }), 200


@bp.route('/<int:tournament_id>', methods=['DELETE'])
@jwt_required()
def delete_tournament(tournament_id):
    current_user_id = get_jwt_identity()
    tournament = Tournament.query.get_or_404(tournament_id)

    # Vérification des permissions (TODO: implémenter la vérification des rôles)
    # Pour l'instant, on permet à n'importe qui de supprimer

    db.session.delete(tournament)
    db.session.commit()

    return jsonify({'message': 'Tournoi supprimé avec succès'}), 200


@bp.route('/<int:tournament_id>/status', methods=['PUT'])
@jwt_required()
def update_tournament_status(tournament_id):
    current_user_id = get_jwt_identity()
    tournament = Tournament.query.get_or_404(tournament_id)

    # Vérification des permissions (TODO: implémenter la vérification des rôles)
    data = request.get_json()

    if 'statut' not in data:
        return jsonify({'error': 'Le champ statut est requis'}), 400

    if data['statut'] not in ['préparation', 'en cours', 'terminé']:
        return jsonify({'error': 'Statut invalide'}), 400

    tournament.statut = data['statut']
    db.session.commit()

    return jsonify({
        'id': tournament.id,
        'statut': tournament.statut
    }), 200


@bp.route('/<int:tournament_id>/bracket', methods=['GET'])
@jwt_required()
def get_tournament_bracket(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    bracket = Bracket.query.filter_by(tournament_id=tournament_id).first()

    if not bracket:
        return jsonify({'error': 'Aucun bracket trouvé pour ce tournoi'}), 404

    # Récupération des matchs du bracket
    matches = Match.query.filter_by(
        tournament_id=tournament_id
    ).order_by(Match.round, Match.position).all()

    return jsonify({
        'bracket': {
            'id': bracket.id,
            'type': bracket.type,
            'format_match': bracket.format_match,
            'nb_joueurs': bracket.nb_joueurs,
            'statut_generation': bracket.statut_generation
        },
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
        } for m in matches]
    }), 200
