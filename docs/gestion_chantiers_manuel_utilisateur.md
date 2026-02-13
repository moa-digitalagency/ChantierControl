# Manuel Utilisateur

Ce document est le guide pratique pour utiliser l'application au quotidien. Il est structuré par module et par rôle.

## 1. Accès et Connexion

L'application est une PWA (Progressive Web App) accessible via navigateur.

1.  **URL** : Accédez à l'adresse fournie par votre administrateur.
2.  **Identifiant** : Entrez votre numéro de téléphone (format national, sans espaces).
3.  **Authentification** : Saisissez votre code PIN personnel à 4 chiffres.
4.  **Validation** : Cliquez sur "Se connecter".

*En cas d'oubli du code PIN, seul votre administrateur d'entreprise peut le réinitialiser.*

---

## 2. Module Administration (Bureau)
*Rôles : Admin, Direction*

### 2.1 Gestion des Chantiers
Pour qu'un chantier soit opérationnel, il doit être créé et assigné.
1.  Allez dans le menu **Chantiers**.
2.  Cliquez sur **Nouveau Chantier**.
3.  Renseignez : Nom, Adresse, Coordonnées GPS (optionnel) et **Budget Prévisionnel**.
4.  **Assignation (Critique)** : Par défaut, personne ne voit le chantier.
    *   Ouvrez la fiche du chantier.
    *   Section "Équipe" > "Assigner".
    *   Sélectionnez les Chefs de Chantier autorisés.

### 2.2 Gestion des Ouvriers
Avant de pouvoir pointer, les ouvriers doivent être créés dans la base.
1.  Allez dans le menu **Ouvriers**.
2.  **Création Unitaire** : Bouton "Nouvel Ouvrier".
    *   Champs obligatoires : Nom, Prénom.
    *   Documents : Importez la photo de profil et la photo de la CNI.
    *   Taux : Définissez le taux horaire (MAD) pour le calcul automatique des salaires.
3.  **Import de Masse** :
    *   Téléchargez le modèle Excel via le bouton "Modèle Import".
    *   Remplissez le fichier et réimportez-le.

---

## 3. Module Terrain (Chefs de Chantier)
*Rôles : Chef de Chantier, Direction*

Votre interface est optimisée pour le mobile. Vous ne voyez que les chantiers qui vous sont assignés.

### 3.1 Pointage Journalier (Appel)
C'est la tâche quotidienne principale.
1.  Allez dans le menu **Pointage**.
2.  Sélectionnez le **Chantier** et la **Date** (par défaut "Aujourd'hui").
3.  La liste affiche vos ouvriers assignés + les visiteurs du jour.
4.  **Saisie Rapide** :
    *   Cliquez sur **Arrivée** quand l'ouvrier commence (remplit l'heure actuelle).
    *   Cliquez sur **Départ** quand il finit.
    *   Gérez les pauses avec **Pause/Reprise**.
5.  **Mode Manuel** : Vous pouvez aussi saisir les heures manuellement (ex: 08:00 - 17:00).
6.  **Validation** : Le calcul des heures et du montant se fait automatiquement.

### 3.2 Saisir un Achat (Matériaux)
1.  Bouton **Nouvel Achat**.
2.  Remplissez : Date, Fournisseur, Montant.
3.  **Justificatif** :
    *   Cliquez sur "Photo" pour prendre le ticket en photo.
    *   **Règle** : Si Montant > 500 MAD, la photo est **obligatoire**.
4.  Validez. La dépense part en validation.

### 3.3 Demander une Avance
Pour obtenir de la trésorerie (Caisse Chantier) :
1.  Bouton **Demande Avance**.
2.  Indiquez le montant souhaité.
3.  Une fois validée par la direction, cette somme vous est attribuée virtuellement.

---

## 4. Module Direction (Contrôle)
*Rôle : Direction*

Vous contrôlez les flux financiers et validez les dépenses terrain.

### 4.1 Validation des Dépenses
Le menu **Validation** centralise toutes les saisies (Achats, Avances, Heures) en attente.
*   **Vérifier** : Cliquez sur la ligne pour voir le détail et la photo.
*   **Valider** : La dépense est acceptée et déduite du budget du chantier.
*   **Refuser** : Motif du refus obligatoire. La dépense est rejetée et archivée.
*   **Modifier** : Vous pouvez corriger un montant ou une affectation avant validation (laisser une remarque est obligatoire).

### 4.2 Suivi et Reporting
*   **Tableau de Bord** : Visualisez les alertes (Budget consommé > 80%).
*   **Fiches Chantier** : Suivez la rentabilité en temps réel.
*   **Rapports PDF** :
    *   *Rapport Chantier* : Bilan financier complet.
    *   *Dossier Ouvrier* : Historique des pointages et salaires pour la paie.

### 4.3 Exports
Pour la comptabilité ou l'archivage :
*   **Excel** : Export de la liste des ouvriers ou des dépenses.
*   **Backup** : (Admin) Export JSON complet de toutes les données de l'entreprise.
