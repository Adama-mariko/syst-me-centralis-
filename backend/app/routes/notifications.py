from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Notification, User
from app.services.notification_service import NotificationService
from app.utils.decorators import role_required
from app.models.user import UserRole
from app.extensions import db

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Récupérer les notifications de l'utilisateur connecté"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        statut = request.args.get('statut')
        
        query = Notification.query.filter_by(destinataire_user_id=current_user_id)
        
        if statut:
            query = query.filter_by(statut=statut)
        
        notifications = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'notifications': [notif.to_dict() for notif in notifications.items],
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/all', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def get_all_notifications():
    """Récupérer toutes les notifications (admin seulement)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        statut = request.args.get('statut')
        type_notification = request.args.get('type_notification')
        
        query = Notification.query
        
        if statut:
            query = query.filter_by(statut=statut)
        
        if type_notification:
            query = query.filter_by(type_notification=type_notification)
        
        notifications = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'notifications': [notif.to_dict() for notif in notifications.items],
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/<int:notification_id>/renvoyer', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def renvoyer_notification(notification_id):
    """Renvoyer une notification"""
    try:
        success = NotificationService.envoyer_notification(notification_id)
        
        if success:
            return jsonify({'message': 'Notification renvoyée avec succès'})
        else:
            return jsonify({'error': 'Échec de l\'envoi de la notification'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/renvoyer-en-attente', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def renvoyer_notifications_en_attente():
    """Renvoyer toutes les notifications en attente"""
    try:
        NotificationService.envoyer_notifications_en_attente()
        return jsonify({'message': 'Traitement des notifications en attente lancé'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/statistiques', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def get_statistiques_notifications():
    """Récupérer les statistiques des notifications"""
    try:
        from sqlalchemy import func
        from app.models.notification import StatutNotification, TypeNotification
        
        # Statistiques par statut
        stats_statut = db.session.query(
            Notification.statut,
            func.count(Notification.id)
        ).group_by(Notification.statut).all()
        
        # Statistiques par type
        stats_type = db.session.query(
            Notification.type_notification,
            func.count(Notification.id)
        ).group_by(Notification.type_notification).all()
        
        # Notifications récentes (dernières 24h)
        from datetime import datetime, timedelta
        hier = datetime.utcnow() - timedelta(days=1)
        notifications_recentes = Notification.query.filter(
            Notification.created_at >= hier
        ).count()
        
        return jsonify({
            'statistiques': {
                'par_statut': {statut.value: count for statut, count in stats_statut},
                'par_type': {type_notif.value: count for type_notif, count in stats_type},
                'notifications_24h': notifications_recentes,
                'total': Notification.query.count()
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/notifications/<int:notification_id>/marquer-lu', methods=['PUT'])
@jwt_required()
def marquer_notification_lue(notification_id):
    """Marquer une notification comme lue"""
    try:
        current_user_id = get_jwt_identity()
        success = NotificationService.marquer_comme_lu(notification_id, current_user_id)
        
        if success:
            return jsonify({'message': 'Notification marquée comme lue'})
        else:
            return jsonify({'error': 'Notification non trouvée ou accès refusé'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/marquer-toutes-lues', methods=['PUT'])
@jwt_required()
def marquer_toutes_notifications_lues():
    """Marquer toutes les notifications comme lues"""
    try:
        current_user_id = get_jwt_identity()
        success = NotificationService.marquer_toutes_comme_lues(current_user_id)
        
        if success:
            return jsonify({'message': 'Toutes les notifications ont été marquées comme lues'})
        else:
            return jsonify({'error': 'Erreur lors du marquage'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/non-lues', methods=['GET'])
@jwt_required()
def get_notifications_non_lues():
    """Récupérer les notifications non lues de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        notifications = NotificationService.get_notifications_non_lues(current_user_id)
        
        return jsonify({
            'notifications': [notif.to_dict() for notif in notifications],
            'total': len(notifications)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/count-non-lues', methods=['GET'])
@jwt_required()
def count_notifications_non_lues():
    """Compter les notifications non lues"""
    try:
        current_user_id = get_jwt_identity()
        count = Notification.query.filter_by(
            destinataire_user_id=current_user_id,
            lu=False
        ).count()
        
        return jsonify({'count': count})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/notifications/test-email', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def test_email():
    """Tester l'envoi d'email (admin seulement)"""
    try:
        data = request.get_json()
        email = data.get('email')
        sujet = data.get('sujet', 'Test Email SMTP')
        message = data.get('message', 'Ceci est un email de test du système de gestion de personnel.')
        
        if not email:
            return jsonify({'error': 'Email requis'}), 400
        
        # Créer et envoyer la notification
        notification = NotificationService.creer_notification(
            TypeNotification.AUTRE,
            None,
            email,
            sujet,
            message
        )
        
        return jsonify({
            'message': f'Email de test envoyé à {email}',
            'notification_id': notification.id,
            'statut': notification.statut.value
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
