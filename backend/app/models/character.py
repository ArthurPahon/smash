from app import db


class Character(db.Model):
    __tablename__ = "character"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    game = db.Column(db.String(50), nullable=False)  # Ultimate, Melee, etc.
    image_url = db.Column(db.String(255))

    def __init__(self, name, game, image_url=None):
        self.name = name
        self.game = game
        self.image_url = image_url

    def to_dict(self):
        """Convert character to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "game": self.game,
            "image_url": self.image_url,
        }

    def get_usage_stats(self):
        """Get character usage statistics"""
        from app.models import Match
        total_matches = Match.query.filter(
            (Match.character1_id == self.id) | (Match.character2_id == self.id)
        ).count()
        wins = Match.query.filter(
            ((Match.character1_id == self.id) & (Match.winner_id == Match.player1_id)) |
            ((Match.character2_id == self.id) & (Match.winner_id == Match.player2_id))
        ).count()
        win_rate = (wins / total_matches) * 100 if total_matches > 0 else 0

        return {
            "total_matches": total_matches,
            "wins": wins,
            "win_rate": win_rate,
        }
