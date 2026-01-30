from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.collaborateur import Collaborateur, StatutCollaborateur
from app.extensions import db
from app.services.auth_service import AuthService
from datetime import datetime

collaborateurs_bp = Blueprint('collaborateurs', __name__)

@collaborateurs_bp.route('', methods=['GET'])
@jwt_required()
def get_collaborateurs():
    """Récupération des collaborateurs"""
    try:
        current_user = AuthService.get_current_user()
        
        # Si RH, filtrer par entreprise
        if current_user.role.value == 'rh_entreprise':
            if not current_user.entreprise_id:
                return jsonify({'message': 'Utilisateur non associé à une entreprise'}), 400
            collaborateurs = Collaborateur.query.filter_by(
                entreprise_actuelle_id=current_user.entreprise_id
            ).all()
        else:
            # Admin peut voir tous les collaborateurs
            collaborateurs = Collaborateur.query.all()
        
        return jsonify({
            'collaborateurs': [collab.to_dict() for collab in collaborateurs]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@collaborateurs_bp.route('', methods=['POST'])
@jwt_required()
def create_collaborateur():
    """Création d'un nouveau collaborateur"""
    try:
        current_user = AuthService.get_current_user()
        
        # Vérifier que l'utilisateur peut créer des collaborateurs
        if current_user.role.value not in ['admin', 'rh_entreprise']:
            return jsonify({'message': 'Permissions insuffisantes'}), 403
        
        data = request.get_json() if request.is_json else {}
        
        # Si c'est un FormData (avec fichier), récupérer les données différemment
        if not request.is_json:
            data = request.form.to_dict()
        
        # Vérification des champs requis
        required_fields = ['nom', 'prenom', 'email', 'date_embauche', 'poste']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Le champ {field} est requis'}), 400
        
        # Vérification de l'unicité de l'email
        if Collaborateur.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Cet email est déjà utilisé'}), 400
        
        # Pour les RH, forcer l'entreprise_actuelle_id à leur entreprise
        if current_user.role.value == 'rh_entreprise':
            if not current_user.entreprise_id:
                return jsonify({'message': 'Utilisateur RH non associé à une entreprise'}), 400
            data['entreprise_actuelle_id'] = current_user.entreprise_id
        
        # Génération du numéro d'employé
        last_collaborateur = Collaborateur.query.order_by(Collaborateur.id.desc()).first()
        numero_employe = f"EMP{(last_collaborateur.id + 1) if last_collaborateur else 1:06d}"
        
        # Gestion de l'upload de photo
        photo_url = None
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file and photo_file.filename:
                import os
                import uuid
                from werkzeug.utils import secure_filename
                
                # Créer le dossier uploads/collaborateurs s'il n'existe pas
                upload_folder = os.path.join('uploads', 'collaborateurs')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Générer un nom de fichier unique
                file_extension = os.path.splitext(secure_filename(photo_file.filename))[1]
                filename = f"{uuid.uuid4().hex}{file_extension}"
                file_path = os.path.join(upload_folder, filename)
                
                # Sauvegarder le fichier
                photo_file.save(file_path)
                photo_url = f"/uploads/collaborateurs/{filename}"
        
        # Création du collaborateur
        collaborateur = Collaborateur(
            numero_employe=numero_employe,
            nom=data['nom'],
            prenom=data['prenom'],
            email=data['email'],
            telephone=data.get('telephone'),
            adresse=data.get('adresse'),
            ville=data.get('ville'),
            code_postal=data.get('code_postal'),
            date_naissance=datetime.strptime(data['date_naissance'], '%Y-%m-%d').date() if data.get('date_naissance') else None,
            date_embauche=datetime.strptime(data['date_embauche'], '%Y-%m-%d').date(),
            poste=data['poste'],
            competences=data.get('competences'),
            salaire=float(data['salaire']) if data.get('salaire') else None,
            entreprise_actuelle_id=int(data['entreprise_actuelle_id']) if data.get('entreprise_actuelle_id') else None,
            photo_url=photo_url
        )
        
        db.session.add(collaborateur)
        db.session.commit()
        
        # Créer un mouvement de traçabilité
        from app.services.mouvement_service import MouvementService
        from app.models.mouvement import TypeMouvement
        
        try:
            MouvementService.enregistrer_mouvement(
                type_mouvement=TypeMouvement.COLLABORATEUR_CREE,
                user_id=current_user.id,
                collaborateur_id=collaborateur.id,
                entreprise_id=collaborateur.entreprise_actuelle_id,
                description=f"Création du collaborateur {collaborateur.prenom} {collaborateur.nom} - Poste: {collaborateur.poste}"
            )
        except Exception as mouvement_error:
            print(f"Erreur lors de la création du mouvement: {mouvement_error}")
        
        # Envoyer un email au collaborateur
        from app.services.notification_service import NotificationService
        from app.models.notification import TypeNotification
        
        try:
            NotificationService.creer_notification(
                TypeNotification.AUTRE,
                None,
                collaborateur.email,
                "Bienvenue dans le système de gestion de personnel",
                f"Bonjour {collaborateur.prenom} {collaborateur.nom},\n\n"
                f"Vous avez été ajouté au système de gestion de personnel.\n\n"
                f"Vos informations:\n"
                f"- Numéro d'employé: {collaborateur.numero_employe}\n"
                f"- Poste: {collaborateur.poste}\n"
                f"- Date d'embauche: {collaborateur.date_embauche}\n"
                f"- Statut: {collaborateur.statut.value}\n\n"
                f"Vous recevrez des notifications par email pour toutes les actions vous concernant.\n\n"
                f"Cordialement,\n"
                f"L'équipe de gestion"
            )
        except Exception as email_error:
            print(f"Erreur lors de l'envoi de l'email: {email_error}")
        
        return jsonify({
            'message': 'Collaborateur créé avec succès',
            'collaborateur': collaborateur.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur création collaborateur: {str(e)}")  # Pour debug
        return jsonify({'message': 'Erreur lors de la création', 'error': str(e)}), 500

@collaborateurs_bp.route('/<int:collaborateur_id>', methods=['GET'])
@jwt_required()
def get_collaborateur(collaborateur_id):
    """Récupération d'un collaborateur spécifique"""
    try:
        current_user = AuthService.get_current_user()
        collaborateur = Collaborateur.query.get_or_404(collaborateur_id)
        
        # Vérification des permissions
        if (current_user.role.value == 'rh_entreprise' and 
            collaborateur.entreprise_actuelle_id != current_user.entreprise_id):
            return jsonify({'message': 'Accès non autorisé'}), 403
        
        return jsonify({'collaborateur': collaborateur.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@collaborateurs_bp.route('/<int:collaborateur_id>', methods=['PUT'])
@jwt_required()
def update_collaborateur(collaborateur_id):
    """Modification d'un collaborateur"""
    try:
        current_user = AuthService.get_current_user()
        collaborateur = Collaborateur.query.get_or_404(collaborateur_id)
        
        # Vérification des permissions
        if (current_user.role.value == 'rh_entreprise' and 
            collaborateur.entreprise_actuelle_id != current_user.entreprise_id):
            return jsonify({'message': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        # Mise à jour des champs
        if 'nom' in data:
            collaborateur.nom = data['nom']
        if 'prenom' in data:
            collaborateur.prenom = data['prenom']
        if 'email' in data:
            # Vérifier l'unicité de l'email
            existing = Collaborateur.query.filter_by(email=data['email']).first()
            if existing and existing.id != collaborateur_id:
                return jsonify({'message': 'Cet email est déjà utilisé'}), 400
            collaborateur.email = data['email']
        if 'telephone' in data:
            collaborateur.telephone = data['telephone']
        if 'poste' in data:
            collaborateur.poste = data['poste']
        if 'competences' in data:
            collaborateur.competences = data['competences']
        if 'salaire' in data:
            collaborateur.salaire = data['salaire']
        if 'statut' in data:
            collaborateur.statut = StatutCollaborateur(data['statut'])
        
        db.session.commit()
        
        # Créer un mouvement de traçabilité
        from app.services.mouvement_service import MouvementService
        from app.models.mouvement import TypeMouvement
        
        try:
            MouvementService.enregistrer_mouvement(
                type_mouvement=TypeMouvement.COLLABORATEUR_MODIFIE,
                user_id=current_user.id,
                collaborateur_id=collaborateur.id,
                entreprise_id=collaborateur.entreprise_actuelle_id,
                description=f"Modification du collaborateur {collaborateur.prenom} {collaborateur.nom}"
            )
        except Exception as mouvement_error:
            print(f"Erreur lors de la création du mouvement: {mouvement_error}")

        
        return jsonify({
            'message': 'Collaborateur modifié avec succès',
            'collaborateur': collaborateur.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la modification', 'error': str(e)}), 500