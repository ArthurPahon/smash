from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Match, Tournament, User


bp = Blueprint("matches", __name__)


@bp.route("/tournaments/<int:tournament_id>/matches", methods=["GET"])
@jwt_required()
def get_matches(tournament_id):
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Filters
    round = request.args.get('round', type=int)
    status = request.args.get('status', '')

    query = Match.query.filter_by(tournament_id=tournament_id)
    if round is not None:
        query = query.filter_by(round=round)
    if status:
        query = query.filter_by(status=status)

    pagination = query.paginate(page=page, per_page=per_page)
    matches = pagination.items

    return jsonify({
        'matches': [{
            'id': m.id,
            'tournament_id': m.tournament_id,
            'round': m.round,
            'player1_id': m.player1_id,
            'player2_id': m.player2_id,
            'winner_id': m.winner_id,
            'score': m.score,
            'status': m.status,
            'scheduled_time': m.scheduled_time.isoformat() if m.scheduled_time else None,
            'player1': {
                'id': m.player1.id,
                'name': m.player1.name,
                'profile_picture': m.player1.profile_picture
            } if m.player1 else None,
            'player2': {
                'id': m.player2.id,
                'name': m.player2.name,
                'profile_picture': m.player2.profile_picture
            } if m.player2 else None,
            'winner': {
                'id': m.winner.id,
                'name': m.winner.name,
                'profile_picture': m.winner.profile_picture
            } if m.winner else None
        } for m in matches],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@bp.route("/matches/<int:match_id>", methods=["GET"])
@jwt_required()
def get_match(match_id):
    match = Match.query.get_or_404(match_id)

    return jsonify({
        'id': match.id,
        'tournament_id': match.tournament_id,
        'round': match.round,
        'player1_id': match.player1_id,
        'player2_id': match.player2_id,
        'winner_id': match.winner_id,
        'score': match.score,
        'status': match.status,
        'scheduled_time': match.scheduled_time.isoformat() if match.scheduled_time else None,
        'player1': {
            'id': match.player1.id,
            'name': match.player1.name,
            'profile_picture': match.player1.profile_picture
        } if match.player1 else None,
        'player2': {
            'id': match.player2.id,
            'name': match.player2.name,
            'profile_picture': match.player2.profile_picture
        } if match.player2 else None,
        'winner': {
            'id': match.winner.id,
            'name': match.winner.name,
            'profile_picture': match.winner.profile_picture
        } if match.winner else None
    }), 200


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
    match = Match(
        tournament_id=tournament_id,
        round=data['round'],
        player1_id=data['player1_id'],
        player2_id=data['player2_id'],
        status='scheduled',
        scheduled_time=datetime.fromisoformat(data['scheduled_time']) if 'scheduled_time' in data else None
    )

    db.session.add(match)
    db.session.commit()

    return jsonify({
        'id': match.id,
        'tournament_id': match.tournament_id,
        'round': match.round,
        'player1_id': match.player1_id,
        'player2_id': match.player2_id,
        'winner_id': match.winner_id,
        'score': match.score,
        'status': match.status,
        'scheduled_time': match.scheduled_time.isoformat() if match.scheduled_time else None
    }), 201


@bp.route("/matches/<int:match_id>", methods=["PUT"])
@jwt_required()
def update_match(match_id):
    current_user_id = int(get_jwt_identity())
    match = Match.query.get_or_404(match_id)
    data = request.get_json()

    # Update fields
    if 'round' in data:
        match.round = data['round']
    if 'player1_id' in data:
        match.player1_id = data['player1_id']
    if 'player2_id' in data:
        match.player2_id = data['player2_id']
    if 'winner_id' in data:
        match.winner_id = data['winner_id']
    if 'score' in data:
        match.score = data['score']
    if 'status' in data:
        if data['status'] not in ['scheduled', 'in_progress', 'completed', 'cancelled']:
            return jsonify({'error': 'Invalid status'}), 400
        match.status = data['status']
    if 'scheduled_time' in data:
        match.scheduled_time = datetime.fromisoformat(data['scheduled_time'])

    db.session.commit()

    return jsonify({
        'id': match.id,
        'tournament_id': match.tournament_id,
        'round': match.round,
        'player1_id': match.player1_id,
        'player2_id': match.player2_id,
        'winner_id': match.winner_id,
        'score': match.score,
        'status': match.status,
        'scheduled_time': match.scheduled_time.isoformat() if match.scheduled_time else None
    }), 200


@bp.route("/matches/<int:match_id>", methods=["DELETE"])
@jwt_required()
def delete_match(match_id):
    current_user_id = int(get_jwt_identity())
    match = Match.query.get_or_404(match_id)

    db.session.delete(match)
    db.session.commit()

    return jsonify({'message': 'Match deleted successfully'}), 200