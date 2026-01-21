from functools import wraps
from flask import jsonify
from app.models.mouvement import Mouvement, TypeMouvement
from app.extensions import db
from app.services.auth_service import AuthService
import json

def log_movement(type_mouvement, description_template):
    """Décorateur pour enregistrer automatiquement les mouvements"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = AuthService.get_current_user()
            
            # Exécuter la fonction originale
            result = f(*args, **kwargs)
            
            # Si la fonction s'est exécutée avec succès (status 200 ou 201)
            if hasattr(result, 'status_code') and result.status_code in [200, 201]:
                try:
                    # Extraire les données de la réponse
                    response_data = result.get_json()
                    
                    # Créer le mouvement
                    mouvement = Mouvement(
                        type_mouvement=type_mouvement,
                        description=description_template.format(**kwargs),
                        user_id=current_user.id,
                        collaborateur_id=kwargs.get('collaborateur_id'),
                        entreprise_id=kwargs.get('entreprise_id'),
                        placement_id=kwargs.get('placement_id'),
                        remplacement_id=kwargs.get('remplacement_id'),
                        donnees_apres=json.dumps(response_data, default=str)
                    )
                    
                    db.session.add(mouvement)
                    db.session.commit()
                    
                except Exception as e:
                    # Ne pas faire échouer la fonction principale si le logging échoue
                    print(f"Erreur lors de l'enregistrement du mouvement: {e}")
            
            return result
        return decorated_function
    return decorator