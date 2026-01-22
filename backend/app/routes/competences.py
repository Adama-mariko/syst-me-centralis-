from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Competence, CollaborateurCompetence, Collaborateur, User
from app.models.competence import NiveauCompetence
from app.extensions import db
from app.utils.decorators import role_required
from app.models.user import UserRole
from app.services.mouvement_service import MouvementService
import csv
import io

competences_bp = Blueprint('competences', __name__)

@competences_bp.route('/competences', methods=['GET'])
@jwt_required()
def get_competences():
    """Récupérer toutes les compétences"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        categorie = request.args.get('categorie')
        search = request.args.get('search')
        
        query = Competence.query.filter_by(is_active=True)
        
        if categorie:
            query = query.filter_by(categorie=categorie)
        
        if search:
            query = query.filter(Competence.nom.contains(search))
        
        competences = query.order_by(Competence.nom).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'competences': [competence.to_dict() for competence in competences.items],
            'total': competences.total,
            'pages': competences.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@competences_bp.route('/competences', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def create_competence():
    """Créer une nouvelle compétence"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validation des données requises
        if 'nom' not in data:
            return jsonify({'error': 'Le nom de la compétence est requis'}), 400
        
        # Vérifier si la compétence existe déjà
        existing = Competence.query.filter_by(nom=data['nom']).first()
        if existing:
            return jsonify({'error': 'Cette compétence existe déjà'}), 400
        
        competence = Competence(
            nom=data['nom'],
            description=data.get('description'),
            categorie=data.get('categorie'),
            niveau_requis=NiveauCompetence(data.get('niveau_requis', 'debutant'))
        )
        
        db.session.add(competence)
        db.session.commit()
        
        # Enregistrer le mouvement
        MouvementService.enregistrer_mouvement(
            type_mouvement='competence_ajout',
            description=f"Création de la compétence: {competence.nom}",
            competence_id=competence.id,
            user_id=current_user_id
        )
        
        return jsonify({
            'message': 'Compétence créée avec succès',
            'competence': competence.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@competences_bp.route('/competences/<int:competence_id>', methods=['PUT'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def update_competence(competence_id):
    """Mettre à jour une compétence"""
    try:
        competence = Competence.query.get_or_404(competence_id)
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Sauvegarder les données avant modification
        donnees_avant = competence.to_dict()
        
        if 'nom' in data:
            competence.nom = data['nom']
        if 'description' in data:
            competence.description = data['description']
        if 'categorie' in data:
            competence.categorie = data['categorie']
        if 'niveau_requis' in data:
            competence.niveau_requis = NiveauCompetence(data['niveau_requis'])
        if 'is_active' in data:
            competence.is_active = data['is_active']
        
        db.session.commit()
        
        # Enregistrer le mouvement
        MouvementService.enregistrer_mouvement(
            type_mouvement='competence_modification',
            description=f"Modification de la compétence: {competence.nom}",
            competence_id=competence.id,
            user_id=current_user_id,
            donnees_avant=donnees_avant,
            donnees_apres=competence.to_dict()
        )
        
        return jsonify({
            'message': 'Compétence mise à jour avec succès',
            'competence': competence.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@competences_bp.route('/competences/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Récupérer toutes les catégories de compétences"""
    try:
        categories = db.session.query(Competence.categorie).filter(
            Competence.categorie.isnot(None),
            Competence.is_active == True
        ).distinct().all()
        
        return jsonify({
            'categories': [cat[0] for cat in categories if cat[0]]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@competences_bp.route('/collaborateurs/<int:collaborateur_id>/competences', methods=['GET'])
@jwt_required()
def get_competences_collaborateur(collaborateur_id):
    """Récupérer les compétences d'un collaborateur"""
    try:
        competences = CollaborateurCompetence.query.filter_by(
            collaborateur_id=collaborateur_id
        ).all()
        
        return jsonify({
            'competences': [comp.to_dict() for comp in competences]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@competences_bp.route('/collaborateurs/<int:collaborateur_id>/competences', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.RH_ENTREPRISE])
def add_competence_collaborateur(collaborateur_id):
    """Ajouter une compétence à un collaborateur"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validation des données requises
        required_fields = ['competence_id', 'niveau']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Vérifier si la compétence existe déjà pour ce collaborateur
        existing = CollaborateurCompetence.query.filter_by(
            collaborateur_id=collaborateur_id,
            competence_id=data['competence_id']
        ).first()
        
        if existing:
            return jsonify({'error': 'Cette compétence est déjà associée à ce collaborateur'}), 400
        
        competence_collab = CollaborateurCompetence(
            collaborateur_id=collaborateur_id,
            competence_id=data['competence_id'],
            niveau=NiveauCompetence(data['niveau']),
            certifie=data.get('certifie', False),
            date_acquisition=data.get('date_acquisition')
        )
        
        db.session.add(competence_collab)
        db.session.commit()
        
        # Enregistrer le mouvement
        MouvementService.enregistrer_mouvement(
            type_mouvement='competence_ajout',
            description=f"Ajout de compétence au collaborateur {collaborateur_id}",
            collaborateur_id=collaborateur_id,
            competence_id=data['competence_id'],
            user_id=current_user_id
        )
        
        return jsonify({
            'message': 'Compétence ajoutée avec succès',
            'competence': competence_collab.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@competences_bp.route('/collaborateurs/import-csv', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.ADMIN])
def import_collaborateurs_csv():
    """Importer des collaborateurs depuis un fichier CSV"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Le fichier doit être au format CSV'}), 400
        
        current_user_id = get_jwt_identity()
        
        # Lire le contenu du fichier CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        collaborateurs_crees = 0
        erreurs = []
        
        for row_num, row in enumerate(csv_input, start=2):  # Start=2 car ligne 1 = headers
            try:
                # Validation des champs requis
                required_fields = ['nom', 'prenom', 'email', 'poste', 'date_embauche']
                for field in required_fields:
                    if field not in row or not row[field].strip():
                        raise ValueError(f"Champ requis manquant: {field}")
                
                # Vérifier si le collaborateur existe déjà
                existing = Collaborateur.query.filter_by(email=row['email'].strip()).first()
                if existing:
                    erreurs.append(f"Ligne {row_num}: Email {row['email']} déjà existant")
                    continue
                
                # Créer le collaborateur
                collaborateur = Collaborateur(
                    numero_employe=row.get('numero_employe', f"EMP{row_num:04d}"),
                    nom=row['nom'].strip(),
                    prenom=row['prenom'].strip(),
                    email=row['email'].strip(),
                    telephone=row.get('telephone', '').strip() or None,
                    adresse=row.get('adresse', '').strip() or None,
                    ville=row.get('ville', '').strip() or None,
                    code_postal=row.get('code_postal', '').strip() or None,
                    date_embauche=row['date_embauche'].strip(),
                    poste=row['poste'].strip(),
                    competences=row.get('competences', '').strip() or None,
                    salaire=float(row['salaire']) if row.get('salaire', '').strip() else None
                )
                
                db.session.add(collaborateur)
                db.session.flush()  # Pour obtenir l'ID
                
                # Traiter les compétences si présentes
                if row.get('competences', '').strip():
                    competences_list = [comp.strip() for comp in row['competences'].split(',')]
                    for comp_nom in competences_list:
                        if comp_nom:
                            # Chercher ou créer la compétence
                            competence = Competence.query.filter_by(nom=comp_nom).first()
                            if not competence:
                                competence = Competence(nom=comp_nom, categorie='Import CSV')
                                db.session.add(competence)
                                db.session.flush()
                            
                            # Associer la compétence au collaborateur
                            comp_collab = CollaborateurCompetence(
                                collaborateur_id=collaborateur.id,
                                competence_id=competence.id,
                                niveau=NiveauCompetence.INTERMEDIAIRE
                            )
                            db.session.add(comp_collab)
                
                collaborateurs_crees += 1
                
            except Exception as e:
                erreurs.append(f"Ligne {row_num}: {str(e)}")
                continue
        
        db.session.commit()
        
        # Enregistrer le mouvement
        MouvementService.enregistrer_mouvement(
            type_mouvement='import_csv',
            description=f"Import CSV: {collaborateurs_crees} collaborateurs créés",
            user_id=current_user_id
        )
        
        return jsonify({
            'message': f'Import terminé: {collaborateurs_crees} collaborateurs créés',
            'collaborateurs_crees': collaborateurs_crees,
            'erreurs': erreurs
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500