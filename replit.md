# Application de Contrôle de Gestion des Chantiers

## Overview
Application web dédiée au contrôle de gestion opérationnelle des chantiers de construction. Elle permet:
- Le suivi des coûts (salaires, achats, transport)
- Le contrôle de trésorerie (acomptes vs dépenses justifiées)
- Des tableaux de bord avec indicateurs clés (KPI)

## Stack Technique
- **Backend**: Python Flask avec SQLAlchemy ORM
- **Frontend**: HTML, CSS avec Tailwind CDN, JavaScript vanilla
- **Base de données**: PostgreSQL

## Structure du Projet
```
algorithms/          # Calculs KPI et indicateurs
config/             # Configuration Flask et database
docs/               # Documentation
lang/               # Support multilingue
models/             # Modèles SQLAlchemy (User, Chantier, Achat, Avance, Heure, Alerte)
routes/             # Blueprints Flask (auth, dashboard, chantiers, saisies, validation, users)
scripts/            # Scripts utilitaires
security/           # Authentification et autorisation (PIN + téléphone)
services/           # Logique métier (calculs, alertes, KPI)
static/
├── css/            # Styles personnalisés
├── img/            # Images statiques
├── js/             # Scripts JavaScript
└── uploads/        # Photos justificatives uploadées
templates/          # Templates HTML Jinja2
utils/              # Fonctions helpers (upload photos, formatage)
app.py              # Point d'entrée Flask
init_db.py          # Initialisation des tables PostgreSQL
requirements.txt    # Dépendances Python
```

## Profils Utilisateurs
| Profil | Accès | Actions |
|--------|-------|---------|
| Direction | Tous les chantiers | Assigner accès, valider saisies, consulter dashboards complets |
| Chef de Chantier | Chantiers assignés | Saisir achats/avances, uploader justificatifs, consulter solde avance |
| Responsable Achats | Chantiers assignés | Saisir achats, uploader justificatifs |

## Utilisateurs de Test
- **Direction**: 0600000000 / PIN: 1234
- **Chef Chantier**: 0611111111 / PIN: 1234
- **Responsable Achats**: 0622222222 / PIN: 1234

## KPI et Indicateurs
- Taux de consommation budget
- Écart budgétaire
- IPC (Indice de Performance des Coûts)
- Solde avance par chef de chantier

## Alertes Automatiques
- Solde avance < 10 000 MAD
- Dépassement budget > 5%
- Consommation budget > 80%
- Saisies en attente > 24h

## Recent Changes
- 26/01/2026: Création initiale de l'application avec toutes les fonctionnalités MVP
  - Authentification téléphone + PIN
  - Gestion des chantiers avec assignation utilisateurs
  - Saisie des achats, avances et heures
  - Validation par la Direction
  - Tableaux de bord avec graphiques (Chart.js)
  - Interface mobile-first avec Tailwind CSS
