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
        
        # Envoyer un email au contact RH de l'entreprise si renseigné
        from app.services.notification_service import NotificationService
        from app.models.notification import TypeNotification
        from app.models.user import User
        from flask_jwt_extended import get_jwt_identity
        
        try:
            # Récupérer l'utilisateur qui a créé
            current_user_id = get_jwt_identity()
            created_by_user = User.query.get(current_user_id)
            
            # Envoyer un email au contact RH de l'entreprise
            if entreprise.contact_rh_email:
                NotificationService.creer_notification(
                    TypeNotification.AUTRE,
                    None,
                    entreprise.contact_rh_email,
                    f"Votre entreprise a été ajoutée au système - {entreprise.nom}",
                    f"Bonjour {entreprise.contact_rh_nom or 'Madame, Monsieur'},\n\n"
                    f"Votre entreprise '{entreprise.nom}' a été ajoutée au système de gestion de personnel par {created_by_user.prenom} {created_by_user.nom}.\n\n"
                    f"Informations de votre entreprise:\n"
                    f"- Nom: {entreprise.nom}\n"
                    f"- SIRET: {entreprise.siret}\n"
                    f"- Adresse: {entreprise.adresse}\n"
                    f"- Ville: {entreprise.ville} ({entreprise.code_postal})\n"
                    f"- Téléphone: {entreprise.telephone or 'Non renseigné'}\n"
                    f"- Email: {entreprise.email or 'Non renseigné'}\n\n"
                    f"Vous recevrez des notifications par email pour toutes les actions concernant votre entreprise.\n\n"
                    f"Cordialement,\n"
                    f"L'équipe de gestion"
                )
        except Exception as email_error:
            print(f"Erreur lors de l'envoi de l'email de création d'entreprise: {email_error}")
        
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
            # Convertir en booléen si c'est une chaîne
            is_active = data['is_active']
            if isinstance(is_active, str):
                is_active = is_active.lower() == 'true'
            entreprise.is_active = is_active
        
        db.session.commit()
        
        # Envoyer un email aux RH de l'entreprise
        from app.services.notification_service import NotificationService
        from app.models.notification import TypeNotification
        from app.models.user import User
        from flask_jwt_extended import get_jwt_identity
        
        try:
            # Récupérer l'utilisateur qui a modifié
            current_user_id = get_jwt_identity()
            modified_by_user = User.query.get(current_user_id)
            
            # Récupérer les RH de l'entreprise
            rh_users = User.query.filter_by(entreprise_id=entreprise.id).all()
            
            # Envoyer un email à chaque RH
            for rh_user in rh_users:
                NotificationService.creer_notification(
                    TypeNotification.AUTRE,
                    rh_user.id,
                    rh_user.email,
                    f"Informations de votre entreprise mises à jour - {entreprise.nom}",
                    f"Bonjour {rh_user.prenom} {rh_user.nom},\n\n"
                    f"Les informations de votre entreprise '{entreprise.nom}' ont été mises à jour par {modified_by_user.prenom} {modified_by_user.nom}.\n\n"
                    f"Informations actuelles:\n"
                    f"- Nom: {entreprise.nom}\n"
                    f"- SIRET: {entreprise.siret or 'Non renseigné'}\n"
                    f"- Adresse: {entreprise.adresse or 'Non renseignée'}\n"
                    f"- Ville: {entreprise.ville}\n"
                    f"- Code postal: {entreprise.code_postal or 'Non renseigné'}\n"
                    f"- Téléphone: {entreprise.telephone or 'Non renseigné'}\n"
                    f"- Email: {entreprise.email or 'Non renseigné'}\n"
                    f"- Contact RH: {entreprise.contact_rh_nom or 'Non renseigné'}\n"
                    f"- Statut: {'Actif' if entreprise.is_active else 'Inactif'}\n\n"
                    f"Cordialement,\n"
                    f"L'équipe de gestion"
                )
            
            # Envoyer aussi un email au contact RH de l'entreprise si renseigné
            if entreprise.contact_rh_email:
                NotificationService.creer_notification(
                    TypeNotification.AUTRE,
                    None,
                    entreprise.contact_rh_email,
                    f"Informations de votre entreprise mises à jour - {entreprise.nom}",
                    f"Bonjour {entreprise.contact_rh_nom or 'Madame, Monsieur'},\n\n"
                    f"Les informations de votre entreprise '{entreprise.nom}' ont été mises à jour.\n\n"
                    f"Informations actuelles:\n"
                    f"- Nom: {entreprise.nom}\n"
                    f"- Ville: {entreprise.ville}\n"
                    f"- Téléphone: {entreprise.telephone or 'Non renseigné'}\n"
                    f"- Email: {entreprise.email or 'Non renseigné'}\n\n"
                    f"Pour plus d'informations, veuillez contacter l'administrateur du système.\n\n"
                    f"Cordialement,\n"
                    f"L'équipe de gestion"
                )
        except Exception as email_error:
            print(f"Erreur lors de l'envoi de l'email de modification d'entreprise: {email_error}")
        
        return jsonify({
            'message': 'Entreprise modifiée avec succès',
            'entreprise': entreprise.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la modification de l'entreprise: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Erreur lors de la modification', 'error': str(e)}), 500