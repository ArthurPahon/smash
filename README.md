# Projet SMASH

## Structure du projet

- `frontend/` : Application React/TypeScript pour l'interface utilisateur
- `backend/` : API Flask/Python pour la logique métier

## Configuration de développement

### Formatage du code

Le projet utilise des outils de formatage pour maintenir un style de code cohérent :

#### Frontend

- **Prettier** : Formateur de code pour JavaScript/TypeScript/React
- **ESLint** : Linter pour détecter et corriger les problèmes de code

Pour installer les dépendances frontend (dans le dossier `frontend/`) :

```bash
npm install --save-dev prettier eslint eslint-config-prettier eslint-plugin-prettier
```

#### Backend

- **Black** : Formateur de code pour Python
- **isort** : Outil pour trier les imports Python
- **flake8** : Linter pour Python

Pour installer les dépendances backend (dans le dossier `backend/`) :

```bash
pip install black isort flake8
```

### Commandes de formatage

- Pour formater tout le projet :

```bash
./format.sh
```

- Pour formater uniquement le frontend :

```bash
cd frontend
./format.sh
```

- Pour formater uniquement le backend :

```bash
cd backend
./format.sh
```

## Démarrage de l'application

Pour démarrer l'application avec Docker :

```bash
docker compose up --build
```
