from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Mouvement, SecurityLog, User
from app.services.mouvement_service import MouvementService
from app.utils.decorators import role_required
from app.models.user import UserRole
from app.extensions import db
from datetime import datetime, timedelta

tracabilite_bp = Blueprint('tracabilite', __name__)

@tracabilite_bp.route('/mouvements', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def get_mouvements():
    """Récupérer tous les mouvements"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        type_mouvement = request.args.get('type_mouvement')
        user_id = request.args.get('user_id', type=int)
        collaborateur_id = request.args.get('collaborateur_id', type=int)
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        query = Mouvement.query
        
        if type_mouvement:
            query = query.filter_by(type_mouvement=type_mouvement)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if collaborateur_id:
            query = query.filter_by(collaborateur_id=collaborateur_id)
        
        if date_debut:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')
            query = query.filter(Mouvement.created_at >= date_debut_obj)
        
        if date_fin:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Mouvement.created_at < date_fin_obj)
        
        mouvements = query.order_by(Mouvement.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'mouvements': [mouvement.to_dict() for mouvement in mouvements.items],
            'total': mouvements.total,
            'pages': mouvements.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tracabilite_bp.route('/mouvements/collaborateur/<int:collaborateur_id>', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def get_historique_collaborateur(collaborateur_id):
    """Récupérer l'historique complet d'un collaborateur"""
    try:
        mouvements = MouvementService.get_historique_collaborateur(collaborateur_id)
        
        return jsonify({
            'historique': [mouvement.to_dict() for mouvement in mouvements]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tracabilite_bp.route('/mouvements/placement/<int:placement_id>', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def get_historique_placement(placement_id):
    """Récupérer l'historique d'un placement"""
    try:
        mouvements = MouvementService.get_historique_placement(placement_id)
        
        return jsonify({
            'historique': [mouvement.to_dict() for mouvement in mouvements]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tracabilite_bp.route('/mouvements/utilisateur/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def get_activite_utilisateur(user_id):
    """Récupérer l'activité récente d'un utilisateur"""
    try:
        limite = request.args.get('limite', 50, type=int)
        mouvements = MouvementService.get_activite_utilisateur(user_id, limite)
        
        return jsonify({
            'activite': [mouvement.to_dict() for mouvement in mouvements]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tracabilite_bp.route('/mouvements/mon-activite', methods=['GET'])
@jwt_required()
def get_mon_activite():
    """Récupérer l'activité de l'utilisateur connecté"""
    try:
        current_user_id = get_jwt_identity()
        limite = request.args.get('limite', 20, type=int)
        
        mouvements = MouvementService.get_activite_utilisateur(current_user_id, limite)
        
        return jsonify({
            'activite': [mouvement.to_dict() for mouvement in mouvements]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tracabilite_bp.route('/security-logs', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN])
def get_security_logs():
    """Récupérer les logs de sécurité (super admin seulement)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        action = request.args.get('action')
        statut = request.args.get('statut')
        user_id = request.args.get('user_id', type=int)
        
        query = SecurityLog.query
        
        if action:
            query = query.filter_by(action=action)
        
        if statut:
            query = query.filter_by(statut=statut)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        logs = query.order_by(SecurityLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tracabilite_bp.route('/mouvements/statistiques', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def get_statistiques_mouvements():
    """Récupérer les statistiques des mouvements"""
    try:
        from sqlalchemy import func
        
        # Statistiques par type de mouvement
        stats_type = db.session.query(
            Mouvement.type_mouvement,
            func.count(Mouvement.id)
        ).group_by(Mouvement.type_mouvement).all()
        
        # Statistiques par utilisateur (top 10)
        stats_users = db.session.query(
            User.nom,
            User.prenom,
            func.count(Mouvement.id)
        ).join(Mouvement).group_by(User.id).order_by(
            func.count(Mouvement.id).desc()
        ).limit(10).all()
        
        # Activité des dernières 24h
        hier = datetime.utcnow() - timedelta(days=1)
        activite_24h = Mouvement.query.filter(
            Mouvement.created_at >= hier
        ).count()
        
        # Activité par heure (dernières 24h)
        activite_horaire = []
        for i in range(24):
            heure_debut = datetime.utcnow() - timedelta(hours=i+1)
            heure_fin = datetime.utcnow() - timedelta(hours=i)
            
            count = Mouvement.query.filter(
                Mouvement.created_at >= heure_debut,
                Mouvement.created_at < heure_fin
            ).count()
            
            activite_horaire.append({
                'heure': heure_debut.strftime('%H:00'),
                'count': count
            })
        
        return jsonify({
            'statistiques': {
                'par_type': {type_mouv.value: count for type_mouv, count in stats_type},
                'top_utilisateurs': [
                    {'nom': f"{nom} {prenom}", 'count': count} 
                    for nom, prenom, count in stats_users
                ],
                'activite_24h': activite_24h,
                'activite_horaire': list(reversed(activite_horaire)),
                'total': Mouvement.query.count()
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500