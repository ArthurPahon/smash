# Ce fichier rend le répertoire routes importable comme module Python

from . import (
    auth,
    characters,
    matches,
    rankings,
    registrations,
    tournaments,
    users
)

__all__ = [
    'auth',
    'characters',
    'matches',
    'rankings',
    'registrations',
    'tournaments',
    'users'
]
