from datetime import datetime

from app import db


class Tournament(db.Model):
    __tablename__ = "tournoi"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    date_debut = db.Column(db.DateTime, nullable=False)
    date_fin = db.Column(db.DateTime, nullable=False)
    lieu = db.Column(db.String(100))
    description = db.Column(db.Text)
    format = db.Column(db.String(50))  # single, double, poules, etc.
    nb_places_max = db.Column(db.Integer)
    statut = db.Column(
        db.String(20), default="préparation"
    )  # préparation, en cours, terminé
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    phases = db.relationship("Phase", backref="tournoi", lazy="dynamic")
    matchs = db.relationship("Match", backref="tournoi", lazy="dynamic")
    inscriptions = db.relationship("Registration", backref="tournoi",
                                   lazy="dynamic")
    classements = db.relationship("Ranking", backref="tournoi", lazy="dynamic")

    def __init__(
        self,
        nom,
        date_debut,
        date_fin,
        lieu=None,
        description=None,
        format=None,
        nb_places_max=None,
    ):
        self.nom = nom
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.lieu = lieu
        self.description = description
        self.format = format
        self.nb_places_max = nb_places_max

    def to_dict(self):
        """Convertir le tournoi en dictionnaire"""
        return {
            "id": self.id,
            "nom": self.nom,
            "date_debut": self.date_debut.isoformat() if self.date_debut else None,
            "date_fin": self.date_fin.isoformat() if self.date_fin else None,
            "lieu": self.lieu,
            "description": self.description,
            "format": self.format,
            "nb_places_max": self.nb_places_max,
            "statut": self.statut,
            "date_creation": (
                self.date_creation.isoformat() if self.date_creation else None
            ),
            "nb_inscrits": self.inscriptions.count(),
        }

    def get_organisateurs(self):
        """Récupérer les organisateurs du tournoi"""
        from app.models.user import Role, User, user_role

        organisateur_role = Role.query.filter_by(nom="organisateur").first()
        if not organisateur_role:
            return []

        return (
            User.query.join(user_role)
            .filter(
                user_role.c.role_id == organisateur_role.id,
                user_role.c.tournoi_id == self.id,
            )
            .all()
        )

    def is_registration_open(self):
        """Vérifier si les inscriptions sont ouvertes"""
        return self.statut == "préparation" and (
            self.nb_places_max is None or self.inscriptions.count() < self.nb_places_max
        )


class Phase(db.Model):
    __tablename__ = "phase"

    id = db.Column(db.Integer, primary_key=True)
    tournoi_id = db.Column(db.Integer, db.ForeignKey("tournoi.id"),
                           nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    ordre = db.Column(db.Integer, nullable=False)
    format = db.Column(db.String(50))  # round-robin, single elim, double elim

    # Relations
    matchs = db.relationship("Match", backref="phase", lazy="dynamic")

    def __init__(self, tournoi_id, nom, ordre, format=None):
        self.tournoi_id = tournoi_id
        self.nom = nom
        self.ordre = ordre
        self.format = format

    def to_dict(self):
        """Convertir la phase en dictionnaire"""
        return {
            "id": self.id,
            "tournoi_id": self.tournoi_id,
            "nom": self.nom,
            "ordre": self.ordre,
            "format": self.format,
        }


class Registration(db.Model):
    __tablename__ = "inscription"

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(
        db.Integer, db.ForeignKey("utilisateur.id"), nullable=False
    )
    tournoi_id = db.Column(db.Integer, db.ForeignKey("tournoi.id"),
                           nullable=False)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(
        db.String(20), default="confirmé"
    )  # confirmé, annulé, liste d'attente
    seed = db.Column(db.Integer)  # Classement initial

    def __init__(self, utilisateur_id, tournoi_id, statut="confirmé",
                 seed=None):
        self.utilisateur_id = utilisateur_id
        self.tournoi_id = tournoi_id
        self.statut = statut
        self.seed = seed

    def to_dict(self):
        """Convertir l'inscription en dictionnaire"""
        return {
            "id": self.id,
            "utilisateur_id": self.utilisateur_id,
            "tournoi_id": self.tournoi_id,
            "date_inscription": (
                self.date_inscription.isoformat() if self.date_inscription else None
            ),
            "statut": self.statut,
            "seed": self.seed,
        }
