from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    JWTManager
)
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User

# Création du Blueprint pour les routes d'authentification
bp = Blueprint("auth", __name__)


# Route pour l'inscription d'un utilisateur
@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Vérification des champs requis
    required_fields = ['nom', 'email', 'mot_de_passe']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Le champ {field} est requis'}), 400

    # Vérification si l'email existe déjà
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Cet email est déjà utilisé'}), 400

    # Création du nouvel utilisateur
    user = User(
        nom=data['nom'],
        email=data['email'],
        mot_de_passe=generate_password_hash(data['mot_de_passe']),
        photo_profil=data.get('photo_profil'),
        pays=data.get('pays'),
        province=data.get('province')
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Utilisateur créé avec succès', 'user_id': user.id}), 201


# Route pour la connexion d'un utilisateur
@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or 'email' not in data or 'mot_de_passe' not in data:
        return jsonify({'error': 'Email et mot de passe requis'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.mot_de_passe, data['mot_de_passe']):
        return jsonify({'error': 'Email ou mot de passe incorrect'}), 401

    # Création du token JWT
    access_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(days=1)
    )

    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'nom': user.nom,
            'email': user.email
        }
    }), 200


# Route pour vérifier si l'utilisateur est connecté
@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # Dans une implémentation plus avancée, on pourrait blacklister le token
    return jsonify({'message': 'Déconnexion réussie'}), 200


@bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    return jsonify({
        'id': user.id,
        'nom': user.nom,
        'email': user.email,
        'photo_profil': user.photo_profil,
        'pays': user.pays,
        'province': user.province,
        'date_inscription': user.date_inscription.isoformat()
    }), 200


@bp.route("/password", methods=["PUT"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'ancien_mot_de_passe' not in data or 'nouveau_mot_de_passe' not in data:
        return jsonify({'error': 'Ancien et nouveau mot de passe requis'}), 400

    user = User.query.get(user_id)

    if not check_password_hash(user.mot_de_passe, data['ancien_mot_de_passe']):
        return jsonify({'error': 'Ancien mot de passe incorrect'}), 401

    user.mot_de_passe = generate_password_hash(data['nouveau_mot_de_passe'])
    db.session.commit()

    return jsonify({'message': 'Mot de passe modifié avec succès'}), 200


@bp.route("/password/reset", methods=["POST"])
def request_password_reset():
    data = request.get_json()

    if not data or 'email' not in data:
        return jsonify({'error': 'Email requis'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        # Pour des raisons de sécurité, on renvoie toujours un succès
        return jsonify({'message': 'Si votre email existe, vous recevrez un lien de réinitialisation'}), 200

    # TODO: Implémenter l'envoi d'email avec le token de réinitialisation
    # Pour l'instant, on renvoie juste un message de succès
    return jsonify({'message': 'Si votre email existe, vous recevrez un lien de réinitialisation'}), 200


@bp.route("/password/reset/<token>", methods=["PUT"])
def reset_password(token):
    data = request.get_json()

    if not data or 'nouveau_mot_de_passe' not in data:
        return jsonify({'error': 'Nouveau mot de passe requis'}), 400

    # TODO: Vérifier le token et réinitialiser le mot de passe
    # Pour l'instant, on renvoie une erreur
    return jsonify({'error': 'Token invalide ou expiré'}), 400
