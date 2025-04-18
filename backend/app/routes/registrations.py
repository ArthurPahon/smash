from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.dao import RegistrationDAO, TournamentDAO

bp = Blueprint('registrations', __name__)
registration_dao = RegistrationDAO()
tournament_dao = TournamentDAO()

@bp.route('/tournaments/<int:tournament_id>/registrations', methods=['GET'])
@jwt_required()
def get_tournament_registrations(tournament_id):
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Filters
    status = request.args.get('status', '')

    # Vérifier si le tournoi existe
    tournament = tournament_dao.get_by_id(tournament_id)
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404

    registrations = registration_dao.get_by_tournament(
        tournament_id,
        status=status,
        page=page,
        per_page=per_page
    )

    return jsonify({
        'registrations': registrations['items'],
        'total': registrations['total'],
        'pages': registrations['pages'],
        'current_page': page
    }), 200

@bp.route('/tournaments/<int:tournament_id>/registrations', methods=['POST'])
@jwt_required()
def register_for_tournament(tournament_id):
    current_user_id = int(get_jwt_identity())

    # Vérifier si le tournoi existe
    tournament = tournament_dao.get_by_id(tournament_id)
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404

    # Vérifier si l'utilisateur est déjà inscrit
    existing_registration = registration_dao.get_by_user_and_tournament(
        current_user_id,
        tournament_id
    )

    if existing_registration:
        return jsonify({
            'error': 'You are already registered for this tournament'
        }), 400

    try:
        # Créer l'inscription
        registration = registration_dao.create({
            'user_id': current_user_id,
            'tournament_id': tournament_id,
            'status': 'confirmed'
        })

        return jsonify(registration), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/registrations/<int:registration_id>', methods=['GET'])
@jwt_required()
def get_registration(registration_id):
    registration = registration_dao.get_by_id(registration_id)
    if not registration:
        return jsonify({'error': 'Registration not found'}), 404

    return jsonify(registration), 200

@bp.route('/registrations/<int:registration_id>', methods=['PUT'])
@jwt_required()
def update_registration(registration_id):
    current_user_id = int(get_jwt_identity())
    registration = registration_dao.get_by_id(registration_id)

    if not registration:
        return jsonify({'error': 'Registration not found'}), 404

    # Vérification des permissions
    if registration['user_id'] != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    update_data = {}

    # Mise à jour des champs
    if 'status' in data:
        if data['status'] not in ['confirmed', 'cancelled', 'waiting_list']:
            return jsonify({'error': 'Invalid status'}), 400
        update_data['status'] = data['status']
    if 'seed' in data:
        update_data['seed'] = data['seed']

    try:
        updated_registration = registration_dao.update(
            registration_id,
            update_data
        )
        return jsonify(updated_registration), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/registrations/<int:registration_id>', methods=['DELETE'])
@jwt_required()
def cancel_registration(registration_id):
    current_user_id = int(get_jwt_identity())
    registration = registration_dao.get_by_id(registration_id)

    if not registration:
        return jsonify({'error': 'Registration not found'}), 404

    # Vérification des permissions
    if registration['user_id'] != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        registration_dao.delete(registration_id)
        return jsonify({
            'message': 'Registration cancelled successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400