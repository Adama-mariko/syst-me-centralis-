from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User, UserRole

class AuthService:
    @staticmethod
    def require_role(required_role):
        """Décorateur pour vérifier le rôle de l'utilisateur"""
        def decorator(f):
            @wraps(f)
            @jwt_required()
            def decorated_function(*args, **kwargs):
                current_user_id = get_jwt_identity()
                print(f"DEBUG AUTH: current_user_id = {current_user_id} (type: {type(current_user_id)})")
                
                # Convertir en entier si c'est une chaîne
                if isinstance(current_user_id, str):
                    try:
                        current_user_id = int(current_user_id)
                    except ValueError:
                        print(f"DEBUG AUTH: Impossible de convertir {current_user_id} en entier")
                        return jsonify({'message': 'Token invalide'}), 403
                
                user = User.query.get(current_user_id)
                print(f"DEBUG AUTH: user = {user}")
                
                if not user or not user.is_active:
                    print(f"DEBUG AUTH: Utilisateur non trouvé ou inactif")
                    return jsonify({'message': 'Utilisateur non autorisé'}), 403
                
                print(f"DEBUG AUTH: user.role = {user.role}, required_role = {required_role}")
                
                if user.role != required_role:
                    print(f"DEBUG AUTH: Permissions insuffisantes")
                    return jsonify({'message': 'Permissions insuffisantes'}), 403
                
                print(f"DEBUG AUTH: Autorisation accordée")
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def require_admin():
        """Décorateur pour les routes admin uniquement"""
        return AuthService.require_role(UserRole.ADMIN)
    
    @staticmethod
    def require_rh():
        """Décorateur pour les routes RH uniquement"""
        return AuthService.require_role(UserRole.RH_ENTREPRISE)
    
    @staticmethod
    def get_current_user():
        """Récupère l'utilisateur connecté"""
        current_user_id = get_jwt_identity()
        # Convertir en entier si c'est une chaîne
        if isinstance(current_user_id, str):
            try:
                current_user_id = int(current_user_id)
            except ValueError:
                return None
        return User.query.get(current_user_id)