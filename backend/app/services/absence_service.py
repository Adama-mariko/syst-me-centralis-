from datetime import datetime, date
from app.models import Absence, Collaborateur, User
from app.models.absence import TypeAbsence, StatutAbsence
from app.extensions import db
from app.services.notification_service import NotificationService
from app.services.mouvement_service import MouvementService

class AbsenceService:
    
    @staticmethod
    def creer_absence(data, demandeur_id):
        """Créer une nouvelle demande d'absence"""
        try:
            # Calculer le nombre de jours
            date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
            date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
            nombre_jours = (date_fin - date_debut).days + 1
            
            absence = Absence(
                collaborateur_id=data['collaborateur_id'],
                type_absence=TypeAbsence(data['type_absence']),
                motif=data.get('motif'),
                date_debut=date_debut,
                date_fin=date_fin,
                nombre_jours=nombre_jours,
                commentaires=data.get('commentaires'),
                demande_par_collaborateur_id=demandeur_id,
                statut=StatutAbsence.EN_ATTENTE
            )
            
            db.session.add(absence)
            db.session.commit()
            
            # Enregistrer le mouvement
            MouvementService.enregistrer_mouvement(
                type_mouvement='absence_demande',
                description=f"Demande d'absence {absence.type_absence.value} du {date_debut} au {date_fin}",
                collaborateur_id=absence.collaborateur_id,
                absence_id=absence.id,
                user_id=demandeur_id
            )
            
            # Envoyer notification aux RH
            NotificationService.notifier_absence_demandee(absence)
            
            return absence
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def approuver_absence(absence_id, user_id, commentaires=None):
        """Approuver une demande d'absence"""
        try:
            absence = Absence.query.get_or_404(absence_id)
            
            if absence.statut != StatutAbsence.EN_ATTENTE:
                raise ValueError("Cette absence ne peut plus être modifiée")
            
            absence.statut = StatutAbsence.APPROUVE
            absence.approuve_par_user_id = user_id
            absence.date_approbation = datetime.utcnow()
            if commentaires:
                absence.commentaires = commentaires
            
            db.session.commit()
            
            # Enregistrer le mouvement
            MouvementService.enregistrer_mouvement(
                type_mouvement='absence_approuve',
                description=f"Absence approuvée: {absence.type_absence.value}",
                collaborateur_id=absence.collaborateur_id,
                absence_id=absence.id,
                user_id=user_id
            )
            
            # Envoyer notification d'approbation
            NotificationService.notifier_absence_approuvee(absence)
            
            return absence
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def refuser_absence(absence_id, user_id, commentaires=None):
        """Refuser une demande d'absence"""
        try:
            absence = Absence.query.get_or_404(absence_id)
            
            if absence.statut != StatutAbsence.EN_ATTENTE:
                raise ValueError("Cette absence ne peut plus être modifiée")
            
            absence.statut = StatutAbsence.REFUSE
            absence.approuve_par_user_id = user_id
            absence.date_approbation = datetime.utcnow()
            if commentaires:
                absence.commentaires = commentaires
            
            db.session.commit()
            
            # Enregistrer le mouvement
            MouvementService.enregistrer_mouvement(
                type_mouvement='absence_refuse',
                description=f"Absence refusée: {absence.type_absence.value}",
                collaborateur_id=absence.collaborateur_id,
                absence_id=absence.id,
                user_id=user_id
            )
            
            # Envoyer notification de refus
            NotificationService.notifier_absence_refusee(absence)
            
            return absence
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_absences_en_attente():
        """Récupérer toutes les absences en attente de validation"""
        return Absence.query.filter_by(statut=StatutAbsence.EN_ATTENTE).all()
    
    @staticmethod
    def get_absences_collaborateur(collaborateur_id):
        """Récupérer toutes les absences d'un collaborateur"""
        return Absence.query.filter_by(collaborateur_id=collaborateur_id).all()
    
    @staticmethod
    def get_absences_periode(date_debut, date_fin, entreprise_id=None):
        """Récupérer les absences sur une période donnée"""
        query = Absence.query.filter(
            Absence.date_debut >= date_debut,
            Absence.date_fin <= date_fin
        )
        
        if entreprise_id:
            query = query.join(Collaborateur).filter(
                Collaborateur.entreprise_actuelle_id == entreprise_id
            )
        
        return query.all()