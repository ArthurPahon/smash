"""
Module d'accès aux données pour les tournois.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from ..database import Database


class TournamentDAO:
    """
    Classe d'accès aux données pour les tournois.
    """

    def __init__(self):
        """
        Initialise la classe TournamentDAO.
        """
        self.db = Database()

    def get_by_id(self, tournament_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un tournoi par son ID.

        Args:
            tournament_id (int): L'ID du tournoi

        Returns:
            dict: Les données du tournoi ou None si non trouvé
        """
        query = """
        SELECT * FROM tournament_details
        WHERE id = %s
        """
        result = self.db.execute_query(query, (tournament_id,))
        return result[0] if result else None

    def create(self, data: Dict[str, Any]) -> int:
        """
        Crée un nouveau tournoi.

        Args:
            data (dict): Les données du tournoi

        Returns:
            int: L'ID du tournoi créé
        """
        query = """
        INSERT INTO tournaments (
            name, description, start_date, end_date, registration_deadline,
            max_participants, format, rules, prize_pool, organizer_id, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        """
        return self.db.execute_query(query, tuple(data.values()))

    def update(self, tournament_id: int, data: Dict[str, Any]) -> bool:
        """
        Met à jour un tournoi.

        Args:
            tournament_id (int): L'ID du tournoi
            data (dict): Les champs à mettre à jour

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        if not data:
            return False

        fields = []
        values = []
        for key, value in data.items():
            fields.append(f"{key} = %s")
            values.append(value)
        values.append(tournament_id)

        query = f"""
            UPDATE tournaments
            SET {', '.join(fields)}
            WHERE id = %s
        """
        self.db.execute_query(query, tuple(values))
        return True

    def delete(self, tournament_id: int) -> bool:
        """
        Supprime un tournoi.

        Args:
            tournament_id (int): L'ID du tournoi

        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        query = "DELETE FROM tournaments WHERE id = %s"
        self.db.execute_query(query, (tournament_id,), fetch=False)
        return True

    def get_all(self, page: int = 1, per_page: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère tous les tournois.

        Args:
            page (int): Le numéro de la page
            per_page (int): Le nombre de tournois par page

        Returns:
            list: La liste des tournois
        """
        offset = (page - 1) * per_page

        # Requête pour compter le total
        count_query = "SELECT COUNT(*) as total FROM tournaments"
        total_result = self.db.execute_query(count_query)
        total = total_result[0]["total"]
        pages = (total + per_page - 1) // per_page

        # Requête pour récupérer les tournois
        query = """
        SELECT * FROM tournament_details
        ORDER BY start_date DESC
        LIMIT %s OFFSET %s
        """
        params = (per_page, offset)

        tournaments = self.db.execute_query(query, params)

        return tournaments

    def get_upcoming(self, page: int = 1, per_page: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les tournois à venir.

        Args:
            page (int): Le numéro de la page
            per_page (int): Le nombre de tournois par page

        Returns:
            list: La liste des tournois à venir
        """
        offset = (page - 1) * per_page

        # Requête pour compter le total
        count_query = """
        SELECT COUNT(*) as total FROM tournaments
        WHERE start_date > NOW() AND status = 'pending'
        """
        total_result = self.db.execute_query(count_query)
        total = total_result[0]["total"]
        pages = (total + per_page - 1) // per_page

        # Requête pour récupérer les tournois
        query = """
        SELECT * FROM tournament_details
        WHERE start_date > NOW() AND status = 'pending'
        ORDER BY start_date ASC
        LIMIT %s OFFSET %s
        """
        params = (per_page, offset)

        tournaments = self.db.execute_query(query, params)

        return tournaments

    def get_by_organizer(
        self, organizer_id: int, page: int = 1, per_page: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Récupère les tournois d'un organisateur.

        Args:
            organizer_id (int): L'ID de l'organisateur
            page (int): Le numéro de la page
            per_page (int): Le nombre de tournois par page

        Returns:
            list: La liste des tournois de l'organisateur
        """
        offset = (page - 1) * per_page

        # Requête pour compter le total
        count_query = """
        SELECT COUNT(*) as total FROM tournaments
        WHERE organizer_id = %s
        """
        total_result = self.db.execute_query(count_query, (organizer_id,))
        total = total_result[0]["total"]
        pages = (total + per_page - 1) // per_page

        # Requête pour récupérer les tournois
        query = """
        SELECT * FROM tournament_details
        WHERE organizer_id = %s
        ORDER BY start_date DESC
        LIMIT %s OFFSET %s
        """
        params = (organizer_id, per_page, offset)

        tournaments = self.db.execute_query(query, params)

        return tournaments

    def search(
        self, query: str, page: int = 1, per_page: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recherche des tournois par nom ou description.

        Args:
            query (str): Le terme de recherche
            page (int): Le numéro de la page
            per_page (int): Le nombre de tournois par page

        Returns:
            list: La liste des tournois correspondants
        """
        offset = (page - 1) * per_page
        search_query = """
            SELECT * FROM tournament_details
            WHERE name LIKE %s OR description LIKE %s
            ORDER BY start_date DESC
            LIMIT %s OFFSET %s
        """
        search_term = f"%{query}%"
        return self.db.execute_query(
            search_query, (search_term, search_term, per_page, offset)
        )

    def get_statistics(self, tournament_id: int) -> Dict[str, Any]:
        """
        Récupère les statistiques d'un tournoi.

        Args:
            tournament_id (int): L'ID du tournoi

        Returns:
            dict: Les statistiques du tournoi
        """
        # Statistiques globales
        global_query = """
        SELECT * FROM tournament_details
        WHERE id = %s
        """
        global_stats = self.db.execute_query(global_query, (tournament_id,))[0]

        # Répartition des personnages
        characters_query = """
        SELECT
            c.name as character_name,
            COUNT(*) as usage_count,
            COUNT(*) * 100.0 / (SELECT COUNT(*) FROM registrations WHERE tournament_id = %s) as percentage
        FROM registrations r
        JOIN characters c ON r.character_id = c.id
        WHERE r.tournament_id = %s
        GROUP BY c.id, c.name
        ORDER BY usage_count DESC
        """
        characters = self.db.execute_query(characters_query, (tournament_id, tournament_id))

        # Inscriptions par jour
        daily_query = """
        SELECT
            DATE(registration_date) as date,
            COUNT(*) as count
        FROM registrations
        WHERE tournament_id = %s
        GROUP BY DATE(registration_date)
        ORDER BY date ASC
        """
        daily_registrations = self.db.execute_query(daily_query, (tournament_id,))

        return {
            "global_stats": global_stats,
            "character_distribution": characters,
            "daily_registrations": daily_registrations
        }