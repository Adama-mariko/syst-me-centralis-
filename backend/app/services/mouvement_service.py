from datetime import datetime
from app.models import Mouvement
from app.extensions import db
import json

class MouvementService:
    
    @staticmethod
    def enregistrer_mouvement(type_mouvement, description, user_id, 
                            collaborateur_id=None, entreprise_id=None, 
                            placement_id=None, remplacement_id=None, absence_id=None,
                            donnees_avant=None, donnees_apres=None):
        """Enregistrer un mouvement pour la traçabilité"""
        try:
            print(f"🔍 MouvementService.enregistrer_mouvement - Type: {type_mouvement}")
            print(f"🔍 MouvementService.enregistrer_mouvement - Description: {description}")
            print(f"🔍 MouvementService.enregistrer_mouvement - User ID: {user_id}")
            print(f"🔍 MouvementService.enregistrer_mouvement - Absence ID: {absence_id}")
            
            # Convertir l'enum en valeur si nécessaire
            from app.models.mouvement import TypeMouvement
            if isinstance(type_mouvement, TypeMouvement):
                type_mouvement_value = type_mouvement.value
            else:
                type_mouvement_value = type_mouvement
            
            mouvement = Mouvement(
                type_mouvement=type_mouvement_value,
                description=description,
                collaborateur_id=collaborateur_id,
                entreprise_id=entreprise_id,
                placement_id=placement_id,
                remplacement_id=remplacement_id,
                absence_id=absence_id,
                user_id=user_id,
                donnees_avant=json.dumps(donnees_avant) if donnees_avant else None,
                donnees_apres=json.dumps(donnees_apres) if donnees_apres else None
            )
            
            print(f"🔍 Objet Mouvement créé, ajout à la session...")
            db.session.add(mouvement)
            db.session.commit()
            print(f"✅ Mouvement sauvegardé avec ID: {mouvement.id}")
            
            return mouvement
            
        except Exception as e:
            print(f"❌ Erreur dans MouvementService.enregistrer_mouvement: {str(e)}")
            print(f"❌ Type d'erreur: {type(e).__name__}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
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