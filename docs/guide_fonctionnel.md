# Guide Fonctionnel

Ce document décrit les fonctionnalités et la logique métier de l'application de Gestion de Chantiers.

## Vue d'Ensemble

L'application est une plateforme SaaS (Software as a Service) destinée aux entreprises du BTP. Elle permet de décentraliser la saisie des informations (dépenses, heures) directement sur le terrain tout en centralisant le contrôle financier au niveau de la direction.

## Structure Hiérarchique (SaaS)

L'application fonctionne sur trois niveaux de responsabilité :

### 1. Niveau Plateforme (Super Admin)
C'est l'administrateur technique ou commercial de la solution SaaS.
*   **Responsabilités** : Créer les comptes "Entreprise", configurer les paramètres globaux (SEO, maintenance), surveiller les métriques globales.
*   **Visibilité** : Voit toutes les entreprises mais n'intervient pas dans leur gestion opérationnelle.

### 2. Niveau Entreprise (Admin)
C'est le dirigeant ou le gestionnaire de l'entreprise cliente.
*   **Responsabilités** : Créer les chantiers, créer les comptes utilisateurs de ses employés, affecter les ressources.
*   **Visibilité** : Accès total aux données de son entreprise uniquement.

### 3. Niveau Opérationnel (Utilisateurs)
Ce sont les employés sur le terrain ou au bureau.
*   **Direction** : Valide les dépenses, consulte les tableaux de bord financiers.
*   **Chef de Chantier / Acheteur** : Saisit les données (Achats, Heures, Avances) pour les chantiers auxquels ils sont assignés.

## Fonctionnalités Principales

### 1. Gestion des Chantiers
Chaque chantier est une entité financière autonome.
*   **Budget Prévisionnel** : Défini à la création, il sert de référence pour le calcul des écarts.
*   **Localisation** : Coordonnées GPS pour situer le chantier (utile pour les livraisons/pointages).
*   **Assignation** : Un chantier n'est visible que par les utilisateurs qui y sont explicitement assignés (sauf pour les Admins/Direction qui voient tout).

### 2. Le Flux de Dépenses (Workflow)
Le cœur du système est le suivi des coûts en temps réel.

#### A. La Saisie (Terrain)
Les utilisateurs (Chefs de chantier) saisissent les informations via leur mobile :
*   **Achats** : Montant, Fournisseur, Photo du ticket/facture.
*   **Main d'œuvre** : Nombre d'heures x Taux horaire (calcul automatique du coût).
*   **Avances** : Demande d'argent liquide pour frais divers.

#### B. La Validation (Bureau)
Rien n'est comptabilisé définitivement sans validation.
*   Les saisies apparaissent en statut "En attente".
*   Un utilisateur ayant les droits de validation (Direction/Admin) peut :
    *   **Valider** : La dépense est intégrée au coût réel du chantier.
    *   **Refuser** : Avec un motif explicatif.

### 3. Tableaux de Bord et KPI
Les données validées alimentent les tableaux de bord en temps réel :
*   **Consommation Budget** : (Total Dépenses Validées / Budget Prévisionnel) %.
*   **Trésorerie** : Suivi des avances distribuées vs justificatifs remontés.
*   **Répartition** : Vue par catégorie (Matériaux, Main d'œuvre, etc.).

### 4. Système d'Alertes
Le système surveille activement les indicateurs critiques :
*   **Alerte Budget** : Déclenchée si les dépenses approchent ou dépassent un pourcentage défini du budget (ex: 80% ou 100%).
*   **Alerte Avance** : Déclenchée si un utilisateur a cumulé un montant d'avances non justifiées trop élevé.

## Cycle de Vie d'une Donnée

1.  **Création** : L'utilisateur remplit le formulaire. Statut = `en_attente`.
2.  **Notification** : (Optionnel) Les gestionnaires voient une notification de nouvelle saisie.
3.  **Traitement** : Le gestionnaire examine la photo et le montant.
4.  **Décision** :
    *   Si OK -> Statut = `valide`. Le montant s'ajoute au "Réalisé".
    *   Si KO -> Statut = `refuse`. La donnée est archivée mais ne compte pas dans le budget.
