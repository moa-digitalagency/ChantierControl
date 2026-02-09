# Guide Fonctionnel

Ce document décrit en détail les fonctionnalités et la logique métier de l'application de Gestion de Chantiers. Il sert de référence pour comprendre le fonctionnement global du système.

## Vue d'Ensemble

L'application est une plateforme SaaS (Software as a Service) conçue pour les entreprises du BTP. Son objectif est de décentraliser la saisie des données financières (dépenses, heures) directement sur le terrain via mobile, tout en centralisant le contrôle et la validation au siège.

## Structure Hiérarchique et Rôles

L'application gère les accès via une structure stricte de rôles.

### 1. Niveau Plateforme (Super Admin)
Administrateur global de la solution SaaS.
*   **Périmètre** : Transverse (toutes les entreprises).
*   **Capacités** : Création/Suspension des entreprises clientes, gestion des premiers administrateurs, configuration globale (SEO, messages).
*   **Restrictions** : Ne voit pas le détail opérationnel (dépenses, chantiers) des clients.

### 2. Niveau Entreprise (Admin / Direction)
Gestionnaires de l'entreprise cliente.
*   **Admin** : Gère les utilisateurs, les chantiers et les paramètres de son entreprise.
*   **Direction** : Rôle opérationnel disposant des droits de validation financière et de vue d'ensemble sur tous les chantiers.
*   **Visibilité** : Totale sur les données de leur entreprise.

### 3. Niveau Opérationnel (Terrain)
Utilisateurs assignés à des tâches spécifiques.
*   **Chef de Chantier** : Saisie complète (Achats, Heures, Avances).
*   **Responsable Achats** : Saisie restreinte (Achats uniquement). Ne peut pas demander d'avances ni saisir d'heures.
*   **Visibilité** : Restreinte aux chantiers auxquels ils sont explicitement assignés.

## Fonctionnalités Métier

### 1. Gestion des Chantiers
Le chantier est l'unité analytique centrale.
*   **Cycle de vie** : Création -> Assignation des équipes -> Activité (Saisies) -> Clôture.
*   **Budget** : Un budget prévisionnel est défini à la création. Il sert de base au calcul du pourcentage d'avancement financier.
*   **Assignation** : Mécanisme de sécurité permettant de limiter l'accès d'un utilisateur (ex: Chef de Chantier A) uniquement à ses chantiers.

### 2. Flux de Dépenses (Workflow)

#### A. Saisie Terrain
Les utilisateurs soumettent les dépenses via des formulaires optimisés pour mobile.
*   **Achats Matériaux** :
    *   Champs : Montant, Date, Fournisseur, Catégorie.
    *   **Règle Métier** : Si le montant dépasse **500 MAD**, l'ajout d'une photo justificative est techniquement obligatoire pour valider le formulaire.
    *   Formats acceptés : JPG, PNG, GIF.
*   **Main d'œuvre (Heures)** :
    *   Calcul : Quantité (Heures) x Taux Unitaire = Coût Total.
    *   Permet de suivre le coût de la main d'œuvre interne ou intérimaire.
*   **Demandes d'Avance** :
    *   Permet aux chefs de chantier de demander de la trésorerie.
    *   *Restriction* : Indisponible pour le rôle "Responsable Achats".

#### B. Validation (Bureau)
Aucune saisie n'impacte le budget réel tant qu'elle n'est pas validée.
*   **Interface de Validation** : Réservée au rôle "Direction".
*   **Actions** :
    *   **Valider** : La dépense passe au statut `valide`. Elle est comptabilisée dans le "Réalisé".
    *   **Refuser** : La dépense passe au statut `refuse`. Un motif (commentaire) est obligatoire.
*   **Alertes** : La validation d'une dépense déclenche le recalcul des indicateurs et peut générer des alertes (ex: Budget dépassé).

### 3. Reporting et KPI
Les tableaux de bord agrègent les données validées en temps réel.

*   **Indicateurs Clés (KPI)** :
    *   **Consommation Budget** : Ratio (Dépenses Validées / Budget Prévisionnel).
    *   **Reste à dépenser** : Budget - Dépenses Validées.
*   **Analyses** :
    *   Derniers achats (liste chronologique).
    *   Répartition par catégorie.
*   **Export** : Génération de rapports PDF synthétiques par chantier pour archivage ou partage.

### 4. Système d'Alertes Automatisé
Le système surveille les seuils critiques à chaque validation.
*   **Alerte Budget** : Se déclenche lorsque les dépenses validées atteignent un seuil critique du budget.
*   **Alerte Anomalie** : Peut être configurée pour détecter des saisies incohérentes.

## Cycle de Vie de la Donnée

1.  **Saisie** : Statut `en_attente`. La donnée est visible mais ne compte pas dans les totaux financiers.
2.  **Traitement** : Le gestionnaire analyse la conformité (prix, photo).
3.  **Décision** :
    *   `valide` : Intégration définitive dans les coûts.
    *   `refuse` : Archivage avec motif.
