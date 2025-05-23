from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db
from app.models import Ranking, Tournament, User, Match, Registration


bp = Blueprint('rankings', __name__)

# Configuration des points
POINTS_CONFIG = {
    'victory': 3,
    'defeat': 0,
    'bye': 1
}


@bp.route('', methods=['GET'])
@jwt_required()
def get_global_rankings():
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Récupération des utilisateurs avec leur nombre de victoires
    query = db.session.query(
        User,
        db.func.count(Ranking.id).label('tournaments_participated'),
        db.func.avg(Ranking.rank).label('average_rank')
    ).join(
        Ranking, User.id == Ranking.user_id
    ).group_by(
        User.id
    ).order_by(
        db.func.avg(Ranking.rank).asc()
    )

    pagination = query.paginate(page=page, per_page=per_page)
    rankings = pagination.items

    return jsonify({
        'rankings': [{
            'user': {
                'id': r[0].id,
                'name': r[0].name,
                'profile_picture': r[0].profile_picture
            },
            'tournaments_participated': r[1],
            'average_rank': float(r[2]) if r[2] else None
        } for r in rankings],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@bp.route('/tournaments/<int:tournament_id>', methods=['GET'])
def get_tournament_rankings(tournament_id):
    # Vérification si le tournoi existe
    tournament = Tournament.query.get_or_404(tournament_id)

    # Récupération des classements du tournoi
    rankings = Ranking.query.filter_by(
        tournament_id=tournament_id
    ).order_by(
        Ranking.rank.asc()
    ).all()

    return jsonify({
        'tournament': {
            'id': tournament.id,
            'name': tournament.name,
            'start_date': tournament.start_date.isoformat(),
            'end_date': tournament.end_date.isoformat()
        },
        'rankings': [{
            'rank': r.rank,
            'user': {
                'id': r.user.id,
                'name': r.user.name,
                'profile_picture': r.user.profile_picture
            }
        } for r in rankings]
    }), 200


@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_rankings(user_id):
    # Vérification si l'utilisateur existe
    user = User.query.get_or_404(user_id)

    # Récupération des classements de l'utilisateur
    rankings = Ranking.query.filter_by(
        user_id=user_id
    ).order_by(
        Ranking.rank.asc()
    ).all()

    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'profile_picture': user.profile_picture
        },
        'rankings': [{
            'tournament': {
                'id': r.tournament.id,
                'name': r.tournament.name,
                'start_date': r.tournament.start_date.isoformat(),
                'end_date': r.tournament.end_date.isoformat()
            },
            'rank': r.rank
        } for r in rankings]
    }), 200


@bp.route('/tournaments/<int:tournament_id>/calculate', methods=['POST'])
def calculate_tournament_rankings(tournament_id):
    # Vérification si le tournoi existe
    tournament = Tournament.query.get_or_404(tournament_id)

    # Vérification si le tournoi est terminé
    if tournament.status != 'finished':
        return jsonify({
            'error': ('Le classement ne peut être calculé que pour un '
                     'tournoi terminé')
        }), 400

    # Récupération des matchs du tournoi
    matches = Match.query.filter_by(
        tournament_id=tournament_id,
        winner_id=None
    ).all()

    if matches:
        error_msg = ('Tous les matchs doivent être terminés pour '
                    'calculer le classement')
        return jsonify({'error': error_msg}), 400

    # Récupération des inscriptions au tournoi
    registrations = Registration.query.filter_by(
        tournament_id=tournament_id,
        status='confirmed'
    ).all()

    # Création d'un dictionnaire pour stocker les points de chaque joueur
    points = {r.user_id: 0 for r in registrations}

    # Calcul des points pour chaque match
    for match in matches:
        if match.winner_id:
            winner = match.winner_id
            loser = match.player2_id if match.player1_id == winner else match.player1_id

            # Attribution des points
            winner_points = POINTS_CONFIG['victory']
            loser_points = POINTS_CONFIG['defeat']

            # Mise à jour ou création du classement pour le gagnant
            winner_ranking = Ranking.query.filter_by(
                user_id=winner,
                tournament_id=tournament_id
            ).first()

            if not winner_ranking:
                winner_ranking = Ranking(
                    user_id=winner,
                    tournament_id=tournament_id,
                    points=winner_points
                )
                db.session.add(winner_ranking)
            else:
                winner_ranking.points += winner_points

            # Mise à jour ou création du classement pour le perdant
            loser_ranking = Ranking.query.filter_by(
                user_id=loser,
                tournament_id=tournament_id
            ).first()

            if not loser_ranking:
                loser_ranking = Ranking(
                    user_id=loser,
                    tournament_id=tournament_id,
                    points=loser_points
                )
                db.session.add(loser_ranking)
            else:
                loser_ranking.points += loser_points

    # Création des classements
    rankings = []
    for user_id, score in points.items():
        ranking = Ranking(
            user_id=user_id,
            tournament_id=tournament_id,
            points=score,
            rank=0  # Sera mis à jour après le tri
        )
        rankings.append(ranking)

    # Tri des classements par points décroissants
    rankings.sort(key=lambda x: x.points, reverse=True)

    # Attribution des rangs
    for i, ranking in enumerate(rankings, 1):
        ranking.rank = i

    # Suppression des anciens classements
    Ranking.query.filter_by(tournament_id=tournament_id).delete()

    # Ajout des nouveaux classements
    db.session.add_all(rankings)
    db.session.commit()

    return jsonify({
        'message': 'Classement calculé avec succès',
        'rankings': [{
            'rank': r.rank,
            'points': r.points,
            'user': {
                'id': r.user.id,
                'name': r.user.name,
                'profile_picture': r.user.profile_picture
            }
        } for r in rankings]
    }), 200