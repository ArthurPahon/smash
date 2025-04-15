from app import db


class Ranking(db.Model):
    __tablename__ = "rankings"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=0)
    matches_played = db.Column(db.Integer, default=0)
    matches_won = db.Column(db.Integer, default=0)
    matches_lost = db.Column(db.Integer, default=0)

    # Relationships
    tournament = db.relationship('Tournament', back_populates='rankings')
    user = db.relationship('User', back_populates='rankings')

    def __init__(
        self, tournament_id, user_id, rank,
        points=0, matches_played=0, matches_won=0, matches_lost=0
    ):
        self.tournament_id = tournament_id
        self.user_id = user_id
        self.rank = rank
        self.points = points
        self.matches_played = matches_played
        self.matches_won = matches_won
        self.matches_lost = matches_lost

    def to_dict(self):
        """Convert ranking to dictionary"""
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "user_id": self.user_id,
            "rank": self.rank,
            "points": self.points,
            "matches_played": self.matches_played,
            "matches_won": self.matches_won,
            "matches_lost": self.matches_lost
        }

    def calculate_points(self, match_result):
        """Calcule les points en fonction du résultat du match"""
        if match_result == 'win':
            self.points += 3
            self.matches_won += 1
        elif match_result == 'loss':
            self.points += 1
            self.matches_lost += 1
        self.matches_played += 1