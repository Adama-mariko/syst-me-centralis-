from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.mouvement import Mouvement, TypeMouvement
from app.extensions import db
from app.services.auth_service import AuthService

mouvements_bp = Blueprint('mouvements', __name__)

@mouvements_bp.route('', methods=['GET'])
@jwt_required()
def get_mouvements():
    """Récupération des mouvements (traçabilité)"""
    try:
        current_user = AuthService.get_current_user()
        
        # Paramètres de filtrage
        collaborateur_id = request.args.get('collaborateur_id', type=int)
        entreprise_id = request.args.get('entreprise_id', type=int)
        type_mouvement = request.args.get('type_mouvement')
        limit = request.args.get('limit', 100, type=int)
        
        query = Mouvement.query
        
        # Filtres
        if collaborateur_id:
            query = query.filter_by(collaborateur_id=collaborateur_id)
        if entreprise_id:
            query = query.filter_by(entreprise_id=entreprise_id)
        if type_mouvement:
            query = query.filter_by(type_mouvement=TypeMouvement(type_mouvement))
        
        # Si RH, filtrer par entreprise
        if current_user.role.value == 'rh_entreprise':
            if not current_user.entreprise_id:
                return jsonify({'message': 'Utilisateur non associé à une entreprise'}), 400
            query = query.filter_by(entreprise_id=current_user.entreprise_id)
        
        # Ordre chronologique inverse et limite
        mouvements = query.order_by(Mouvement.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'mouvements': [mouvement.to_dict() for mouvement in mouvements],
            'total': query.count()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@mouvements_bp.route('', methods=['POST'])
@jwt_required()
def create_mouvement():
    """Création d'un nouveau mouvement (traçabilité)"""
    try:
        data = request.get_json()
        current_user = AuthService.get_current_user()
        
        # Vérification des champs requis
        required_fields = ['type_mouvement', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Le champ {field} est requis'}), 400
        
        # Création du mouvement
        mouvement = Mouvement(
            type_mouvement=TypeMouvement(data['type_mouvement']),
            description=data['description'],
            collaborateur_id=data.get('collaborateur_id'),
            entreprise_id=data.get('entreprise_id'),
            placement_id=data.get('placement_id'),
            remplacement_id=data.get('remplacement_id'),
            user_id=current_user.id,
            donnees_avant=data.get('donnees_avant'),
            donnees_apres=data.get('donnees_apres')
        )
        
        db.session.add(mouvement)
        db.session.commit()
        
        return jsonify({
            'message': 'Mouvement enregistré avec succès',
            'mouvement': mouvement.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la création', 'error': str(e)}), 500

@mouvements_bp.route('/<int:mouvement_id>', methods=['GET'])
@jwt_required()
def get_mouvement(mouvement_id):
    """Récupération d'un mouvement spécifique"""
    try:
        current_user = AuthService.get_current_user()
        mouvement = Mouvement.query.get_or_404(mouvement_id)
        
        # Vérification des permissions pour RH
        if (current_user.role.value == 'rh_entreprise' and 
            mouvement.entreprise_id != current_user.entreprise_id):
            return jsonify({'message': 'Accès non autorisé'}), 403
        
        return jsonify({'mouvement': mouvement.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500