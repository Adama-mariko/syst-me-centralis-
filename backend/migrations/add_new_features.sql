-- Migration pour ajouter les nouvelles fonctionnalités
-- Système de gestion de personnel - Nouvelles fonctionnalités

USE personnel_management;

-- 1. Table des absences (E5)
CREATE TABLE IF NOT EXISTS absences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    collaborateur_id INT NOT NULL,
    type_absence ENUM('conge_paye', 'conge_sans_solde', 'maladie', 'formation', 'maternite', 'paternite', 'autre') NOT NULL,
    motif TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    nombre_jours INT NOT NULL,
    statut ENUM('en_attente', 'approuve', 'refuse', 'annule') DEFAULT 'en_attente',
    commentaires TEXT,
    document_justificatif VARCHAR(255),
    demande_par_collaborateur_id INT NOT NULL,
    approuve_par_user_id INT,
    date_approbation DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (collaborateur_id) REFERENCES collaborateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (demande_par_collaborateur_id) REFERENCES collaborateurs(id) ON DELETE RESTRICT,
    FOREIGN KEY (approuve_par_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 2. Table des notifications/emails (E8)
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_notification ENUM('placement_cree', 'placement_valide', 'placement_refuse', 'absence_demandee', 'absence_approuvee', 'absence_refusee', 'remplacement_propose', 'rappel_validation', 'autre') NOT NULL,
    destinataire_user_id INT,
    destinataire_email VARCHAR(120),
    sujet VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    statut ENUM('en_attente', 'envoye', 'echec') DEFAULT 'en_attente',
    date_envoi DATETIME,
    tentatives INT DEFAULT 0,
    erreur_message TEXT,
    placement_id INT,
    absence_id INT,
    remplacement_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (destinataire_user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (placement_id) REFERENCES placements(id) ON DELETE CASCADE,
    FOREIGN KEY (absence_id) REFERENCES absences(id) ON DELETE CASCADE,
    FOREIGN KEY (remplacement_id) REFERENCES remplacements(id) ON DELETE CASCADE
);

-- 3. Table des rapports/signalements (E9)
CREATE TABLE IF NOT EXISTS rapports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_rapport ENUM('mensuel_placements', 'mensuel_absences', 'mensuel_remplacements', 'annuel_global', 'personnalise') NOT NULL,
    titre VARCHAR(255) NOT NULL,
    description TEXT,
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    entreprise_id INT,
    ville VARCHAR(100),
    statut ENUM('en_cours', 'genere', 'erreur') DEFAULT 'en_cours',
    fichier_path VARCHAR(500),
    donnees_json TEXT,
    genere_par_user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (entreprise_id) REFERENCES entreprises(id) ON DELETE SET NULL,
    FOREIGN KEY (genere_par_user_id) REFERENCES users(id) ON DELETE RESTRICT
);

-- 4. Table des logs de sécurité (E10)
CREATE TABLE IF NOT EXISTS security_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    resource_id INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    statut ENUM('succes', 'echec', 'tentative_suspecte') NOT NULL,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 5. Table des compétences (pour E2 - import CSV)
CREATE TABLE IF NOT EXISTS competences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    categorie VARCHAR(50),
    niveau_requis ENUM('debutant', 'intermediaire', 'avance', 'expert') DEFAULT 'debutant',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 6. Table de liaison collaborateur-compétences
CREATE TABLE IF NOT EXISTS collaborateur_competences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    collaborateur_id INT NOT NULL,
    competence_id INT NOT NULL,
    niveau ENUM('debutant', 'intermediaire', 'avance', 'expert') NOT NULL,
    certifie BOOLEAN DEFAULT FALSE,
    date_acquisition DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collaborateur_id) REFERENCES collaborateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (competence_id) REFERENCES competences(id) ON DELETE CASCADE,
    UNIQUE KEY unique_collaborateur_competence (collaborateur_id, competence_id)
);

-- Mise à jour de la table users pour les nouveaux rôles (E10)
ALTER TABLE users MODIFY COLUMN role ENUM('super_admin', 'admin', 'rh_entreprise', 'viewer') NOT NULL;

-- Mise à jour de la table mouvements pour une meilleure traçabilité (E7)
ALTER TABLE mouvements 
ADD COLUMN absence_id INT,
ADD COLUMN competence_id INT,
ADD COLUMN ip_address VARCHAR(45),
ADD COLUMN user_agent TEXT,
ADD FOREIGN KEY (absence_id) REFERENCES absences(id) ON DELETE SET NULL,
ADD FOREIGN KEY (competence_id) REFERENCES competences(id) ON DELETE SET NULL;

-- Mise à jour du type_mouvement pour inclure les nouvelles actions
ALTER TABLE mouvements MODIFY COLUMN type_mouvement ENUM(
    'placement', 'remplacement', 'validation', 'modification', 'suppression',
    'absence_demande', 'absence_approuve', 'absence_refuse',
    'competence_ajout', 'competence_modification', 'competence_suppression',
    'import_csv', 'export_rapport', 'connexion', 'deconnexion'
) NOT NULL;

-- Index pour les nouvelles tables
CREATE INDEX idx_absences_collaborateur ON absences(collaborateur_id);
CREATE INDEX idx_absences_dates ON absences(date_debut, date_fin);
CREATE INDEX idx_absences_statut ON absences(statut);
CREATE INDEX idx_notifications_destinataire ON notifications(destinataire_user_id);
CREATE INDEX idx_notifications_statut ON notifications(statut);
CREATE INDEX idx_notifications_type ON notifications(type_notification);
CREATE INDEX idx_rapports_type ON rapports(type_rapport);
CREATE INDEX idx_rapports_periode ON rapports(periode_debut, periode_fin);
CREATE INDEX idx_security_logs_user ON security_logs(user_id);
CREATE INDEX idx_security_logs_action ON security_logs(action);
CREATE INDEX idx_security_logs_date ON security_logs(created_at);
CREATE INDEX idx_competences_nom ON competences(nom);
CREATE INDEX idx_collaborateur_competences_collab ON collaborateur_competences(collaborateur_id);

-- Données initiales pour les compétences
INSERT INTO competences (nom, description, categorie, niveau_requis) VALUES
('Microsoft Office', 'Suite bureautique Microsoft (Word, Excel, PowerPoint)', 'Bureautique', 'intermediaire'),
('Comptabilité', 'Gestion comptable et financière', 'Finance', 'intermediaire'),
('Service Client', 'Accueil et relation clientèle', 'Commercial', 'debutant'),
('Gestion de Projet', 'Planification et suivi de projets', 'Management', 'intermediaire'),
('Anglais', 'Langue anglaise parlée et écrite', 'Langues', 'intermediaire'),
('Conduite', 'Permis de conduire B', 'Transport', 'debutant'),
('Vente', 'Techniques de vente et négociation', 'Commercial', 'intermediaire'),
('Ressources Humaines', 'Gestion du personnel et recrutement', 'RH', 'avance'),
('Marketing Digital', 'Marketing en ligne et réseaux sociaux', 'Marketing', 'intermediaire'),
('Logistique', 'Gestion des stocks et approvisionnement', 'Logistique', 'intermediaire')
ON DUPLICATE KEY UPDATE nom=nom;

-- Mise à jour du super admin
UPDATE users SET role = 'super_admin' WHERE email = 'admin@personnel.com';