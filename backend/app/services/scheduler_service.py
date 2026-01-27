"""
Service de planification des tâches automatiques
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, date
from app.extensions import db
from app.models.placement import Placement, StatutPlacement
from app.models.remplacement import Remplacement, StatutRemplacement
from app.models.collaborateur import Collaborateur, StatutCollaborateur
from app.models.absence import Absence, StatutAbsence
from app.services.notification_service import NotificationService
from app.services.mouvement_service import MouvementService
from app.models.mouvement import TypeMouvement
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerService:
    """Service de gestion des tâches planifiées"""
    
    scheduler = None
    
    @staticmethod
    def init_scheduler(app):
        """Initialiser le scheduler avec le contexte Flask"""
        if SchedulerService.scheduler is None:
            SchedulerService.scheduler = BackgroundScheduler()
            
            # Tâche quotidienne à 8h00 - Mise à jour des statuts
            SchedulerService.scheduler.add_job(
                func=lambda: SchedulerService.mettre_a_jour_statuts(app),
                trigger=CronTrigger(hour=8, minute=0),
                id='mise_a_jour_statuts',
                name='Mise à jour automatique des statuts',
                replace_existing=True
            )
            
            # Tâche quotidienne à 8h30 - Rappels placements
            SchedulerService.scheduler.add_job(
                func=lambda: SchedulerService.envoyer_rappels_placements(app),
                trigger=CronTrigger(hour=8, minute=30),
                id='rappels_placements',
                name='Rappels placements expirant bientôt',
                replace_existing=True
            )
            
            # Tâche quotidienne à 9h00 - Rappels validations
            SchedulerService.scheduler.add_job(
                func=lambda: SchedulerService.envoyer_rappels_validations(app),
                trigger=CronTrigger(hour=9, minute=0),
                id='rappels_validations',
                name='Rappels validations en attente',
                replace_existing=True
            )
            
            # Tâche hebdomadaire - Lundi à 9h00
            SchedulerService.scheduler.add_job(
                func=lambda: SchedulerService.generer_rapport_hebdomadaire(app),
                trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
                id='rapport_hebdomadaire',
                name='Génération rapport hebdomadaire',
                replace_existing=True
            )
            
            # Tâche mensuelle - 1er du mois à 9h00
            SchedulerService.scheduler.add_job(
                func=lambda: SchedulerService.generer_rapport_mensuel(app),
                trigger=CronTrigger(day=1, hour=9, minute=0),
                id='rapport_mensuel',
                name='Génération rapport mensuel',
                replace_existing=True
            )
            
            SchedulerService.scheduler.start()
            logger.info("✅ Scheduler démarré avec succès")
            logger.info(f"📅 Tâches planifiées: {len(SchedulerService.scheduler.get_jobs())}")
    
    @staticmethod
    def mettre_a_jour_statuts(app):
        """Proposer des mises à jour de statuts (nécessite validation admin/RH)"""
        with app.app_context():
            try:
                logger.info("🔄 Vérification des statuts à mettre à jour...")
                aujourd_hui = date.today()
                from app.models.user import User, UserRole
                
                # Récupérer les admins
                admins = User.query.filter(
                    User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])
                ).all()
                
                compteurs = {
                    'placements_a_demarrer': 0,
                    'placements_a_terminer': 0,
                    'remplacements_a_demarrer': 0,
                    'remplacements_a_terminer': 0
                }
                
                # 1. Placements qui devraient commencer aujourd'hui
                placements_a_demarrer = Placement.query.filter(
                    Placement.date_debut == aujourd_hui,
                    Placement.statut == StatutPlacement.CONFIRME
                ).all()
                
                for placement in placements_a_demarrer:
                    compteurs['placements_a_demarrer'] += 1
                    
                    # Envoyer notification de validation aux admins
                    for admin in admins:
                        NotificationService.creer_notification(
                            TypeNotification.PLACEMENT_MODIFIE,
                            admin.id,
                            admin.email,
                            f"Validation requise: Placement à démarrer",
                            f"Le placement de {placement.collaborateur.prenom} {placement.collaborateur.nom} "
                            f"chez {placement.entreprise.nom} devrait démarrer aujourd'hui. "
                            f"Veuillez valider le changement de statut vers 'En cours'.",
                            placement_id=placement.id
                        )
                    
                    logger.info(f"✓ Validation demandée pour placement {placement.id} (à démarrer)")
                
                # 2. Placements qui devraient se terminer aujourd'hui
                placements_a_terminer = Placement.query.filter(
                    Placement.date_fin == aujourd_hui,
                    Placement.statut == StatutPlacement.EN_COURS
                ).all()
                
                for placement in placements_a_terminer:
                    compteurs['placements_a_terminer'] += 1
                    
                    # Envoyer notification de validation aux admins
                    for admin in admins:
                        NotificationService.creer_notification(
                            TypeNotification.PLACEMENT_MODIFIE,
                            admin.id,
                            admin.email,
                            f"Validation requise: Placement à terminer",
                            f"Le placement de {placement.collaborateur.prenom} {placement.collaborateur.nom} "
                            f"chez {placement.entreprise.nom} devrait se terminer aujourd'hui. "
                            f"Veuillez valider le changement de statut vers 'Terminé'.",
                            placement_id=placement.id
                        )
                    
                    logger.info(f"✓ Validation demandée pour placement {placement.id} (à terminer)")
                
                # 3. Remplacements qui devraient commencer aujourd'hui
                remplacements_a_demarrer = Remplacement.query.filter(
                    Remplacement.date_debut == aujourd_hui,
                    Remplacement.statut == StatutRemplacement.PLANIFIE
                ).all()
                
                for remplacement in remplacements_a_demarrer:
                    compteurs['remplacements_a_demarrer'] += 1
                    
                    # Envoyer notification de validation aux admins
                    for admin in admins:
                        NotificationService.creer_notification(
                            TypeNotification.REMPLACEMENT_MODIFIE,
                            admin.id,
                            admin.email,
                            f"Validation requise: Remplacement à démarrer",
                            f"Le remplacement de {remplacement.remplace.prenom} {remplacement.remplace.nom} "
                            f"par {remplacement.remplacant.prenom} {remplacement.remplacant.nom} "
                            f"devrait démarrer aujourd'hui. Veuillez valider.",
                            remplacement_id=remplacement.id
                        )
                    
                    logger.info(f"✓ Validation demandée pour remplacement {remplacement.id} (à démarrer)")
                
                # 4. Remplacements qui devraient se terminer aujourd'hui
                remplacements_a_terminer = Remplacement.query.filter(
                    Remplacement.date_fin == aujourd_hui,
                    Remplacement.statut == StatutRemplacement.EN_COURS
                ).all()
                
                for remplacement in remplacements_a_terminer:
                    compteurs['remplacements_a_terminer'] += 1
                    
                    # Envoyer notification de validation aux admins
                    for admin in admins:
                        NotificationService.creer_notification(
                            TypeNotification.REMPLACEMENT_MODIFIE,
                            admin.id,
                            admin.email,
                            f"Validation requise: Remplacement à terminer",
                            f"Le remplacement de {remplacement.remplace.prenom} {remplacement.remplace.nom} "
                            f"par {remplacement.remplacant.prenom} {remplacement.remplacant.nom} "
                            f"devrait se terminer aujourd'hui. Veuillez valider.",
                            remplacement_id=remplacement.id
                        )
                    
                    logger.info(f"✓ Validation demandée pour remplacement {remplacement.id} (à terminer)")
                
                db.session.commit()
                
                logger.info(f"✅ Vérification terminée:")
                logger.info(f"   - {compteurs['placements_a_demarrer']} placements à démarrer (validation requise)")
                logger.info(f"   - {compteurs['placements_a_terminer']} placements à terminer (validation requise)")
                logger.info(f"   - {compteurs['remplacements_a_demarrer']} remplacements à démarrer (validation requise)")
                logger.info(f"   - {compteurs['remplacements_a_terminer']} remplacements à terminer (validation requise)")
                
                return compteurs
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la vérification des statuts: {e}")
                db.session.rollback()
                return None
    
    @staticmethod
    def envoyer_rappels_placements(app):
        """Envoyer des rappels pour les placements expirant bientôt"""
        with app.app_context():
            try:
                logger.info("🔔 Envoi des rappels pour placements expirant bientôt...")
                
                # Placements se terminant dans 7 jours
                date_limite = date.today() + timedelta(days=7)
                
                placements = Placement.query.filter(
                    Placement.date_fin == date_limite,
                    Placement.statut == StatutPlacement.EN_COURS
                ).all()
                
                for placement in placements:
                    NotificationService.notifier_placement_expire_bientot(placement, 7)
                    logger.info(f"✓ Rappel envoyé pour placement {placement.id}")
                
                logger.info(f"✅ {len(placements)} rappels envoyés")
                return len(placements)
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'envoi des rappels: {e}")
                return 0
    
    @staticmethod
    def envoyer_rappels_validations(app):
        """Envoyer des rappels pour les validations en attente"""
        with app.app_context():
            try:
                logger.info("🔔 Envoi des rappels pour validations en attente...")
                
                # Placements en attente depuis plus de 48h
                date_limite = datetime.utcnow() - timedelta(hours=48)
                
                placements = Placement.query.filter(
                    Placement.statut == StatutPlacement.EN_ATTENTE,
                    Placement.created_at < date_limite
                ).all()
                
                # Absences en attente depuis plus de 24h
                date_limite_absence = datetime.utcnow() - timedelta(hours=24)
                
                absences = Absence.query.filter(
                    Absence.statut == StatutAbsence.EN_ATTENTE,
                    Absence.created_at < date_limite_absence
                ).all()
                
                total_rappels = len(placements) + len(absences)
                
                # TODO: Envoyer les rappels aux RH
                
                logger.info(f"✅ {total_rappels} rappels à envoyer")
                return total_rappels
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'envoi des rappels: {e}")
                return 0
    
    @staticmethod
    def generer_rapport_hebdomadaire(app):
        """Générer le rapport hebdomadaire"""
        with app.app_context():
            try:
                logger.info("📊 Génération du rapport hebdomadaire...")
                
                # Calculer la période (7 derniers jours)
                date_fin = date.today()
                date_debut = date_fin - timedelta(days=7)
                
                # Statistiques
                stats = {
                    'placements_crees': Placement.query.filter(
                        Placement.created_at >= datetime.combine(date_debut, datetime.min.time())
                    ).count(),
                    'remplacements_crees': Remplacement.query.filter(
                        Remplacement.created_at >= datetime.combine(date_debut, datetime.min.time())
                    ).count(),
                    'absences_demandees': Absence.query.filter(
                        Absence.created_at >= datetime.combine(date_debut, datetime.min.time())
                    ).count()
                }
                
                logger.info(f"✅ Rapport hebdomadaire généré: {stats}")
                
                # TODO: Envoyer le rapport aux admins
                
                return stats
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la génération du rapport: {e}")
                return None
    
    @staticmethod
    def generer_rapport_mensuel(app):
        """Générer le rapport mensuel"""
        with app.app_context():
            try:
                logger.info("📊 Génération du rapport mensuel...")
                
                # Calculer la période (mois dernier)
                aujourd_hui = date.today()
                premier_jour_mois = aujourd_hui.replace(day=1)
                
                # Statistiques
                stats = {
                    'placements_crees': Placement.query.filter(
                        Placement.created_at >= datetime.combine(premier_jour_mois, datetime.min.time())
                    ).count(),
                    'remplacements_crees': Remplacement.query.filter(
                        Remplacement.created_at >= datetime.combine(premier_jour_mois, datetime.min.time())
                    ).count(),
                    'absences_demandees': Absence.query.filter(
                        Absence.created_at >= datetime.combine(premier_jour_mois, datetime.min.time())
                    ).count()
                }
                
                logger.info(f"✅ Rapport mensuel généré: {stats}")
                
                # TODO: Envoyer le rapport aux admins
                
                return stats
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la génération du rapport: {e}")
                return None
    
    @staticmethod
    def executer_maintenant(job_id, app):
        """Exécuter une tâche immédiatement (pour tests)"""
        if SchedulerService.scheduler:
            job = SchedulerService.scheduler.get_job(job_id)
            if job:
                job.func()
                return True
        return False
    
    @staticmethod
    def get_jobs_info():
        """Récupérer les informations sur les tâches planifiées"""
        if SchedulerService.scheduler:
            jobs = []
            for job in SchedulerService.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
            return jobs
        return []
    
    @staticmethod
    def shutdown():
        """Arrêter le scheduler"""
        if SchedulerService.scheduler:
            SchedulerService.scheduler.shutdown()
            logger.info("🛑 Scheduler arrêté")
