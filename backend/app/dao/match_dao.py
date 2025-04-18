"""
Module d'accès aux données pour les matchs.
"""

from typing import Dict, List, Optional, Any
from ..database import Database


class MatchDAO:
    """
    Classe d'accès aux données pour les matchs.
    """

    def __init__(self):
        """
        Initialise la classe MatchDAO.
        """
        self.db = Database()

    def get_by_id(self, match_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un match par son ID.

        Args:
            match_id (int): L'ID du match

        Returns:
            dict: Les données du match ou None si non trouvé
        """
        query = """
        SELECT m.*,
               t.name as tournament_name,
               p1.name as player1_name,
               p2.name as player2_name,
               w.name as winner_name,
               l.name as loser_name,
               c1.name as character1_name,
               c2.name as character2_name
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.id
        JOIN users p1 ON m.player1_id = p1.id
        JOIN users p2 ON m.player2_id = p2.id
        LEFT JOIN users w ON m.winner_id = w.id
        LEFT JOIN users l ON m.loser_id = l.id
        LEFT JOIN registrations r1 ON m.tournament_id = r1.tournament_id AND m.player1_id = r1.user_id
        LEFT JOIN registrations r2 ON m.tournament_id = r2.tournament_id AND m.player2_id = r2.user_id
        LEFT JOIN characters c1 ON r1.character_id = c1.id
        LEFT JOIN characters c2 ON r2.character_id = c2.id
        WHERE m.id = %s
        """
        result = self.db.execute_query(query, (match_id,))
        return result[0] if result else None

    def create(self, data: Dict[str, Any]) -> int:
        """
        Crée un nouveau match.

        Args:
            data (dict): Les données du match

        Returns:
            int: L'ID du match créé
        """
        query = """
        INSERT INTO matches (
            tournament_id, player1_id, player2_id,
            round_number, scheduled_time, status
        ) VALUES (
            %(tournament_id)s, %(player1_id)s, %(player2_id)s,
            %(round_number)s, %(scheduled_time)s, %(status)s
        )
        """
        return self.db.execute_query(query, data)

    def update(self, match_id: int, data: Dict[str, Any]) -> bool:
        """
        Met à jour un match.

        Args:
            match_id (int): L'ID du match
            data (dict): Les champs à mettre à jour

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        fields = []
        values = []
        for key, value in data.items():
            fields.append(f"{key} = %s")
            values.append(value)
        values.append(match_id)

        query = f"""
            UPDATE matches
            SET {', '.join(fields)}
            WHERE id = %s
        """
        self.db.execute_query(query, tuple(values))
        return True

    def delete(self, match_id: int) -> bool:
        """
        Supprime un match.

        Args:
            match_id (int): L'ID du match

        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        query = "DELETE FROM matches WHERE id = %s"
        self.db.execute_query(query, (match_id,))
        return True

    def get_by_tournament(
        self, tournament_id: int, page: int = 1, per_page: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Récupère les matchs d'un tournoi.

        Args:
            tournament_id (int): L'ID du tournoi
            page (int): Le numéro de la page
            per_page (int): Le nombre de matchs par page

        Returns:
            list: Les matchs du tournoi
        """
        offset = (page - 1) * per_page
        query = """
        SELECT m.*,
               t.name as tournament_name,
               p1.name as player1_name,
               p2.name as player2_name,
               w.name as winner_name,
               l.name as loser_name,
               c1.name as character1_name,
               c2.name as character2_name
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.id
        JOIN users p1 ON m.player1_id = p1.id
        JOIN users p2 ON m.player2_id = p2.id
        LEFT JOIN users w ON m.winner_id = w.id
        LEFT JOIN users l ON m.loser_id = l.id
        LEFT JOIN registrations r1 ON m.tournament_id = r1.tournament_id AND m.player1_id = r1.user_id
        LEFT JOIN registrations r2 ON m.tournament_id = r2.tournament_id AND m.player2_id = r2.user_id
        LEFT JOIN characters c1 ON r1.character_id = c1.id
        LEFT JOIN characters c2 ON r2.character_id = c2.id
        WHERE m.tournament_id = %s
        ORDER BY m.scheduled_time ASC
        LIMIT %s OFFSET %s
        """
        return self.db.execute_query(query, (tournament_id, per_page, offset))

    def get_by_player(
        self, player_id: int, page: int = 1, per_page: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Récupère les matchs d'un joueur.

        Args:
            player_id (int): L'ID du joueur
            page (int): Le numéro de la page
            per_page (int): Le nombre de matchs par page

        Returns:
            list: Les matchs du joueur
        """
        offset = (page - 1) * per_page
        query = """
        SELECT m.*,
               t.name as tournament_name,
               p1.name as player1_name,
               p2.name as player2_name,
               w.name as winner_name,
               l.name as loser_name,
               c1.name as character1_name,
               c2.name as character2_name
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.id
        JOIN users p1 ON m.player1_id = p1.id
        JOIN users p2 ON m.player2_id = p2.id
        LEFT JOIN users w ON m.winner_id = w.id
        LEFT JOIN users l ON m.loser_id = l.id
        LEFT JOIN registrations r1 ON m.tournament_id = r1.tournament_id AND m.player1_id = r1.user_id
        LEFT JOIN registrations r2 ON m.tournament_id = r2.tournament_id AND m.player2_id = r2.user_id
        LEFT JOIN characters c1 ON r1.character_id = c1.id
        LEFT JOIN characters c2 ON r2.character_id = c2.id
        WHERE m.player1_id = %s OR m.player2_id = %s
        ORDER BY m.scheduled_time ASC
        LIMIT %s OFFSET %s
        """
        return self.db.execute_query(
            query, (player_id, player_id, per_page, offset)
        )

    def get_upcoming(
        self, page: int = 1, per_page: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Récupère les matchs à venir.

        Args:
            page (int): Le numéro de la page
            per_page (int): Le nombre de matchs par page

        Returns:
            list: Les matchs à venir
        """
        offset = (page - 1) * per_page
        query = """
        SELECT * FROM upcoming_matches
        WHERE scheduled_time > NOW()
        ORDER BY scheduled_time ASC
        LIMIT %s OFFSET %s
        """
        return self.db.execute_query(query, (per_page, offset))

    def get_upcoming_by_player(self, player_id, limit=5):
        """
        Récupère les prochains matchs d'un joueur.

        Args:
            player_id (int): L'ID du joueur
            limit (int): Le nombre de matchs à récupérer

        Returns:
            list: Les prochains matchs du joueur
        """
        query = """
        SELECT * FROM upcoming_matches
        WHERE player1_id = %s OR player2_id = %s
        ORDER BY scheduled_time ASC
        LIMIT %s
        """
        return self.db.execute_query(query, (player_id, player_id, limit))

    def update_result(
        self, match_id: int, winner_id: int, score: str
    ) -> bool:
        """
        Met à jour le résultat d'un match.

        Args:
            match_id (int): L'ID du match
            winner_id (int): L'ID du gagnant
            score (str): Le score du match

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        query = """
        UPDATE matches
        SET winner_id = %s, score = %s, status = 'completed'
        WHERE id = %s
        """
        self.db.execute_query(query, (winner_id, score, match_id))
        return True

    def get_statistics(self, match_id: int) -> Dict[str, Any]:
        """
        Récupère les statistiques d'un match.

        Args:
            match_id (int): L'ID du match

        Returns:
            dict: Les statistiques du match
        """
        query = """
        SELECT * FROM upcoming_matches
        WHERE match_id = %s
        """
        result = self.db.execute_query(query, (match_id,))
        return result[0] if result else {}