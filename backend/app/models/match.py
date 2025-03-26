from app import db


class Match(db.Model):
    __tablename__ = "match"

    id = db.Column(db.Integer, primary_key=True)
    phase_id = db.Column(db.Integer, db.ForeignKey("phase.id"), nullable=False)
    tournoi_id = db.Column(db.Integer, db.ForeignKey("tournoi.id"),
                           nullable=False)
    round = db.Column(db.Integer, nullable=False)
    heure_prevue = db.Column(db.DateTime)
    statut = db.Column(db.String(20), default="à venir")  # à venir, en cours, terminé

    # Relations
    participants = db.relationship("MatchParticipant", backref="match", lazy="dynamic")

    def __init__(
        self, phase_id, tournoi_id, round, heure_prevue=None, statut="à venir"
    ):
        self.phase_id = phase_id
        self.tournoi_id = tournoi_id
        self.round = round
        self.heure_prevue = heure_prevue
        self.statut = statut

    def to_dict(self):
        """Convertir le match en dictionnaire"""
        return {
            "id": self.id,
            "phase_id": self.phase_id,
            "tournoi_id": self.tournoi_id,
            "round": self.round,
            "heure_prevue": (
                self.heure_prevue.isoformat() if self.heure_prevue else None
            ),
            "statut": self.statut,
            "participants": [p.to_dict() for p in self.participants],
        }

    def add_participant(self, utilisateur_id, personnage_id=None, score=0):
        """Ajouter un participant au match"""
        participant = MatchParticipant(
            match_id=self.id,
            utilisateur_id=utilisateur_id,
            personnage_id=personnage_id,
            score=score,
        )
        db.session.add(participant)
        db.session.commit()
        return participant

    def update_score(self, utilisateur_id, score):
        """Mettre à jour le score d'un participant"""
        participant = self.participants.filter_by(utilisateur_id=utilisateur_id).first()
        if participant:
            participant.score = score
            db.session.commit()
            return True
        return False

    def declare_winner(self, utilisateur_id):
        """Déclarer un vainqueur pour le match"""
        # Réinitialiser tous les vainqueurs
        for p in self.participants:
            p.vainqueur = False

        # Définir le nouveau vainqueur
        participant = self.participants.filter_by(utilisateur_id=utilisateur_id).first()
        if participant:
            participant.vainqueur = True
            self.statut = "terminé"
            db.session.commit()
            return True
        return False


class MatchParticipant(db.Model):
    __tablename__ = "participant_match"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"), nullable=False)
    utilisateur_id = db.Column(
        db.Integer, db.ForeignKey("utilisateur.id"), nullable=False
    )
    personnage_id = db.Column(db.Integer, db.ForeignKey("personnage.id"))
    score = db.Column(db.Integer, default=0)
    vainqueur = db.Column(db.Boolean, default=False)

    def __init__(
        self, match_id, utilisateur_id, personnage_id=None, score=0,
        vainqueur=False
    ):
        self.match_id = match_id
        self.utilisateur_id = utilisateur_id
        self.personnage_id = personnage_id
        self.score = score
        self.vainqueur = vainqueur

    def to_dict(self):
        """Convertir le participant en dictionnaire"""
        return {
            "id": self.id,
            "match_id": self.match_id,
            "utilisateur_id": self.utilisateur_id,
            "personnage_id": self.personnage_id,
            "score": self.score,
            "vainqueur": self.vainqueur,
        }
