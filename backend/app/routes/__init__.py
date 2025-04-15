# Ce fichier rend le répertoire routes importable comme module Python

from . import (
    auth,
    characters,
    rankings,
    registrations,
    tournaments,
    users
)

__all__ = [
    'auth',
    'characters',
    'rankings',
    'registrations',
    'tournaments',
    'users'
]
