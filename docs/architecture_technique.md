# Architecture Technique

Ce document détaille l'architecture technique de l'application SaaS de Gestion de Chantiers.

## Stack Technique

L'application est construite sur une stack Python robuste et standardisée :

*   **Langage** : Python 3.12+
*   **Framework Web** : Flask (Utilisation de Blueprints pour la modularité)
*   **ORM (Object Relational Mapper)** : SQLAlchemy (via Flask-SQLAlchemy)
*   **Base de Données** : PostgreSQL (Production) / SQLite (Développement)
*   **Moteur de Templates** : Jinja2 (Rendu côté serveur)
*   **Frontend** : HTML5, CSS3 (Tailwind CSS suggéré par la structure), JavaScript (Vanilla)
*   **Serveur WSGI** : Gunicorn (Recommandé pour la production)

## Structure du Projet

L'application suit une architecture modulaire basée sur les **Blueprints** Flask.

```text
/
├── app.py                 # Point d'entrée de l'application
├── config/                # Configuration (Variables d'environnement)
├── docs/                  # Documentation technique et fonctionnelle
├── models/                # Définitions des modèles de données (SQLAlchemy)
├── routes/                # Contrôleurs (Logique métier par fonctionnalité)
│   ├── auth.py            # Authentification
│   ├── superadmin.py      # Espace Super Admin (SaaS)
│   ├── admin.py           # Espace Admin Entreprise
│   ├── chantiers.py       # Gestion des chantiers
│   ├── saisies.py         # Saisie des dépenses/heures
│   ├── validation.py      # Workflow de validation
│   └── ...
├── services/              # Logique métier complexe (si séparée des routes)
├── static/                # Fichiers statiques (CSS, JS, Images)
├── templates/             # Vues HTML (Jinja2)
└── utils/                 # Fonctions utilitaires
```

## Schéma de Base de Données

Le modèle de données est relationnel et centré sur l'entité `Entreprise` (Multi-tenant).

### Entités Principales

1.  **AppSettings**
    *   Stockage clé-valeur pour la configuration dynamique de l'application (SEO, Seuils d'alerte, Contact).

2.  **Entreprise**
    *   Représente le client (Tenant).
    *   Contient les informations de facturation et de contact.
    *   Relation : 1 Entreprise -> N Users, N Chantiers.
    *   *Note* : Possède une clé étrangère circulaire `admin_principal_id` vers `User` (gérée avec `use_alter=True`).

3.  **User**
    *   Utilisateurs de la plateforme.
    *   Authentification via `telephone` (unique) et `pin_hash`.
    *   Rôles : `super_admin`, `admin`, `user` (avec sous-rôles fonctionnels).
    *   Relation : Appartient à une `Entreprise` (sauf Super Admin).

4.  **Chantier**
    *   Le cœur opérationnel.
    *   Stocke la localisation (GPS) et le budget prévisionnel.
    *   Relation : Appartient à une `Entreprise`.

5.  **ChantierAssignment**
    *   Table de liaison pour assigner des utilisateurs spécifiques à des chantiers.
    *   Permet de restreindre la vue des chefs de chantier/acheteurs.

### Entités Opérationnelles (Flux Financier)

Ces entités tracent l'activité sur les chantiers. Elles sont toutes liées à un `Chantier` et à un `User` (créateur).

6.  **Achat** : Dépenses matérielles/fournisseurs. Inclut photo justificative.
7.  **Avance** : Demandes d'argent liquide.
8.  **Heure** : Suivi de la main d'œuvre (Quantité x Tarif).

### Entités de Contrôle

9.  **Alerte** : Notifications système (Dépassement budget, etc.).

## Sécurité

### Authentification
*   Système sans mot de passe complexe : **Numéro de téléphone + Code PIN (4 chiffres)**.
*   Protection contre la force brute : Rate limiting implémenté en mémoire (5 essais / 15 min par IP).
*   Hashage des PINs avant stockage (Sécurité critique).

### Contrôle d'Accès (RBAC)
*   Les décorateurs (`@login_required`, `@super_admin_required`) protègent les routes.
*   Cloisonnement des données : Un utilisateur ne voit que les données de son `entreprise_id`.

## Déploiement

L'application est conçue pour être "12-factor app compliant". La configuration passe par des variables d'environnement.

### Variables Critiques
*   `DATABASE_URL` : Chaîne de connexion BDD.
*   `SECRET_KEY` : Signature des sessions Flask.
*   `SUPER_ADMIN_*` : Variables utilisées par `init_db.py` pour le bootstrapping (création du premier compte).

### Initialisation
Le script `init_db.py` gère :
1.  La création des tables.
2.  L'injection du compte Super Admin initial (idempotent).
