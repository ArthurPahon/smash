import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging

# Chargement des variables d'environnement
load_dotenv()

# Configuration des logs
logger = logging.getLogger(__name__)

class Database:
    """
    Classe singleton pour gérer la connexion à la base de données MySQL.
    Utilise le pattern Singleton pour s'assurer qu'une seule connexion est créée.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        """
        Établit une connexion à la base de données si elle n'existe pas déjà.
        """
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=os.environ.get("DB_HOST", "db"),
                    user=os.environ.get("DB_USER", "root"),
                    password=os.environ.get("DB_PASSWORD", "password"),
                    database=os.environ.get("DB_NAME", "smash")
                )
                logger.info("Connexion à la base de données établie")
            except Error as e:
                logger.error(f"Erreur de connexion à la base de données: {e}")
                raise

    def disconnect(self):
        """
        Ferme la connexion à la base de données si elle est ouverte.
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Connexion à la base de données fermée")

    def execute_query(self, query, params=None, fetch=True):
        """
        Exécute une requête SQL et retourne les résultats si fetch=True.

        Args:
            query (str): La requête SQL à exécuter
            params (tuple): Les paramètres de la requête
            fetch (bool): Si True, retourne les résultats de la requête

        Returns:
            list: Les résultats de la requête si fetch=True, sinon l'ID de la dernière ligne insérée
        """
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.lastrowid
            return result
        except Error as e:
            logger.error(f"Erreur d'exécution de la requête: {e}")
            logger.error(f"Requête: {query}")
            logger.error(f"Paramètres: {params}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def execute_procedure(self, procedure_name, params=None):
        """
        Exécute une procédure stockée et retourne les résultats.

        Args:
            procedure_name (str): Le nom de la procédure à exécuter
            params (tuple): Les paramètres de la procédure

        Returns:
            list: Les résultats de la procédure
        """
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.callproc(procedure_name, params or ())
            result = []
            for result_set in cursor.stored_results():
                result.extend(result_set.fetchall())
            return result
        except Error as e:
            logger.error(f"Erreur d'exécution de la procédure: {e}")
            logger.error(f"Procédure: {procedure_name}")
            logger.error(f"Paramètres: {params}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def execute_many(self, query, params_list):
        """
        Exécute une requête SQL avec plusieurs ensembles de paramètres.

        Args:
            query (str): La requête SQL à exécuter
            params_list (list): Liste de tuples de paramètres

        Returns:
            int: Le nombre de lignes affectées
        """
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.executemany(query, params_list)
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            logger.error(f"Erreur d'exécution de la requête multiple: {e}")
            logger.error(f"Requête: {query}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def begin_transaction(self):
        """
        Démarre une transaction.
        """
        self.connect()
        self.connection.start_transaction()

    def commit_transaction(self):
        """
        Valide une transaction.
        """
        if self.connection and self.connection.is_connected():
            self.connection.commit()

    def rollback_transaction(self):
        """
        Annule une transaction.
        """
        if self.connection and self.connection.is_connected():
            self.connection.rollback()