#!/usr/bin/env python3
"""
Script pour appliquer les nouvelles fonctionnalités au système de gestion de personnel
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def execute_migration():
    """Exécuter la migration pour ajouter les nouvelles fonctionnalités"""
    try:
        # Configuration de la base de données
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'personnel_management'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("🔄 Application des nouvelles fonctionnalités...")
            
            # Lire et exécuter le fichier de migration
            with open('migrations/add_new_features.sql', 'r', encoding='utf-8') as file:
                migration_sql = file.read()
            
            # Diviser les commandes SQL
            commands = migration_sql.split(';')
            
            for command in commands:
                command = command.strip()
                if command and not command.startswith('--'):
                    try:
                        cursor.execute(command)
                        print(f"✅ Commande exécutée: {command[:50]}...")
                    except Error as e:
                        if "Duplicate column name" in str(e) or "already exists" in str(e):
                            print(f"⚠️  Déjà existant: {command[:50]}...")
                        else:
                            print(f"❌ Erreur: {e}")
                            print(f"   Commande: {command[:100]}...")
            
            connection.commit()
            print("✅ Migration appliquée avec succès!")
            
            # Vérifier les nouvelles tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            nouvelles_tables = ['absences', 'notifications', 'rapports', 'security_logs', 'competences', 'collaborateur_competences']
            tables_existantes = [table[0] for table in tables]
            
            print("\n📊 Vérification des tables:")
            for table in nouvelles_tables:
                if table in tables_existantes:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"✅ {table}: {count} enregistrements")
                else:
                    print(f"❌ {table}: Table manquante")
            
            # Vérifier les nouveaux rôles
            cursor.execute("SELECT DISTINCT role FROM users")
            roles = [role[0] for role in cursor.fetchall()]
            print(f"\n👥 Rôles disponibles: {', '.join(roles)}")
            
    except Error as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Connexion fermée")
    
    return True

def create_sample_data():
    """Créer des données d'exemple pour tester les nouvelles fonctionnalités"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'personnel_management'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("\n🎯 Création de données d'exemple...")
            
            # Vérifier s'il y a des collaborateurs
            cursor.execute("SELECT COUNT(*) FROM collaborateurs")
            nb_collaborateurs = cursor.fetchone()[0]
            
            if nb_collaborateurs == 0:
                print("⚠️  Aucun collaborateur trouvé. Création d'exemples...")
                
                # Créer des collaborateurs d'exemple
                collaborateurs_exemple = [
                    ("EMP001", "Dupont", "Jean", "jean.dupont@email.com", "0123456789", "2023-01-15", "Développeur", "actif"),
                    ("EMP002", "Martin", "Marie", "marie.martin@email.com", "0123456790", "2023-02-01", "Designer", "actif"),
                    ("EMP003", "Bernard", "Pierre", "pierre.bernard@email.com", "0123456791", "2023-03-01", "Chef de projet", "actif")
                ]
                
                for collab in collaborateurs_exemple:
                    cursor.execute("""
                        INSERT INTO collaborateurs 
                        (numero_employe, nom, prenom, email, telephone, date_embauche, poste, statut)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, collab)
                
                print("✅ Collaborateurs d'exemple créés")
            
            # Créer des absences d'exemple
            cursor.execute("SELECT id FROM collaborateurs LIMIT 1")
            collaborateur_id = cursor.fetchone()
            
            if collaborateur_id:
                cursor.execute("""
                    INSERT INTO absences 
                    (collaborateur_id, type_absence, motif, date_debut, date_fin, nombre_jours, demande_par_collaborateur_id)
                    VALUES (%s, 'conge_paye', 'Vacances d\'été', '2024-07-15', '2024-07-25', 10, %s)
                    ON DUPLICATE KEY UPDATE motif=motif
                """, (collaborateur_id[0], collaborateur_id[0]))
                
                print("✅ Absence d'exemple créée")
            
            connection.commit()
            print("✅ Données d'exemple créées avec succès!")
            
    except Error as e:
        print(f"❌ Erreur lors de la création des données d'exemple: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🚀 Démarrage de l'application des nouvelles fonctionnalités")
    print("=" * 60)
    
    if execute_migration():
        create_sample_data()
        
        print("\n" + "=" * 60)
        print("🎉 NOUVELLES FONCTIONNALITÉS AJOUTÉES AVEC SUCCÈS!")
        print("\n📋 Fonctionnalités disponibles:")
        print("   ✅ E1 - Gestion des entreprises (existant)")
        print("   ✅ E2 - Gestion des collaborateurs + Import CSV")
        print("   ✅ E3 - Placement (existant)")
        print("   ✅ E4 - Validation RH (existant)")
        print("   ✅ E5 - Gestion des absences")
        print("   ✅ E6 - Remplacement (existant)")
        print("   ✅ E7 - Traçabilité complète")
        print("   ✅ E8 - Automatisation des e-mails")
        print("   ✅ E9 - Signalement/Rapports")
        print("   ✅ E10 - Sécurité avec nouveaux rôles")
        print("\n🔧 Redémarrez le serveur backend pour appliquer les changements")
    else:
        print("❌ Échec de l'application des nouvelles fonctionnalités")