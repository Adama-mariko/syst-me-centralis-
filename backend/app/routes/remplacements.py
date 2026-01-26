from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.remplacement import Remplacement, TypeRemplacement, StatutRemplacement
from app.models.collaborateur import Collaborateur
from app.extensions import db
from app.services.auth_service import AuthService
from datetime import datetime

remplacements_bp = Blueprint('remplacements', __name__)

def parse_date(date_string):
    """Parse date from ISO format or simple format"""
    try:
        # Try ISO format first (from Angular datepicker)
        if 'T' in date_string:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00')).date()
        else:
            # Try simple format
            return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(f"Format de date invalide: {date_string}")

@remplacements_bp.route('', methods=['GET'])
@jwt_required()
def get_remplacements():
    """Récupération des remplacements"""
    try:
        current_user = AuthService.get_current_user()
        
        # Si RH, filtrer par entreprise des collaborateurs
        if current_user.role.value == 'rh_entreprise':
            if not current_user.entreprise_id:
                return jsonify({'message': 'Utilisateur non associé à une entreprise'}), 400
            
            # Récupérer les IDs des collaborateurs de l'entreprise
            collaborateurs_ids = db.session.query(Collaborateur.id).filter(
                Collaborateur.entreprise_actuelle_id == current_user.entreprise_id
            ).subquery()
            
            # Récupérer les remplacements où au moins un des collaborateurs appartient à l'entreprise
            remplacements = Remplacement.query.filter(
                (Remplacement.remplace_id.in_(collaborateurs_ids)) |
                (Remplacement.remplacant_id.in_(collaborateurs_ids))
            ).all()
        else:
            # Admin peut voir tous les remplacements
            remplacements = Remplacement.query.all()
        
        return jsonify({
            'remplacements': [remplacement.to_dict() for remplacement in remplacements]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@remplacements_bp.route('', methods=['POST'])
@AuthService.require_admin()
def create_remplacement():
    """Création d'un nouveau remplacement"""
    try:
        data = request.get_json()
        current_user = AuthService.get_current_user()
        
        print(f"[DEBUG] Données reçues: {data}")
        print(f"[DEBUG] Utilisateur actuel: {current_user.id}")
        
        # Vérification des champs requis
        required_fields = ['remplace_id', 'remplacant_id', 'type_remplacement', 'date_debut', 'date_fin']
        for field in required_fields:
            if not data.get(field):
                print(f"[ERROR] Champ manquant: {field}")
                return jsonify({'message': f'Le champ {field} est requis'}), 400
        
        print(f"[DEBUG] Tous les champs requis sont présents")
        
        # Vérifier que les collaborateurs sont différents
        if data['remplace_id'] == data['remplacant_id']:
            print(f"[ERROR] Collaborateurs identiques: {data['remplace_id']}")
            return jsonify({'message': 'Un collaborateur ne peut pas se remplacer lui-même'}), 400
        
        print(f"[DEBUG] Collaborateurs différents: remplace={data['remplace_id']}, remplacant={data['remplacant_id']}")
        
        # Vérifier que les collaborateurs existent
        remplace = Collaborateur.query.get(data['remplace_id'])
        remplacant = Collaborateur.query.get(data['remplacant_id'])
        
        if not remplace:
            print(f"[ERROR] Collaborateur remplacé non trouvé: {data['remplace_id']}")
            return jsonify({'message': 'Collaborateur remplacé non trouvé'}), 400
            
        if not remplacant:
            print(f"[ERROR] Collaborateur remplaçant non trouvé: {data['remplacant_id']}")
            return jsonify({'message': 'Collaborateur remplaçant non trouvé'}), 400
        
        print(f"[DEBUG] Collaborateurs trouvés: {remplace.nom} -> {remplacant.nom}")
        
        # Parsing des dates
        try:
            date_debut = parse_date(data['date_debut'])
            date_fin = parse_date(data['date_fin'])
            print(f"[DEBUG] Dates parsées: {date_debut} -> {date_fin}")
        except Exception as e:
            print(f"[ERROR] Erreur parsing dates: {e}")
            return jsonify({'message': f'Format de date invalide: {str(e)}'}), 400
        
        # Vérification du type de remplacement
        try:
            type_remplacement = TypeRemplacement(data['type_remplacement'])
            print(f"[DEBUG] Type de remplacement: {type_remplacement}")
        except Exception as e:
            print(f"[ERROR] Type de remplacement invalide: {e}")
            return jsonify({'message': f'Type de remplacement invalide: {data["type_remplacement"]}'}), 400
        
        # Création du remplacement
        print(f"[DEBUG] Création du remplacement...")
        remplacement = Remplacement(
            remplace_id=data['remplace_id'],
            remplacant_id=data['remplacant_id'],
            type_remplacement=type_remplacement,
            motif=data.get('motif'),
            date_debut=date_debut,
            date_fin=date_fin,
            commentaires=data.get('commentaires'),
            created_by_user_id=current_user.id
        )
        
        print(f"[DEBUG] Objet remplacement créé: {remplacement}")
        
        db.session.add(remplacement)
        print(f"[DEBUG] Remplacement ajouté à la session")
        
        db.session.commit()
        print(f"[DEBUG] Transaction commitée avec succès")
        
        return jsonify({
            'message': 'Remplacement créé avec succès',
            'remplacement': remplacement.to_dict()
        }), 201
        
    except Exception as e:
        print(f"[ERROR] Exception dans create_remplacement: {str(e)}")
        print(f"[ERROR] Type d'exception: {type(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la création', 'error': str(e)}), 500

@remplacements_bp.route('/<int:remplacement_id>', methods=['GET'])
@jwt_required()
def get_remplacement(remplacement_id):
    """Récupération d'un remplacement spécifique"""
    try:
        current_user = AuthService.get_current_user()
        remplacement = Remplacement.query.get_or_404(remplacement_id)
        
        # Vérification des permissions pour RH
        if current_user.role.value == 'rh_entreprise':
            # Vérifier que le collaborateur remplacé appartient à l'entreprise
            if remplacement.remplace.entreprise_actuelle_id != current_user.entreprise_id:
                return jsonify({'message': 'Accès non autorisé'}), 403
        
        return jsonify({'remplacement': remplacement.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération', 'error': str(e)}), 500

@remplacements_bp.route('/<int:remplacement_id>', methods=['PUT'])
@jwt_required()
def update_remplacement(remplacement_id):
    """Modification d'un remplacement"""
    try:
        current_user = AuthService.get_current_user()
        remplacement = Remplacement.query.get_or_404(remplacement_id)
        
        # Vérification des permissions pour RH
        if current_user.role.value == 'rh_entreprise':
            if remplacement.remplace.entreprise_actuelle_id != current_user.entreprise_id:
                return jsonify({'message': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        # Mise à jour des champs
        if 'type_remplacement' in data:
            remplacement.type_remplacement = TypeRemplacement(data['type_remplacement'])
        if 'motif' in data:
            remplacement.motif = data['motif']
        if 'date_debut' in data:
            remplacement.date_debut = parse_date(data['date_debut'])
        if 'date_fin' in data:
            remplacement.date_fin = parse_date(data['date_fin'])
        if 'statut' in data:
            remplacement.statut = StatutRemplacement(data['statut'])
        if 'commentaires' in data:
            remplacement.commentaires = data['commentaires']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Remplacement modifié avec succès',
            'remplacement': remplacement.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la modification', 'error': str(e)}), 500