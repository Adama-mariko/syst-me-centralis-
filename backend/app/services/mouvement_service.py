from datetime import datetime
from app.models import Mouvement
from app.extensions import db
import json

class MouvementService:
    
    @staticmethod
    def enregistrer_mouvement(type_mouvement, description, user_id, 
                            collaborateur_id=None, entreprise_id=None, 
                            placement_id=None, remplacement_id=None, absence_id=None,
                            competence_id=None, donnees_avant=None, donnees_apres=None,
                            ip_address=None, user_agent=None):
        """Enregistrer un mouvement pour la traçabilité"""
        try:
            mouvement = Mouvement(
                type_mouvement=type_mouvement,
                description=description,
                collaborateur_id=collaborateur_id,
                entreprise_id=entreprise_id,
                placement_id=placement_id,
                remplacement_id=remplacement_id,
                absence_id=absence_id,
                competence_id=competence_id,
                user_id=user_id,
                donnees_avant=json.dumps(donnees_avant) if donnees_avant else None,
                donnees_apres=json.dumps(donnees_apres) if donnees_apres else None,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.add(mouvement)
            db.session.commit()
            
            return mouvement
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_historique_collaborateur(collaborateur_id):
        """Récupérer l'historique complet d'un collaborateur"""
        return Mouvement.query.filter_by(
            collaborateur_id=collaborateur_id
        ).order_by(Mouvement.created_at.desc()).all()
    
    @staticmethod
    def get_historique_placement(placement_id):
        """Récupérer l'historique d'un placement"""
        return Mouvement.query.filter_by(
            placement_id=placement_id
        ).order_by(Mouvement.created_at.desc()).all()
    
    @staticmethod
    def get_mouvements_periode(date_debut, date_fin, type_mouvement=None):
        """Récupérer les mouvements sur une période"""
        query = Mouvement.query.filter(
            Mouvement.created_at >= date_debut,
            Mouvement.created_at <= date_fin
        )
        
        if type_mouvement:
            query = query.filter_by(type_mouvement=type_mouvement)
        
        return query.order_by(Mouvement.created_at.desc()).all()
    
    @staticmethod
    def get_activite_utilisateur(user_id, limite=50):
        """Récupérer l'activité récente d'un utilisateur"""
        return Mouvement.query.filter_by(
            user_id=user_id
        ).order_by(Mouvement.created_at.desc()).limit(limite).all()