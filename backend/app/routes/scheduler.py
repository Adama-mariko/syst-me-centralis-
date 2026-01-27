"""
Routes pour gérer les tâches automatiques planifiées
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.services.scheduler_service import SchedulerService
from app.utils.decorators import role_required
from app.models.user import UserRole

scheduler_bp = Blueprint('scheduler', __name__)

@scheduler_bp.route('/scheduler/jobs', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def get_jobs():
    """Récupérer la liste des tâches planifiées"""
    try:
        jobs = SchedulerService.get_jobs_info()
        return jsonify({
            'jobs': jobs,
            'total': len(jobs)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scheduler_bp.route('/scheduler/jobs/<job_id>/execute', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def execute_job(job_id):
    """Exécuter une tâche immédiatement"""
    try:
        success = SchedulerService.executer_maintenant(job_id, current_app._get_current_object())
        
        if success:
            return jsonify({'message': f'Tâche {job_id} exécutée avec succès'})
        else:
            return jsonify({'error': 'Tâche non trouvée'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scheduler_bp.route('/scheduler/update-statuts', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def update_statuts_now():
    """Mettre à jour les statuts immédiatement (pour tests)"""
    try:
        compteurs = SchedulerService.mettre_a_jour_statuts(current_app._get_current_object())
        
        if compteurs:
            return jsonify({
                'message': 'Mise à jour des statuts effectuée',
                'compteurs': compteurs
            })
        else:
            return jsonify({'error': 'Erreur lors de la mise à jour'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scheduler_bp.route('/scheduler/rappels-placements', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def send_rappels_placements_now():
    """Envoyer les rappels placements immédiatement (pour tests)"""
    try:
        count = SchedulerService.envoyer_rappels_placements(current_app._get_current_object())
        
        return jsonify({
            'message': 'Rappels envoyés',
            'count': count
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scheduler_bp.route('/scheduler/rapport-hebdomadaire', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def generate_rapport_hebdomadaire_now():
    """Générer le rapport hebdomadaire immédiatement (pour tests)"""
    try:
        stats = SchedulerService.generer_rapport_hebdomadaire(current_app._get_current_object())
        
        if stats:
            return jsonify({
                'message': 'Rapport hebdomadaire généré',
                'statistiques': stats
            })
        else:
            return jsonify({'error': 'Erreur lors de la génération'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scheduler_bp.route('/scheduler/rapport-mensuel', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def generate_rapport_mensuel_now():
    """Générer le rapport mensuel immédiatement (pour tests)"""
    try:
        stats = SchedulerService.generer_rapport_mensuel(current_app._get_current_object())
        
        if stats:
            return jsonify({
                'message': 'Rapport mensuel généré',
                'statistiques': stats
            })
        else:
            return jsonify({'error': 'Erreur lors de la génération'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
