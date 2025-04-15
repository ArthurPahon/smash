from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Registration, Tournament, User

bp = Blueprint('registrations', __name__)

@bp.route('/tournaments/<int:tournament_id>/registrations', methods=['GET'])
@jwt_required()
def get_tournament_registrations(tournament_id):
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Filters
    status = request.args.get('status', '')

    query = Registration.query.filter_by(tournament_id=tournament_id)
    if status:
        query = query.filter_by(status=status)

    pagination = query.paginate(page=page, per_page=per_page)
    registrations = pagination.items

    return jsonify({
        'registrations': [{
            'id': r.id,
            'user_id': r.user_id,
            'tournament_id': r.tournament_id,
            'registration_date': r.registration_date.isoformat(),
            'status': r.status,
            'seed': r.seed,
            'user': {
                'id': r.user.id,
                'name': r.user.name,
                'profile_picture': r.user.profile_picture
            }
        } for r in registrations],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@bp.route('/tournaments/<int:tournament_id>/registrations', methods=['POST'])
@jwt_required()
def register_for_tournament(tournament_id):
    current_user_id = int(get_jwt_identity())

    # Check if tournament exists
    tournament = Tournament.query.get_or_404(tournament_id)

    # Check if user is already registered
    existing_registration = Registration.query.filter_by(
        user_id=current_user_id,
        tournament_id=tournament_id
    ).first()

    if existing_registration:
        return jsonify({'error': 'You are already registered for this tournament'}), 400

    # Create registration
    registration = Registration(
        user_id=current_user_id,
        tournament_id=tournament_id,
        registration_date=datetime.utcnow(),
        status='confirmed'
    )

    db.session.add(registration)
    db.session.commit()

    return jsonify({
        'id': registration.id,
        'user_id': registration.user_id,
        'tournament_id': registration.tournament_id,
        'registration_date': registration.registration_date.isoformat(),
        'status': registration.status,
        'seed': registration.seed
    }), 201

@bp.route('/registrations/<int:registration_id>', methods=['GET'])
@jwt_required()
def get_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)

    return jsonify({
        'id': registration.id,
        'user_id': registration.user_id,
        'tournament_id': registration.tournament_id,
        'registration_date': registration.registration_date.isoformat(),
        'status': registration.status,
        'seed': registration.seed,
        'user': {
            'id': registration.user.id,
            'name': registration.user.name,
            'profile_picture': registration.user.profile_picture
        },
        'tournament': {
            'id': registration.tournament.id,
            'name': registration.tournament.name,
            'start_date': registration.tournament.start_date.isoformat(),
            'end_date': registration.tournament.end_date.isoformat()
        }
    }), 200

@bp.route('/registrations/<int:registration_id>', methods=['PUT'])
@jwt_required()
def update_registration(registration_id):
    current_user_id = int(get_jwt_identity())
    registration = Registration.query.get_or_404(registration_id)

    # Permission check
    if registration.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    # Update fields
    if 'status' in data:
        if data['status'] not in ['confirmed', 'cancelled', 'waiting_list']:
            return jsonify({'error': 'Invalid status'}), 400
        registration.status = data['status']
    if 'seed' in data:
        registration.seed = data['seed']

    db.session.commit()

    return jsonify({
        'id': registration.id,
        'user_id': registration.user_id,
        'tournament_id': registration.tournament_id,
        'registration_date': registration.registration_date.isoformat(),
        'status': registration.status,
        'seed': registration.seed
    }), 200

@bp.route('/registrations/<int:registration_id>', methods=['DELETE'])
@jwt_required()
def cancel_registration(registration_id):
    current_user_id = int(get_jwt_identity())
    registration = Registration.query.get_or_404(registration_id)

    # Permission check
    if registration.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(registration)
    db.session.commit()

    return jsonify({'message': 'Registration cancelled successfully'}), 200