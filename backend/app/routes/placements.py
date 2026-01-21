from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.placement import Placement, StatutPlacement
from app.extensions import db
from app.services.auth_service import AuthService
from datetime import datetime

placements_bp = Blueprint('placements', __name__)

@placements_bp.route('', methods=['GET'])
@jwt_required()
def get_placements():
    """Récupération des placements"""
    try:
        current_user = AuthService.get_current_user()
        
        # Si RH, filtrer par entreprise
        if current_user.role.value == 'rh_entreprise':
            if not current_user.entreprise_id:
                return jsonify({'message': 'Utilisateur non associé à une entreprise'}), 400
            placements = Placement.query.filter_by(
                entreprise_id=current_user.entreprise_id
            ).all()
        else:
            # Admin peut voir tous les placements
            placements = Placement.query.all()
        
        return jsonify({
            'placements': [placement.to_dict() for placement in placements]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@placements_bp.route('', methods=['POST'])
@AuthService.require_admin()
def create_placement():
    """Création d'un nouveau placement"""
    try:
        data = request.get_json()
        current_user = AuthService.get_current_user()
        
        # Vérification des champs requis
        required_fields = ['collaborateur_id', 'entreprise_id', 'poste_demande', 'date_debut']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Le champ {field} est requis'}), 400
        
        # Création du placement
        placement = Placement(
            collaborateur_id=data['collaborateur_id'],
            entreprise_id=data['entreprise_id'],
            poste_demande=data['poste_demande'],
            description=data.get('description'),
            date_debut=datetime.strptime(data['date_debut'], '%Y-%m-%d').date(),
            date_fin=datetime.strptime(data['date_fin'], '%Y-%m-%d').date() if data.get('date_fin') else None,
            salaire_propose=data.get('salaire_propose'),
            commentaires=data.get('commentaires'),
            created_by_user_id=current_user.id
        )
        
        db.session.add(placement)
        db.session.commit()
        
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
        
        # Vérification des permissions
        if (current_user.role.value == 'rh_entreprise' and 
            placement.entreprise_id != current_user.entreprise_id):
            return jsonify({'message': 'Accès non autorisé'}), 403
        
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
        
        # Vérification des permissions
        if (current_user.role.value == 'rh_entreprise' and 
            placement.entreprise_id != current_user.entreprise_id):
            return jsonify({'message': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        # Mise à jour des champs
        if 'poste_demande' in data:
            placement.poste_demande = data['poste_demande']
        if 'description' in data:
            placement.description = data['description']
        if 'date_debut' in data:
            placement.date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
        if 'date_fin' in data:
            placement.date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date() if data['date_fin'] else None
        if 'salaire_propose' in data:
            placement.salaire_propose = data['salaire_propose']
        if 'statut' in data:
            placement.statut = StatutPlacement(data['statut'])
        if 'commentaires' in data:
            placement.commentaires = data['commentaires']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Placement modifié avec succès',
            'placement': placement.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la modification', 'error': str(e)}), 500