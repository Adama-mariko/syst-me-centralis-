from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
import os
import uuid
from app.models.user import User, UserRole
from app.models.entreprise import Entreprise
from app.extensions import db
from app.services.auth_service import AuthService

admin_bp = Blueprint('admin', __name__)

# Configuration pour l'upload de fichiers
UPLOAD_FOLDER = 'uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_folder():
    """Créer le dossier d'upload s'il n'existe pas"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@admin_bp.route('/users', methods=['GET'])
@AuthService.require_admin()
def get_users():
    """Récupération de tous les utilisateurs"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@admin_bp.route('/users', methods=['POST'])
@AuthService.require_admin()
def create_user():
    """Création d'un nouvel utilisateur"""
    try:
        data = request.get_json()
        
        # Vérification des champs requis
        required_fields = ['email', 'password', 'nom', 'prenom', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Le champ {field} est requis'}), 400
        
        # Vérification de l'unicité de l'email
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Cet email est déjà utilisé'}), 400
        
        # Création de l'utilisateur
        user = User(
            email=data['email'],
            nom=data['nom'],
            prenom=data['prenom'],
            role=UserRole(data['role']),
            entreprise_id=data.get('entreprise_id')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la création', 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@AuthService.require_admin()
def update_user(user_id):
    """Modification d'un utilisateur"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Mise à jour des champs
        if 'email' in data:
            # Vérifier l'unicité de l'email
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'message': 'Cet email est déjà utilisé'}), 400
            user.email = data['email']
        
        if 'nom' in data:
            user.nom = data['nom']
        if 'prenom' in data:
            user.prenom = data['prenom']
        if 'role' in data:
            user.role = UserRole(data['role'])
        if 'entreprise_id' in data:
            user.entreprise_id = data['entreprise_id']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'password' in data:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Utilisateur modifié avec succès',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la modification', 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@AuthService.require_admin()
def delete_user(user_id):
    """Suppression d'un utilisateur"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Désactiver plutôt que supprimer
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Utilisateur désactivé avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la suppression', 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/avatar', methods=['POST'])
@AuthService.require_admin()
def upload_avatar(user_id):
    """Upload d'avatar pour un utilisateur"""
    try:
        print(f"DEBUG: Upload avatar pour user_id: {user_id}")
        print(f"DEBUG: Files dans request: {list(request.files.keys())}")
        
        user = User.query.get_or_404(user_id)
        print(f"DEBUG: Utilisateur trouvé: {user.email}")
        
        # Vérifier qu'un fichier a été envoyé
        if 'avatar' not in request.files:
            print("DEBUG: Aucun fichier 'avatar' dans request.files")
            return jsonify({'message': 'Aucun fichier sélectionné'}), 400
        
        file = request.files['avatar']
        print(f"DEBUG: Fichier reçu: {file.filename}, taille: {file.content_length}")
        
        # Vérifier que le fichier n'est pas vide
        if file.filename == '':
            print("DEBUG: Nom de fichier vide")
            return jsonify({'message': 'Aucun fichier sélectionné'}), 400
        
        # Vérifier le type de fichier
        if not allowed_file(file.filename):
            print(f"DEBUG: Type de fichier non autorisé: {file.filename}")
            return jsonify({'message': 'Type de fichier non autorisé. Utilisez: png, jpg, jpeg, gif, webp'}), 400
        
        print("DEBUG: Type de fichier autorisé")
        
        # Vérifier la taille du fichier
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        print(f"DEBUG: Taille du fichier: {file_size} bytes")
        
        if file_size > MAX_FILE_SIZE:
            print(f"DEBUG: Fichier trop volumineux: {file_size} > {MAX_FILE_SIZE}")
            return jsonify({'message': 'Le fichier est trop volumineux (max 5MB)'}), 400
        
        # Créer le dossier d'upload
        create_upload_folder()
        
        # Générer un nom de fichier unique
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Sauvegarder le fichier
        file.save(file_path)
        
        # Supprimer l'ancien avatar s'il existe
        if user.avatar_url:
            old_file_path = user.avatar_url.replace('/uploads/', 'uploads/')
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        
        # Mettre à jour l'utilisateur avec la nouvelle URL
        avatar_url = f"/uploads/avatars/{unique_filename}"
        user.avatar_url = avatar_url
        db.session.commit()
        
        return jsonify({
            'message': 'Avatar mis à jour avec succès',
            'avatar_url': user.get_avatar_url()
        }), 200
        
    except Exception as e:
        print(f"DEBUG: Exception dans upload_avatar: {str(e)}")
        print(f"DEBUG: Type d'exception: {type(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de l\'upload', 'error': str(e)}), 500