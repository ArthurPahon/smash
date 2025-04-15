from app import db


class Character(db.Model):
    __tablename__ = "characters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    game = db.Column(db.String(50), nullable=False)  # Ultimate, Melee, etc.
    image_url = db.Column(db.String(255))

    # Relations
    users = db.relationship(
        'User',
        secondary='user_characters',
        backref=db.backref('favorite_characters', lazy='dynamic')
    )
    matches = db.relationship(
        'Match',
        secondary='match_characters',
        back_populates='characters'
    )

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
        # Pour l'instant, retourner des statistiques fictives
        # TODO: Implémenter la logique de statistiques réelle
        return {
            "total_matches": 0,
            "wins": 0,
            "win_rate": 0,
        }


# Tables d'association pour les relations many-to-many
user_characters = db.Table(
    'user_characters',
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    ),
    db.Column(
        'character_id',
        db.Integer,
        db.ForeignKey('characters.id', ondelete='CASCADE'),
        primary_key=True
    )
)

match_characters = db.Table(
    'match_characters',
    db.Column(
        'match_id',
        db.Integer,
        db.ForeignKey('matches.id'),
        primary_key=True
    ),
    db.Column(
        'character_id',
        db.Integer,
        db.ForeignKey('characters.id'),
        primary_key=True
    ),
    db.Column(
        'player_id',
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
)
