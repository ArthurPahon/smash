"""
Module d'accès aux données pour les classements des joueurs.
"""

from app.database import Database


class RankingDAO:
    """
    Classe d'accès aux données pour les classements des joueurs.
    """

    def __init__(self):
        """
        Initialise la classe RankingDAO.
        """
        self.db = Database()

    def get_by_id(self, ranking_id):
        """
        Récupère un classement par son ID.

        Args:
            ranking_id (int): L'ID du classement

        Returns:
            dict: Les données du classement ou None si non trouvé
        """
        query = """
        SELECT r.*, u.name as user_name, t.name as tournament_name
        FROM rankings r
        JOIN users u ON r.user_id = u.id
        JOIN tournaments t ON r.tournament_id = t.id
        WHERE r.id = %s
        """
        result = self.db.execute_query(query, (ranking_id,))
        return result[0] if result else None

    def create(self, tournament_id, user_id, points, position):
        """
        Crée un nouveau classement.

        Args:
            tournament_id (int): L'ID du tournoi
            user_id (int): L'ID de l'utilisateur
            points (int): Le nombre de points
            position (int): La position dans le classement

        Returns:
            dict: Les données du classement créé
        """
        query = """
        INSERT INTO rankings (tournament_id, user_id, points, position)
        VALUES (%s, %s, %s, %s)
        """
        params = (tournament_id, user_id, points, position)
        ranking_id = self.db.execute_query(query, params, fetch=False)
        return self.get_by_id(ranking_id)

    def update(self, ranking_id, **kwargs):
        """
        Met à jour un classement.

        Args:
            ranking_id (int): L'ID du classement
            **kwargs: Les champs à mettre à jour

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        if not kwargs:
            return False

        set_clause = ", ".join([f"{k} = %s" for k in kwargs.keys()])
        query = f"UPDATE rankings SET {set_clause} WHERE id = %s"
        params = list(kwargs.values()) + [ranking_id]

        self.db.execute_query(query, params, fetch=False)
        return True

    def delete(self, ranking_id):
        """
        Supprime un classement.

        Args:
            ranking_id (int): L'ID du classement

        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        query = "DELETE FROM rankings WHERE id = %s"
        self.db.execute_query(query, (ranking_id,), fetch=False)
        return True

    def get_by_tournament(self, tournament_id, page=1, per_page=10):
        """
        Récupère le classement d'un tournoi.

        Args:
            tournament_id (int): L'ID du tournoi
            page (int): Le numéro de la page
            per_page (int): Le nombre de joueurs par page

        Returns:
            tuple: (classement, total, pages)
        """
        offset = (page - 1) * per_page

        # Requête pour compter le total
        count_query = """
        SELECT COUNT(*) as total FROM rankings
        WHERE tournament_id = %s
        """
        total_result = self.db.execute_query(count_query, (tournament_id,))
        total = total_result[0]["total"]
        pages = (total + per_page - 1) // per_page

        # Requête pour récupérer le classement
        query = """
        SELECT r.*, u.name as user_name
        FROM rankings r
        JOIN users u ON r.user_id = u.id
        WHERE r.tournament_id = %s
        ORDER BY r.position ASC
        LIMIT %s OFFSET %s
        """
        params = (tournament_id, per_page, offset)

        rankings = self.db.execute_query(query, params)

        return rankings, total, pages

    def get_by_user(self, user_id, page=1, per_page=10):
        """
        Récupère les classements d'un utilisateur.

        Args:
            user_id (int): L'ID de l'utilisateur
            page (int): Le numéro de la page
            per_page (int): Le nombre de classements par page

        Returns:
            tuple: (classements, total, pages)
        """
        offset = (page - 1) * per_page

        # Requête pour compter le total
        count_query = """
        SELECT COUNT(*) as total FROM rankings
        WHERE user_id = %s
        """
        total_result = self.db.execute_query(count_query, (user_id,))
        total = total_result[0]["total"]
        pages = (total + per_page - 1) // per_page

        # Requête pour récupérer les classements
        query = """
        SELECT r.*, t.name as tournament_name
        FROM rankings r
        JOIN tournaments t ON r.tournament_id = t.id
        WHERE r.user_id = %s
        ORDER BY r.position ASC
        LIMIT %s OFFSET %s
        """
        params = (user_id, per_page, offset)

        rankings = self.db.execute_query(query, params)

        return rankings, total, pages

    def get_global_ranking(self, page=1, per_page=10):
        """
        Récupère le classement global des joueurs.

        Args:
            page (int): Le numéro de la page
            per_page (int): Le nombre de joueurs par page

        Returns:
            tuple: (classement, total, pages)
        """
        offset = (page - 1) * per_page

        # Requête pour compter le total
        count_query = """
        SELECT COUNT(DISTINCT user_id) as total FROM rankings
        """
        total_result = self.db.execute_query(count_query)
        total = total_result[0]["total"]
        pages = (total + per_page - 1) // per_page

        # Requête pour récupérer le classement global
        query = """
        SELECT u.id, u.name,
               COUNT(DISTINCT r.tournament_id) as tournaments_played,
               SUM(CASE WHEN r.position = 1 THEN 1 ELSE 0 END) as first_places,
               SUM(CASE WHEN r.position = 2 THEN 1 ELSE 0 END) as second_places,
               SUM(CASE WHEN r.position = 3 THEN 1 ELSE 0 END) as third_places,
               AVG(r.position) as average_position,
               SUM(r.points) as total_points
        FROM users u
        JOIN rankings r ON u.id = r.user_id
        GROUP BY u.id, u.name
        ORDER BY total_points DESC, average_position ASC
        LIMIT %s OFFSET %s
        """
        params = (per_page, offset)

        rankings = self.db.execute_query(query, params)

        return rankings, total, pages

    def update_tournament_ranking(self, tournament_id):
        """
        Met à jour le classement d'un tournoi.

        Args:
            tournament_id (int): L'ID du tournoi

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        try:
            # Supprimer l'ancien classement
            delete_query = "DELETE FROM rankings WHERE tournament_id = %s"
            self.db.execute_query(delete_query, (tournament_id,), fetch=False)

            # Calculer et insérer le nouveau classement
            insert_query = """
            INSERT INTO rankings (tournament_id, user_id, points, position)
            SELECT
                r.tournament_id,
                r.user_id,
                COALESCE(SUM(
                    CASE
                        WHEN m.winner_id = r.user_id THEN 3
                        WHEN m.loser_id = r.user_id THEN 0
                        ELSE 1
                    END
                ), 0) as points,
                ROW_NUMBER() OVER (
                    ORDER BY COALESCE(SUM(
                        CASE
                            WHEN m.winner_id = r.user_id THEN 3
                            WHEN m.loser_id = r.user_id THEN 0
                            ELSE 1
                        END
                    ), 0) DESC
                ) as position
            FROM registrations r
            LEFT JOIN matches m ON (
                m.tournament_id = r.tournament_id AND
                (m.player1_id = r.user_id OR m.player2_id = r.user_id)
            )
            WHERE r.tournament_id = %s
            GROUP BY r.tournament_id, r.user_id
            """
            self.db.execute_query(insert_query, (tournament_id,), fetch=False)

            return True
        except Exception:
            return False

    def get_statistics(self, user_id):
        """
        Récupère les statistiques de classement d'un utilisateur.

        Args:
            user_id (int): L'ID de l'utilisateur

        Returns:
            dict: Les statistiques de classement
        """
        # Statistiques globales
        global_query = """
        SELECT
            COUNT(DISTINCT tournament_id) as tournaments_played,
            SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as first_places,
            SUM(CASE WHEN position = 2 THEN 1 ELSE 0 END) as second_places,
            SUM(CASE WHEN position = 3 THEN 1 ELSE 0 END) as third_places,
            AVG(position) as average_position,
            SUM(points) as total_points
        FROM rankings
        WHERE user_id = %s
        """
        global_stats = self.db.execute_query(global_query, (user_id,))[0]

        # Évolution du classement
        evolution_query = """
        SELECT t.name as tournament_name, r.position, r.points
        FROM rankings r
        JOIN tournaments t ON r.tournament_id = t.id
        WHERE r.user_id = %s
        ORDER BY t.start_date ASC
        """
        evolution = self.db.execute_query(evolution_query, (user_id,))

        return {
            "global_stats": global_stats,
            "evolution": evolution
        }