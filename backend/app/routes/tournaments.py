from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.dao import TournamentDAO, RegistrationDAO

bp = Blueprint("tournaments", __name__)
tournament_dao = TournamentDAO()
registration_dao = RegistrationDAO()

@bp.route("", methods=["GET"])
@jwt_required()
def get_tournaments():
    current_app.logger.info("=== DÉBUT DE LA ROUTE GET /tournaments ===")
    current_app.logger.info(f"Headers de la requête: {dict(request.headers)}")

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')

    current_app.logger.info(
        f"Paramètres de la requête - page: {page}, "
        f"per_page: {per_page}, search: {search}, status: {status}"
    )

    tournaments = tournament_dao.get_all(page=page, per_page=per_page)
    if search:
        tournaments = tournament_dao.search(
            search, page=page, per_page=per_page
        )
    if status and status != 'all':
        tournaments = [t for t in tournaments if t['status'] == status]

    return jsonify({
        'tournaments': tournaments,
        'current_page': page
    }), 200

@bp.route("/<int:tournament_id>", methods=["GET"])
@jwt_required()
def get_tournament(tournament_id):
    tournament = tournament_dao.get_by_id(tournament_id)
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    return jsonify(tournament), 200

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
        tournament_data = {
            'name': data['name'],
            'description': data.get('description'),
            'start_date': datetime.fromisoformat(data['start_date']),
            'end_date': datetime.fromisoformat(data['end_date']),
            'registration_deadline': (
                datetime.fromisoformat(data['registration_deadline'])
                if ('registration_deadline' in data and
                    data['registration_deadline'])
                else None
            ),
            'max_participants': data.get('max_participants'),
            'format': data.get('format', 'Simple'),
            'game': data.get('game'),
            'rules': data.get('rules'),
            'prizes': data.get('prizes'),
            'address': data.get('address'),
            'organizer_id': current_user_id
        }

        tournament_id = tournament_dao.create(tournament_data)
        tournament = tournament_dao.get_by_id(tournament_id)

        return jsonify(tournament), 201
    except Exception as e:
        current_app.logger.error(f"Error creating tournament: {str(e)}")
        return jsonify({'error': str(e)}), 422

@bp.route("/<int:tournament_id>", methods=["PUT"])
@jwt_required()
def update_tournament(tournament_id):
    tournament = tournament_dao.get_by_id(tournament_id)
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404

    data = request.get_json()

    try:
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'start_date' in data:
            update_data['start_date'] = datetime.fromisoformat(
                data['start_date']
            )
        if 'end_date' in data:
            update_data['end_date'] = datetime.fromisoformat(data['end_date'])
        if 'registration_deadline' in data:
            update_data['registration_deadline'] = datetime.fromisoformat(
                data['registration_deadline']
            )
        if 'max_participants' in data:
            update_data['max_participants'] = data['max_participants']
        if 'status' in data:
            update_data['status'] = data['status']
        if 'format' in data:
            update_data['format'] = data['format']
        if 'game' in data:
            update_data['game'] = data['game']
        if 'rules' in data:
            update_data['rules'] = data['rules']
        if 'prizes' in data:
            update_data['prizes'] = data['prizes']
        if 'address' in data:
            update_data['address'] = data['address']

        tournament_dao.update(tournament_id, update_data)
        updated_tournament = tournament_dao.get_by_id(tournament_id)
        return jsonify(updated_tournament), 200
    except Exception as e:
        current_app.logger.error(f"Error updating tournament: {str(e)}")
        return jsonify({'error': str(e)}), 422

@bp.route("/<int:tournament_id>", methods=["DELETE"])
@jwt_required()
def delete_tournament(tournament_id):
    tournament = tournament_dao.get_by_id(tournament_id)
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404

    try:
        tournament_dao.delete(tournament_id)
        return jsonify({'message': 'Tournament deleted successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Error deleting tournament: {str(e)}")
        return jsonify({'error': str(e)}), 422

@bp.route("/<int:tournament_id>/register", methods=["POST"])
@jwt_required()
def register_to_tournament(tournament_id):
    current_user_id = int(get_jwt_identity())
    current_app.logger.info(
        f"Tentative d'inscription - User ID: {current_user_id}, "
        f"Tournament ID: {tournament_id}"
    )

    tournament = tournament_dao.get_by_id(tournament_id)
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404

    current_app.logger.info(f"Tournoi trouvé: {tournament['name']}")

    # Vérifier si l'utilisateur est déjà inscrit
    if registration_dao.get_by_user_and_tournament(
        current_user_id, tournament_id
    ):
        current_app.logger.info(
            f"L'utilisateur {current_user_id} est déjà inscrit au "
            f"tournoi {tournament_id}"
        )
        return jsonify({'error': 'Already registered'}), 400

    # Vérifier si le tournoi est complet
    if (tournament['max_participants'] and
            tournament['current_participants'] >=
            tournament['max_participants']):
        current_app.logger.info(f"Le tournoi {tournament_id} est complet")
        return jsonify({'error': 'Tournament is full'}), 400

    # Vérifier si la date limite d'inscription est dépassée
    if (tournament['registration_deadline'] and
            datetime.utcnow() > tournament['registration_deadline']):
        current_app.logger.info(
            f"La date limite d'inscription est dépassée pour le "
            f"tournoi {tournament_id}"
        )
        return jsonify({'error': 'Registration deadline has passed'}), 400

    try:
        registration_data = {
            'user_id': current_user_id,
            'tournament_id': tournament_id
        }
        registration_dao.create(registration_data)
        current_app.logger.info(
            f"Inscription réussie - User ID: {current_user_id}, "
            f"Tournament ID: {tournament_id}"
        )
        return jsonify({'message': 'Successfully registered'}), 201
    except Exception as e:
        current_app.logger.error(f"Error registering to tournament: {str(e)}")
        return jsonify({'error': str(e)}), 422

@bp.route("/<int:tournament_id>/unregister", methods=["POST"])
@jwt_required()
def unregister_from_tournament(tournament_id):
    current_user_id = int(get_jwt_identity())
    registration = registration_dao.get_by_user_and_tournament(
        current_user_id, tournament_id
    )
    if not registration:
        return jsonify({'error': 'Registration not found'}), 404

    try:
        registration_dao.delete(registration['id'])
        return jsonify({'message': 'Successfully unregistered'}), 200
    except Exception as e:
        current_app.logger.error(
            f"Error unregistering from tournament: {str(e)}"
        )
        return jsonify({'error': str(e)}), 422