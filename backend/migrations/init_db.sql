-- Script d'initialisation de la base de données
-- Création de la base de données
CREATE DATABASE IF NOT EXISTS personnel_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE personnel_management;

-- Création d'un utilisateur admin par défaut
-- Mot de passe: admin123 (à changer en production)
INSERT INTO users (email, password_hash, nom, prenom, role, is_active, created_at, updated_at) 
VALUES (
    'admin@personnel.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LQ4YCOuLQv3c1yqBWVHxkd0LQ4YCOuLQv3c1yq', 
    'Admin', 
    'Système', 
    'admin', 
    1, 
    NOW(), 
    NOW()
) ON DUPLICATE KEY UPDATE email=email;

-- Exemple d'entreprise
INSERT INTO entreprises (nom, siret, adresse, ville, code_postal, telephone, email, contact_rh_nom, contact_rh_email, is_active, created_at, updated_at)
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
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE nom=nom;