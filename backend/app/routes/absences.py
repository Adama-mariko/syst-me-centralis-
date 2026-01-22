from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Absence, User
from app.services.absence_service import AbsenceService
from app.utils.decorators import role_required
from app.models.user import UserRole

absences_bp = Blueprint('absences', __name__)

@absences_bp.route('/absences', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def get_absences():
    """Récupérer toutes les absences"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        statut = request.args.get('statut')
        collaborateur_id = request.args.get('collaborateur_id', type=int)
        
        query = Absence.query
        
        if statut:
            query = query.filter_by(statut=statut)
        
        if collaborateur_id:
            query = query.filter_by(collaborateur_id=collaborateur_id)
        
        # Filtrer par entreprise pour les RH
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role == UserRole.RH_ENTREPRISE:
            from app.models import Collaborateur
            query = query.join(Collaborateur).filter(
                Collaborateur.entreprise_actuelle_id == current_user.entreprise_id
            )
        
        absences = query.order_by(Absence.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'absences': [absence.to_dict() for absence in absences.items],
            'total': absences.total,
            'pages': absences.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@absences_bp.route('/absences', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def create_absence():
    """Créer une nouvelle demande d'absence"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validation des données requises
        required_fields = ['collaborateur_id', 'type_absence', 'date_debut', 'date_fin']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        absence = AbsenceService.creer_absence(data, current_user_id)
        
        return jsonify({
            'message': 'Demande d\'absence créée avec succès',
            'absence': absence.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@absences_bp.route('/absences/<int:absence_id>', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def get_absence(absence_id):
    """Récupérer une absence spécifique"""
    try:
        absence = Absence.query.get_or_404(absence_id)
        
        # Vérifier les permissions
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role == UserRole.RH_ENTREPRISE:
            if absence.collaborateur.entreprise_actuelle_id != current_user.entreprise_id:
                return jsonify({'error': 'Accès non autorisé'}), 403
        
        return jsonify({'absence': absence.to_dict()})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@absences_bp.route('/absences/<int:absence_id>/approuver', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def approuver_absence(absence_id):
    """Approuver une demande d'absence"""
    try:
        data = request.get_json() or {}
        current_user_id = get_jwt_identity()
        
        absence = AbsenceService.approuver_absence(
            absence_id, 
            current_user_id, 
            data.get('commentaires')
        )
        
        return jsonify({
            'message': 'Absence approuvée avec succès',
            'absence': absence.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@absences_bp.route('/absences/<int:absence_id>/refuser', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def refuser_absence(absence_id):
    """Refuser une demande d'absence"""
    try:
        data = request.get_json() or {}
        current_user_id = get_jwt_identity()
        
        absence = AbsenceService.refuser_absence(
            absence_id, 
            current_user_id, 
            data.get('commentaires')
        )
        
        return jsonify({
            'message': 'Absence refusée',
            'absence': absence.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@absences_bp.route('/absences/en-attente', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def get_absences_en_attente():
    """Récupérer toutes les absences en attente de validation"""
    try:
        absences = AbsenceService.get_absences_en_attente()
        
        # Filtrer par entreprise pour les RH
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role == UserRole.RH_ENTREPRISE:
            absences = [a for a in absences if a.collaborateur.entreprise_actuelle_id == current_user.entreprise_id]
        
        return jsonify({
            'absences': [absence.to_dict() for absence in absences]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@absences_bp.route('/collaborateurs/<int:collaborateur_id>/absences', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def get_absences_collaborateur(collaborateur_id):
    """Récupérer toutes les absences d'un collaborateur"""
    try:
        absences = AbsenceService.get_absences_collaborateur(collaborateur_id)
        
        return jsonify({
            'absences': [absence.to_dict() for absence in absences]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500