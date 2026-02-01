# Gestion Chantiers SaaS

Une plateforme SaaS complète pour la gestion financière et opérationnelle des chantiers BTP. Centralisez le suivi budgétaire, simplifiez les remontées terrain (achats, heures) et gardez le contrôle de votre trésorerie.

## 📚 Documentation Complète

La documentation détaillée se trouve dans le dossier [`docs/`](docs/) :

*   [**Guide Fonctionnel**](docs/guide_fonctionnel.md) : Tout savoir sur les fonctionnalités.
*   [**Manuel Utilisateur**](docs/manuel_utilisateur.md) : Guides pas-à-pas pour chaque rôle (Admin, Chef de Chantier, etc.).
*   [**Architecture Technique**](docs/architecture_technique.md) : Stack technique, base de données et structure du code.
*   [**Modèle SaaS**](docs/modele_saas.md) : Fonctionnement multi-tenant.

## 🚀 Installation Rapide

### Prérequis
*   Python 3.12+
*   PostgreSQL (ou SQLite pour le dev)

### Démarrage

1.  **Cloner et Installer**
    ```bash
    git clone <votre-repo>
    cd <votre-repo>
    pip install -r requirements.txt
    ```

2.  **Configuration**
    Créez un fichier `.env` (voir `docs/architecture_technique.md` pour les détails) ou définissez les variables :
    ```bash
    export DATABASE_URL="postgresql://..."  # ou sqlite:///site.db
    export SECRET_KEY="votre_cle_secrete"
    export SUPER_ADMIN_TELEPHONE="0600000000"
    export SUPER_ADMIN_PIN="1234"
    ```

3.  **Initialisation**
    ```bash
    python init_db.py
    ```

4.  **Lancement**
    ```bash
    python app.py
    ```
    Accédez à l'application sur `http://localhost:5000`.

## 👥 Rôles Principaux

*   **Super Admin** : Gère les entreprises clientes.
*   **Admin Entreprise** : Gère ses chantiers et ses équipes.
*   **Utilisateurs (Terrain/Bureau)** : Saisissent les dépenses ou valident les comptes.

---
*Voir le dossier [docs/](docs/) pour plus d'informations.*
