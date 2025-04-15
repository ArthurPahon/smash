from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db
from app.models.tournament import Tournament
from app.models.registration import Registration

bp = Blueprint("tournaments", __name__)

@bp.route("", methods=["GET"])
@jwt_required()
def get_tournaments():
    current_app.logger.info("=== DÉBUT DE LA ROUTE GET /tournaments ===")
    current_app.logger.info(f"Headers de la requête: {dict(request.headers)}")

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')

    current_app.logger.info(f"Paramètres de la requête - page: {page}, per_page: {per_page}, search: {search}, status: {status}")

    query = Tournament.query
    if search:
        query = query.filter(Tournament.name.ilike(f'%{search}%'))
    if status and status != 'all':
        query = query.filter(Tournament.status == status)

    pagination = query.paginate(page=page, per_page=per_page)
    tournaments = pagination.items

    return jsonify({
        'tournaments': [t.to_dict() for t in tournaments],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@bp.route("/<int:tournament_id>", methods=["GET"])
@jwt_required()
def get_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    return jsonify(tournament.to_dict()), 200

@bp.route("", methods=["POST"])
@jwt_required()
def create_tournament():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    # Validation des champs requis
    required_fields = ['name', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Le champ {field} est requis'}), 400

    try:
        tournament = Tournament(
            name=data['name'],
            description=data.get('description'),
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            registration_deadline=datetime.fromisoformat(data['registration_deadline']) if 'registration_deadline' in data and data['registration_deadline'] else None,
            max_participants=data.get('max_participants'),
            format=data.get('format', 'Simple'),
            game=data.get('game'),
            rules=data.get('rules'),
            prizes=data.get('prizes'),
            address=data.get('address'),
            organizer_id=current_user_id
        )

        db.session.add(tournament)
        db.session.commit()

        return jsonify(tournament.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating tournament: {str(e)}")
        return jsonify({'error': str(e)}), 422

@bp.route("/<int:tournament_id>", methods=["PUT"])
@jwt_required()
def update_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    data = request.get_json()

    try:
        if 'name' in data:
            tournament.name = data['name']
        if 'description' in data:
            tournament.description = data['description']
        if 'start_date' in data:
            tournament.start_date = datetime.fromisoformat(data['start_date'])
        if 'end_date' in data:
            tournament.end_date = datetime.fromisoformat(data['end_date'])
        if 'registration_deadline' in data:
            tournament.registration_deadline = datetime.fromisoformat(data['registration_deadline'])
        if 'max_participants' in data:
            tournament.max_participants = data['max_participants']
        if 'status' in data:
            tournament.status = data['status']
        if 'format' in data:
            tournament.format = data['format']
        if 'game' in data:
            tournament.game = data['game']
        if 'rules' in data:
            tournament.rules = data['rules']
        if 'prizes' in data:
            tournament.prizes = data['prizes']
        if 'address' in data:
            tournament.address = data['address']

        db.session.commit()
        return jsonify(tournament.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating tournament: {str(e)}")
        return jsonify({'error': str(e)}), 422

@bp.route("/<int:tournament_id>", methods=["DELETE"])
@jwt_required()
def delete_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    try:
        db.session.delete(tournament)
        db.session.commit()
        return jsonify({'message': 'Tournament deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting tournament: {str(e)}")
        return jsonify({'error': str(e)}), 422

@bp.route("/<int:tournament_id>/register", methods=["POST"])
@jwt_required()
def register_to_tournament(tournament_id):
    current_user_id = int(get_jwt_identity())
    current_app.logger.info(f"Tentative d'inscription - User ID: {current_user_id}, Tournament ID: {tournament_id}")

    tournament = Tournament.query.get_or_404(tournament_id)
    current_app.logger.info(f"Tournoi trouvé: {tournament.name}")

    # Vérifier si l'utilisateur est déjà inscrit
    existing_registration = Registration.query.filter_by(
        user_id=current_user_id,
        tournament_id=tournament_id
    ).first()

    if existing_registration:
        current_app.logger.info(f"L'utilisateur {current_user_id} est déjà inscrit au tournoi {tournament_id}")
        return jsonify({'error': 'Already registered'}), 400

    # Vérifier si le tournoi est complet
    if (tournament.max_participants and
            len(tournament.registrations) >= tournament.max_participants):
        current_app.logger.info(f"Le tournoi {tournament_id} est complet")
        return jsonify({'error': 'Tournament is full'}), 400

    # Vérifier si la date limite d'inscription est dépassée
    if (tournament.registration_deadline and
            datetime.utcnow() > tournament.registration_deadline):
        current_app.logger.info(f"La date limite d'inscription est dépassée pour le tournoi {tournament_id}")
        return jsonify({'error': 'Registration deadline has passed'}), 400

    try:
        registration = Registration(
            user_id=current_user_id,
            tournament_id=tournament_id
        )
        db.session.add(registration)

        # Initialiser current_participants s'il est None
        if tournament.current_participants is None:
            tournament.current_participants = 0
            current_app.logger.info(f"Initialisation de current_participants à 0 pour le tournoi {tournament_id}")

        # Log avant l'incrémentation
        current_app.logger.info(f"État avant incrémentation - current_participants: {tournament.current_participants}")

        tournament.current_participants += 1

        # Log après l'incrémentation
        current_app.logger.info(f"État après incrémentation - current_participants: {tournament.current_participants}")

        db.session.commit()
        current_app.logger.info(f"Inscription réussie - User ID: {current_user_id}, Tournament ID: {tournament_id}")
        return jsonify({'message': 'Successfully registered'}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error registering to tournament: {str(e)}")
        current_app.logger.error(f"Type d'erreur: {type(e)}")
        current_app.logger.error(f"État du tournoi - current_participants: {tournament.current_participants}, max_participants: {tournament.max_participants}")

        # Si c'est une erreur de base de données SQLAlchemy
        if hasattr(e, 'orig'):
            current_app.logger.error(f"Erreur SQL originale: {e.orig}")

        return jsonify({'error': str(e)}), 422

@bp.route("/<int:tournament_id>/unregister", methods=["POST"])
@jwt_required()
def unregister_from_tournament(tournament_id):
    current_user_id = int(get_jwt_identity())
    registration = Registration.query.filter_by(
        user_id=current_user_id,
        tournament_id=tournament_id
    ).first_or_404()

    try:
        db.session.delete(registration)
        registration.tournament.current_participants -= 1
        db.session.commit()
        return jsonify({'message': 'Successfully unregistered'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error unregistering from tournament: {str(e)}"
        )
        return jsonify({'error': str(e)}), 422