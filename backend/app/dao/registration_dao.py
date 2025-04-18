"""
Module d'accès aux données pour les inscriptions aux tournois.
"""

from app.database import Database


class RegistrationDAO:
    """
    Classe d'accès aux données pour les inscriptions aux tournois.
    """

    def __init__(self):
        """
        Initialise la classe RegistrationDAO.
        """
        self.db = Database()

    def get_by_id(self, registration_id):
        """
        Récupère une inscription par son ID.

        Args:
            registration_id (int): L'ID de l'inscription

        Returns:
            dict: Les données de l'inscription ou None si non trouvée
        """
        query = """
        SELECT r.*, u.name as user_name, c.name as character_name,
               t.name as tournament_name
        FROM registrations r
        JOIN users u ON r.user_id = u.id
        LEFT JOIN characters c ON r.character_id = c.id
        JOIN tournaments t ON r.tournament_id = t.id
        WHERE r.id = %s
        """
        result = self.db.execute_query(query, (registration_id,))
        return result[0] if result else None

    def create(self, tournament_id, user_id, character_id=None):
        """
        Crée une nouvelle inscription à un tournoi.

        Args:
            tournament_id (int): L'ID du tournoi
            user_id (int): L'ID de l'utilisateur
            character_id (int, optional): L'ID du personnage choisi

        Returns:
            dict: Les données de l'inscription créée
        """
        # Vérifier si le tournoi est plein
        tournament_query = """
        SELECT t.max_participants, COUNT(r.id) as current_participants
        FROM tournaments t
        LEFT JOIN registrations r ON t.id = r.tournament_id
        WHERE t.id = %s
        GROUP BY t.id, t.max_participants
        """
        tournament_result = self.db.execute_query(tournament_query, (tournament_id,))

        if not tournament_result:
            return None

        tournament = tournament_result[0]
        if tournament["current_participants"] >= tournament["max_participants"]:
            return None

        # Vérifier si l'utilisateur est déjà inscrit
        existing_query = """
        SELECT 1 FROM registrations
        WHERE tournament_id = %s AND user_id = %s
        """
        existing_result = self.db.execute_query(existing_query, (tournament_id, user_id))
        if existing_result:
            return None

        # Créer l'inscription
        query = """
        INSERT INTO registrations (tournament_id, user_id, character_id)
        VALUES (%s, %s, %s)
        """
        params = (tournament_id, user_id, character_id)
        registration_id = self.db.execute_query(query, params, fetch=False)
        return self.get_by_id(registration_id)

    def update(self, registration_id, **kwargs):
        """
        Met à jour une inscription.

        Args:
            registration_id (int): L'ID de l'inscription
            **kwargs: Les champs à mettre à jour

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        if not kwargs:
            return False

        set_clause = ", ".join([f"{k} = %s" for k in kwargs.keys()])
        query = f"UPDATE registrations SET {set_clause} WHERE id = %s"
        params = list(kwargs.values()) + [registration_id]

        self.db.execute_query(query, params, fetch=False)
        return True

    def delete(self, registration_id):
        """
        Supprime une inscription.

        Args:
            registration_id (int): L'ID de l'inscription

        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        query = "DELETE FROM registrations WHERE id = %s"
        self.db.execute_query(query, (registration_id,), fetch=False)
        return True

    def get_by_tournament(self, tournament_id, page=1, per_page=10):
        """
        Récupère les inscriptions d'un tournoi.

        Args:
            tournament_id (int): L'ID du tournoi
            page (int): Le numéro de la page
            per_page (int): Le nombre d'inscriptions par page

        Returns:
            tuple: (inscriptions, total, pages)
        """
        offset = (page - 1) * per_page

        # Requête pour compter le total
        count_query = """
        SELECT COUNT(*) as total FROM registrations
        WHERE tournament_id = %s
        """
        total_result = self.db.execute_query(count_query, (tournament_id,))
        total = total_result[0]["total"]
        pages = (total + per_page - 1) // per_page

        # Requête pour récupérer les inscriptions
        query = """
        SELECT r.*, u.name as user_name, c.name as character_name
        FROM registrations r
        JOIN users u ON r.user_id = u.id
        LEFT JOIN characters c ON r.character_id = c.id
        WHERE r.tournament_id = %s
        ORDER BY r.registration_date ASC
        LIMIT %s OFFSET %s
        """
        params = (tournament_id, per_page, offset)

        registrations = self.db.execute_query(query, params)

        return registrations, total, pages

    def get_by_user(self, user_id, page=1, per_page=10):
        """
        Récupère les inscriptions d'un utilisateur.

        Args:
            user_id (int): L'ID de l'utilisateur
            page (int): Le numéro de la page
            per_page (int): Le nombre d'inscriptions par page

        Returns:
            tuple: (inscriptions, total, pages)
        """
        offset = (page - 1) * per_page

        # Requête pour compter le total
        count_query = """
        SELECT COUNT(*) as total FROM registrations
        WHERE user_id = %s
        """
        total_result = self.db.execute_query(count_query, (user_id,))
        total = total_result[0]["total"]
        pages = (total + per_page - 1) // per_page

        # Requête pour récupérer les inscriptions
        query = """
        SELECT r.*, t.name as tournament_name, c.name as character_name
        FROM registrations r
        JOIN tournaments t ON r.tournament_id = t.id
        LEFT JOIN characters c ON r.character_id = c.id
        WHERE r.user_id = %s
        ORDER BY r.registration_date DESC
        LIMIT %s OFFSET %s
        """
        params = (user_id, per_page, offset)

        registrations = self.db.execute_query(query, params)

        return registrations, total, pages

    def get_upcoming_by_user(self, user_id, limit=5):
        """
        Récupère les prochaines inscriptions d'un utilisateur.

        Args:
            user_id (int): L'ID de l'utilisateur
            limit (int): Le nombre d'inscriptions à récupérer

        Returns:
            list: Les prochaines inscriptions de l'utilisateur
        """
        query = """
        SELECT r.*, t.name as tournament_name, c.name as character_name
        FROM registrations r
        JOIN tournaments t ON r.tournament_id = t.id
        LEFT JOIN characters c ON r.character_id = c.id
        WHERE r.user_id = %s
        AND t.start_date > NOW()
        AND t.status = 'pending'
        ORDER BY t.start_date ASC
        LIMIT %s
        """
        return self.db.execute_query(query, (user_id, limit))

    def update_character(self, registration_id, character_id):
        """
        Met à jour le personnage choisi pour une inscription.

        Args:
            registration_id (int): L'ID de l'inscription
            character_id (int): L'ID du personnage

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        query = """
        UPDATE registrations
        SET character_id = %s
        WHERE id = %s
        """
        try:
            self.db.execute_query(query, (character_id, registration_id), fetch=False)
            return True
        except Exception:
            return False

    def check_availability(self, tournament_id):
        """
        Vérifie si un tournoi a encore des places disponibles.

        Args:
            tournament_id (int): L'ID du tournoi

        Returns:
            dict: Informations sur la disponibilité du tournoi
        """
        query = """
        SELECT t.max_participants, COUNT(r.id) as current_participants,
               t.registration_deadline
        FROM tournaments t
        LEFT JOIN registrations r ON t.id = r.tournament_id
        WHERE t.id = %s
        GROUP BY t.id, t.max_participants, t.registration_deadline
        """
        result = self.db.execute_query(query, (tournament_id,))

        if not result:
            return None

        tournament = result[0]
        return {
            "available": tournament["current_participants"] < tournament["max_participants"],
            "current_participants": tournament["current_participants"],
            "max_participants": tournament["max_participants"],
            "registration_deadline": tournament["registration_deadline"]
        }

    def get_statistics(self, tournament_id):
        """
        Récupère les statistiques des inscriptions d'un tournoi.

        Args:
            tournament_id (int): L'ID du tournoi

        Returns:
            dict: Les statistiques des inscriptions
        """
        # Nombre total d'inscriptions
        total_query = """
        SELECT COUNT(*) as total_registrations
        FROM registrations
        WHERE tournament_id = %s
        """
        total_result = self.db.execute_query(total_query, (tournament_id,))
        total_registrations = total_result[0]["total_registrations"]

        # Répartition par personnage
        characters_query = """
        SELECT c.name, COUNT(*) as usage_count
        FROM registrations r
        JOIN characters c ON r.character_id = c.id
        WHERE r.tournament_id = %s
        GROUP BY c.id, c.name
        ORDER BY usage_count DESC
        """
        characters = self.db.execute_query(characters_query, (tournament_id,))

        # Inscriptions par jour
        daily_query = """
        SELECT DATE(registration_date) as date, COUNT(*) as count
        FROM registrations
        WHERE tournament_id = %s
        GROUP BY DATE(registration_date)
        ORDER BY date ASC
        """
        daily_registrations = self.db.execute_query(daily_query, (tournament_id,))

        return {
            "total_registrations": total_registrations,
            "character_distribution": characters,
            "daily_registrations": daily_registrations
        }