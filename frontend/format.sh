#!/bin/bash
# Script pour formater le code TypeScript/React avec Prettier et ESLint

echo "Formatage du code avec Prettier..."
npm run format

echo "Vérification du code avec ESLint..."
npm run lint

echo "Formatage terminé !"