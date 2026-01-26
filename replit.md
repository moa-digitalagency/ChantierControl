# Application de Contrôle de Gestion des Chantiers (SaaS)

## Overview
Application web SaaS multi-entreprises dédiée au contrôle de gestion opérationnelle des chantiers de construction. Elle permet:
- Le suivi des coûts (salaires, achats, transport)
- Le contrôle de trésorerie (acomptes vs dépenses justifiées)
- Des tableaux de bord avec indicateurs clés (KPI)
- Gestion multi-entreprises avec hiérarchie de rôles

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
models/             # Modèles SQLAlchemy (User, Entreprise, Chantier, Achat, Avance, Heure, Alerte)
routes/             # Blueprints Flask (auth, dashboard, chantiers, saisies, validation, superadmin, admin)
scripts/            # Scripts utilitaires
security/           # Authentification et autorisation (PIN + téléphone)
services/           # Logique métier (calculs, alertes, KPI)
static/
├── css/            # Styles personnalisés
├── img/            # Images statiques
├── js/             # Scripts JavaScript
└── uploads/        # Photos justificatives uploadées
templates/          # Templates HTML Jinja2
├── superadmin/     # Templates Super Admin
├── admin/          # Templates Admin
├── dashboard/      # Tableaux de bord
├── chantiers/      # Gestion chantiers
├── saisies/        # Formulaires de saisie
└── validation/     # Validation des saisies
utils/              # Fonctions helpers (upload photos, formatage)
app.py              # Point d'entrée Flask
init_db.py          # Initialisation des tables PostgreSQL
requirements.txt    # Dépendances Python
```

## Hiérarchie des Rôles
| Niveau | Rôle | Accès | Actions |
|--------|------|-------|---------|
| 1 | Super Admin | Global | Crée les Entreprises et Admins |
| 2 | Admin | Son entreprise | Crée Direction, Chefs Chantier, Resp. Achats, gère les chantiers |
| 3 | Direction | Chantiers entreprise | Valide les saisies, consulte les dashboards complets |
| 4 | Chef de Chantier | Chantiers assignés | Saisit achats, avances, heures, upload justificatifs |
| 5 | Resp. Achats | Chantiers assignés | Saisit les achats uniquement |

## Configuration Super Admin
Le compte Super Admin est créé via variables d'environnement au premier lancement de init_db.py:
- `SUPER_ADMIN_TELEPHONE` (requis) : Numéro de téléphone
- `SUPER_ADMIN_PIN` (requis) : Code PIN à 4 chiffres
- `SUPER_ADMIN_NOM` (optionnel, défaut: 'Super')
- `SUPER_ADMIN_PRENOM` (optionnel, défaut: 'Admin')

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
- 26/01/2026: Passage en mode SaaS multi-entreprises
  - Ajout modèle Entreprise
  - Création rôles super_admin et admin
  - Routes d'administration Super Admin et Admin
  - Filtrage par entreprise sur tous les dashboards et KPI
  - Super Admin initialisé via variables d'environnement
  - Navigation adaptée selon le rôle
