# Liste Détaillée des Fonctionnalités

Ce document recense de manière exhaustive toutes les fonctionnalités techniques et métier de l'application, classées par module.

## 1. Module Authentification (`/auth`)

| Fonctionnalité | Endpoint | Rôles | Règles Métier & Contraintes | Résultat |
| :--- | :--- | :--- | :--- | :--- |
| **Connexion** | `GET/POST /login` | Tous | • Identifiant : Numéro de téléphone (Unique).<br>• Mot de passe : Code PIN (4 chiffres).<br>• Sécurité : Rate Limiting (5 essais/15min). | Session utilisateur créée. Redirection vers Dashboard selon rôle. |
| **Déconnexion** | `GET /logout` | Connecté | Aucune. | Session détruite. Redirection vers Login. |

## 2. Module Super Admin (`/superadmin`)

| Fonctionnalité | Endpoint | Rôles | Règles Métier & Contraintes | Résultat |
| :--- | :--- | :--- | :--- | :--- |
| **Dashboard SA** | `GET /` | Super Admin | Vue globale des entreprises inscrites. | Liste des entreprises avec statut (Actif/Inactif). |
| **Créer Entreprise** | `GET/POST /entreprise/new` | Super Admin | • Nom et Adresse obligatoires.<br>• **Création Admin obligatoire** : Le formulaire crée en même temps le 1er utilisateur Admin de l'entreprise. | Entrée `Entreprise` + Entrée `User` (Admin) créées. |
| **Modifier Entreprise** | `GET/POST /entreprise/<id>` | Super Admin | Modification nom/adresse. | Mise à jour BDD. |
| **Suspendre Entreprise** | `POST /entreprise/<id>/toggle` | Super Admin | Bascule le statut `actif` (True/False). | Si False : Plus aucun utilisateur de cette entreprise ne peut se connecter. |
| **Gérer Paramètres** | `GET/POST /settings` | Super Admin | Clé-Valeur pour config globale (SEO, App Name). | Mise à jour table `AppSettings`. |

## 3. Module Administration Entreprise (`/admin`)

| Fonctionnalité | Endpoint | Rôles | Règles Métier & Contraintes | Résultat |
| :--- | :--- | :--- | :--- | :--- |
| **Dashboard Admin** | `GET /` | Admin | Vue synthétique des utilisateurs et chantiers de *son* entreprise. | Liste filtrée par `entreprise_id`. |
| **Créer Utilisateur** | `GET/POST /user/new` | Admin | • Champs : Nom, Prénom, Tél, PIN, Rôle.<br>• Tél doit être unique dans tout le système.<br>• PIN : 4 chiffres obligatoires.<br>• Rôles possibles : `direction`, `chef_chantier`, `responsable_achats`. | Nouvel utilisateur créé et lié à l'entreprise. |
| **Modifier Utilisateur** | `GET/POST /user/<id>/edit` | Admin | • Impossible de modifier un Super Admin ou un user d'une autre entreprise.<br>• PIN modifiable (re-hashé). | Mise à jour profil utilisateur. |
| **Activer/Désactiver User** | `POST /user/<id>/toggle` | Admin | Bascule `actif`. | L'utilisateur ne peut plus se connecter si désactivé. |
| **Créer Chantier** | `GET/POST /chantier/new` | Admin | • Nom obligatoire.<br>• Budget Prévisionnel (Float). | Nouveau chantier créé (visible par personne sauf Admin/Direction par défaut). |

## 4. Module Gestion Chantiers (`/chantiers`)

