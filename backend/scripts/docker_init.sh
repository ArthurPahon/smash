#!/bin/bash

# Attendre que la base de données soit prête
echo "Attente de la base de données..."
while ! mysqladmin ping -h"db" -P"3306" --silent; do
    sleep 1
done
echo "Base de données prête!"

# Initialiser les migrations
echo "Initialisation des migrations..."
python scripts/init_migrations.py

# Initialiser la base de données avec les données de test
echo "Initialisation des données de test..."
python scripts/init_db.py

echo "Configuration de la base de données terminée!"