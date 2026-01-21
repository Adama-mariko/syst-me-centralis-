-- Script de création des tables pour le système de gestion de personnel
-- Base de données: personnel_management

USE personnel_management;

-- 1. Table des entreprises (doit être créée en premier car référencée par users)
CREATE TABLE IF NOT EXISTS entreprises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    siret VARCHAR(14) UNIQUE NOT NULL,
    adresse TEXT NOT NULL,
    ville VARCHAR(100) NOT NULL,
    code_postal VARCHAR(10) NOT NULL,
    telephone VARCHAR(20),
    email VARCHAR(120),
    contact_rh_nom VARCHAR(100),
    contact_rh_email VARCHAR(120),
    contact_rh_telephone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    role ENUM('admin', 'rh_entreprise') NOT NULL,
    entreprise_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (entreprise_id) REFERENCES entreprises(id) ON DELETE SET NULL
);

-- 3. Table des collaborateurs
CREATE TABLE IF NOT EXISTS collaborateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_employe VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    telephone VARCHAR(20),
    adresse TEXT,
    ville VARCHAR(100),
    code_postal VARCHAR(10),
    date_naissance DATE,
    date_embauche DATE NOT NULL,
    poste VARCHAR(100) NOT NULL,
    competences TEXT,
    salaire DECIMAL(10, 2),
    statut ENUM('actif', 'inactif', 'en_conge', 'arret_maladie') DEFAULT 'actif',
    entreprise_actuelle_id INT,
    is_validated_by_rh BOOLEAN DEFAULT FALSE,
    validated_by_user_id INT,
    validation_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (entreprise_actuelle_id) REFERENCES entreprises(id) ON DELETE SET NULL,
    FOREIGN KEY (validated_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 4. Table des placements
CREATE TABLE IF NOT EXISTS placements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    collaborateur_id INT NOT NULL,
    entreprise_id INT NOT NULL,
    poste_demande VARCHAR(100) NOT NULL,
    description TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    salaire_propose DECIMAL(10, 2),
    statut ENUM('en_attente', 'confirme', 'en_cours', 'termine', 'annule') DEFAULT 'en_attente',
    commentaires TEXT,
    created_by_user_id INT NOT NULL,
    validated_by_rh_user_id INT,
    validation_rh_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (collaborateur_id) REFERENCES collaborateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (entreprise_id) REFERENCES entreprises(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (validated_by_rh_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 5. Table des remplacements
CREATE TABLE IF NOT EXISTS remplacements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    remplace_id INT NOT NULL,
    remplacant_id INT NOT NULL,
    type_remplacement ENUM('conge', 'maladie', 'formation', 'autre') NOT NULL,
    motif TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    statut ENUM('planifie', 'en_cours', 'termine', 'annule') DEFAULT 'planifie',
    commentaires TEXT,
    created_by_user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (remplace_id) REFERENCES collaborateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (remplacant_id) REFERENCES collaborateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE RESTRICT,
    CHECK (remplace_id != remplacant_id)
);

-- 6. Table des mouvements (traçabilité)
CREATE TABLE IF NOT EXISTS mouvements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_mouvement ENUM('placement', 'remplacement', 'validation', 'modification', 'suppression') NOT NULL,
    description TEXT NOT NULL,
    collaborateur_id INT,
    entreprise_id INT,
    placement_id INT,
    remplacement_id INT,
    user_id INT NOT NULL,
    donnees_avant TEXT,
    donnees_apres TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collaborateur_id) REFERENCES collaborateurs(id) ON DELETE SET NULL,
    FOREIGN KEY (entreprise_id) REFERENCES entreprises(id) ON DELETE SET NULL,
    FOREIGN KEY (placement_id) REFERENCES placements(id) ON DELETE SET NULL,
    FOREIGN KEY (remplacement_id) REFERENCES remplacements(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
);

-- Index pour améliorer les performances
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_entreprise ON users(entreprise_id);
CREATE INDEX idx_collaborateurs_email ON collaborateurs(email);
CREATE INDEX idx_collaborateurs_entreprise ON collaborateurs(entreprise_actuelle_id);
CREATE INDEX idx_collaborateurs_numero ON collaborateurs(numero_employe);
CREATE INDEX idx_placements_collaborateur ON placements(collaborateur_id);
CREATE INDEX idx_placements_entreprise ON placements(entreprise_id);
CREATE INDEX idx_placements_statut ON placements(statut);
CREATE INDEX idx_remplacements_dates ON remplacements(date_debut, date_fin);
CREATE INDEX idx_mouvements_type ON mouvements(type_mouvement);
CREATE INDEX idx_mouvements_date ON mouvements(created_at);

-- Données initiales
-- Utilisateur admin par défaut (mot de passe: admin123)
INSERT INTO users (email, password_hash, nom, prenom, role, is_active) 
VALUES (
    'admin@personnel.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LQ4YCOuLQv3c1yqBWVHxkd0LQ4YCOuLQv3c1yq', 
    'Admin', 
    'Système', 
    'admin', 
    TRUE
) ON DUPLICATE KEY UPDATE email=email;

-- Entreprise exemple
INSERT INTO entreprises (nom, siret, adresse, ville, code_postal, telephone, email, contact_rh_nom, contact_rh_email, is_active)
VALUES (
    'Entreprise Exemple SARL',
    '12345678901234',
    '123 Rue de la Paix',
    'Paris',
    '75001',
    '01.23.45.67.89',
    'contact@exemple.com',
    'Marie Dupont',
    'rh@exemple.com',
    TRUE
) ON DUPLICATE KEY UPDATE nom=nom;