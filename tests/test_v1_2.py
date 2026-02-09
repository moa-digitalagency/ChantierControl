import unittest
import os
import tempfile
from app import create_app
from models import db, User, Chantier, Achat, Entreprise
from security import hash_pin
from datetime import date

class TestV1_2(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            # db.create_all() is called in create_app, but we might need to ensure it uses the right db
            # In fact, create_app already called create_all on the path in env var.

            # Create Enterprise
            ent = Entreprise(nom="Test Entreprise")
            db.session.add(ent)
            db.session.commit()
            self.ent_id = ent.id

            # Create Direction User
            self.direction = User(
                telephone="0600000000",
                pin_hash=hash_pin("1234"),
                nom="Direction",
                prenom="User",
                role="direction",
                entreprise_id=self.ent_id
            )
            db.session.add(self.direction)
            db.session.commit()
            self.direction_id = self.direction.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def login(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.direction_id
            sess['user_role'] = 'direction'
            sess['user_nom'] = 'Direction User'

    def test_create_user_with_role_label(self):
        self.login()
        response = self.client.post('/utilisateurs/nouveau', data={
            'telephone': '0611111111',
            'pin': '1234',
            'nom': 'New',
            'prenom': 'User',
            'role': 'chef_chantier',
            'role_label': 'Sous-chef'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            user = User.query.filter_by(telephone='0611111111').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.role_label, 'Sous-chef')
            self.assertEqual(user.entreprise_id, self.ent_id)

    def test_create_chantier_assignment(self):
        self.login()
        response = self.client.post('/chantiers/nouveau', data={
            'nom': 'Chantier Test',
            'adresse': 'Test Address',
            'budget_previsionnel': '100000'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            chantier = Chantier.query.filter_by(nom='Chantier Test').first()
            self.assertIsNotNone(chantier)
            self.assertEqual(chantier.entreprise_id, self.ent_id)

    def test_edit_achat(self):
        self.login()
        # Create Chantier first
        with self.app.app_context():
            chantier = Chantier(nom="Chantier Achat", entreprise_id=self.ent_id)
            db.session.add(chantier)
            db.session.commit()
            chantier_id = chantier.id

            # Create Achat
            achat = Achat(
                chantier_id=chantier_id,
                user_id=self.direction_id,
                montant=100.0,
                date_achat=date.today(),
                fournisseur="Test Fournisseur",
                statut='en_attente'
            )
            db.session.add(achat)
            db.session.commit()
            achat_id = achat.id

        # Edit Achat without remark
        response = self.client.post(f'/saisies/achat/{achat_id}/modifier', data={
            'montant': '200.0',
            'fournisseur': 'New Fournisseur',
            'date_achat': date.today().isoformat(),
            'remarque_modification': ''
        }, follow_redirects=True)
        self.assertIn(b'Une remarque est obligatoire', response.data)

        # Edit Achat with remark
        response = self.client.post(f'/saisies/achat/{achat_id}/modifier', data={
            'montant': '200.0',
            'fournisseur': 'New Fournisseur',
            'date_achat': date.today().isoformat(),
            'remarque_modification': 'Correction montant'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            achat = db.session.get(Achat, achat_id)
            self.assertEqual(achat.montant, 200.0)
            self.assertEqual(achat.remarque_modification, 'Correction montant')

    def test_delete_achat(self):
        self.login()
        with self.app.app_context():
            chantier = Chantier(nom="Chantier Delete", entreprise_id=self.ent_id)
            db.session.add(chantier)
            db.session.commit()

            achat = Achat(
                chantier_id=chantier.id,
                user_id=self.direction_id,
                montant=100.0,
                date_achat=date.today(),
                fournisseur="Test Fournisseur",
                statut='en_attente'
            )
            db.session.add(achat)
            db.session.commit()
            achat_id = achat.id

        response = self.client.post(f'/saisies/achat/{achat_id}/supprimer', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            achat = db.session.get(Achat, achat_id)
            self.assertIsNone(achat)

if __name__ == '__main__':
    unittest.main()
