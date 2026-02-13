# Gestion Chantiers SaaS 🏗️

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

> **La solution complète pour piloter la rentabilité de vos chantiers BTP.**
> Centralisez vos achats, gérez vos équipes terrain et suivez votre trésorerie en temps réel.

---

## 📖 Table des Matières
- [Fonctionnalités Clés](#-fonctionnalités-clés)
- [Documentation](#-documentation-officielle)
- [Installation Rapide](#-installation-rapide)
- [Architecture](#-architecture)
- [Stack Technique](#-stack-technique)

---

## 🚀 Fonctionnalités Clés

Une plateforme tout-en-un conçue pour les entreprises du BTP multi-chantiers.

*   **Multi-Tenancy** : Isolation stricte des données par entreprise.
*   **Gestion Financière** :
    *   Saisie des **Achats** avec photo justificative obligatoire (> 500 MAD).
    *   Gestion de la **Trésorerie** (Avances Caisse).
    *   Suivi budgétaire en temps réel (Consommé vs Prévisionnel).
*   **Main d'Oeuvre & RH** :
    *   Fiches Ouvriers complètes (CNI, Photos).
    *   **Pointage Journalier** (Check-in/Check-out, Pauses).
    *   Calcul automatique des salaires et heures supplémentaires.
*   **Rapports & Exports** :
    *   Génération de **PDFs** professionnels (Fiche Chantier, Dossier Ouvrier).
    *   Exports **Excel** pour la comptabilité.
*   **Rôles & Permissions** :
    *   *Super Admin* (Plateforme), *Admin* (Entreprise), *Direction* (Validation), *Chef de Chantier* (Terrain), *Responsable Achats*.

👉 **[Voir la liste exhaustive des fonctionnalités](docs/features_full_list.md)**

---

## 📚 Documentation Officielle

Toute la documentation technique et fonctionnelle se trouve dans le dossier [`docs/`](docs/).

| Document | Description | Cible |
| :--- | :--- | :--- |
| **[Guide Fonctionnel](docs/features_full_list.md)** | La "Bible" des fonctionnalités, règles de gestion et validations. | Tous |
| **[Manuel Utilisateur](docs/manuel_utilisateur.md)** | Guides pas-à-pas pour chaque rôle (Admin, Terrain, Direction). | Utilisateurs Finaux |
| **[Architecture Technique](docs/architecture_technique.md)** | Structure du code, Schéma BDD, Flux de données. | Développeurs |
| **[Guide d'Installation](docs/guide_installation.md)** | Procédures de déploiement (Dev & Prod). | DevOps |

---

## ⚡ Installation Rapide

Pour lancer l'application en mode développement local :

1.  **Cloner et Installer**
    ```bash
    git clone <votre-repo>
    cd gestion-chantiers
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configuration**
    Créez un fichier `.env` à la racine :
    ```bash
    SECRET_KEY="votre_cle_secrete_dev"
    SUPER_ADMIN_TELEPHONE="0600000000"
    SUPER_ADMIN_PIN="1234"
    ```

3.  **Lancer**
    ```bash
    python init_db.py  # Crée la BDD et le Super Admin
    python app.py      # Lance le serveur sur http://localhost:5000
    ```

---

## 🏗 Architecture

Le projet suit une architecture **Monolithique Modulaire** basée sur Flask Blueprints.

*   **Backend** : Python / Flask / SQLAlchemy.
*   **Frontend** : Jinja2 (SSR) / Tailwind CSS / Vanilla JS.
*   **Base de Données** : PostgreSQL (Prod) / SQLite (Dev).
*   **Sécurité** : Auth par Téléphone + PIN, Hachage Argon2, Protection CSRF.

Chaque module métier (Auth, Admin, Main d'Oeuvre, Finances) est isolé dans son propre contrôleur (`routes/`).

---

## 🛠 Stack Technique

*   **Core** : Python 3.12+, Flask 3.0.0
*   **Data** : SQLAlchemy, PostgreSQL, Pandas
*   **Reporting** : ReportLab (PDF), OpenPyXL (Excel)
*   **Server** : Gunicorn
*   **UI** : Tailwind CSS, Chart.js

---
*© 2024 Gestion Chantiers SaaS. Documentation générée par l'équipe technique.*
