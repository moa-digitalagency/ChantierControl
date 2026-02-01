# Gestion Chantiers SaaS

Une application SaaS complète pour la gestion financière et administrative des chantiers BTP. Conçue pour permettre aux entreprises de suivre leurs budgets, achats, et main d'œuvre en temps réel.

## Architecture SaaS

L'application fonctionne sur un modèle hiérarchique :

1.  **Super Admin** :
    *   Création et gestion des entreprises (clients).
    *   Création du compte Administrateur Principal pour chaque entreprise.
    *   Vue globale sur les statistiques de la plateforme.
    *   Configuration globale (SEO, Paramètres).

2.  **Admin (Gestionnaire d'Entreprise)** :
    *   Création et gestion des chantiers de son entreprise.
    *   Gestion des utilisateurs de son entreprise (Direction, Chef de Chantier, Responsable Achats).
    *   Attribution des rôles et des chantiers.

3.  **Utilisateurs** :
    *   **Direction** : Validation des achats/avances, accès aux tableaux de bord financiers.
    *   **Chef de Chantier** : Saisie des dépenses, heures, et demandes d'avances sur le terrain.
    *   **Responsable Achats** : Saisie et suivi des achats fournisseurs.

## Fonctionnalités Clés

*   **Tableau de Bord Intuitif** : KPI en temps réel (Consommation budget, Ecart, Solde avance).
*   **Gestion des Chantiers** : Suivi par chantier avec géolocalisation.
*   **Workflow de Validation** : Système de validation à plusieurs niveaux pour les dépenses.
*   **Rapports PDF** : Génération automatique de rapports de chantier.
*   **Alertes Intelligentes** : Notifications (Email/SMS simulation) en cas de dépassement de budget ou solde bas.
*   **Gestion Multi-Rôles** : Permissions adaptées à chaque métier du BTP.

## Déploiement

### Prérequis

*   Python 3.12+
*   PostgreSQL

### Installation

1.  Cloner le dépôt :
    ```bash
    git clone <votre-repo>
    cd <votre-repo>
    ```

2.  Installer les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

3.  Configurer les variables d'environnement (voir ci-dessous).

4.  Initialiser la base de données :
    ```bash
    python init_db.py
    ```
    *Cette commande créera les tables et le compte Super Admin initial si les variables d'environnement sont définies.*

5.  Lancer l'application :
    ```bash
    gunicorn app:app
    # ou pour le développement
    python app.py
    ```

## Variables d'Environnement

Créez un fichier `.env` à la racine du projet ou configurez votre environnement de déploiement avec les variables suivantes :

### Configuration Générale
*   `DATABASE_URL` : URL de connexion à la base de données PostgreSQL (ex: `postgresql://user:pass@localhost:5432/dbname`).
*   `SECRET_KEY` : Clé secrète pour Flask (générer une chaîne aléatoire longue).

### Identifiants Super Admin (Requis pour l'initialisation)
Ces variables sont utilisées par `init_db.py` pour créer le premier compte Super Admin.

*   `SUPER_ADMIN_TELEPHONE` : Numéro de téléphone pour la connexion (ex: `0600000000`).
*   `SUPER_ADMIN_PIN` : Code PIN à 4 chiffres (ex: `1234`).
*   `SUPER_ADMIN_NOM` : Nom du Super Admin (défaut: `Super`).
*   `SUPER_ADMIN_PRENOM` : Prénom du Super Admin (défaut: `Admin`).

### Notifications (Simulation)
*   Les notifications sont actuellement simulées et les logs sont écrits dans la console et `notifications.log`.
*   Pour une intégration réelle, configurez les services de messagerie ici.

## Utilisation

1.  Connectez-vous avec les identifiants Super Admin définis.
2.  Créez une nouvelle Entreprise et son Administrateur.
3.  Déconnectez-vous et reconnectez-vous avec le compte Admin créé.
4.  Créez vos chantiers et utilisateurs (Chefs de chantier, etc.).
5.  Commencez à saisir et suivre vos dépenses !
