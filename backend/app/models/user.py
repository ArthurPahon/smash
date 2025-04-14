from datetime import datetime

import bcrypt

from app import db

# Association table for user-role relationship
user_role = db.Table(
    "user_role",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
    db.Column("tournament_id", db.Integer, db.ForeignKey("tournament.id")),
)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    country = db.Column(db.String(100))
    state = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    roles = db.relationship('Role', secondary=user_role, backref=db.backref('users', lazy='dynamic'))
    registrations = db.relationship('Registration', back_populates='user')
    matches_as_player1 = db.relationship('Match', foreign_keys='Match.player1_id', back_populates='player1')
    matches_as_player2 = db.relationship('Match', foreign_keys='Match.player2_id', back_populates='player2')
    matches_won = db.relationship('Match', foreign_keys='Match.winner_id', back_populates='winner')
    matches_lost = db.relationship('Match', foreign_keys='Match.loser_id', back_populates='loser')
    rankings = db.relationship('Ranking', back_populates='user')

    def __repr__(self):
        return f'<User {self.name}>'

    def __init__(self, name, email, password, profile_picture=None):
        self.name = name
        self.email = email
        self.set_password(password)
        self.profile_picture = profile_picture

    def set_password(self, password):
        """Hash and store the password"""
        self.password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password):
        """Verify the password"""
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password.encode("utf-8")
        )

    def has_role(self, role_name, tournament_id=None):
        """Check if user has a specific role"""
        for role in self.roles:
            if role.name == role_name:
                if tournament_id:
                    assoc = (
                        db.session.query(user_role)
                        .filter_by(
                            user_id=self.id,
                            role_id=role.id,
                            tournament_id=tournament_id,
                        )
                        .first()
                    )
                    return assoc is not None
                return True
        return False

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "registration_date": (
                self.registration_date.isoformat() if self.registration_date else None
            ),
            "country": self.country,
            "state": self.state,
            "is_active": self.is_active,
            "roles": [role.to_dict() for role in self.roles]
        }


class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def to_dict(self):
        """Convert role to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }
