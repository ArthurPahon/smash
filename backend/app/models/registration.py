from datetime import datetime
from app import db


class Registration(db.Model):
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey('tournaments.id'), nullable=False
    )
    registration_date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    status = db.Column(db.String(20), default='registered')  # registered, cancelled
    seed = db.Column(db.Integer)  # Pour le placement dans le bracket

    # Relations
    user = db.relationship('User', back_populates='registrations')
    tournament = db.relationship('Tournament', back_populates='registrations')

    def __init__(self, user_id, tournament_id, **kwargs):
        self.user_id = user_id
        self.tournament_id = tournament_id
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tournament_id': self.tournament_id,
            'registration_date': self.registration_date.isoformat(),
            'status': self.status,
            'seed': self.seed
        }