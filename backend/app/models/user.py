from datetime import datetime

import bcrypt

from app import db

# Table d'association pour la relation utilisateur-rôle
user_role = db.Table(
    "utilisateur_role",
    db.Column(
        "utilisateur_id", db.Integer, db.ForeignKey("utilisateur.id"), primary_key=True
    ),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
    db.Column("tournoi_id", db.Integer, db.ForeignKey("tournoi.id")),
)


class User(db.Model):
    __tablename__ = "utilisateur"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(100), nullable=False)
    photo_profil = db.Column(db.String(255))
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relations
    roles = db.relationship(
        "Role", secondary=user_role, backref=db.backref("utilisateurs", lazy="dynamic")
    )
    inscriptions = db.relationship(
        "Registration", backref="utilisateur", lazy="dynamic"
    )
    participations = db.relationship(
        "MatchParticipant", backref="utilisateur", lazy="dynamic"
    )
    classements = db.relationship("Ranking", backref="utilisateur", lazy="dynamic")

    def __init__(self, nom, email, mot_de_passe, photo_profil=None):
        self.nom = nom
        self.email = email
        self.set_password(mot_de_passe)
        self.photo_profil = photo_profil

    def set_password(self, mot_de_passe):
        """Hachage et stockage du mot de passe"""
        self.mot_de_passe = bcrypt.hashpw(
            mot_de_passe.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, mot_de_passe):
        """Vérification du mot de passe"""
        return bcrypt.checkpw(
            mot_de_passe.encode("utf-8"), self.mot_de_passe.encode("utf-8")
        )

    def has_role(self, role_name, tournoi_id=None):
        """Vérification si l'utilisateur a un rôle spécifique"""
        for role in self.roles:
            if role.nom == role_name:
                # Vérifier si le rôle est lié à un tournoi spécifique
                if tournoi_id:
                    assoc = (
                        db.session.query(user_role)
                        .filter_by(
                            utilisateur_id=self.id,
                            role_id=role.id,
                            tournoi_id=tournoi_id,
                        )
                        .first()
                    )
                    return assoc is not None
                return True
        return False

    def to_dict(self):
        """Convertir l'utilisateur en dictionnaire"""
        return {
            "id": self.id,
            "nom": self.nom,
            "email": self.email,
            "photo_profil": self.photo_profil,
            "date_inscription": (
                self.date_inscription.isoformat() if self.date_inscription else None
            ),
            "is_active": self.is_active,
        }


class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __init__(self, nom, description=None):
        self.nom = nom
        self.description = description

    def to_dict(self):
        """Convertir le rôle en dictionnaire"""
        return {"id": self.id, "nom": self.nom, "description": self.description}
