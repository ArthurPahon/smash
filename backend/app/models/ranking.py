from datetime import datetime

from app import db


class Ranking(db.Model):
    __tablename__ = "classement"

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(
        db.Integer, db.ForeignKey("utilisateur.id"), nullable=False
    )
    tournoi_id = db.Column(
        db.Integer, db.ForeignKey("tournoi.id")
    )  # NULL pour classement global
    points = db.Column(db.Integer, default=0)
    rang = db.Column(db.Integer)
    date_mise_a_jour = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, utilisateur_id, points=0, rang=None, tournoi_id=None):
        self.utilisateur_id = utilisateur_id
        self.tournoi_id = tournoi_id
        self.points = points
        self.rang = rang

    def to_dict(self):
        """Convertir le classement en dictionnaire"""
        return {
            "id": self.id,
            "utilisateur_id": self.utilisateur_id,
            "tournoi_id": self.tournoi_id,
            "points": self.points,
            "rang": self.rang,
            "date_mise_a_jour": (
                self.date_mise_a_jour.isoformat() if self.date_mise_a_jour else None
            ),
        }

    @staticmethod
    def calculate_tournament_rankings(tournoi_id):
        """Calculer les classements pour un tournoi spécifique"""
        from app.models.match import Match

        # Supprimer les classements existants pour ce tournoi
        Ranking.query.filter_by(tournoi_id=tournoi_id).delete()

        # Récupérer tous les participants et leurs matchs
        matches = Match.query.filter_by(tournoi_id=tournoi_id, statut="terminé").all()

        # Calculer les points pour chaque joueur
        player_points = {}

        for match in matches:
            for participant in match.participants:
                user_id = participant.utilisateur_id

                if user_id not in player_points:
                    player_points[user_id] = 0

                # Ajouter des points pour chaque victoire
                if participant.vainqueur:
                    player_points[user_id] += 3

                # Ajouter des points pour chaque match joué
                player_points[user_id] += 1

        # Créer les enregistrements de classement
        rankings = []
        for user_id, points in player_points.items():
            ranking = Ranking(
                utilisateur_id=user_id, tournoi_id=tournoi_id, points=points
            )
            db.session.add(ranking)
            rankings.append(ranking)

        # Trier les classements par points
        rankings.sort(key=lambda r: r.points, reverse=True)

        # Attribuer les rangs
        for i, ranking in enumerate(rankings):
            ranking.rang = i + 1

        db.session.commit()
        return rankings

    @staticmethod
    def update_global_rankings():
        """Mettre à jour les classements globaux"""
        # Supprimer les classements globaux existants
        Ranking.query.filter_by(tournoi_id=None).delete()

        # Récupérer tous les utilisateurs qui ont participé à au moins un tournoi
        from sqlalchemy import func

        from app.models.tournament import Registration

        users_with_registrations = (
            db.session.query(
                Registration.utilisateur_id,
                func.count(Registration.id).label("tournament_count"),
            )
            .group_by(Registration.utilisateur_id)
            .all()
        )

        # Calculer les points globaux pour chaque utilisateur
        for user_id, _ in users_with_registrations:
            # Récupérer tous les classements de tournoi de l'utilisateur
            tournament_rankings = Ranking.query.filter(
                Ranking.utilisateur_id == user_id, Ranking.tournoi_id is not None
            ).all()

            # Calculer les points globaux
            total_points = sum(ranking.points for ranking in tournament_rankings)

            # Créer un nouveau classement global
            global_ranking = Ranking(
                utilisateur_id=user_id, tournoi_id=None, points=total_points
            )
            db.session.add(global_ranking)

        # Récupérer et trier tous les classements globaux
        global_rankings = Ranking.query.filter_by(tournoi_id=None).all()
        global_rankings.sort(key=lambda r: r.points, reverse=True)

        # Attribuer les rangs
        for i, ranking in enumerate(global_rankings):
            ranking.rang = i + 1

        db.session.commit()
        return global_rankings
