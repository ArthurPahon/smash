#!/bin/bash
# Script pour formater le code Python avec Black et isort

echo "Formatage du code avec isort..."
isort .

echo "Formatage du code avec Black..."
black .

echo "Vérification du code avec flake8..."
flake8

echo "Formatage terminé !"