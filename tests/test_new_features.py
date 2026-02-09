import unittest
import os
import sys
import tempfile
from datetime import date, datetime

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User, Chantier, Achat, Alerte
from services.pdf_service import generate_chantier_report
from services import process_alerts

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        # db.create_all() is called in create_app

        # Create Dummy User and Chantier
        self.user = User(
            telephone="0600000000",
            pin_hash="hash",
            nom="Test",
            prenom="User",
            role="direction",
            actif=True
        )
        db.session.add(self.user)

        self.chantier = Chantier(
            nom="Chantier Test",
            budget_previsionnel=100000,
            statut="en_cours"
        )
        db.session.add(self.chantier)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_pdf_generation(self):
        # Add some data
        achat = Achat(
            chantier_id=self.chantier.id,
            user_id=self.user.id,
            montant=5000,
            date_achat=date.today(),
            fournisseur="Test Fournisseur",
            statut="valide"
        )
        db.session.add(achat)
        db.session.commit()

        output_path = generate_chantier_report(self.chantier.id)
        self.assertTrue(output_path)
        self.assertTrue(os.path.exists(output_path))
        os.remove(output_path)

    def test_alert_processing(self):
        # Create condition for alert (Budget Overrun)
        # Budget is 100k. Spend 110k.
        achat = Achat(
            chantier_id=self.chantier.id,
            user_id=self.user.id,
            montant=110000,
            date_achat=date.today(),
            fournisseur="Big Spender",
            statut="valide"
        )
        db.session.add(achat)
        db.session.commit()

        process_alerts(self.chantier.id)

        # Check if alert created in DB
        alerts = Alerte.query.filter_by(chantier_id=self.chantier.id).all()
        self.assertTrue(len(alerts) > 0)

        messages = [a.message for a in alerts]
        print("Generated messages:", messages)

        found = False
        for msg in messages:
            if "Dépassement budget" in msg:
                found = True
                break
        self.assertTrue(found, "Alert for budget overrun not found")

if __name__ == '__main__':
    unittest.main()
