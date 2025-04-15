from datetime import datetime
from app import db

class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    loser_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    score = db.Column(db.String(50))  # Format: "2-1" ou similaire
    round = db.Column(db.Integer)  # Numéro du round dans le bracket
    bracket_position = db.Column(db.Integer)  # Position dans le bracket
    status = db.Column(db.String(20), default='pending')  # pending, ongoing, completed
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    # Relations
    tournament = db.relationship('Tournament', back_populates='matches')
    player1 = db.relationship('User', foreign_keys=[player1_id], back_populates='matches_as_player1')
    player2 = db.relationship('User', foreign_keys=[player2_id], back_populates='matches_as_player2')
    winner = db.relationship('User', foreign_keys=[winner_id], back_populates='matches_won')
    loser = db.relationship('User', foreign_keys=[loser_id], back_populates='matches_lost')
    characters = db.relationship(
        'Character',
        secondary='match_characters',
        back_populates='matches',
        lazy='dynamic'
    )

    def __init__(self, tournament_id, player1_id, player2_id, round, bracket_position, **kwargs):
        self.tournament_id = tournament_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.round = round
        self.bracket_position = bracket_position
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'player1': {
                'id': self.player1.id,
                'name': self.player1.name
            } if self.player1 else None,
            'player2': {
                'id': self.player2.id,
                'name': self.player2.name
            } if self.player2 else None,
            'winner': {
                'id': self.winner.id,
                'name': self.winner.name
            } if self.winner else None,
            'loser': {
                'id': self.loser.id,
                'name': self.loser.name
            } if self.loser else None,
            'score': self.score,
            'round': self.round,
            'bracket_position': self.bracket_position,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }

class Bracket(db.Model):
    __tablename__ = 'brackets'

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    type = db.Column(db.String(50))  # winners, losers (pour double elimination)
    round_count = db.Column(db.Integer)
    current_round = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='preparation')  # preparation, ongoing, completed

    # Relations
    tournament = db.relationship('Tournament', back_populates='brackets')

    def __init__(self, tournament_id, type, round_count, **kwargs):
        self.tournament_id = tournament_id
        self.type = type
        self.round_count = round_count
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'type': self.type,
            'round_count': self.round_count,
            'current_round': self.current_round,
            'status': self.status
        }