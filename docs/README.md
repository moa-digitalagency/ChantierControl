# Application de Contrôle de Gestion des Chantiers

## Description
Application web dédiée au contrôle de gestion opérationnelle des chantiers de construction.

## Fonctionnalités
- Suivi des coûts (salaires, achats, transport)
- Contrôle de trésorerie (acomptes vs dépenses justifiées)
- Tableaux de bord avec indicateurs clés

## Profils Utilisateurs

| Profil | Accès | Actions |
|--------|-------|---------|
| Direction | Tous les chantiers | Assigner accès, valider saisies, consulter dashboards |
| Chef de Chantier | Chantiers assignés | Saisir achats/avances, uploader justificatifs |
| Responsable Achats | Chantiers assignés | Saisir achats, uploader justificatifs |

## Utilisateurs de Test

- Direction: 0600000000 / PIN: 1234
- Chef Chantier: 0611111111 / PIN: 1234
- Responsable Achats: 0622222222 / PIN: 1234

## Stack Technique
- Backend: Python Flask
- Frontend: HTML, CSS avec Tailwind
- Base de données: PostgreSQL
