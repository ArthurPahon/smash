#!/bin/bash

# Création de l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt

# Initialisation des migrations
python scripts/init_migrations.py

# Initialisation de la base de données
python scripts/init_db.py

echo "Base de données configurée avec succès!"