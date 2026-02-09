# Manuel Utilisateur

Ce document sert de guide pratique pour utiliser l'application au quotidien. Il est structuré par rôle.

## Accès et Connexion

L'application est accessible via navigateur web (compatible mobile et desktop).

1.  **URL** : Accédez à l'adresse fournie par votre administrateur.
2.  **Identifiant** : Entrez votre numéro de téléphone (format national, sans espaces).
3.  **Authentification** : Saisissez votre code PIN personnel à 4 chiffres.
4.  **Validation** : Cliquez sur "Se connecter".

*En cas d'oubli du code PIN, contactez votre administrateur d'entreprise.*

---

## 1. Rôle : Super Admin

Vous gérez l'infrastructure multi-clients.

### Gestion des Entreprises
*   **Créer** : Menu "Entreprises" > "Nouvelle Entreprise". Renseignez le Nom et l'Adresse.
*   **Activer/Suspendre** : Le bouton "Toggle" permet de couper l'accès à une entreprise instantanément (ex: défaut de paiement).
*   **Premier Admin** : À la création d'une entreprise, vous devez obligatoirement créer son premier compte Administrateur.

### Configuration Globale
*   **Paramètres** : Définissez les variables d'environnement visibles (Nom de l'app, SEO).

---

## 2. Rôle : Administrateur d'Entreprise

Vous pilotez votre organisation. Vous ne saisissez pas de dépenses, vous structurez l'outil.

### Gestion des Utilisateurs
1.  Menu **Utilisateurs** > **Ajouter un utilisateur**.
2.  Renseignez : Nom, Prénom, Téléphone (Unique), Code PIN (4 chiffres).
3.  **Attribuez le rôle** :
    *   *Direction* : Peut tout voir et tout valider.
    *   *Chef de Chantier* : Peut saisir tout type de dépense sur ses chantiers.
    *   *Responsable Achats* : Peut saisir des achats, mais pas d'heures ni d'avances.

### Gestion des Chantiers
1.  Menu **Chantiers** > **Nouveau Chantier**.
2.  Renseignez : Nom, Adresse, Coordonnées GPS (optionnel), **Budget Prévisionnel**.
3.  **Assignation (Critique)** : Par défaut, personne ne voit le chantier. Allez dans la fiche du chantier > Section "Équipe" > "Assigner". Sélectionnez les utilisateurs autorisés.

---

## 3. Rôle : Chef de Chantier / Opérationnel

Vous êtes sur le terrain. Votre interface est simplifiée pour la saisie mobile.

### Saisir un Achat (Matériaux/Fournitures)
1.  Sélectionnez le chantier actif.
2.  Bouton **"Nouvel Achat"**.
3.  Remplissez : Date, Fournisseur, Montant.
4.  **Justificatif** :
    *   Cliquez sur "Photo" pour prendre le ticket en photo ou choisir un fichier.
    *   Formats acceptés : JPG, PNG, GIF.
    *   **Règle** : Si Montant > 500 MAD, la photo est **obligatoire**.
5.  Validez.

### Saisir des Heures (Main d'œuvre)
1.  Bouton **"Saisie Heures"**.
2.  Renseignez : Date, Nombre d'heures, Taux horaire.
3.  Le coût total est calculé automatiquement.
4.  Validez.

### Demander une Avance (Trésorerie)
*Note : Non disponible pour le rôle Responsable Achats.*
1.  Bouton **"Demande Avance"**.
2.  Indiquez le montant souhaité et la date.
3.  Une fois validée par la direction, cette somme vous est attribuée. Vous devrez ensuite la justifier par des "Achats".

---

## 4. Rôle : Direction (Validation)

Vous contrôlez les flux financiers et analysez la rentabilité.

### Validation des Dépenses
Le menu "Validation" centralise toutes les saisies en attente.
1.  Examinez la ligne (cliquez pour voir la photo).
2.  **Valider** : La dépense est acceptée et déduite du budget du chantier.
3.  **Refuser** : Vous **devez** saisir un motif de refus. La dépense est rejetée et archivée.

### Suivi et Reporting
*   **Tableau de Bord** : Visualisez en un coup d'œil les chantiers en alerte (Budget consommé > 80%).
*   **Fiche Chantier** :
    *   Consultez le graphique de consommation budgétaire.
    *   Visualisez la liste des derniers achats validés.
    *   **Export PDF** : Cliquez sur "Générer Rapport" pour télécharger un document complet de la situation financière du chantier.
