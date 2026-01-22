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