# Guide d'Installation et Déploiement

Ce document décrit la procédure d'installation pour un environnement de développement local et les prérequis pour la production.

## 1. Prérequis Système

*   **OS** : Linux (Ubuntu/Debian recommandé), macOS, ou Windows (WSL2).
*   **Langage** : Python 3.12 ou supérieur.
*   **Base de Données** :
    *   *Dev* : SQLite (inclus par défaut).
    *   *Prod* : PostgreSQL 14+.
*   **Gestionnaire de Paquets** : pip.

## 2. Installation Locale (Développement)

### 2.1 Cloner le dépôt
```bash
git clone <votre-repo-url>
cd gestion-chantiers
```

### 2.2 Environnement Virtuel
Il est impératif d'isoler les dépendances.
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 2.3 Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2.4 Configuration (.env)
Créez un fichier `.env` à la racine du projet.

```bash
# Sécurité (Obligatoire)
SECRET_KEY="votre_cle_secrete_tres_longue_et_aleatoire"

# Base de Données (Optionnel en dev -> SQLite par défaut)
# DATABASE_URL="postgresql://user:password@localhost:5432/gestion_chantiers"

# Création du Super Admin (Pour init_db.py)
SUPER_ADMIN_TELEPHONE="0600000000"
SUPER_ADMIN_PIN="1234"
```

### 2.5 Initialisation de la Base de Données
Ce script crée les tables et l'utilisateur Super Admin par défaut.
```bash
python init_db.py
```
*Si tout se passe bien, aucune erreur n'est affichée.*

### 2.6 Lancement du Serveur
```bash
python app.py
```
Accédez à l'application sur `http://localhost:5000`.

---

## 3. Déploiement en Production

Pour un environnement de production (VPS, Heroku, Dokku, Render...), ne jamais utiliser le serveur de développement Flask (`python app.py`).

### 3.1 Serveur WSGI (Gunicorn)
Utilisez Gunicorn, déjà présent dans `requirements.txt`.

Commande de lancement :
```bash
gunicorn app:app --workers 4 --bind 0.0.0.0:$PORT
```

### 3.2 Variables d'Environnement de Production
Assurez-vous de définir ces variables dans votre hébergeur :

| Variable | Description | Exemple |
| :--- | :--- | :--- |
| `SECRET_KEY` | Clé de signature de session (CRITIQUE). | `5f35...` |
| `DATABASE_URL` | URL de connexion PostgreSQL. | `postgresql://...` |
| `FLASK_ENV` | Environnement. | `production` |
| `SUPER_ADMIN_TELEPHONE` | Pour réinitialisation ou seed. | `0661...` |

### 3.3 Maintenance (Migrations)
Si le schéma de base de données change, il faudra exécuter les migrations. Actuellement, le projet utilise `init_db.py` qui fait un `create_all()`. Pour les mises à jour sur une base existante, il est recommandé d'intégrer `Flask-Migrate` (Alembic).

## 4. Dépannage Courant

*   **Erreur `psycopg2`** : Assurez-vous d'avoir les bibliothèques de développement PostgreSQL installées (`libpq-dev` sur Ubuntu).
*   **Erreur `ReportLab`** : Nécessite parfois des polices système ou des dépendances graphiques.
*   **Port déjà utilisé** : Tuez le processus utilisant le port 5000 (`lsof -i :5000` puis `kill -9 <PID>`).
