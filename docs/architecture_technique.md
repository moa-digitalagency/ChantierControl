# Architecture Technique

Ce document détaille les composants techniques, le modèle de données et les flux de l'application SaaS.

## Stack Technique

Application Python/Flask monolithique modulaire.

*   **Backend** : Python 3.12+
*   **Framework** : Flask
*   **ORM** : SQLAlchemy (via Flask-SQLAlchemy)
*   **Base de Données** : PostgreSQL (Production) / SQLite (Dev)
*   **Frontend** : Templates Jinja2 (Server-Side Rendering) + HTML5/CSS3 + JS Vanilla.
*   **Services Tiers** :
    *   Génération PDF : `ReportLab` ou équivalent (via `services/pdf_service.py`).
    *   Stockage Fichiers : Local (dossier `static/uploads` ou similaire) pour les justificatifs.

## Structure du Code

L'application est découpée en **Blueprints** Flask pour séparer les responsabilités par domaine métier.

```text
/
├── app.py                 # Factory, Configuration DB, Register Blueprints
├── models/                # Modèles SQLAlchemy (Single file currently)
│   └── __init__.py        # Définition de toutes les classes (User, Chantier, etc.)
├── routes/                # Contrôleurs (Vues)
│   ├── auth.py            # Login/Logout
│   ├── admin.py           # Gestion Entreprise (Users, Chantiers)
│   ├── chantiers.py       # Détails, Assignations, Rapports
│   ├── saisies.py         # Formulaires (Achats, Heures, Avances)
│   └── validation.py      # Workflow de validation Direction
├── services/              # Logique métier pure
│   ├── notification_service.py # Gestion des alertes
│   └── pdf_service.py     # Moteur de rapport
└── static/                # Assets publics
```

## Modèle de Données (Schema)

Le schéma est conçu pour le **Multi-Tenancy** strict.

### Cœur du Système
1.  **Entreprise** : Le Tenant.
    *   `admin_principal_id` : Clé étrangère vers `User` (Gérée avec `use_alter=True` pour éviter la dépendance circulaire).
2.  **User** : L'utilisateur.
    *   `entreprise_id` : Partitionne les données. Un user appartient à une seule entreprise.
    *   `role` : `super_admin`, `admin`, `direction`, `chef_chantier`, `responsable_achats`.
    *   Auth : `telephone` (Unique) + `pin_hash` (PBKDF2 ou Scrypt).

### Opérationnel
3.  **Chantier** : Projet financier.
    *   Lié à `Entreprise`.
    *   Budget prévisionnel (Float).
4.  **ChantierAssignment** : Table de liaison `User` <-> `Chantier`.
    *   Définit quels chantiers sont visibles pour un utilisateur "terrain".
    *   Attribut `actif` (Boolean) pour gérer l'historique sans supprimer.

### Flux Financiers (Transactions)
Toutes les transactions (`Achat`, `Avance`, `Heure`) partagent des états communs :
*   `statut` : `en_attente` -> `valide` | `refuse`.
*   `valide_par_id` : Traçabilité du validateur.
*   `photo_justificatif` : Chemin vers le fichier (Obligatoire si montant > 500 sur Achat).

## Algorithmes et Services

### Calcul des KPI
*   Calculé à la volée lors de l'affichage du Dashboard Chantier.
*   **Consommation** : `Sum(Achats validés + Heures validées) / Budget`.

### Système d'Alertes (`services/notification_service.py`)
*   Déclenché via `process_alerts(chantier_id)` après chaque validation financière.
*   Vérifie si `Dépenses / Budget > Seuil (ex: 80%, 100%)`.
*   Crée une entrée en base `Alerte`.

### Génération de Rapports
*   Route : `/chantiers/<id>/rapport`
*   Génère un PDF binaire à la volée contenant le résumé financier et la liste des dernières dépenses.

## Sécurité

1.  **Isolation des Données** :
    *   Toutes les requêtes ORM filtrent par `current_user.entreprise_id`.
    *   Middleware/Décorateur vérifie l'appartenance de l'objet (Chantier/User) à l'entreprise de l'utilisateur connecté.
2.  **Uploads** :
    *   Vérification des extensions (JPG, PNG, GIF).
    *   Renommage sécurisé des fichiers pour éviter les collisions et les injections.
3.  **Protection Brute-Force** :
    *   Limitation des tentatives de login (Rate Limiting mémoire).

## Déploiement

*   **Variables d'Environnement** :
    *   `DATABASE_URL` : PostgreSQL connection string.
    *   `SECRET_KEY` : Flask session signing.
*   **Initialisation** :
    *   `python init_db.py` : Crée les tables et le premier Super Admin si inexistant.
