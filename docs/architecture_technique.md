# Architecture Technique

Ce document détaille les composants techniques, le modèle de données (Schéma BDD) et les flux de l'application SaaS.

## 1. Stack Technique

Application monolithique modulaire basée sur Python et Flask, optimisée pour le déploiement sur PaaS (Replit, Heroku, Dokku).

*   **Backend** : Python 3.12+
*   **Framework Web** : Flask 3.0.0
*   **ORM** : SQLAlchemy (via Flask-SQLAlchemy 3.1.1)
*   **Base de Données** : PostgreSQL (Production) / SQLite (Développement)
*   **Serveur WSGI** : Gunicorn 21.2.0
*   **Traitement de Données** : Pandas 2.1.4, NumPy, OpenPyXL (Imports/Exports Excel)
*   **Rapports PDF** : ReportLab 4.0.9
*   **Frontend** :
    *   Moteur de Templates : Jinja2 (Rendu Côté Serveur)
    *   CSS : Tailwind CSS (CDN)
    *   JS : Vanilla JS + Chart.js (CDN)

## 2. Structure du Code

L'application suit une architecture MVC (Modèle-Vue-Contrôleur) où les Vues sont gérées par les routes Flask.

```text
/
├── app.py                 # Point d'entrée, Factory, Configuration DB
├── init_db.py             # Script d'initialisation (Tables + Super Admin)
├── config/                # Fichiers de configuration
├── models/                # Modèles SQLAlchemy (Définition du Schéma)
│   └── __init__.py        # Tous les modèles (User, Chantier, Ouvrier...)
├── routes/                # Contrôleurs (Blueprints Flask)
│   ├── auth.py            # Authentification (Login/Logout)
│   ├── admin.py           # Admin Entreprise (Users, Chantiers)
│   ├── main_oeuvre.py     # Gestion Ouvriers, Pointages, Salaires
│   ├── saisies.py         # Formulaires (Achats, Heures, Avances)
│   ├── superadmin.py      # Gestion des Tenants (Entreprises)
│   └── validation.py      # Workflow de validation Direction
├── services/              # Logique métier transversale
│   ├── notification_service.py # Moteur d'alertes budgétaires
│   └── pdf_service.py     # Générateur de rapports PDF
├── utils/                 # Utilitaires (Photos, Dates, Exports)
├── static/                # Assets (CSS, JS, Images, Uploads)
└── templates/             # Vues HTML (Jinja2)
```

## 3. Modèle de Données (Schéma Relationnel)

Le schéma est conçu pour un **Multi-Tenancy** strict via la colonne `entreprise_id` présente sur toutes les tables critiques.

### 3.1 Cœur du Système (Tenancy & Auth)
*   **Entreprise** : Le Client (Tenant).
    *   Contient : Nom, Logo, Paramètres régionaux.
*   **User** : L'utilisateur final.
    *   Clés : `telephone` (Unique globalement), `pin_hash`.
    *   Rôles : `super_admin`, `admin`, `direction`, `chef_chantier`, `responsable_achats`.
    *   Liaison : `entreprise_id` (1:N).

### 3.2 Opérationnel (Chantiers)
*   **Chantier** : Le centre de coût.
    *   Contient : Budget, GPS, Statut.
*   **ChantierAssignment** : Table de liaison `User` <-> `Chantier`.
    *   Permet d'assigner spécifiquement un Chef de Chantier à un ou plusieurs projets.

### 3.3 Main d'Oeuvre (RH Chantier)
*   **Ouvrier** : Profil travailleur.
    *   Contient : CNI, Photo, Taux Horaire, Poste.
    *   Liaison : Assigné à un `Chantier` principal (mais peut travailler ailleurs).
*   **Pointage** : Enregistrement journalier de présence.
    *   Clés : `ouvrier_id`, `chantier_id`, `date`.
    *   Données : `check_in`, `check_out`, `break_start`, `break_end`.
    *   Calculés : `heures`, `montant`.

### 3.4 Flux Financiers (Transactions)
Toutes les transactions partagent un cycle de vie commun (`en_attente` -> `valide` | `refuse`).

*   **Achat** : Dépense matérielle. (Si > 500 MAD, photo requise).
*   **Avance** : Flux de trésorerie vers un utilisateur.
*   **Heure** : Coût de main d'œuvre externe/globale (distinct du Pointage nominatif).

## 4. Flux de Données & Sécurité

### Isolation des Données
Toutes les requêtes de lecture/écriture sont filtrées par `current_user.entreprise_id`.
*   *Exemple* : `Ouvrier.query.filter_by(entreprise_id=user.entreprise_id)` est systématique.

### Gestion des Uploads
*   Les fichiers (Photos Achats, CNI, Profils) sont stockés dans `static/uploads/`.
*   Renommage unique via UUID pour éviter les collisions.
*   Validation des extensions autorisées (Images uniquement).

### Moteur de Calcul (Pointage)
Le calcul des heures travaillées se fait via une logique Python `datetime` :
`Heures = (Fin - Début) - (Fin Pause - Début Pause)`
*   Gère le cas des shifts de nuit (fin le lendemain).

## 5. Déploiement

Voir le document [Guide d'Installation](guide_installation.md) pour les détails sur les variables d'environnement et la procédure de mise en production.
