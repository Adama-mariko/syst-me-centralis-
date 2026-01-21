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
@AuthService.require_admin()
def create_collaborateur():
    """Création d'un nouveau collaborateur"""
    try:
        data = request.get_json()
        
        # Vérification des champs requis
        required_fields = ['nom', 'prenom', 'email', 'date_embauche', 'poste']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Le champ {field} est requis'}), 400
        
        # Vérification de l'unicité de l'email
        if Collaborateur.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Cet email est déjà utilisé'}), 400
        
        # Génération du numéro d'employé
        last_collaborateur = Collaborateur.query.order_by(Collaborateur.id.desc()).first()
        numero_employe = f"EMP{(last_collaborateur.id + 1) if last_collaborateur else 1:06d}"
        
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
            salaire=data.get('salaire'),
            entreprise_actuelle_id=data.get('entreprise_actuelle_id')
        )
        
        db.session.add(collaborateur)
        db.session.commit()
        
        return jsonify({
            'message': 'Collaborateur créé avec succès',
            'collaborateur': collaborateur.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
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
        
        return jsonify({
            'message': 'Collaborateur modifié avec succès',
            'collaborateur': collaborateur.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la modification', 'error': str(e)}), 500