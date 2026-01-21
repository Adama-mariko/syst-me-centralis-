from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.collaborateur import Collaborateur
from app.models.placement import Placement, StatutPlacement
from app.extensions import db
from app.services.auth_service import AuthService
from datetime import datetime

rh_bp = Blueprint('rh', __name__)

@rh_bp.route('/collaborateurs', methods=['GET'])
@AuthService.require_rh()
def get_collaborateurs_entreprise():
    """Récupération des collaborateurs de l'entreprise RH"""
    try:
        current_user = AuthService.get_current_user()
        
        if not current_user.entreprise_id:
            return jsonify({'message': 'Utilisateur non associé à une entreprise'}), 400
        
        collaborateurs = Collaborateur.query.filter_by(
            entreprise_actuelle_id=current_user.entreprise_id
        ).all()
        
        return jsonify({
            'collaborateurs': [collab.to_dict() for collab in collaborateurs]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@rh_bp.route('/collaborateurs/<int:collaborateur_id>/validate', methods=['POST'])
@AuthService.require_rh()
def validate_collaborateur(collaborateur_id):
    """Validation d'un collaborateur par les RH"""
    try:
        current_user = AuthService.get_current_user()
        collaborateur = Collaborateur.query.get_or_404(collaborateur_id)
        
        # Vérifier que le collaborateur appartient à l'entreprise
        if collaborateur.entreprise_actuelle_id != current_user.entreprise_id:
            return jsonify({'message': 'Collaborateur non autorisé'}), 403
        
        collaborateur.is_validated_by_rh = True
        collaborateur.validated_by_user_id = current_user.id
        collaborateur.validation_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Collaborateur validé avec succès',
            'collaborateur': collaborateur.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la validation', 'error': str(e)}), 500

@rh_bp.route('/placements', methods=['GET'])
@AuthService.require_rh()
def get_placements_entreprise():
    """Récupération des placements de l'entreprise"""
    try:
        current_user = AuthService.get_current_user()
        
        if not current_user.entreprise_id:
            return jsonify({'message': 'Utilisateur non associé à une entreprise'}), 400
        
        placements = Placement.query.filter_by(
            entreprise_id=current_user.entreprise_id
        ).all()
        
        return jsonify({
            'placements': [placement.to_dict() for placement in placements]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@rh_bp.route('/placements/<int:placement_id>/validate', methods=['POST'])
@AuthService.require_rh()
def validate_placement(placement_id):
    """Validation d'un placement par les RH"""
    try:
        current_user = AuthService.get_current_user()
        placement = Placement.query.get_or_404(placement_id)
        
        # Vérifier que le placement appartient à l'entreprise
        if placement.entreprise_id != current_user.entreprise_id:
            return jsonify({'message': 'Placement non autorisé'}), 403
        
        placement.validated_by_rh_user_id = current_user.id
        placement.validation_rh_date = datetime.utcnow()
        placement.statut = StatutPlacement.CONFIRME
        
        db.session.commit()
        
        return jsonify({
            'message': 'Placement validé avec succès',
            'placement': placement.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la validation', 'error': str(e)}), 500