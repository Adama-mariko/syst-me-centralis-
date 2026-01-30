-- Migration pour mettre à jour l'enum type_mouvement dans la table mouvements

-- Modifier la colonne pour utiliser les nouvelles valeurs d'enum
ALTER TABLE mouvements 
MODIFY COLUMN type_mouvement ENUM(
    'placement_cree',
    'placement_modifie',
    'placement_valide',
    'placement_supprime',
    'remplacement_cree',
    'remplacement_modifie',
    'remplacement_supprime',
    'absence_demande',
    'absence_approuve',
    'absence_refuse',
    'collaborateur_cree',
    'collaborateur_modifie',
    'collaborateur_statut_change',
    'entreprise_cree',
    'entreprise_modifie',
    'utilisateur_cree',
    'utilisateur_modifie',
    'utilisateur_role_change',
    'competence_ajout',
    'competence_modification'
) NOT NULL;

-- Mettre à jour les anciennes valeurs vers les nouvelles
UPDATE mouvements SET type_mouvement = 'absence_demande' WHERE type_mouvement = 'ABSENCE_DEMANDE';
UPDATE mouvements SET type_mouvement = 'absence_approuve' WHERE type_mouvement = 'ABSENCE_APPROUVE';
UPDATE mouvements SET type_mouvement = 'absence_refuse' WHERE type_mouvement = 'ABSENCE_REFUSE';
