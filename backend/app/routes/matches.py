from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.dao import MatchDAO


bp = Blueprint("matches", __name__)
match_dao = MatchDAO()


@bp.route("/tournaments/<int:tournament_id>/matches", methods=["GET"])
@jwt_required()
def get_matches(tournament_id):
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Filters
    round = request.args.get('round', type=int)
    status = request.args.get('status', '')

    matches = match_dao.get_by_tournament(tournament_id, page=page, per_page=per_page)
    if round is not None:
        matches = [m for m in matches if m['round'] == round]
    if status:
        matches = [m for m in matches if m['status'] == status]

    return jsonify({
        'matches': matches,
        'current_page': page
    }), 200


@bp.route("/matches/<int:match_id>", methods=["GET"])
@jwt_required()
def get_match(match_id):
    match = match_dao.get_by_id(match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404

    return jsonify(match), 200


@bp.route("/tournaments/<int:tournament_id>/matches", methods=["POST"])
@jwt_required()
def create_match(tournament_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    # Validate required fields
    required_fields = ['round', 'player1_id', 'player2_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Create match
    match_data = {
        'tournament_id': tournament_id,
        'round': data['round'],
        'player1_id': data['player1_id'],
        'player2_id': data['player2_id'],
        'status': 'scheduled',
        'scheduled_time': (
            datetime.fromisoformat(data['scheduled_time'])
            if 'scheduled_time' in data
            else None
        )
    }

    match_id = match_dao.create(match_data)
    match = match_dao.get_by_id(match_id)

    return jsonify(match), 201


@bp.route("/matches/<int:match_id>", methods=["PUT"])
@jwt_required()
def update_match(match_id):
    current_user_id = int(get_jwt_identity())
    match = match_dao.get_by_id(match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404

    data = request.get_json()
    update_data = {}

    # Update fields
    if 'round' in data:
        update_data['round'] = data['round']
    if 'player1_id' in data:
        update_data['player1_id'] = data['player1_id']
    if 'player2_id' in data:
        update_data['player2_id'] = data['player2_id']
    if 'winner_id' in data:
        update_data['winner_id'] = data['winner_id']
    if 'score' in data:
        update_data['score'] = data['score']
    if 'status' in data:
        if data['status'] not in ['scheduled', 'in_progress', 'completed', 'cancelled']:
            return jsonify({'error': 'Invalid status'}), 400
        update_data['status'] = data['status']
    if 'scheduled_time' in data:
        update_data['scheduled_time'] = datetime.fromisoformat(data['scheduled_time'])

    match_dao.update(match_id, update_data)
    updated_match = match_dao.get_by_id(match_id)

    return jsonify(updated_match), 200


@bp.route("/matches/<int:match_id>", methods=["DELETE"])
@jwt_required()
def delete_match(match_id):
    current_user_id = int(get_jwt_identity())
    match = match_dao.get_by_id(match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404

    match_dao.delete(match_id)
    return jsonify({'message': 'Match deleted successfully'}), 200