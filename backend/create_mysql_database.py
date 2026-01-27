import pymysql
from config.config import Config

# Connexion à MySQL sans spécifier de base de données
connection = pymysql.connect(
    host=Config.DB_HOST,
    port=int(Config.DB_PORT),
    user=Config.DB_USER,
    password=Config.DB_PASSWORD
)

try:
    with connection.cursor() as cursor:
        # Créer la base de données si elle n'existe pas
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ Base de données '{Config.DB_NAME}' créée avec succès!")
        
        # Vérifier que la base existe
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print("\nBases de données disponibles:")
        for db in databases:
            print(f"  - {db[0]}")
            
    connection.commit()
finally:
    connection.close()

print(f"\n✓ Vous pouvez maintenant lancer le serveur Flask!")
