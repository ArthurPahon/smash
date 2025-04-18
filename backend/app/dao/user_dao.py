"""
Module d'accès aux données pour les utilisateurs.
"""

import bcrypt
from app.database import Database


class UserDAO:
    """
    Classe d'accès aux données pour les utilisateurs.
    """

    def __init__(self):
        """
        Initialise la classe UserDAO.
        """
        self.db = Database()

    def get_by_id(self, user_id):
        """
        Récupère un utilisateur par son ID.

        Args:
            user_id (int): L'ID de l'utilisateur

        Returns:
            dict: Les données de l'utilisateur ou None si non trouvé
        """
        query = "SELECT * FROM users WHERE id = %s"
        result = self.db.execute_query(query, (user_id,))
        return result[0] if result else None

    def get_by_email(self, email):
        """
        Récupère un utilisateur par son email.

        Args:
            email (str): L'email de l'utilisateur

        Returns:
            dict: Les données de l'utilisateur ou None si non trouvé
        """
        query = "SELECT * FROM users WHERE email = %s"
        result = self.db.execute_query(query, (email,))
        return result[0] if result else None

    def create(self, name, email, password, profile_picture=None,
               country=None, state=None):
        """
        Crée un nouvel utilisateur.

        Args:
            name (str): Le nom de l'utilisateur
            email (str): L'email de l'utilisateur
            password (str): Le mot de passe de l'utilisateur
            profile_picture (str, optional): L'URL de la photo de profil
            country (str, optional): Le pays de l'utilisateur
            state (str, optional): L'état/région de l'utilisateur

        Returns:
            dict: Les données de l'utilisateur créé
        """
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        query = """
        INSERT INTO users (name, email, password, profile_picture,
                          country, state)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (name, email, hashed_password, profile_picture,
                 country, state)
        user_id = self.db.execute_query(query, params, fetch=False)
        return self.get_by_id(user_id)

    def update(self, user_id, **kwargs):
        """
        Met à jour un utilisateur.

        Args:
            user_id (int): L'ID de l'utilisateur
            **kwargs: Les champs à mettre à jour

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        if not kwargs:
            return False

        set_clause = ", ".join([f"{k} = %s" for k in kwargs.keys()])
        query = f"UPDATE users SET {set_clause} WHERE id = %s"
        params = list(kwargs.values()) + [user_id]

        self.db.execute_query(query, params, fetch=False)
        return True

    def delete(self, user_id):
        """
        Supprime un utilisateur.

        Args:
            user_id (int): L'ID de l'utilisateur

        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        query = "DELETE FROM users WHERE id = %s"
        self.db.execute_query(query, (user_id,), fetch=False)
        return True

    def check_password(self, email, password):
        """
        Vérifie si le mot de passe correspond à l'email.

        Args:
            email (str): L'email de l'utilisateur
            password (str): Le mot de passe à vérifier

        Returns:
            bool: True si le mot de passe correspond, False sinon
        """
        user = self.get_by_email(email)
        if not user:
            return False

        return bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        )

    def get_roles(self, user_id, tournament_id=None):
        """
        Récupère les rôles d'un utilisateur.

        Args:
            user_id (int): L'ID de l'utilisateur
            tournament_id (int, optional): L'ID du tournoi

        Returns:
            list: La liste des rôles de l'utilisateur
        """
        query = """
        SELECT r.* FROM roles r
        JOIN user_role ur ON r.id = ur.role_id
        WHERE ur.user_id = %s
        """
        params = [user_id]

        if tournament_id:
            query += " AND ur.tournament_id = %s"
            params.append(tournament_id)

        return self.db.execute_query(query, params)

    def has_role(self, user_id, role_name, tournament_id=None):
        """
        Vérifie si un utilisateur a un rôle spécifique.

        Args:
            user_id (int): L'ID de l'utilisateur
            role_name (str): Le nom du rôle
            tournament_id (int, optional): L'ID du tournoi

        Returns:
            bool: True si l'utilisateur a le rôle, False sinon
        """
        query = """
        SELECT 1 FROM roles r
        JOIN user_role ur ON r.id = ur.role_id
        WHERE ur.user_id = %s AND r.name = %s
        """
        params = [user_id, role_name]

        if tournament_id:
            query += " AND ur.tournament_id = %s"
            params.append(tournament_id)

        result = self.db.execute_query(query, params)
        return len(result) > 0

    def add_role(self, user_id, role_id, tournament_id=None):
        """
        Ajoute un rôle à un utilisateur.

        Args:
            user_id (int): L'ID de l'utilisateur
            role_id (int): L'ID du rôle
            tournament_id (int, optional): L'ID du tournoi

        Returns:
            bool: True si l'ajout a réussi, False sinon
        """
        query = """
        INSERT INTO user_role (user_id, role_id, tournament_id)
        VALUES (%s, %s, %s)
        """
        params = (user_id, role_id, tournament_id)

        try:
            self.db.execute_query(query, params, fetch=False)
            return True
        except Exception:
            return False

    def remove_role(self, user_id, role_id, tournament_id=None):
        """
        Supprime un rôle d'un utilisateur.

        Args:
            user_id (int): L'ID de l'utilisateur
            role_id (int): L'ID du rôle
            tournament_id (int, optional): L'ID du tournoi

        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        query = """
        DELETE FROM user_role
        WHERE user_id = %s AND role_id = %s
        """
        params = [user_id, role_id]

        if tournament_id:
            query += " AND tournament_id = %s"
            params.append(tournament_id)

        try:
            self.db.execute_query(query, params, fetch=False)
            return True
        except Exception:
            return False

    def get_all(self, page=1, per_page=10, search=None):
        """
        Récupère tous les utilisateurs avec pagination.

        Args:
            page (int): Le numéro de la page
            per_page (int): Le nombre d'utilisateurs par page
            search (str, optional): Le terme de recherche

        Returns:
            tuple: (utilisateurs, total, pages)
        """
        offset = (page - 1) * per_page

        # Requête pour compter le total
        count_query = "SELECT COUNT(*) as total FROM users"
        params = []

        if search:
            count_query += " WHERE name LIKE %s OR email LIKE %s"
            params.extend([f"%{search}%", f"%{search}%"])

        total_result = self.db.execute_query(count_query, params)
        total = total_result[0]["total"]
        pages = (total + per_page - 1) // per_page

        # Requête pour récupérer les utilisateurs
        query = "SELECT * FROM users"
        if search:
            query += " WHERE name LIKE %s OR email LIKE %s"

        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        users = self.db.execute_query(query, params)

        return users, total, pages