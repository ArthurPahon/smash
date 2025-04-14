from app import db


class Match(db.Model):
    __tablename__ = "match"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournament.id"), nullable=False
    )
    bracket_id = db.Column(
        db.Integer, db.ForeignKey("bracket.id"), nullable=False
    )
    phase_id = db.Column(db.Integer, db.ForeignKey("phase.id"))
    round = db.Column(db.Integer, nullable=False)
    match_number = db.Column(db.Integer, nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    player2_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    winner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    loser_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    score = db.Column(db.String(50))  # Format: "3-2"
    status = db.Column(
        db.String(20), default="pending"
    )  # pending, in_progress, completed
    scheduled_time = db.Column(db.DateTime)
    character1_id = db.Column(db.Integer, db.ForeignKey("character.id"))
    character2_id = db.Column(db.Integer, db.ForeignKey("character.id"))

    # Relationships
    tournament = db.relationship('Tournament', back_populates='matches')
    bracket = db.relationship('Bracket', back_populates='matches')
    phase = db.relationship('Phase', back_populates='matches')
    player1 = db.relationship('User', foreign_keys=[player1_id])
    player2 = db.relationship('User', foreign_keys=[player2_id])
    winner = db.relationship('User', foreign_keys=[winner_id])
    loser = db.relationship('User', foreign_keys=[loser_id])
    character1 = db.relationship('Character', foreign_keys=[character1_id])
    character2 = db.relationship('Character', foreign_keys=[character2_id])

    def __init__(
        self,
        tournament_id,
        bracket_id,
        round,
        match_number,
        phase_id=None,
        player1_id=None,
        player2_id=None,
        winner_id=None,
        loser_id=None,
        score=None,
        status="pending",
        scheduled_time=None,
        character1_id=None,
        character2_id=None
    ):
        self.tournament_id = tournament_id
        self.bracket_id = bracket_id
        self.phase_id = phase_id
        self.round = round
        self.match_number = match_number
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.winner_id = winner_id
        self.loser_id = loser_id
        self.score = score
        self.status = status
        self.scheduled_time = scheduled_time
        self.character1_id = character1_id
        self.character2_id = character2_id

    def to_dict(self):
        """Convert match to dictionary"""
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "bracket_id": self.bracket_id,
            "phase_id": self.phase_id,
            "round": self.round,
            "match_number": self.match_number,
            "player1_id": self.player1_id,
            "player2_id": self.player2_id,
            "winner_id": self.winner_id,
            "loser_id": self.loser_id,
            "score": self.score,
            "status": self.status,
            "scheduled_time": (
                self.scheduled_time.isoformat() if self.scheduled_time else None
            ),
            "character1_id": self.character1_id,
            "character2_id": self.character2_id
        }


class Bracket(db.Model):
    __tablename__ = "bracket"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournament.id"), nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    format = db.Column(db.String(50))  # round-robin, single elim, double elim

    # Relationships
    tournament = db.relationship('Tournament', back_populates='bracket')
    matches = db.relationship('Match', back_populates='bracket')

    def __init__(self, tournament_id, name, order, format=None):
        self.tournament_id = tournament_id
        self.name = name
        self.order = order
        self.format = format

    def to_dict(self):
        """Convert bracket to dictionary"""
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "name": self.name,
            "order": self.order,
            "format": self.format
        }
