# Liste Détaillée des Fonctionnalités

Ce document constitue la référence exhaustive de toutes les fonctionnalités de la plateforme SaaS de Gestion de Chantiers. Il détaille les règles métier, les validations, les rôles autorisés et les comportements du système.

---

## 1. Module Authentification & Sécurité

### 1.1 Connexion (`/login`)
*   **Identifiant** : Numéro de téléphone (doit être unique dans tout le système).
*   **Authentification** : Code PIN à 4 chiffres (haché via Argon2/Scrypt).
*   **Mécanisme** : Session Flask sécurisée avec cookie HTTPOnly.
*   **Redirection Automatique** :
    *   `Super Admin` -> `/superadmin`
    *   `Admin` -> `/admin`
    *   `Autre` -> `/dashboard`

### 1.2 Isolation des Données (Multi-Tenancy)
*   **Règle Stricte** : Chaque requête est filtrée par `entreprise_id`.
*   Un utilisateur ne peut voir, modifier ou interagir qu'avec les données de son entreprise.
*   **Exception** : Le Super Admin a une vue globale mais cloisonnée par entreprise.

---

## 2. Module Super Admin (`/superadmin`)
*Réservé au rôle `super_admin`.*

### 2.1 Gestion des Entreprises
*   **Création** : Nom, Adresse, Téléphone, Logo, Timezone, Pays.
    *   *Side Effect* : La création d'une entreprise entraîne obligatoirement la création d'un premier utilisateur **Admin**.
*   **Suspension** : Possibilité de désactiver une entreprise.
    *   *Conséquence* : Blocage immédiat de la connexion pour **tous** les utilisateurs de cette entreprise.
*   **Paramètres Globaux** : Configuration technique (Clés API, SEO).

---

## 3. Module Administration Entreprise (`/admin`)
*Réservé au rôle `admin`.*

### 3.1 Gestion des Utilisateurs
*   **Création** : Nom, Prénom, Tél, PIN, Rôle.
*   **Rôles Disponibles** :
    *   `Direction` : Accès total (Validation, Financier, Tous les chantiers).
    *   `Chef de Chantier` : Accès limité aux chantiers assignés, Saisie dépenses, Pointage.
    *   `Responsable Achats` : Saisie Achats uniquement (Pas d'accès Avances).
*   **Validation** : Le téléphone doit être unique. Le PIN doit faire 4 chiffres.

### 3.2 Gestion des Chantiers
*   **Création** : Nom, Adresse, Coordonnées GPS (Lat/Lon), Budget Prévisionnel.
*   **Statut** : `En cours`, `Terminé`, `Suspendu`.

### 3.3 Sauvegarde & Export
*   **Export JSON** : Dump complet des données de l'entreprise (Users, Chantiers, Finances, Ouvriers) pour sauvegarde locale.

---

## 4. Module Gestion Main d'Oeuvre (`/main_oeuvre`)
*Accessible à `Admin`, `Direction`. `Chef de Chantier` (limité aux chantiers assignés).*

### 4.1 Gestion des Ouvriers
*   **Fiche Ouvrier** :
    *   Données : Nom, Prénom, Tél, Poste, Taux Horaire, CNI, Photo Profil, Photo CNI.
    *   **Affectation** : Un ouvrier est lié à un chantier principal (ou aucun).
*   **Import Excel** : Importation en masse via fichier `.xlsx` (Colonnes : Nom, Prénom, Tél, Poste, Taux).
*   **Documents** : Upload et stockage sécurisé des photos (CNI/Profil) dans `static/uploads`.

### 4.2 Pointage (Attendance)
*   **Interface** : Tableau journalier par chantier.
*   **Logique d'Affichage** :
    1.  Affiche les ouvriers assignés au chantier sélectionné.
    2.  Affiche les "Visiteurs" (ouvriers assignés ailleurs mais ayant pointé sur ce chantier ce jour-là).
*   **Saisie** :
    *   `Check-in` / `Check-out` (Heure d'arrivée/départ).
    *   `Pause Début` / `Pause Fin`.
*   **Calcul Automatique** :
    *   `Heures Travaillées` = (Départ - Arrivée) - (Fin Pause - Début Pause).
    *   `Montant` = Heures Travaillées * Taux Horaire de l'ouvrier.
*   **Actions Rapides** : Boutons "Arrivée", "Pause", "Reprise", "Départ" qui enregistrent l'heure actuelle (Now).

### 4.3 Salaires & Rapports
*   **Filtrage** : Par Chantier, Période (Mois, Semaine, Personnalisé).
*   **Agrégation** : Total Heures et Total Montant par ouvrier sur la période.
*   **Exports PDF** :
    *   *Fiche Identité* : Informations signalétiques uniquement.
    *   *Dossier Complet* : Identité + Tableau détaillé de l'historique des pointages et salaires.

---

## 5. Module Opérationnel & Saisies (`/saisies`)

### 5.1 Gestion des Achats
*   **Saisie** : Chantier, Fournisseur, Date, Description, Montant, Catégorie.
*   **Règle de Gestion** : Si Montant > 500 MAD, l'upload d'une **Photo Justificative** est obligatoire.
*   **Statut Initial** : `En attente`.

### 5.2 Gestion des Avances
*   **Restriction** : Interdit au rôle `Responsable Achats`.
*   **Saisie** : Bénéficiaire (Utilisateur connecté), Montant, Date.
*   **Statut Initial** : `En attente`.

### 5.3 Gestion des Heures (Hors Ouvriers)
*   *Note : Module distinct du Pointage, utilisé pour la sous-traitance ou main d'œuvre non salariée.*
*   **Saisie** : Quantité, Tarif Unitaire, Date, Type de travail.
*   **Calcul** : Coût Total = Quantité * Tarif.

---

## 6. Module Validation (`/validation`)
*Réservé au rôle `Direction`.*

### 6.1 Workflow de Validation
*   **Vue Centralisée** : Liste de toutes les saisies (Achats, Avances, Heures) en statut `En attente`.
*   **Actions** :
    *   **Valider** : La dépense devient réelle et impacte le budget du chantier.
    *   **Refuser** : Motif du refus obligatoire. La dépense est archivée mais n'impacte pas le budget.
    *   **Modifier** : La Direction peut corriger une saisie (Montant, Date) avant validation. Une "Remarque de modification" est alors obligatoire.

---

## 7. Tableaux de Bord & Reporting (`/dashboard`)

### 7.1 Dashboard
*   **KPIs** : Budget Consommé vs Prévisionnel (Barres de progression).
*   **Alertes** : Notifications automatiques si un chantier dépasse un seuil critique de budget (ex: 80%, 100%).
*   **Activités Récentes** : Flux des dernières dépenses validées.

### 7.2 Rapports Financiers
*   **Fiche Chantier** : Résumé financier global.
*   **Export PDF** : Rapport officiel généré avec `ReportLab`, incluant en-tête entreprise, tableau des dépenses et totaux.

---

## 8. Stack Technique & Performance
*   **Backend** : Python / Flask.
*   **Base de Données** : SQLAlchemy (Abstraction) / PostgreSQL (Prod).
*   **Frontend** : Jinja2 (Rendu serveur), Tailwind CSS (Design), JS Vanilla (Interactions).
*   **Rendu Graphique** : Chart.js pour les visualisations budgétaires.
*   **Performance** : Chargement optimisé des tableaux (Pagination/Lazy Loading sur les grandes listes via SQLAlchemy dynamic relationships).
