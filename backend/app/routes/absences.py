from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import text
from app.models import Absence, User
from app.models.absence import TypeAbsence, StatutAbsence
from app.services.absence_service import AbsenceService
from app.utils.decorators import role_required
from app.models.user import UserRole
from app.extensions import db

absences_bp = Blueprint('absences', __name__)

@absences_bp.route('/absences', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def get_absences():
    """Récupérer toutes les absences"""
    try:
        print(f"🔍 GET /api/absences - Début de la requête")
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        statut = request.args.get('statut')
        collaborateur_id = request.args.get('collaborateur_id', type=int)
        
        print(f"🔍 Paramètres: page={page}, per_page={per_page}, statut={statut}, collaborateur_id={collaborateur_id}")
        
        query = Absence.query
        
        if statut:
            query = query.filter_by(statut=statut)
        
        if collaborateur_id:
            query = query.filter_by(collaborateur_id=collaborateur_id)
        
        # Filtrer par entreprise pour les RH
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        print(f"🔍 Utilisateur actuel: {current_user.email}, rôle: {current_user.role}")
        
        if current_user.role == UserRole.RH_ENTREPRISE:
            from app.models import Collaborateur
            query = query.join(Collaborateur, Absence.collaborateur_id == Collaborateur.id).filter(
                Collaborateur.entreprise_actuelle_id == current_user.entreprise_id
            )
            print(f"🔍 Filtrage par entreprise: {current_user.entreprise_id}")
        
        print(f"🔍 Exécution de la requête...")
        absences = query.order_by(Absence.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        print(f"✅ Requête exécutée, {len(absences.items)} absences trouvées")
        
        return jsonify({
            'absences': [absence.to_dict() for absence in absences.items],
            'total': absences.total,
            'pages': absences.pages,
            'current_page': page
        })
        
    except Exception as e:
        print(f"❌ Erreur dans GET /api/absences: {str(e)}")
        print(f"❌ Type d'erreur: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@absences_bp.route('/absences', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def create_absence():
    """Créer une nouvelle demande d'absence"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        print(f"🔍 Données reçues pour création d'absence: {data}")
        print(f"🔍 Utilisateur actuel: {current_user_id}")
        
        # Validation des données requises
        required_fields = ['collaborateur_id', 'type_absence', 'date_debut', 'date_fin']
        for field in required_fields:
            if field not in data:
                print(f"❌ Champ manquant: {field}")
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        print(f"✅ Validation des champs OK, appel du service...")
        absence = AbsenceService.creer_absence(data, current_user_id)
        print(f"✅ Absence créée avec succès: {absence.id}")
        
        return jsonify({
            'message': 'Demande d\'absence créée avec succès',
            'absence': absence.to_dict()
        }), 201
        
    except Exception as e:
        print(f"❌ Erreur lors de la création d'absence: {str(e)}")
        print(f"❌ Type d'erreur: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
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
@role_required([UserRole.RH_ENTREPRISE])
def approuver_absence(absence_id):
    """Approuver une demande d'absence - SEULS LES RH"""
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
@role_required([UserRole.RH_ENTREPRISE])
def refuser_absence(absence_id):
    """Refuser une demande d'absence - SEULS LES RH"""
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

@absences_bp.route('/absences/<int:absence_id>', methods=['PUT'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def update_absence(absence_id):
    """Mettre à jour une absence"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        print(f"🔍 Mise à jour de l'absence {absence_id} avec les données: {data}")
        
        absence = Absence.query.get_or_404(absence_id)
        
        # Vérifier les permissions
        current_user = User.query.get(current_user_id)
        if current_user.role == UserRole.RH_ENTREPRISE:
            if absence.collaborateur.entreprise_actuelle_id != current_user.entreprise_id:
                return jsonify({'error': 'Accès non autorisé'}), 403
        
        # On ne peut modifier que les absences en attente
        if absence.statut.value != 'en_attente':
            return jsonify({'error': 'Seules les absences en attente peuvent être modifiées'}), 400
        
        # Mettre à jour les champs
        if 'type_absence' in data:
            absence.type_absence = TypeAbsence(data['type_absence'])
        if 'motif' in data:
            absence.motif = data['motif']
        if 'date_debut' in data:
            absence.date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
        if 'date_fin' in data:
            absence.date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
        if 'commentaires' in data:
            absence.commentaires = data['commentaires']
        
        # Recalculer le nombre de jours
        if absence.date_debut and absence.date_fin:
            absence.nombre_jours = (absence.date_fin - absence.date_debut).days + 1
        
        db.session.commit()
        print(f"✅ Absence {absence_id} mise à jour avec succès")
        
        return jsonify({
            'message': 'Absence mise à jour avec succès',
            'absence': absence.to_dict()
        })
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour d'absence: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@absences_bp.route('/absences/<int:absence_id>', methods=['DELETE'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def delete_absence(absence_id):
    """Supprimer une absence"""
    try:
        print(f"🔍 Tentative de suppression de l'absence {absence_id}")
        absence = Absence.query.get_or_404(absence_id)
        
        # Vérifier les permissions
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role == UserRole.RH_ENTREPRISE:
            if absence.collaborateur.entreprise_actuelle_id != current_user.entreprise_id:
                return jsonify({'error': 'Accès non autorisé'}), 403
        
        # On ne peut supprimer que les absences en attente
        if absence.statut.value != 'en_attente':
            return jsonify({'error': 'Seules les absences en attente peuvent être supprimées'}), 400
        
        print(f"🔍 Suppression de l'absence {absence_id} en cours...")
        
        # Supprimer d'abord les mouvements liés à cette absence avec du SQL brut
        # pour éviter les problèmes d'enum
        db.session.execute(text("DELETE FROM mouvements WHERE absence_id = :absence_id"), 
                          {"absence_id": absence_id})
        print(f"🔍 Mouvements liés supprimés")
        
        # Maintenant supprimer l'absence
        db.session.delete(absence)
        db.session.commit()
        print(f"✅ Absence {absence_id} et ses mouvements supprimés avec succès")
        
        return jsonify({'message': 'Absence supprimée avec succès'})
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression d'absence: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        db.session.rollback()
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