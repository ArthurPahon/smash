from datetime import datetime
from app import db


class Tournament(db.Model):
    __tablename__ = 'tournaments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    registration_deadline = db.Column(db.DateTime, nullable=True)
    max_participants = db.Column(db.Integer)
    current_participants = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, ongoing, completed, cancelled
    format = db.Column(
        db.String(20),
        default='single_elimination'
    )  # single_elimination, double_elimination, round_robin
    rules = db.Column(db.Text)
    prize_pool = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relations
    organizer_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    organizer = db.relationship(
        'User',
        backref=db.backref('organized_tournaments', lazy=True),
        lazy='joined'
    )
    registrations = db.relationship(
        'Registration',
        back_populates='tournament'
    )
    matches = db.relationship('Match', back_populates='tournament', lazy=True)
    brackets = db.relationship('Bracket', back_populates='tournament', lazy=True)
    rankings = db.relationship('Ranking', back_populates='tournament')

    def __init__(
        self,
        name,
        start_date,
        end_date,
        registration_deadline,
        organizer_id,
        **kwargs
    ):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.registration_deadline = registration_deadline
        self.organizer_id = organizer_id
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'registration_deadline': (
                self.registration_deadline.isoformat()
                if self.registration_deadline else None
            ),
            'max_participants': self.max_participants,
            'current_participants': self.current_participants,
            'status': self.status,
            'format': self.format,
            'rules': self.rules,
            'prize_pool': self.prize_pool,
            'organizer': {
                'id': self.organizer.id,
                'name': self.organizer.name
            } if self.organizer else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'registrations': [{
                'id': reg.id,
                'user_id': reg.user_id,
                'tournament_id': reg.tournament_id,
                'registration_date': reg.registration_date.isoformat() if reg.registration_date else None,
                'status': reg.status,
                'seed': reg.seed
            } for reg in self.registrations]
        }