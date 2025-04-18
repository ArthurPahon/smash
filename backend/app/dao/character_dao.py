"""
Module d'accès aux données pour les personnages.
"""

from app.database import Database


class CharacterDAO:
    """
    Classe d'accès aux données pour les personnages.
    """

    def __init__(self):
        """
        Initialise la classe CharacterDAO.
        """
        self.db = Database()

    def get_by_id(self, character_id):
        """
        Récupère un personnage par son ID.

        Args:
            character_id (int): L'ID du personnage

        Returns:
            dict: Les données du personnage ou None si non trouvé
        """
        query = """
        SELECT * FROM characters
        WHERE id = %s
        """
        result = self.db.execute_query(query, (character_id,))
        return result[0] if result else None

    def create(self, name, description, image_url, tier):
        """
        Crée un nouveau personnage.

        Args:
            name (str): Le nom du personnage
            description (str): La description du personnage
            image_url (str): L'URL de l'image du personnage
            tier (str): Le tier du personnage

        Returns:
            dict: Les données du personnage créé
        """
        query = """
        INSERT INTO characters (name, description, image_url, tier)
        VALUES (%s, %s, %s, %s)
        """
        params = (name, description, image_url, tier)
        character_id = self.db.execute_query(query, params, fetch=False)
        return self.get_by_id(character_id)

    def update(self, character_id, **kwargs):
        """
        Met à jour un personnage.

        Args:
            character_id (int): L'ID du personnage
            **kwargs: Les champs à mettre à jour

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        if not kwargs:
            return False

        set_clause = ", ".join([f"{k} = %s" for k in kwargs.keys()])
        query = f"UPDATE characters SET {set_clause} WHERE id = %s"
        params = list(kwargs.values()) + [character_id]

        self.db.execute_query(query, params, fetch=False)
        return True

    def delete(self, character_id):
        """
        Supprime un personnage.

        Args:
            character_id (int): L'ID du personnage

        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        query = "DELETE FROM characters WHERE id = %s"
        self.db.execute_query(query, (character_id,), fetch=False)
        return True

    def get_all(self, page=1, per_page=10):
        """
        Récupère tous les personnages.

        Args:
            page (int): Le numéro de la page
            per_page (int): Le nombre de personnages par page

        Returns:
            tuple: (personnages, total, pages)
        """
        offset = (page - 1) * per_page

        # Requête pour compter le total
        count_query = "SELECT COUNT(*) as total FROM characters"
        total_result = self.db.execute_query(count_query)
        total = total_result[0]["total"]
        pages = (total + per_page - 1) // per_page

        # Requête pour récupérer les personnages
        query = """
        SELECT * FROM characters
        ORDER BY name ASC
        LIMIT %s OFFSET %s
        """
        params = (per_page, offset)

        characters = self.db.execute_query(query, params)

        return characters, total, pages

    def get_by_tier(self, tier, page=1, per_page=10):
        """
        Récupère les personnages par tier.

        Args:
            tier (str): Le tier des personnages
            page (int): Le numéro de la page
            per_page (int): Le nombre de personnages par page

        Returns:
            tuple: (personnages, total, pages)
        """
        offset = (page - 1) * per_page

        # Requête pour compter le total
        count_query = """
        SELECT COUNT(*) as total FROM characters
        WHERE tier = %s
        """
        total_result = self.db.execute_query(count_query, (tier,))
        total = total_result[0]["total"]
        pages = (total + per_page - 1) // per_page

        # Requête pour récupérer les personnages
        query = """
        SELECT * FROM characters
        WHERE tier = %s
        ORDER BY name ASC
        LIMIT %s OFFSET %s
        """
        params = (tier, per_page, offset)

        characters = self.db.execute_query(query, params)

        return characters, total, pages

    def search(self, search_term, page=1, per_page=10):
        """
        Recherche des personnages par nom ou description.

        Args:
            search_term (str): Le terme de recherche
            page (int): Le numéro de la page
            per_page (int): Le nombre de personnages par page

        Returns:
            tuple: (personnages, total, pages)
        """
        offset = (page - 1) * per_page
        search_pattern = f"%{search_term}%"

        # Requête pour compter le total
        count_query = """
        SELECT COUNT(*) as total FROM characters
        WHERE name LIKE %s OR description LIKE %s
        """
        total_result = self.db.execute_query(count_query, (search_pattern, search_pattern))
        total = total_result[0]["total"]
        pages = (total + per_page - 1) // per_page

        # Requête pour récupérer les personnages
        query = """
        SELECT * FROM characters
        WHERE name LIKE %s OR description LIKE %s
        ORDER BY name ASC
        LIMIT %s OFFSET %s
        """
        params = (search_pattern, search_pattern, per_page, offset)

        characters = self.db.execute_query(query, params)

        return characters, total, pages

    def get_usage_statistics(self, character_id):
        """
        Récupère les statistiques d'utilisation d'un personnage.

        Args:
            character_id (int): L'ID du personnage

        Returns:
            dict: Les statistiques d'utilisation
        """
        # Statistiques globales
        global_query = """
        SELECT
            COUNT(*) as total_uses,
            COUNT(DISTINCT r.tournament_id) as tournaments_used,
            COUNT(DISTINCT r.user_id) as unique_users
        FROM registrations r
        WHERE r.character_id = %s
        """
        global_stats = self.db.execute_query(global_query, (character_id,))[0]

        # Utilisation par tournoi
        tournament_query = """
        SELECT
            t.name as tournament_name,
            COUNT(*) as uses,
            COUNT(DISTINCT r.user_id) as unique_users
        FROM registrations r
        JOIN tournaments t ON r.tournament_id = t.id
        WHERE r.character_id = %s
        GROUP BY t.id, t.name
        ORDER BY uses DESC
        """
        tournament_stats = self.db.execute_query(tournament_query, (character_id,))

        # Utilisation par utilisateur
        user_query = """
        SELECT
            u.name as user_name,
            COUNT(*) as uses,
            COUNT(DISTINCT r.tournament_id) as tournaments
        FROM registrations r
        JOIN users u ON r.user_id = u.id
        WHERE r.character_id = %s
        GROUP BY u.id, u.name
        ORDER BY uses DESC
        """
        user_stats = self.db.execute_query(user_query, (character_id,))

        return {
            "global_stats": global_stats,
            "tournament_stats": tournament_stats,
            "user_stats": user_stats
        }

    def get_tier_distribution(self):
        """
        Récupère la distribution des personnages par tier.

        Returns:
            dict: La distribution des personnages par tier
        """
        query = """
        SELECT
            tier,
            COUNT(*) as count,
            COUNT(*) * 100.0 / (SELECT COUNT(*) FROM characters) as percentage
        FROM characters
        GROUP BY tier
        ORDER BY tier ASC
        """
        return self.db.execute_query(query)