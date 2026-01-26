#!/usr/bin/env python3
import os
import sys

os.environ.setdefault('DATABASE_URL', os.environ.get('DATABASE_URL', ''))

from app import app
from models import db, User, Entreprise
from security import hash_pin

def init_database():
    with app.app_context():
        db.create_all()
        print("Tables créées avec succès!")
        
        super_admin = User.query.filter_by(role='super_admin').first()
        
        if not super_admin:
            sa_telephone = os.environ.get('SUPER_ADMIN_TELEPHONE')
            sa_pin = os.environ.get('SUPER_ADMIN_PIN')
            sa_nom = os.environ.get('SUPER_ADMIN_NOM', 'Super')
            sa_prenom = os.environ.get('SUPER_ADMIN_PRENOM', 'Admin')
            
            if not sa_telephone or not sa_pin:
                print("")
                print("=" * 60)
                print("CONFIGURATION REQUISE")
                print("=" * 60)
                print("Variables d'environnement pour le Super Admin:")
                print("  - SUPER_ADMIN_TELEPHONE (requis)")
                print("  - SUPER_ADMIN_PIN (requis)")
                print("  - SUPER_ADMIN_NOM (optionnel, défaut: 'Super')")
                print("  - SUPER_ADMIN_PRENOM (optionnel, défaut: 'Admin')")
                print("=" * 60)
                return False
            
            super_admin = User(
                telephone=sa_telephone,
                pin_hash=hash_pin(sa_pin),
                nom=sa_nom,
                prenom=sa_prenom,
                role='super_admin',
                entreprise_id=None,
                actif=True
            )
            db.session.add(super_admin)
            db.session.commit()
            print("")
            print("=" * 60)
            print("SUPER ADMIN CREE AVEC SUCCES")
            print("=" * 60)
            print(f"  Nom: {sa_prenom} {sa_nom}")
            print(f"  Téléphone: {sa_telephone}")
            print(f"  Rôle: Super Administrateur")
            print("=" * 60)
        else:
            print(f"Super Admin existant: {super_admin.prenom} {super_admin.nom} ({super_admin.telephone})")
        
        print("")
        print("Base de données initialisée avec succès!")
        print("")
        print("Hiérarchie des rôles:")
        print("  1. Super Admin → Crée les Admins (gestionnaires d'entreprise)")
        print("  2. Admin → Crée Direction, Chefs Chantier, Resp. Achats")
        print("  3. Direction → Valide les saisies, consulte les dashboards")
        print("  4. Chef Chantier → Saisit achats, avances, heures")
        print("  5. Resp. Achats → Saisit les achats uniquement")
        return True

if __name__ == '__main__':
    init_database()
