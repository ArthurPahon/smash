from app import db


class Character(db.Model):
    __tablename__ = "personnage"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    jeu = db.Column(db.String(50), nullable=False)  # Ultimate, Melee, etc.
    image_url = db.Column(db.String(255))

    # Relations
    participations = db.relationship(
        "MatchParticipant", backref="personnage", lazy="dynamic"
    )

    def __init__(self, nom, jeu, image_url=None):
        self.nom = nom
        self.jeu = jeu
        self.image_url = image_url

    def to_dict(self):
        """Convertir le personnage en dictionnaire"""
        return {
            "id": self.id,
            "nom": self.nom,
            "jeu": self.jeu,
            "image_url": self.image_url,
        }

    def get_usage_stats(self):
        """Obtenir les statistiques d'utilisation du personnage"""
        total_matches = self.participations.count()
        wins = self.participations.filter_by(vainqueur=True).count()
        win_rate = (wins / total_matches) * 100 if total_matches > 0 else 0

        return {"total_matches": total_matches, "wins": wins, "win_rate": win_rate}
