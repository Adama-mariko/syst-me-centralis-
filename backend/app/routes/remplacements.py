from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.remplacement import Remplacement, TypeRemplacement, StatutRemplacement
from app.models.collaborateur import Collaborateur
from app.extensions import db
from app.services.auth_service import AuthService
from datetime import datetime

remplacements_bp = Blueprint('remplacements', __name__)

@remplacements_bp.route('', methods=['GET'])
@jwt_required()
def get_remplacements():
    """Récupération des remplacements"""
    try:
        current_user = AuthService.get_current_user()
        
        # Si RH, filtrer par entreprise des collaborateurs
        if current_user.role.value == 'rh_entreprise':
            if not current_user.entreprise_id:
                return jsonify({'message': 'Utilisateur non associé à une entreprise'}), 400
            
            # Récupérer les remplacements où les collaborateurs appartiennent à l'entreprise
            remplacements = db.session.query(Remplacement).join(
                Collaborateur, Remplacement.remplace_id == Collaborateur.id
            ).filter(
                Collaborateur.entreprise_actuelle_id == current_user.entreprise_id
            ).all()
        else:
            # Admin peut voir tous les remplacements
            remplacements = Remplacement.query.all()
        
        return jsonify({
            'remplacements': [remplacement.to_dict() for remplacement in remplacements]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@remplacements_bp.route('', methods=['POST'])
@AuthService.require_admin()
def create_remplacement():
    """Création d'un nouveau remplacement"""
    try:
        data = request.get_json()
        current_user = AuthService.get_current_user()
        
        # Vérification des champs requis
        required_fields = ['remplace_id', 'remplacant_id', 'type_remplacement', 'date_debut', 'date_fin']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Le champ {field} est requis'}), 400
        
        # Vérifier que les collaborateurs sont différents
        if data['remplace_id'] == data['remplacant_id']:
            return jsonify({'message': 'Un collaborateur ne peut pas se remplacer lui-même'}), 400
        
        # Création du remplacement
        remplacement = Remplacement(
            remplace_id=data['remplace_id'],
            remplacant_id=data['remplacant_id'],
            type_remplacement=TypeRemplacement(data['type_remplacement']),
            motif=data.get('motif'),
            date_debut=datetime.strptime(data['date_debut'], '%Y-%m-%d').date(),
            date_fin=datetime.strptime(data['date_fin'], '%Y-%m-%d').date(),
            commentaires=data.get('commentaires'),
            created_by_user_id=current_user.id
        )
        
        db.session.add(remplacement)
        db.session.commit()
        
        return jsonify({
            'message': 'Remplacement créé avec succès',
            'remplacement': remplacement.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la création', 'error': str(e)}), 500

@remplacements_bp.route('/<int:remplacement_id>', methods=['GET'])
@jwt_required()
def get_remplacement(remplacement_id):
    """Récupération d'un remplacement spécifique"""
    try:
        current_user = AuthService.get_current_user()
        remplacement = Remplacement.query.get_or_404(remplacement_id)
        
        # Vérification des permissions pour RH
        if current_user.role.value == 'rh_entreprise':
            # Vérifier que le collaborateur remplacé appartient à l'entreprise
            if remplacement.remplace.entreprise_actuelle_id != current_user.entreprise_id:
                return jsonify({'message': 'Accès non autorisé'}), 403
        
        return jsonify({'remplacement': remplacement.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@remplacements_bp.route('/<int:remplacement_id>', methods=['PUT'])
@jwt_required()
def update_remplacement(remplacement_id):
    """Modification d'un remplacement"""
    try:
        current_user = AuthService.get_current_user()
        remplacement = Remplacement.query.get_or_404(remplacement_id)
        
        # Vérification des permissions pour RH
        if current_user.role.value == 'rh_entreprise':
            if remplacement.remplace.entreprise_actuelle_id != current_user.entreprise_id:
                return jsonify({'message': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        # Mise à jour des champs
        if 'type_remplacement' in data:
            remplacement.type_remplacement = TypeRemplacement(data['type_remplacement'])
        if 'motif' in data:
            remplacement.motif = data['motif']
        if 'date_debut' in data:
            remplacement.date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
        if 'date_fin' in data:
            remplacement.date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
        if 'statut' in data:
            remplacement.statut = StatutRemplacement(data['statut'])
        if 'commentaires' in data:
            remplacement.commentaires = data['commentaires']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Remplacement modifié avec succès',
            'remplacement': remplacement.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la modification', 'error': str(e)}), 500