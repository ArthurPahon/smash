from datetime import timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required
)
from app.dao import UserDAO
from werkzeug.security import generate_password_hash, check_password_hash

# Création du Blueprint pour les routes d'authentification
bp = Blueprint("auth", __name__)
user_dao = UserDAO()


# Route pour l'inscription d'un utilisateur
@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Vérification des champs requis
    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Le champ {field} est requis'}), 400

    # Vérification si l'email existe déjà
    if user_dao.get_by_email(data['email']):
        return jsonify({'error': 'Cet email est déjà utilisé'}), 400

    # Préparation des données utilisateur
    user_data = {
        'name': data['name'],
        'email': data['email'],
        'password': generate_password_hash(data['password']),
        'profile_picture': data.get('profile_picture'),
        'country': data.get('country'),
        'state': data.get('state')
    }

    # Création du nouvel utilisateur
    user_id = user_dao.create(user_data)

    return jsonify({
        'message': 'Utilisateur créé avec succès',
        'user_id': user_id
    }), 201


# Route pour la connexion d'un utilisateur
@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email et mot de passe requis'}), 400

    user = user_dao.get_by_email(data['email'])

    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Email ou mot de passe incorrect'}), 401

    # Création du token JWT
    access_token = create_access_token(
        identity=str(user['id']),
        expires_delta=timedelta(days=1)
    )

    # Suppression du mot de passe avant d'envoyer les données
    user.pop('password', None)
    return jsonify({
        'access_token': access_token,
        'user': user
    }), 200


# Route pour la déconnexion
@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # Dans une implémentation plus avancée, on pourrait blacklister le token
    return jsonify({'message': 'Déconnexion réussie'}), 200


@bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = user_dao.get_by_id(user_id)

    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    # Suppression du mot de passe avant d'envoyer les données
    user.pop('password', None)
    return jsonify(user), 200


@bp.route("/password", methods=["PUT"])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Ancien et nouveau mot de passe requis'}), 400

    user = user_dao.get_by_id(user_id)

    if not user or not check_password_hash(user['password'], data['old_password']):
        return jsonify({'error': 'Ancien mot de passe incorrect'}), 401

    user_dao.update(user_id, {
        'password': generate_password_hash(data['new_password'])
    })

    return jsonify({'message': 'Mot de passe modifié avec succès'}), 200


@bp.route("/password/reset", methods=["POST"])
def request_password_reset():
    data = request.get_json()

    if not data or 'email' not in data:
        return jsonify({'error': 'Email requis'}), 400

    user = user_dao.get_by_email(data['email'])

    if not user:
        # Pour des raisons de sécurité, on renvoie toujours un succès
        msg = 'Si votre email existe, vous recevrez un lien de réinitialisation'
        return jsonify({'message': msg}), 200

    # TODO: Implémenter l'envoi d'email avec le token de réinitialisation
    # Pour l'instant, on renvoie juste un message de succès
    msg = 'Si votre email existe, vous recevrez un lien de réinitialisation'
    return jsonify({'message': msg}), 200


@bp.route("/password/reset/<token>", methods=["PUT"])
def reset_password(token):
    data = request.get_json()

    if not data or 'new_password' not in data:
        return jsonify({'error': 'Nouveau mot de passe requis'}), 400

    # TODO: Vérifier le token et réinitialiser le mot de passe
    # Pour l'instant, on renvoie une erreur
    return jsonify({'error': 'Token invalide ou expiré'}), 400
