import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from app.models import Notification, User
from app.models.notification import TypeNotification, StatutNotification
from app.extensions import db
import os

class NotificationService:
    
    @staticmethod
    def creer_notification(type_notif, destinataire_user_id, destinataire_email, sujet, message, 
                          placement_id=None, absence_id=None, remplacement_id=None):
        """Créer une nouvelle notification"""
        try:
            notification = Notification(
                type_notification=type_notif,
                destinataire_user_id=destinataire_user_id,
                destinataire_email=destinataire_email,
                sujet=sujet,
                message=message,
                placement_id=placement_id,
                absence_id=absence_id,
                remplacement_id=remplacement_id
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Essayer d'envoyer immédiatement
            NotificationService.envoyer_notification(notification.id)
            
            return notification
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def envoyer_notification(notification_id):
        """Envoyer une notification par email"""
        try:
            notification = Notification.query.get(notification_id)
            if not notification:
                return False
            
            # Configuration SMTP (à adapter selon votre serveur)
            smtp_server = os.getenv('SMTP_SERVER', 'localhost')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME', '')
            smtp_password = os.getenv('SMTP_PASSWORD', '')
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = smtp_username or 'noreply@personnel.com'
            msg['To'] = notification.destinataire_email
            msg['Subject'] = notification.sujet
            
            # Corps du message
            body = f"""
            {notification.message}
            
            ---
            Système de Gestion de Personnel
            Ceci est un message automatique, ne pas répondre.
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Envoyer l'email (simulation si pas de serveur SMTP configuré)
            if smtp_server == 'localhost' and not smtp_username:
                # Mode simulation pour développement
                print(f"[EMAIL SIMULATION] To: {notification.destinataire_email}")
                print(f"[EMAIL SIMULATION] Subject: {notification.sujet}")
                print(f"[EMAIL SIMULATION] Body: {notification.message}")
                
                notification.statut = StatutNotification.ENVOYE
                notification.date_envoi = datetime.utcnow()
            else:
                # Envoi réel
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                text = msg.as_string()
                server.sendmail(smtp_username, notification.destinataire_email, text)
                server.quit()
                
                notification.statut = StatutNotification.ENVOYE
                notification.date_envoi = datetime.utcnow()
            
            notification.tentatives += 1
            db.session.commit()
            
            return True
            
        except Exception as e:
            notification.statut = StatutNotification.ECHEC
            notification.tentatives += 1
            notification.erreur_message = str(e)
            db.session.commit()
            return False
    
    @staticmethod
    def notifier_placement_cree(placement):
        """Notifier la création d'un placement"""
        # Notifier les RH de l'entreprise
        rh_users = User.query.filter_by(
            entreprise_id=placement.entreprise_id,
            role='rh_entreprise'
        ).all()
        
        for rh_user in rh_users:
            NotificationService.creer_notification(
                TypeNotification.PLACEMENT_CREE,
                rh_user.id,
                rh_user.email,
                f"Nouveau placement proposé - {placement.collaborateur.nom} {placement.collaborateur.prenom}",
                f"Un nouveau placement a été proposé pour {placement.collaborateur.nom} {placement.collaborateur.prenom} "
                f"au poste de {placement.poste_demande} dans votre entreprise {placement.entreprise.nom}. "
                f"Veuillez valider ou refuser cette proposition.",
                placement_id=placement.id
            )
    
    @staticmethod
    def notifier_placement_valide(placement):
        """Notifier la validation d'un placement"""
        NotificationService.creer_notification(
            TypeNotification.PLACEMENT_VALIDE,
            None,
            placement.collaborateur.email,
            f"Placement validé - {placement.poste_demande}",
            f"Félicitations ! Votre placement au poste de {placement.poste_demande} "
            f"chez {placement.entreprise.nom} a été validé. "
            f"Date de début: {placement.date_debut}",
            placement_id=placement.id
        )
    
    @staticmethod
    def notifier_absence_demandee(absence):
        """Notifier une demande d'absence"""
        # Notifier les RH
        rh_users = User.query.filter_by(role='rh_entreprise').all()
        
        for rh_user in rh_users:
            NotificationService.creer_notification(
                TypeNotification.ABSENCE_DEMANDEE,
                rh_user.id,
                rh_user.email,
                f"Demande d'absence - {absence.collaborateur.nom} {absence.collaborateur.prenom}",
                f"Une demande d'absence de type {absence.type_absence.value} a été soumise "
                f"par {absence.collaborateur.nom} {absence.collaborateur.prenom} "
                f"du {absence.date_debut} au {absence.date_fin} ({absence.nombre_jours} jours). "
                f"Motif: {absence.motif or 'Non spécifié'}",
                absence_id=absence.id
            )
    
    @staticmethod
    def notifier_absence_approuvee(absence):
        """Notifier l'approbation d'une absence"""
        NotificationService.creer_notification(
            TypeNotification.ABSENCE_APPROUVEE,
            None,
            absence.collaborateur.email,
            f"Absence approuvée - {absence.type_absence.value}",
            f"Votre demande d'absence de type {absence.type_absence.value} "
            f"du {absence.date_debut} au {absence.date_fin} a été approuvée. "
            f"Commentaires: {absence.commentaires or 'Aucun commentaire'}",
            absence_id=absence.id
        )
    
    @staticmethod
    def notifier_absence_refusee(absence):
        """Notifier le refus d'une absence"""
        NotificationService.creer_notification(
            TypeNotification.ABSENCE_REFUSEE,
            None,
            absence.collaborateur.email,
            f"Absence refusée - {absence.type_absence.value}",
            f"Votre demande d'absence de type {absence.type_absence.value} "
            f"du {absence.date_debut} au {absence.date_fin} a été refusée. "
            f"Raison: {absence.commentaires or 'Non spécifiée'}",
            absence_id=absence.id
        )
    
    @staticmethod
    def envoyer_notifications_en_attente():
        """Envoyer toutes les notifications en attente"""
        notifications = Notification.query.filter_by(
            statut=StatutNotification.EN_ATTENTE
        ).filter(
            Notification.tentatives < 3
        ).all()
        
        for notification in notifications:
            NotificationService.envoyer_notification(notification.id)

    @staticmethod
    def notifier_collaborateur_cree(collaborateur, created_by_user):
        """Notifier un collaborateur qu'il a été créé dans le système"""
        NotificationService.creer_notification(
            TypeNotification.AUTRE,
            None,  # Pas d'utilisateur dans l'app
            collaborateur.email,
            "Bienvenue dans le système de gestion de personnel",
            f"Bonjour {collaborateur.prenom} {collaborateur.nom},\n\n"
            f"Vous avez été ajouté au système de gestion de personnel par {created_by_user.prenom} {created_by_user.nom}.\n\n"
            f"Informations:\n"
            f"- Poste: {collaborateur.poste}\n"
            f"- Date d'embauche: {collaborateur.date_embauche}\n"
            f"- Statut: {collaborateur.statut.value}\n\n"
            f"Vous recevrez des notifications par email pour toutes les actions vous concernant.\n\n"
            f"Cordialement,\n"
            f"L'équipe de gestion"
        )
    
    @staticmethod
    def notifier_collaborateur_modifie(collaborateur, modified_by_user, changements):
        """Notifier un collaborateur que ses informations ont été modifiées"""
        NotificationService.creer_notification(
            TypeNotification.AUTRE,
            None,
            collaborateur.email,
            "Vos informations ont été mises à jour",
            f"Bonjour {collaborateur.prenom} {collaborateur.nom},\n\n"
            f"Vos informations ont été mises à jour par {modified_by_user.prenom} {modified_by_user.nom}.\n\n"
            f"Changements effectués:\n{changements}\n\n"
            f"Cordialement,\n"
            f"L'équipe de gestion"
        )
    
    @staticmethod
    def notifier_placement_au_collaborateur(placement):
        """Notifier le collaborateur d'un nouveau placement"""
        NotificationService.creer_notification(
            TypeNotification.PLACEMENT_CREE,
            None,
            placement.collaborateur.email,
            f"Nouveau placement proposé - {placement.entreprise.nom}",
            f"Bonjour {placement.collaborateur.prenom} {placement.collaborateur.nom},\n\n"
            f"Un nouveau placement vous a été proposé:\n\n"
            f"- Entreprise: {placement.entreprise.nom}\n"
            f"- Poste: {placement.poste_demande}\n"
            f"- Date de début: {placement.date_debut}\n"
            f"- Date de fin: {placement.date_fin if placement.date_fin else 'Non définie'}\n"
            f"- Salaire proposé: {placement.salaire_propose} FCFA" if placement.salaire_propose else "",
            f"\n\nCe placement est en attente de validation par les RH de l'entreprise.\n\n"
            f"Cordialement,\n"
            f"L'équipe de gestion",
            placement_id=placement.id
        )
    
    @staticmethod
    def notifier_remplacement_au_remplace(remplacement):
        """Notifier le collaborateur remplacé"""
        NotificationService.creer_notification(
            TypeNotification.REMPLACEMENT_CREE,
            None,
            remplacement.remplace.email,
            f"Information: Remplacement prévu",
            f"Bonjour {remplacement.remplace.prenom} {remplacement.remplace.nom},\n\n"
            f"Un remplacement a été organisé pour votre absence:\n\n"
            f"- Remplaçant: {remplacement.remplacant.prenom} {remplacement.remplacant.nom}\n"
            f"- Type: {remplacement.type_remplacement.value}\n"
            f"- Du {remplacement.date_debut} au {remplacement.date_fin}\n"
            f"- Motif: {remplacement.motif or 'Non spécifié'}\n\n"
            f"Cordialement,\n"
            f"L'équipe de gestion",
            remplacement_id=remplacement.id
        )
    
    @staticmethod
    def notifier_placement_expire_bientot(placement, jours_restants):
        """Notifier qu'un placement expire bientôt"""
        from app.models.user import User, UserRole
        
        # Notifier les admins
        admins = User.query.filter(
            User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])
        ).all()
        
        for admin in admins:
            NotificationService.creer_notification(
                TypeNotification.PLACEMENT_EXPIRE_BIENTOT,
                admin.id,
                admin.email,
                f"Placement expire dans {jours_restants} jours",
                f"Le placement de {placement.collaborateur.prenom} {placement.collaborateur.nom} "
                f"chez {placement.entreprise.nom} expire dans {jours_restants} jours "
                f"(Date de fin: {placement.date_fin}). "
                f"Pensez à renouveler ou créer un nouveau placement.",
                placement_id=placement.id
            )
    
    @staticmethod
    def notifier_conflit_detecte(user_id, message, placement_id=None):
        """Notifier la détection d'un conflit"""
        user = User.query.get(user_id)
        if user:
            NotificationService.creer_notification(
                TypeNotification.CONFLIT_DETECTE,
                user_id,
                user.email,
                "Conflit détecté",
                message,
                placement_id=placement_id
            )
    
    @staticmethod
    def marquer_comme_lu(notification_id, user_id):
        """Marquer une notification comme lue"""
        try:
            notification = Notification.query.get(notification_id)
            if notification and notification.destinataire_user_id == user_id:
                notification.lu = True
                notification.date_lecture = datetime.utcnow()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def marquer_toutes_comme_lues(user_id):
        """Marquer toutes les notifications d'un utilisateur comme lues"""
        try:
            notifications = Notification.query.filter_by(
                destinataire_user_id=user_id,
                lu=False
            ).all()
            
            for notification in notifications:
                notification.lu = True
                notification.date_lecture = datetime.utcnow()
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def get_notifications_non_lues(user_id):
        """Récupérer les notifications non lues d'un utilisateur"""
        return Notification.query.filter_by(
            destinataire_user_id=user_id,
            lu=False
        ).order_by(Notification.created_at.desc()).all()
    
    @staticmethod
    def get_notifications_utilisateur(user_id, limit=50):
        """Récupérer toutes les notifications d'un utilisateur"""
        return Notification.query.filter_by(
            destinataire_user_id=user_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()
