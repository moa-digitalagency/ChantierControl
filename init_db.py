#!/usr/bin/env python3
import os
import sys
import time
from sqlalchemy.exc import OperationalError
from sqlalchemy import inspect, text

# NOTE: Do NOT set default DATABASE_URL here using os.environ.setdefault.
# It overrides the default in app.py if the env var is missing.

from app import app
from models import db, User, Entreprise
from security import hash_pin

def wait_for_db(app):
    """Waits for the database to be available."""
    print("Waiting for database connection...")
    with app.app_context():
        retries = 30
        while retries > 0:
            try:
                # Try to connect
                with db.engine.connect() as conn:
                    pass
                print("Database is ready!")
                return True
            except OperationalError:
                retries -= 1
                print(f"Database unavailable, retrying in 1s... ({retries} left)")
                time.sleep(1)
            except Exception as e:
                print(f"Unexpected error connecting to DB: {e}")
                return False
    return False

def init_database():
    # Ensure DB is ready (useful for Docker/deployment)
    if not wait_for_db(app):
        print("Could not connect to database after retries.")
        sys.exit(1)

    with app.app_context():
        try:
            db.create_all()
            print("Tables créées avec succès!")

            # Migration logic for v1.2
            inspector = inspect(db.engine)

            # Check users table
            columns = [c['name'] for c in inspector.get_columns('users')]
            if 'role_label' not in columns:
                print("Migration: Ajout de role_label à la table users")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN role_label VARCHAR(100)"))
                    conn.commit()

            # Check achats table
            columns = [c['name'] for c in inspector.get_columns('achats')]
            if 'remarque_modification' not in columns:
                print("Migration: Ajout de remarque_modification à la table achats")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE achats ADD COLUMN remarque_modification TEXT"))
                    conn.commit()

            # Check avances table
            columns = [c['name'] for c in inspector.get_columns('avances')]
            if 'remarque_modification' not in columns:
                print("Migration: Ajout de remarque_modification à la table avances")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE avances ADD COLUMN remarque_modification TEXT"))
                    conn.commit()

            # Check heures table
            columns = [c['name'] for c in inspector.get_columns('heures')]
            if 'remarque_modification' not in columns:
                print("Migration: Ajout de remarque_modification à la table heures")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE heures ADD COLUMN remarque_modification TEXT"))
                    conn.commit()

        except Exception as e:
            print(f"Erreur lors de l'initialisation de la base: {e}")
            # Continue execution to allow super admin check
        
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
                sys.exit(1)
            
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
