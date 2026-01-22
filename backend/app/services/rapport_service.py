import json
import csv
import io
from datetime import datetime, date
from app.models import Rapport, Placement, Absence, Remplacement, Collaborateur, Entreprise
from app.models.rapport import TypeRapport, StatutRapport
from app.extensions import db
from sqlalchemy import func, and_

class RapportService:
    
    @staticmethod
    def generer_rapport_placements(periode_debut, periode_fin, entreprise_id=None, ville=None, user_id=None):
        """Générer un rapport des placements"""
        try:
            # Créer l'enregistrement du rapport
            rapport = Rapport(
                type_rapport=TypeRapport.MENSUEL_PLACEMENTS,
                titre=f"Rapport des placements - {periode_debut} à {periode_fin}",
                description="Rapport détaillé des placements sur la période sélectionnée",
                periode_debut=datetime.strptime(periode_debut, '%Y-%m-%d').date(),
                periode_fin=datetime.strptime(periode_fin, '%Y-%m-%d').date(),
                entreprise_id=entreprise_id,
                ville=ville,
                genere_par_user_id=user_id,
                statut=StatutRapport.EN_COURS
            )
            
            db.session.add(rapport)
            db.session.commit()
            
            # Récupérer les données
            query = Placement.query.filter(
                and_(
                    Placement.date_debut >= rapport.periode_debut,
                    Placement.date_debut <= rapport.periode_fin
                )
            )
            
            if entreprise_id:
                query = query.filter_by(entreprise_id=entreprise_id)
            
            if ville:
                query = query.join(Entreprise).filter(Entreprise.ville == ville)
            
            placements = query.all()
            
            # Calculer les statistiques
            stats = {
                'total_placements': len(placements),
                'placements_confirmes': len([p for p in placements if p.statut.value == 'confirme']),
                'placements_en_cours': len([p for p in placements if p.statut.value == 'en_cours']),
                'placements_termines': len([p for p in placements if p.statut.value == 'termine']),
                'placements_annules': len([p for p in placements if p.statut.value == 'annule']),
                'salaire_moyen': sum([p.salaire_propose or 0 for p in placements]) / len(placements) if placements else 0
            }
            
            # Données détaillées
            donnees_detaillees = []
            for placement in placements:
                donnees_detaillees.append({
                    'id': placement.id,
                    'collaborateur': f"{placement.collaborateur.nom} {placement.collaborateur.prenom}",
                    'entreprise': placement.entreprise.nom,
                    'poste': placement.poste_demande,
                    'date_debut': placement.date_debut.isoformat(),
                    'date_fin': placement.date_fin.isoformat() if placement.date_fin else None,
                    'salaire': float(placement.salaire_propose) if placement.salaire_propose else None,
                    'statut': placement.statut.value
                })
            
            # Sauvegarder les données
            donnees_rapport = {
                'statistiques': stats,
                'donnees': donnees_detaillees,
                'periode': {
                    'debut': rapport.periode_debut.isoformat(),
                    'fin': rapport.periode_fin.isoformat()
                }
            }
            
            rapport.donnees_json = json.dumps(donnees_rapport, ensure_ascii=False)
            rapport.statut = StatutRapport.GENERE
            
            db.session.commit()
            
            return rapport
            
        except Exception as e:
            if rapport:
                rapport.statut = StatutRapport.ERREUR
                db.session.commit()
            raise e
    
    @staticmethod
    def generer_rapport_absences(periode_debut, periode_fin, entreprise_id=None, user_id=None):
        """Générer un rapport des absences"""
        try:
            rapport = Rapport(
                type_rapport=TypeRapport.MENSUEL_ABSENCES,
                titre=f"Rapport des absences - {periode_debut} à {periode_fin}",
                description="Rapport détaillé des absences sur la période sélectionnée",
                periode_debut=datetime.strptime(periode_debut, '%Y-%m-%d').date(),
                periode_fin=datetime.strptime(periode_fin, '%Y-%m-%d').date(),
                entreprise_id=entreprise_id,
                genere_par_user_id=user_id,
                statut=StatutRapport.EN_COURS
            )
            
            db.session.add(rapport)
            db.session.commit()
            
            # Récupérer les données
            query = Absence.query.filter(
                and_(
                    Absence.date_debut >= rapport.periode_debut,
                    Absence.date_debut <= rapport.periode_fin
                )
            )
            
            if entreprise_id:
                query = query.join(Collaborateur).filter(
                    Collaborateur.entreprise_actuelle_id == entreprise_id
                )
            
            absences = query.all()
            
            # Calculer les statistiques
            stats = {
                'total_absences': len(absences),
                'absences_approuvees': len([a for a in absences if a.statut.value == 'approuve']),
                'absences_refusees': len([a for a in absences if a.statut.value == 'refuse']),
                'absences_en_attente': len([a for a in absences if a.statut.value == 'en_attente']),
                'total_jours': sum([a.nombre_jours for a in absences]),
                'repartition_types': {}
            }
            
            # Répartition par type
            for absence in absences:
                type_abs = absence.type_absence.value
                if type_abs not in stats['repartition_types']:
                    stats['repartition_types'][type_abs] = 0
                stats['repartition_types'][type_abs] += 1
            
            # Données détaillées
            donnees_detaillees = []
            for absence in absences:
                donnees_detaillees.append({
                    'id': absence.id,
                    'collaborateur': f"{absence.collaborateur.nom} {absence.collaborateur.prenom}",
                    'type_absence': absence.type_absence.value,
                    'date_debut': absence.date_debut.isoformat(),
                    'date_fin': absence.date_fin.isoformat(),
                    'nombre_jours': absence.nombre_jours,
                    'statut': absence.statut.value,
                    'motif': absence.motif
                })
            
            donnees_rapport = {
                'statistiques': stats,
                'donnees': donnees_detaillees,
                'periode': {
                    'debut': rapport.periode_debut.isoformat(),
                    'fin': rapport.periode_fin.isoformat()
                }
            }
            
            rapport.donnees_json = json.dumps(donnees_rapport, ensure_ascii=False)
            rapport.statut = StatutRapport.GENERE
            
            db.session.commit()
            
            return rapport
            
        except Exception as e:
            if rapport:
                rapport.statut = StatutRapport.ERREUR
                db.session.commit()
            raise e
    
    @staticmethod
    def exporter_csv(rapport_id):
        """Exporter un rapport en CSV"""
        rapport = Rapport.query.get_or_404(rapport_id)
        
        if not rapport.donnees_json:
            raise ValueError("Aucune donnée disponible pour l'export")
        
        donnees = json.loads(rapport.donnees_json)
        
        # Créer le CSV en mémoire
        output = io.StringIO()
        
        if rapport.type_rapport == TypeRapport.MENSUEL_PLACEMENTS:
            fieldnames = ['ID', 'Collaborateur', 'Entreprise', 'Poste', 'Date début', 'Date fin', 'Salaire', 'Statut']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in donnees['donnees']:
                writer.writerow({
                    'ID': item['id'],
                    'Collaborateur': item['collaborateur'],
                    'Entreprise': item['entreprise'],
                    'Poste': item['poste'],
                    'Date début': item['date_debut'],
                    'Date fin': item['date_fin'] or '',
                    'Salaire': item['salaire'] or '',
                    'Statut': item['statut']
                })
        
        elif rapport.type_rapport == TypeRapport.MENSUEL_ABSENCES:
            fieldnames = ['ID', 'Collaborateur', 'Type', 'Date début', 'Date fin', 'Jours', 'Statut', 'Motif']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in donnees['donnees']:
                writer.writerow({
                    'ID': item['id'],
                    'Collaborateur': item['collaborateur'],
                    'Type': item['type_absence'],
                    'Date début': item['date_debut'],
                    'Date fin': item['date_fin'],
                    'Jours': item['nombre_jours'],
                    'Statut': item['statut'],
                    'Motif': item['motif'] or ''
                })
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
    
    @staticmethod
    def get_rapports_utilisateur(user_id):
        """Récupérer tous les rapports générés par un utilisateur"""
        return Rapport.query.filter_by(
            genere_par_user_id=user_id
        ).order_by(Rapport.created_at.desc()).all()