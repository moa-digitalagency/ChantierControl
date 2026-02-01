# Modèle SaaS et Multi-Tenancy

Ce document explique le modèle économique et structurel de l'application en tant que Software as a Service (SaaS).

## Architecture Multi-Tenant

L'application est conçue selon une architecture **Multi-Tenant (Multi-locataire) à base de données partagée**.

### Principe
Tous les clients (Entreprises) utilisent la même instance de l'application et la même base de données. Cependant, une séparation logique stricte est appliquée à chaque requête pour garantir l'étanchéité des données.

*   Chaque table majeure (`User`, `Chantier`, `Achat`, etc.) contient (directement ou par cascade) une référence à l'`entreprise_id`.
*   Le code de l'application filtre systématiquement les requêtes SQL pour n'inclure que les données de l'entreprise de l'utilisateur connecté.

### Avantages
1.  **Maintenance Simplifiée** : Une seule mise à jour du code profite à tous les clients instantanément.
2.  **Infrastructure Unique** : Pas besoin de déployer un serveur par client.
3.  **Onboarding Rapide** : Créer un nouveau client prend quelques secondes (création d'une entrée en base de données).

## Gestion des Abonnements (Business)

Bien que le module de paiement ne soit pas (encore) intégré directement dans le code, la structure de la base de données est prête pour la gestion commerciale.

### Cycle de Vie Client

1.  **Prospection / Création** :
    *   Le Super Admin crée l'entreprise dans le système.
    *   L'état est défini sur `Actif`.
    *   Le client peut commencer immédiatement.

2.  **Suspension** :
    *   En cas de non-paiement ou de fin de contrat, le Super Admin peut passer l'indicateur `actif` de l'entreprise à `False`.
    *   **Conséquence** : Plus aucun utilisateur de cette entreprise ne peut se connecter. Les données sont conservées mais inaccessibles.

3.  **Réactivation** :
    *   Le passage à `actif = True` rétablit l'accès instantanément.

## Hiérarchie des Données

```text
PLATEFORME (SaaS Provider)
└── Super Admin (Vous)
    │
    ├── ENTREPRISE A (Client A)
    │   ├── Admin A (Patron)
    │   ├── Chantier A1
    │   │   ├── Dépenses
    │   │   └── Chefs de chantier
    │   └── Chantier A2
    │
    └── ENTREPRISE B (Client B)
        ├── Admin B (Patron)
        └── Chantier B1
```

## Sécurité et Isolation

L'isolation est garantie par le backend :
*   Un utilisateur est lié définitivement à une entreprise à sa création via `entreprise_id`.
*   Il est impossible pour un utilisateur "Admin" de voir les données d'une autre entreprise, car toutes les requêtes de lecture/écriture vérifient cet ID.
