#!/bin/bash
# Script global pour formater le code du projet

echo "=== Formatage du code frontend ==="
cd frontend
./format.sh

echo ""
echo "=== Formatage du code backend ==="
cd ../backend
./format.sh

echo ""
echo "=== Formatage global terminé ! ==="