| Fonctionnalité | Endpoint | Rôles | Règles Métier & Contraintes | Résultat |
| :--- | :--- | :--- | :--- | :--- |
| **Liste Chantiers** | `GET /` | Tous | • Direction : Voit *tous* les chantiers.<br>• Autres : Voient uniquement les chantiers *assignés*. | Liste filtrée. |
| **Créer Chantier (Dir)** | `GET/POST /nouveau` | Direction | Idem Admin. Ajout possible de Coordonnées GPS. | Nouveau chantier. |
| **Détail Chantier** | `GET /<id>` | Assignés / Dir | • Affiche KPI (Budget consommé).<br>• Affiche Alertes actives.<br>• Affiche 5 derniers achats. | Vue synthétique du projet. |
| **Assigner Utilisateur** | `GET/POST /<id>/assigner` | Direction | • Sélection parmi les utilisateurs actifs (hors Direction).<br>• Si déjà assigné (inactif), réactive l'assignation. | Entrée `ChantierAssignment` créée/mise à jour. |
| **Désassigner Utilisateur** | `POST /<id>/desassigner/<uid>` | Direction | Soft delete (passe `actif=False` dans l'assignation). | L'utilisateur ne voit plus le chantier. |
| **Rapport PDF** | `GET /<id>/rapport` | Assignés / Dir | Génération à la volée d'un PDF. | Téléchargement fichier `.pdf`. |

## 5. Module Saisies Terrain (`/saisies`)

| Fonctionnalité | Endpoint | Rôles | Règles Métier & Contraintes | Résultat |
| :--- | :--- | :--- | :--- | :--- |
| **Saisir Achat** | `GET/POST /achat` | Tous (sauf Admin) | • Sélection Chantier (parmi assignés).<br>• Montant, Date, Fournisseur.<br>• **Règle Photo** : Obligatoire si Montant > 500.<br>• Format Photo : JPG, PNG, GIF. | Création entrée `Achat` statut `en_attente`. Photo sauvegardée. |
| **Saisir Heures** | `GET/POST /heure` | Tous (sauf Admin/Resp.Achats*) | • Quantité x Tarif Unitaire = Coût Total.<br>• *Note: Le code n'interdit pas explicitement Resp.Achats pour l'instant, mais logique métier le suggère.* | Création entrée `Heure` statut `en_attente`. |
| **Demander Avance** | `GET/POST /avance` | Tous (sauf Resp.Achats) | • **Interdit** au rôle `responsable_achats`.<br>• Montant, Description. | Création entrée `Avance` statut `en_attente`. |

## 6. Module Validation & Contrôle (`/validation`)

| Fonctionnalité | Endpoint | Rôles | Règles Métier & Contraintes | Résultat |
| :--- | :--- | :--- | :--- | :--- |
| **Liste à Valider** | `GET /` | Direction | Affiche toutes les saisies (Achats, Avances, Heures) en statut `en_attente`, triées par date (récent -> ancien). | Vue globale des flux entrants. |
| **Valider Achat** | `POST /achat/<id>/valider` | Direction | • Passe le statut à `valide`.<br>• Enregistre l'ID du validateur et la date.<br>• **Déclenche le calcul des Alertes**. | Dépense intégrée au budget réel. |
| **Refuser Achat** | `POST /achat/<id>/refuser` | Direction | • **Commentaire obligatoire**.<br>• Passe le statut à `refuse`. | Dépense archivée, hors budget. |
| **Valider/Refuser Avance** | `POST /avance/...` | Direction | Idem Achat. | Mouvement de trésorerie validé/refusé. |
| **Valider/Refuser Heure** | `POST /heure/...` | Direction | Idem Achat. | Coût main d'œuvre validé/refusé. |

## 7. Automatisations & Services

| Service | Déclencheur | Logique | Résultat |
| :--- | :--- | :--- | :--- |
| **KPI Calcul** | Accès Détail Chantier | `(Total Achats Validés + Total Heures Validées) / Budget` | Pourcentage d'avancement financier affiché. |
| **Alertes Budget** | Validation Dépense | Si `Conso > Seuil (ex: 80%)` | Création entrée `Alerte` (visible sur Dashboard). |
| **Upload Photo** | Saisie Achat/Avance | • Renommage sécurisé (UUID ou Timestamp).<br>• Vérification extension. | Fichier stocké dans `static/uploads/`. |
