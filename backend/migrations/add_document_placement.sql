-- Migration: Ajout du champ document_url à la table placements
-- Date: 2026-01-26

ALTER TABLE placements ADD COLUMN document_url VARCHAR(255) DEFAULT NULL;

-- Commentaire pour la colonne
ALTER TABLE placements MODIFY COLUMN document_url VARCHAR(255) 
COMMENT 'URL du document associé au placement (contrat, lettre de mission, etc.)';
