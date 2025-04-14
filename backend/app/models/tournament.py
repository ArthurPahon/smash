from datetime import datetime

from app import db
from app.models.user import user_role


class Tournament(db.Model):
    __tablename__ = "tournament"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    address = db.Column(db.String(255))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="preparation")  # preparation, ongoing, finished
    format = db.Column(db.String(50))  # single, double, poules, etc.
    nb_places_max = db.Column(db.Integer)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    registrations = db.relationship('Registration', back_populates='tournament')
    matches = db.relationship('Match', back_populates='tournament')
    bracket = db.relationship('Bracket', back_populates='tournament', uselist=False)
    rankings = db.relationship('Ranking', back_populates='tournament')
    user_roles = db.relationship(
        'User',
        secondary=user_role,
        backref=db.backref('tournaments', lazy='dynamic'),
        overlaps="roles,users"
    )

    def __repr__(self):
        return f'<Tournament {self.name}>'

    def __init__(
        self, name, start_date, end_date, address=None,
        description=None, status="preparation", format=None, nb_places_max=None
    ):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.address = address
        self.description = description
        self.status = status
        self.format = format
        self.nb_places_max = nb_places_max

    def to_dict(self):
        """Convert tournament to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "address": self.address,
            "description": self.description,
            "status": self.status,
            "format": self.format,
            "nb_places_max": self.nb_places_max,
            "date_creation": (
                self.date_creation.isoformat() if self.date_creation else None
            ),
            "nb_inscrits": self.registrations.count(),
        }

    def get_organisateurs(self):
        """Récupérer les organisateurs du tournoi"""
        from app.models.user import Role, User

        organisateur_role = Role.query.filter_by(name="organisateur").first()
        if not organisateur_role:
            return []

        return (
            User.query.join(user_role)
            .filter(
                user_role.c.role_id == organisateur_role.id,
                user_role.c.tournament_id == self.id,
            )
            .all()
        )

    def is_registration_open(self):
        """Vérifier si les inscriptions sont ouvertes"""
        return self.status == "preparation" and (
            self.nb_places_max is None or self.registrations.count() < self.nb_places_max
        )


class Phase(db.Model):
    __tablename__ = "phase"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournament.id"), nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    format = db.Column(db.String(50))  # round-robin, single elim, double elim

    # Relationships
    tournament = db.relationship('Tournament', backref='phases')
    matches = db.relationship('Match', back_populates='phase')

    def __init__(self, tournament_id, name, order, format=None):
        self.tournament_id = tournament_id
        self.name = name
        self.order = order
        self.format = format

    def to_dict(self):
        """Convert phase to dictionary"""
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "name": self.name,
            "order": self.order,
            "format": self.format,
        }


class Registration(db.Model):
    __tablename__ = "registration"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournament.id"), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="confirmed")  # confirmed, cancelled, waiting_list
    seed = db.Column(db.Integer)  # Initial ranking

    # Relationships
    user = db.relationship('User', back_populates='registrations')
    tournament = db.relationship('Tournament', back_populates='registrations')

    def __init__(
        self, user_id, tournament_id, status="confirmed",
        seed=None
    ):
        self.user_id = user_id
        self.tournament_id = tournament_id
        self.status = status
        self.seed = seed

    def to_dict(self):
        """Convert registration to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tournament_id": self.tournament_id,
            "registration_date": (
                self.registration_date.isoformat() if self.registration_date else None
            ),
            "status": self.status,
            "seed": self.seed
        }
