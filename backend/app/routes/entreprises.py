from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.entreprise import Entreprise
from app.extensions import db
from app.services.auth_service import AuthService

entreprises_bp = Blueprint('entreprises', __name__)

@entreprises_bp.route('', methods=['GET'])
@jwt_required()
def get_entreprises():
    """Récupération des entreprises"""
    try:
        current_user = AuthService.get_current_user()
        
        # Si RH, ne voir que son entreprise
        if current_user.role.value == 'rh_entreprise':
            if not current_user.entreprise_id:
                return jsonify({'message': 'Utilisateur non associé à une entreprise'}), 400
            entreprise = Entreprise.query.get(current_user.entreprise_id)
            entreprises = [entreprise] if entreprise else []
        else:
            # Admin peut voir toutes les entreprises
            entreprises = Entreprise.query.filter_by(is_active=True).all()
        
        return jsonify({
            'entreprises': [entreprise.to_dict() for entreprise in entreprises]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@entreprises_bp.route('', methods=['POST'])
@AuthService.require_admin()
def create_entreprise():
    """Création d'une nouvelle entreprise"""
    try:
        data = request.get_json() if request.is_json else {}
        
        # Si c'est un FormData (avec fichier), récupérer les données différemment
        if not request.is_json:
            data = request.form.to_dict()
        
        # Vérification des champs requis
        required_fields = ['nom', 'siret', 'adresse', 'ville', 'code_postal']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Le champ {field} est requis'}), 400
        
        # Vérification de l'unicité du SIRET
        if Entreprise.query.filter_by(siret=data['siret']).first():
            return jsonify({'message': 'Ce SIRET est déjà utilisé'}), 400
        
        # Gestion de l'upload de logo
        logo_url = None
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename:
                import os
                import uuid
                from werkzeug.utils import secure_filename
                
                # Créer le dossier uploads/logos s'il n'existe pas
                upload_folder = os.path.join('uploads', 'logos')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Générer un nom de fichier unique
                file_extension = os.path.splitext(secure_filename(logo_file.filename))[1]
                filename = f"{uuid.uuid4().hex}{file_extension}"
                file_path = os.path.join(upload_folder, filename)
                
                # Sauvegarder le fichier
                logo_file.save(file_path)
                logo_url = f"/uploads/logos/{filename}"
        
        # Création de l'entreprise
        entreprise = Entreprise(
            nom=data['nom'],
            siret=data['siret'],
            adresse=data['adresse'],
            ville=data['ville'],
            code_postal=data['code_postal'],
            telephone=data.get('telephone'),
            email=data.get('email'),
            contact_rh_nom=data.get('contact_rh_nom'),
            contact_rh_email=data.get('contact_rh_email'),
            contact_rh_telephone=data.get('contact_rh_telephone'),
            logo_url=logo_url
        )
        
        db.session.add(entreprise)
        db.session.commit()
        
        return jsonify({
            'message': 'Entreprise créée avec succès',
            'entreprise': entreprise.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur création entreprise: {str(e)}")  # Pour debug
        return jsonify({'message': 'Erreur lors de la création', 'error': str(e)}), 500

@entreprises_bp.route('/<int:entreprise_id>', methods=['GET'])
@jwt_required()
def get_entreprise(entreprise_id):
    """Récupération d'une entreprise spécifique"""
    try:
        current_user = AuthService.get_current_user()
        entreprise = Entreprise.query.get_or_404(entreprise_id)
        
        # Vérification des permissions
        if (current_user.role.value == 'rh_entreprise' and 
            current_user.entreprise_id != entreprise_id):
            return jsonify({'message': 'Accès non autorisé'}), 403
        
        return jsonify({'entreprise': entreprise.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@entreprises_bp.route('/<int:entreprise_id>', methods=['PUT'])
@AuthService.require_admin()
def update_entreprise(entreprise_id):
    """Modification d'une entreprise"""
    try:
        entreprise = Entreprise.query.get_or_404(entreprise_id)
        data = request.get_json() if request.is_json else {}
        
        # Si c'est un FormData (avec fichier), récupérer les données différemment
        if not request.is_json:
            data = request.form.to_dict()
        
        # Gestion de l'upload de logo
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename:
                import os
                import uuid
                from werkzeug.utils import secure_filename
                
                # Créer le dossier uploads/logos s'il n'existe pas
                upload_folder = os.path.join('uploads', 'logos')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Générer un nom de fichier unique
                file_extension = os.path.splitext(secure_filename(logo_file.filename))[1]
                filename = f"{uuid.uuid4().hex}{file_extension}"
                file_path = os.path.join(upload_folder, filename)
                
                # Sauvegarder le fichier
                logo_file.save(file_path)
                entreprise.logo_url = f"/uploads/logos/{filename}"
        
        # Mise à jour des champs
        if 'nom' in data:
            entreprise.nom = data['nom']
        if 'siret' in data:
            # Vérifier l'unicité du SIRET
            existing = Entreprise.query.filter_by(siret=data['siret']).first()
            if existing and existing.id != entreprise_id:
                return jsonify({'message': 'Ce SIRET est déjà utilisé'}), 400
            entreprise.siret = data['siret']
        if 'adresse' in data:
            entreprise.adresse = data['adresse']
        if 'ville' in data:
            entreprise.ville = data['ville']
        if 'code_postal' in data:
            entreprise.code_postal = data['code_postal']
        if 'telephone' in data:
            entreprise.telephone = data['telephone']
        if 'email' in data:
            entreprise.email = data['email']
        if 'contact_rh_nom' in data:
            entreprise.contact_rh_nom = data['contact_rh_nom']
        if 'contact_rh_email' in data:
            entreprise.contact_rh_email = data['contact_rh_email']
        if 'contact_rh_telephone' in data:
            entreprise.contact_rh_telephone = data['contact_rh_telephone']
        if 'is_active' in data:
            entreprise.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Entreprise modifiée avec succès',
            'entreprise': entreprise.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la modification', 'error': str(e)}), 500