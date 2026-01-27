from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.placement import Placement, StatutPlacement
from app.models.entreprise import Entreprise
from app.models.user import UserRole
from app.models.mouvement import TypeMouvement
from app.extensions import db
from app.services.auth_service import AuthService
from app.services.mouvement_service import MouvementService
from app.services.notification_service import NotificationService
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid
import json

placements_bp = Blueprint('placements', __name__)

# Configuration pour l'upload de fichiers
UPLOAD_FOLDER = 'uploads/placements'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_document(file):
    """Sauvegarder un document et retourner l'URL"""
    if file and allowed_file(file.filename):
        # Générer un nom de fichier unique
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Sauvegarder le fichier
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Retourner l'URL relative
        return f"/uploads/placements/{unique_filename}"
    return None

@placements_bp.route('', methods=['GET'])
@jwt_required()
def get_placements():
    """Récupération des placements"""
    try:
        current_user = AuthService.get_current_user()
        
        # RH et Admin peuvent voir tous les placements
        print(f"[DEBUG] {current_user.email} (role: {current_user.role.value}) demande les placements")
        placements = Placement.query.all()
        print(f"[DEBUG] {len(placements)} placements trouvés au total")
        
        return jsonify({
            'placements': [placement.to_dict() for placement in placements]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@placements_bp.route('', methods=['POST'])
@jwt_required()
def create_placement():
    """Création d'un nouveau placement"""
    try:
        current_user = AuthService.get_current_user()
        print(f"[DEBUG] Tentative de création placement par: {current_user.email} (role: {current_user.role.value})")
        
        # Vérifier que l'utilisateur est admin, super_admin ou rh_entreprise
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.RH_ENTREPRISE]:
            print(f"[ERROR] Permissions insuffisantes pour {current_user.email}")
            return jsonify({'message': 'Permissions insuffisantes'}), 403
        
        # Récupérer les données du formulaire (FormData)
        data = request.form.to_dict()
        
        print(f"[DEBUG] Données reçues pour création placement: {data}")
        print(f"[DEBUG] Utilisateur créateur: {current_user.email} (ID: {current_user.id})")
        
        # Vérification des champs requis
        required_fields = ['collaborateur_id', 'entreprise_id', 'poste_demande', 'date_debut']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Le champ {field} est requis'}), 400
        
        print(f"[DEBUG] Placement à créer: collaborateur_id={data['collaborateur_id']}, entreprise_id={data['entreprise_id']}")
        
        # Vérifier que l'entreprise existe
        entreprise = Entreprise.query.get(data['entreprise_id'])
        if not entreprise:
            print(f"[ERROR] Entreprise {data['entreprise_id']} non trouvée")
            return jsonify({'message': 'Entreprise non trouvée'}), 400
        
        print(f"[DEBUG] Entreprise trouvée: {entreprise.nom} (ID: {entreprise.id})")
        
        # Gérer l'upload du document
        document_url = None
        if 'document' in request.files:
            file = request.files['document']
            if file.filename:
                document_url = save_document(file)
                print(f"[DEBUG] Document sauvegardé: {document_url}")
        
        # Conversion des dates
        try:
            # Gérer les différents formats de date possibles
            date_debut_str = data['date_debut']
            if 'T' in date_debut_str:
                # Format ISO avec heure (2024-01-15T00:00:00.000Z)
                date_debut = datetime.fromisoformat(date_debut_str.replace('Z', '+00:00')).date()
            else:
                # Format simple (2024-01-15)
                date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
        except Exception as e:
            return jsonify({'message': f'Format de date_debut invalide: {e}'}), 400
            
        date_fin = None
        if data.get('date_fin'):
            try:
                date_fin_str = data['date_fin']
                if 'T' in date_fin_str:
                    # Format ISO avec heure
                    date_fin = datetime.fromisoformat(date_fin_str.replace('Z', '+00:00')).date()
                else:
                    # Format simple
                    date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
            except Exception as e:
                return jsonify({'message': f'Format de date_fin invalide: {e}'}), 400
        
        # Création du placement
        placement = Placement(
            collaborateur_id=data['collaborateur_id'],
            entreprise_id=data['entreprise_id'],
            poste_demande=data['poste_demande'],
            description=data.get('description'),
            date_debut=date_debut,
            date_fin=date_fin,
            salaire_propose=data.get('salaire_propose'),
            commentaires=data.get('commentaires'),
            document_url=document_url,
            created_by_user_id=current_user.id
        )
        
        db.session.add(placement)
        db.session.commit()
        
        print(f"[DEBUG] Placement créé avec succès: ID={placement.id}, entreprise_id={placement.entreprise_id}")
        
        # Enregistrer le mouvement de traçabilité
        try:
            MouvementService.enregistrer_mouvement(
                type_mouvement=TypeMouvement.PLACEMENT_CREE,
                description=f"Placement créé: {placement.poste_demande} chez {entreprise.nom}",
                user_id=current_user.id,
                collaborateur_id=placement.collaborateur_id,
                entreprise_id=placement.entreprise_id,
                placement_id=placement.id,
                donnees_apres={
                    'poste': placement.poste_demande,
                    'date_debut': placement.date_debut.isoformat(),
                    'date_fin': placement.date_fin.isoformat() if placement.date_fin else None,
                    'salaire': float(placement.salaire_propose) if placement.salaire_propose else None
                }
            )
        except Exception as e:
            print(f"[WARNING] Erreur lors de l'enregistrement du mouvement: {e}")
        
        # Envoyer notification automatique aux RH de l'entreprise
        try:
            NotificationService.notifier_placement_cree(placement)
        except Exception as e:
            print(f"[WARNING] Erreur lors de l'envoi de la notification: {e}")
        
        return jsonify({
            'message': 'Placement créé avec succès',
            'placement': placement.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la création', 'error': str(e)}), 500

@placements_bp.route('/<int:placement_id>', methods=['GET'])
@jwt_required()
def get_placement(placement_id):
    """Récupération d'un placement spécifique"""
    try:
        current_user = AuthService.get_current_user()
        placement = Placement.query.get_or_404(placement_id)
        
        # RH et Admin peuvent voir tous les placements
        return jsonify({'placement': placement.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@placements_bp.route('/<int:placement_id>', methods=['PUT'])
@jwt_required()
def update_placement(placement_id):
    """Modification d'un placement"""
    try:
        current_user = AuthService.get_current_user()
        placement = Placement.query.get_or_404(placement_id)
        
        # RH et Admin peuvent modifier tous les placements
        # Récupérer les données du formulaire (FormData)
        data = request.form.to_dict()
        
        # Sauvegarder l'état avant modification pour la traçabilité
        donnees_avant = {
            'poste': placement.poste_demande,
            'date_debut': placement.date_debut.isoformat(),
            'date_fin': placement.date_fin.isoformat() if placement.date_fin else None,
            'salaire': float(placement.salaire_propose) if placement.salaire_propose else None,
            'statut': placement.statut.value
        }
        
        # Gérer l'upload du document
        if 'document' in request.files:
            file = request.files['document']
            if file.filename:
                # Supprimer l'ancien document si nécessaire
                if placement.document_url:
                    old_file_path = placement.document_url.replace('/uploads/', 'uploads/')
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                # Sauvegarder le nouveau document
                document_url = save_document(file)
                if document_url:
                    placement.document_url = document_url
        
        # Mise à jour des champs
        if 'poste_demande' in data:
            placement.poste_demande = data['poste_demande']
        if 'description' in data:
            placement.description = data['description']
        if 'date_debut' in data:
            date_debut_str = data['date_debut']
            if 'T' in date_debut_str:
                placement.date_debut = datetime.fromisoformat(date_debut_str.replace('Z', '+00:00')).date()
            else:
                placement.date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
        if 'date_fin' in data:
            if data['date_fin']:
                date_fin_str = data['date_fin']
                if 'T' in date_fin_str:
                    placement.date_fin = datetime.fromisoformat(date_fin_str.replace('Z', '+00:00')).date()
                else:
                    placement.date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
            else:
                placement.date_fin = None
        if 'salaire_propose' in data:
            placement.salaire_propose = data['salaire_propose']
        if 'statut' in data:
            placement.statut = StatutPlacement(data['statut'])
        if 'commentaires' in data:
            placement.commentaires = data['commentaires']
        
        db.session.commit()
        
        # Enregistrer le mouvement de traçabilité
        try:
            donnees_apres = {
                'poste': placement.poste_demande,
                'date_debut': placement.date_debut.isoformat(),
                'date_fin': placement.date_fin.isoformat() if placement.date_fin else None,
                'salaire': float(placement.salaire_propose) if placement.salaire_propose else None,
                'statut': placement.statut.value
            }
            
            MouvementService.enregistrer_mouvement(
                type_mouvement=TypeMouvement.PLACEMENT_MODIFIE,
                description=f"Placement modifié: {placement.poste_demande}",
                user_id=current_user.id,
                collaborateur_id=placement.collaborateur_id,
                entreprise_id=placement.entreprise_id,
                placement_id=placement.id,
                donnees_avant=donnees_avant,
                donnees_apres=donnees_apres
            )
        except Exception as e:
            print(f"[WARNING] Erreur lors de l'enregistrement du mouvement: {e}")
        
        return jsonify({
            'message': 'Placement modifié avec succès',
            'placement': placement.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la modification', 'error': str(e)}), 500

@placements_bp.route('/<int:placement_id>/validate', methods=['PUT'])
@jwt_required()
def validate_placement(placement_id):
    """Validation d'un placement par RH"""
    try:
        current_user = AuthService.get_current_user()
        placement = Placement.query.get_or_404(placement_id)
        
        print(f"[DEBUG] Validation placement {placement_id} par {current_user.email}")
        
        # Vérifier que l'utilisateur est RH ou Admin
        if current_user.role not in [UserRole.RH_ENTREPRISE, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            print(f"[ERROR] Permissions insuffisantes pour {current_user.email}")
            return jsonify({'message': 'Permissions insuffisantes'}), 403
        
        # Mettre à jour le statut
        placement.statut = StatutPlacement.CONFIRME
        placement.validated_by_rh_user_id = current_user.id
        placement.validation_rh_date = datetime.utcnow()
        
        db.session.commit()
        
        print(f"[DEBUG] Placement {placement_id} validé avec succès")
        
        # Enregistrer le mouvement de traçabilité
        try:
            MouvementService.enregistrer_mouvement(
                type_mouvement=TypeMouvement.PLACEMENT_VALIDE,
                description=f"Placement validé par RH: {placement.poste_demande}",
                user_id=current_user.id,
                collaborateur_id=placement.collaborateur_id,
                entreprise_id=placement.entreprise_id,
                placement_id=placement.id
            )
        except Exception as e:
            print(f"[WARNING] Erreur lors de l'enregistrement du mouvement: {e}")
        
        # Envoyer notification de validation
        try:
            NotificationService.notifier_placement_valide(placement)
        except Exception as e:
            print(f"[WARNING] Erreur lors de l'envoi de la notification: {e}")
        
        return jsonify({
            'message': 'Placement validé avec succès',
            'placement': placement.to_dict()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Erreur validation placement: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la validation', 'error': str(e)}), 500

@placements_bp.route('/<int:placement_id>', methods=['DELETE'])
@jwt_required()
def delete_placement(placement_id):
    """Suppression d'un placement"""
    try:
        current_user = AuthService.get_current_user()
        placement = Placement.query.get_or_404(placement_id)
        
        # Sauvegarder les informations avant suppression
        placement_info = {
            'poste': placement.poste_demande,
            'collaborateur_id': placement.collaborateur_id,
            'entreprise_id': placement.entreprise_id,
            'date_debut': placement.date_debut.isoformat(),
            'date_fin': placement.date_fin.isoformat() if placement.date_fin else None
        }
        
        # Supprimer le placement
        db.session.delete(placement)
        db.session.commit()
        
        # Enregistrer le mouvement de traçabilité
        try:
            MouvementService.enregistrer_mouvement(
                type_mouvement=TypeMouvement.PLACEMENT_SUPPRIME,
                description=f"Placement supprimé: {placement_info['poste']}",
                user_id=current_user.id,
                collaborateur_id=placement_info['collaborateur_id'],
                entreprise_id=placement_info['entreprise_id'],
                donnees_avant=placement_info
            )
        except Exception as e:
            print(f"[WARNING] Erreur lors de l'enregistrement du mouvement: {e}")
        
        return jsonify({'message': 'Placement supprimé avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la suppression', 'error': str(e)}), 500
