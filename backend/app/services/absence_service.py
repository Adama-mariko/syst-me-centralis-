from datetime import datetime, date
from app.models import Absence, Collaborateur, User
from app.models.absence import TypeAbsence, StatutAbsence
from app.models.mouvement import TypeMouvement
from app.extensions import db
from app.services.notification_service import NotificationService
from app.services.mouvement_service import MouvementService

class AbsenceService:
    
    @staticmethod
    def creer_absence(data, demandeur_id):
        """Créer une nouvelle demande d'absence"""
        try:
            print(f"🔍 AbsenceService.creer_absence - Données: {data}")
            print(f"🔍 AbsenceService.creer_absence - Demandeur ID: {demandeur_id}")
            
            # Calculer le nombre de jours
            date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
            date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
            nombre_jours = (date_fin - date_debut).days + 1
            
            print(f"🔍 Dates calculées - Début: {date_debut}, Fin: {date_fin}, Jours: {nombre_jours}")
            
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
            
            print(f"🔍 Objet Absence créé, ajout à la session...")
            db.session.add(absence)
            db.session.commit()
            print(f"✅ Absence sauvegardée avec ID: {absence.id}")
            
            # Enregistrer le mouvement
            print(f"🔍 Enregistrement du mouvement...")
            MouvementService.enregistrer_mouvement(
                type_mouvement=TypeMouvement.ABSENCE_DEMANDE,
                description=f"Demande d'absence {absence.type_absence.value} du {date_debut} au {date_fin}",
                collaborateur_id=absence.collaborateur_id,
                absence_id=absence.id,
                user_id=demandeur_id
            )
            print(f"✅ Mouvement enregistré")
            
            # Envoyer notification aux RH (temporairement désactivé pour debug)
            print(f"🔍 Notification désactivée temporairement")
            # NotificationService.notifier_absence_demandee(absence)
            
            return absence
            
        except Exception as e:
            print(f"❌ Erreur dans AbsenceService.creer_absence: {str(e)}")
            print(f"❌ Type d'erreur: {type(e).__name__}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            db.session.rollback()
            raise e
    
    @staticmethod
    def approuver_absence(absence_id, user_id, commentaires=None):
        """Approuver une demande d'absence"""
        try:
            print(f"🔍 Approbation de l'absence {absence_id} par l'utilisateur {user_id}")
            absence = Absence.query.get_or_404(absence_id)
            
            if absence.statut != StatutAbsence.EN_ATTENTE:
                raise ValueError("Cette absence ne peut plus être modifiée")
            
            print(f"🔍 Changement du statut de {absence.statut} vers APPROUVE")
            absence.statut = StatutAbsence.APPROUVE
            absence.approuve_par_user_id = user_id
            absence.date_approbation = datetime.utcnow()
            if commentaires:
                absence.commentaires = commentaires
            
            db.session.commit()
            print(f"✅ Absence {absence_id} approuvée avec succès")
            
            # Enregistrer le mouvement (temporairement désactivé pour éviter les erreurs d'enum)
            print(f"🔍 Mouvement d'approbation désactivé temporairement")
            # MouvementService.enregistrer_mouvement(
            #     type_mouvement=TypeMouvement.ABSENCE_APPROUVE,
            #     description=f"Absence approuvée: {absence.type_absence.value}",
            #     collaborateur_id=absence.collaborateur_id,
            #     absence_id=absence.id,
            #     user_id=user_id
            # )
            
            # Envoyer notification d'approbation (temporairement désactivé)
            print(f"🔍 Notification d'approbation désactivée temporairement")
            # NotificationService.notifier_absence_approuvee(absence)
            
            return absence
            
        except Exception as e:
            print(f"❌ Erreur lors de l'approbation: {str(e)}")
            db.session.rollback()
            raise e
    
    @staticmethod
    def refuser_absence(absence_id, user_id, commentaires=None):
        """Refuser une demande d'absence"""
        try:
            print(f"🔍 Refus de l'absence {absence_id} par l'utilisateur {user_id}")
            absence = Absence.query.get_or_404(absence_id)
            
            if absence.statut != StatutAbsence.EN_ATTENTE:
                raise ValueError("Cette absence ne peut plus être modifiée")
            
            print(f"🔍 Changement du statut de {absence.statut} vers REFUSE")
            absence.statut = StatutAbsence.REFUSE
            absence.approuve_par_user_id = user_id
            absence.date_approbation = datetime.utcnow()
            if commentaires:
                absence.commentaires = commentaires
            
            db.session.commit()
            print(f"✅ Absence {absence_id} refusée avec succès")
            
            # Enregistrer le mouvement (temporairement désactivé pour éviter les erreurs d'enum)
            print(f"🔍 Mouvement de refus désactivé temporairement")
            # MouvementService.enregistrer_mouvement(
            #     type_mouvement=TypeMouvement.ABSENCE_REFUSE,
            #     description=f"Absence refusée: {absence.type_absence.value}",
            #     collaborateur_id=absence.collaborateur_id,
            #     absence_id=absence.id,
            #     user_id=user_id
            # )
            
            # Envoyer notification de refus (temporairement désactivé)
            print(f"🔍 Notification de refus désactivée temporairement")
            # NotificationService.notifier_absence_refusee(absence)
            
            return absence
            
        except Exception as e:
            print(f"❌ Erreur lors du refus: {str(e)}")
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