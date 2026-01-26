#!/usr/bin/env python3
import os
import sys

os.environ.setdefault('DATABASE_URL', os.environ.get('DATABASE_URL', ''))

from app import app
from models import db, User, Chantier, ChantierAssignment, Achat, Avance, Heure, Alerte
from security import hash_pin

def init_database():
    with app.app_context():
        db.create_all()
        print("Tables créées avec succès!")
        
        existing_admin = User.query.filter_by(telephone='0600000000').first()
        if not existing_admin:
            admin = User(
                telephone='0600000000',
                pin_hash=hash_pin('1234'),
                nom='Admin',
                prenom='Direction',
                role='direction'
            )
            db.session.add(admin)
            
            chef = User(
                telephone='0611111111',
                pin_hash=hash_pin('1234'),
                nom='Alami',
                prenom='Mohamed',
                role='chef_chantier'
            )
            db.session.add(chef)
            
            resp = User(
                telephone='0622222222',
                pin_hash=hash_pin('1234'),
                nom='Benani',
                prenom='Fatima',
                role='responsable_achats'
            )
            db.session.add(resp)
            
            db.session.commit()
            print("Utilisateurs de test créés:")
            print("  - Direction: 0600000000 / PIN: 1234")
            print("  - Chef Chantier: 0611111111 / PIN: 1234")
            print("  - Resp. Achats: 0622222222 / PIN: 1234")
            
            chantier = Chantier(
                nom='Résidence Les Jardins',
                adresse='123 Boulevard Mohammed V, Casablanca',
                latitude=33.5731,
                longitude=-7.5898,
                budget_previsionnel=500000
            )
            db.session.add(chantier)
            db.session.commit()
            
            assignment = ChantierAssignment(
                user_id=chef.id,
                chantier_id=chantier.id
            )
            db.session.add(assignment)
            db.session.commit()
            
            print(f"Chantier de test créé: {chantier.nom}")
        else:
            print("La base de données contient déjà des données.")

if __name__ == '__main__':
    init_database()
