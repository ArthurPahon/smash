from app import db

from .user import User, Role
from .tournament import Tournament, Registration
from .match import Match, Bracket
from .character import Character
from .ranking import Ranking, Classement

__all__ = [
    'User',
    'Role',
    'Tournament',
    'Registration',
    'Match',
    'Bracket',
    'Character',
    'Ranking',
    'Classement'
]
