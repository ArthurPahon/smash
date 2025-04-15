from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.tournament import Tournament
from app.models.registration import Registration

bp = Blueprint("tournaments", __name__)

@bp.route("", methods=["GET"])
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

    try:
        current_app.logger.info("Exécution de la requête de pagination")
        pagination = query.paginate(page=page, per_page=per_page)
        tournaments = pagination.items
        current_app.logger.info(f"Nombre de tournois trouvés: {len(tournaments)}")

        result = {
            'tournaments': [t.to_dict() for t in tournaments],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
        current_app.logger.info("Réponse préparée avec succès")
        current_app.logger.info("=== FIN DE LA ROUTE GET /tournaments ===")
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des tournois: {str(e)}")
        current_app.logger.error(f"Type d'erreur: {type(e)}")
        current_app.logger.error("Traceback complet:", exc_info=True)
        current_app.logger.error("=== FIN DE LA ROUTE GET /tournaments (AVEC ERREUR) ===")
        return jsonify({'error': str(e)}), 422

@bp.route("/<int:tournament_id>", methods=["GET"])
@jwt_required()
def get_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    return jsonify(tournament.to_dict()), 200

@bp.route("", methods=["POST"])
@jwt_required()
def create_tournament():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    required_fields = ['name', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Field {field} is required'}), 400

    try:
        tournament = Tournament(
            name=data['name'],
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            organizer_id=current_user_id,
            description=data.get('description'),
            registration_deadline=datetime.fromisoformat(
                data['registration_deadline']
            ) if 'registration_deadline' in data else None,
            max_participants=data.get('max_participants'),
            format=data.get('format'),
            rules=data.get('rules'),
            prize_pool=data.get('prize_pool')
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
    current_user_id = get_jwt_identity()
    tournament = Tournament.query.get_or_404(tournament_id)

    if tournament.organizer_id != current_user_id:
        return jsonify({'error': 'Not authorized'}), 403

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
            tournament.registration_deadline = datetime.fromisoformat(
                data['registration_deadline']
            )
        if 'max_participants' in data:
            tournament.max_participants = data['max_participants']
        if 'format' in data:
            tournament.format = data['format']
        if 'rules' in data:
            tournament.rules = data['rules']
        if 'prize_pool' in data:
            tournament.prize_pool = data['prize_pool']
        if 'status' in data:
            if data['status'] not in [
                'preparation', 'ongoing', 'finished', 'cancelled'
            ]:
                return jsonify({'error': 'Invalid status'}), 400
            tournament.status = data['status']

        db.session.commit()
        return jsonify(tournament.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating tournament: {str(e)}")
        return jsonify({'error': str(e)}), 422

@bp.route("/<int:tournament_id>", methods=["DELETE"])
@jwt_required()
def delete_tournament(tournament_id):
    current_user_id = get_jwt_identity()
    tournament = Tournament.query.get_or_404(tournament_id)

    if tournament.organizer_id != current_user_id:
        return jsonify({'error': 'Not authorized'}), 403

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
    current_user_id = get_jwt_identity()
    tournament = Tournament.query.get_or_404(tournament_id)

    # Vérifier si l'utilisateur est déjà inscrit
    existing_registration = Registration.query.filter_by(
        user_id=current_user_id,
        tournament_id=tournament_id
    ).first()

    if existing_registration:
        return jsonify({'error': 'Already registered'}), 400

    # Vérifier si le tournoi est complet
    if (tournament.max_participants and
            len(tournament.registrations) >= tournament.max_participants):
        return jsonify({'error': 'Tournament is full'}), 400

    # Vérifier si la date limite d'inscription est dépassée
    if (tournament.registration_deadline and
            datetime.utcnow() > tournament.registration_deadline):
        return jsonify({'error': 'Registration deadline has passed'}), 400

    try:
        registration = Registration(
            user_id=current_user_id,
            tournament_id=tournament_id
        )
        db.session.add(registration)
        db.session.commit()
        return jsonify({'message': 'Successfully registered'}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error registering to tournament: {str(e)}"
        )
        return jsonify({'error': str(e)}), 422

@bp.route("/<int:tournament_id>/unregister", methods=["POST"])
@jwt_required()
def unregister_from_tournament(tournament_id):
    current_user_id = get_jwt_identity()
    registration = Registration.query.filter_by(
        user_id=current_user_id,
        tournament_id=tournament_id
    ).first_or_404()

    try:
        db.session.delete(registration)
        db.session.commit()
        return jsonify({'message': 'Successfully unregistered'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error unregistering from tournament: {str(e)}"
        )
        return jsonify({'error': str(e)}), 422