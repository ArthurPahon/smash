from flask import Blueprint, jsonify, request
from app.models.match import Match, Bracket
from app import db
from flask_jwt_extended import jwt_required
from datetime import datetime
import json


bp = Blueprint('matches', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_matches():
    matches = Match.query.all()
    return jsonify([match.to_dict() for match in matches]), 200


@bp.route('/<int:match_id>', methods=['GET'])
@jwt_required()
def get_match(match_id):
    match = Match.query.get_or_404(match_id)
    return jsonify(match.to_dict()), 200


@bp.route('', methods=['POST'])
@jwt_required()
def create_match():
    data = request.get_json()

    match = Match(
        tournament_id=data['tournament_id'],
        player1_id=data['player1_id'],
        player2_id=data['player2_id'],
        round=data.get('round', 1),
        bracket_position=data.get('bracket_position', 0),
        status='pending',
        start_time=datetime.now()
    )

    db.session.add(match)
    db.session.commit()

    return jsonify(match.to_dict()), 201


@bp.route('/<int:match_id>', methods=['PUT'])
@jwt_required()
def update_match(match_id):
    match = Match.query.get_or_404(match_id)
    data = request.get_json()

    if 'winner_id' in data:
        match.winner_id = data['winner_id']
        match.status = 'finished'
        # Mise à jour du statut du tournoi si nécessaire
        tournament = match.tournament
        if tournament and tournament.status == 'in_progress':
            all_matches = Match.query.filter_by(tournament_id=tournament.id).all()
            if all(m.status == 'finished' for m in all_matches):
                tournament.status = 'finished'
                db.session.commit()
    if 'score' in data:
        try:
            score_data = data['score']
            if not isinstance(score_data, dict):
                return jsonify({
                    'error': 'Le score doit être un objet avec les clés player1 et player2'
                }), 400

            if 'player1' not in score_data or 'player2' not in score_data:
                return jsonify({
                    'error': 'Le score doit contenir les clés player1 et player2'
                }), 400

            match.score = json.dumps(score_data)
        except Exception as e:
            return jsonify({
                'error': f'Format de score invalide: {str(e)}'
            }), 400
    if 'status' in data:
        match.status = data['status']
    if 'end_time' in data:
        match.end_time = datetime.now()

    db.session.commit()
    return jsonify(match.to_dict()), 200


@bp.route('/brackets', methods=['GET'])
@jwt_required()
def get_brackets():
    brackets = Bracket.query.all()
    return jsonify([bracket.to_dict() for bracket in brackets]), 200


@bp.route('/brackets/<int:bracket_id>', methods=['GET'])
@jwt_required()
def get_bracket(bracket_id):
    bracket = Bracket.query.get_or_404(bracket_id)
    return jsonify(bracket.to_dict()), 200