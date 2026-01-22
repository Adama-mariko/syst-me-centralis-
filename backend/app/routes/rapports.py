from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Rapport, User
from app.services.rapport_service import RapportService
from app.utils.decorators import role_required
from app.models.user import UserRole
from datetime import datetime

rapports_bp = Blueprint('rapports', __name__)

@rapports_bp.route('/rapports', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def get_rapports():
    """Récupérer tous les rapports"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        type_rapport = request.args.get('type_rapport')
        
        query = Rapport.query
        
        if type_rapport:
            query = query.filter_by(type_rapport=type_rapport)
        
        rapports = query.order_by(Rapport.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'rapports': [rapport.to_dict() for rapport in rapports.items],
            'total': rapports.total,
            'pages': rapports.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rapports_bp.route('/rapports/placements', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def generer_rapport_placements():
    """Générer un rapport des placements"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validation des données requises
        required_fields = ['periode_debut', 'periode_fin']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        rapport = RapportService.generer_rapport_placements(
            periode_debut=data['periode_debut'],
            periode_fin=data['periode_fin'],
            entreprise_id=data.get('entreprise_id'),
            ville=data.get('ville'),
            user_id=current_user_id
        )
        
        return jsonify({
            'message': 'Rapport généré avec succès',
            'rapport': rapport.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rapports_bp.route('/rapports/absences', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def generer_rapport_absences():
    """Générer un rapport des absences"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validation des données requises
        required_fields = ['periode_debut', 'periode_fin']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        rapport = RapportService.generer_rapport_absences(
            periode_debut=data['periode_debut'],
            periode_fin=data['periode_fin'],
            entreprise_id=data.get('entreprise_id'),
            user_id=current_user_id
        )
        
        return jsonify({
            'message': 'Rapport généré avec succès',
            'rapport': rapport.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rapports_bp.route('/rapports/<int:rapport_id>', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def get_rapport(rapport_id):
    """Récupérer un rapport spécifique"""
    try:
        rapport = Rapport.query.get_or_404(rapport_id)
        return jsonify({'rapport': rapport.to_dict()})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rapports_bp.route('/rapports/<int:rapport_id>/export/csv', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def exporter_rapport_csv(rapport_id):
    """Exporter un rapport en CSV"""
    try:
        rapport = Rapport.query.get_or_404(rapport_id)
        csv_content = RapportService.exporter_csv(rapport_id)
        
        # Créer la réponse avec le fichier CSV
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=rapport_{rapport.id}_{datetime.now().strftime("%Y%m%d")}.csv'
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rapports_bp.route('/rapports/mes-rapports', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def get_mes_rapports():
    """Récupérer les rapports générés par l'utilisateur connecté"""
    try:
        current_user_id = get_jwt_identity()
        rapports = RapportService.get_rapports_utilisateur(current_user_id)
        
        return jsonify({
            'rapports': [rapport.to_dict() for rapport in rapports]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rapports_bp.route('/rapports/statistiques', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def get_statistiques_globales():
    """Récupérer les statistiques globales du système"""
    try:
        from app.models import Placement, Absence, Collaborateur, Entreprise
        from sqlalchemy import func
        
        # Statistiques générales
        stats = {
            'total_collaborateurs': Collaborateur.query.count(),
            'total_entreprises': Entreprise.query.filter_by(is_active=True).count(),
            'total_placements': Placement.query.count(),
            'total_absences': Absence.query.count(),
            'placements_actifs': Placement.query.filter_by(statut='en_cours').count(),
            'absences_en_attente': Absence.query.filter_by(statut='en_attente').count()
        }
        
        # Statistiques par mois (derniers 6 mois)
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta
        
        stats_mensuelles = []
        for i in range(6):
            date_fin = datetime.now().replace(day=1) - relativedelta(months=i)
            date_debut = date_fin - relativedelta(months=1)
            
            placements_mois = Placement.query.filter(
                Placement.created_at >= date_debut,
                Placement.created_at < date_fin
            ).count()
            
            absences_mois = Absence.query.filter(
                Absence.created_at >= date_debut,
                Absence.created_at < date_fin
            ).count()
            
            stats_mensuelles.append({
                'mois': date_debut.strftime('%Y-%m'),
                'placements': placements_mois,
                'absences': absences_mois
            })
        
        stats['evolution_mensuelle'] = list(reversed(stats_mensuelles))
        
        return jsonify({'statistiques': stats})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500