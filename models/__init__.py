from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class AppSettings(db.Model):
    __tablename__ = 'app_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    category = db.Column(db.String(50), default='general')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Entreprise(db.Model):
    __tablename__ = 'entreprises'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    adresse = db.Column(db.String(500))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    logo = db.Column(db.String(500))
    actif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_principal_id = db.Column(db.Integer, db.ForeignKey('users.id', use_alter=True, name='fk_entreprise_admin'), nullable=True)
    
    users = db.relationship('User', back_populates='entreprise', lazy='dynamic', foreign_keys='User.entreprise_id')
    chantiers = db.relationship('Chantier', back_populates='entreprise', lazy='dynamic')
    admin_principal = db.relationship('User', foreign_keys=[admin_principal_id], post_update=True)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    telephone = db.Column(db.String(20), unique=True, nullable=False)
    pin_hash = db.Column(db.String(256), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    role_label = db.Column(db.String(100))  # Libellé du poste personnalisé
    entreprise_id = db.Column(db.Integer, db.ForeignKey('entreprises.id'), nullable=True)
    actif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    entreprise = db.relationship('Entreprise', back_populates='users', foreign_keys=[entreprise_id])
    created_by = db.relationship('User', remote_side=[id], backref='created_users', foreign_keys=[created_by_id])
    assignments = db.relationship('ChantierAssignment', back_populates='user', lazy='dynamic')
    achats = db.relationship('Achat', back_populates='saisi_par', lazy='dynamic', foreign_keys='Achat.user_id')
    avances = db.relationship('Avance', back_populates='beneficiaire', lazy='dynamic', foreign_keys='Avance.user_id')
    heures = db.relationship('Heure', back_populates='saisi_par', lazy='dynamic', foreign_keys='Heure.user_id')

class Chantier(db.Model):
    __tablename__ = 'chantiers'
    
    id = db.Column(db.Integer, primary_key=True)
    entreprise_id = db.Column(db.Integer, db.ForeignKey('entreprises.id'), nullable=True)
    nom = db.Column(db.String(200), nullable=False)
    adresse = db.Column(db.String(500))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    budget_previsionnel = db.Column(db.Float, default=0)
    statut = db.Column(db.String(50), default='en_cours')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    entreprise = db.relationship('Entreprise', back_populates='chantiers')
    assignments = db.relationship('ChantierAssignment', back_populates='chantier', lazy='dynamic')
    achats = db.relationship('Achat', back_populates='chantier', lazy='dynamic')
    avances = db.relationship('Avance', back_populates='chantier', lazy='dynamic')
    heures = db.relationship('Heure', back_populates='chantier', lazy='dynamic')

class ChantierAssignment(db.Model):
    __tablename__ = 'chantier_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantiers.id'), nullable=False)
    date_assignation = db.Column(db.DateTime, default=datetime.utcnow)
    actif = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', back_populates='assignments')
    chantier = db.relationship('Chantier', back_populates='assignments')

class Achat(db.Model):
    __tablename__ = 'achats'
    
    id = db.Column(db.Integer, primary_key=True)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantiers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    date_achat = db.Column(db.Date, nullable=False)
    fournisseur = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(100), default='achats')
    photo_justificatif = db.Column(db.String(500))
    statut = db.Column(db.String(50), default='en_attente')
    remarque_modification = db.Column(db.Text)  # Raison de la modification
    commentaire_validation = db.Column(db.Text)
    valide_par_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_validation = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chantier = db.relationship('Chantier', back_populates='achats')
    saisi_par = db.relationship('User', foreign_keys=[user_id], back_populates='achats')
    valide_par = db.relationship('User', foreign_keys=[valide_par_id])

class Avance(db.Model):
    __tablename__ = 'avances'
    
    id = db.Column(db.Integer, primary_key=True)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantiers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    date_avance = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    photo_justificatif = db.Column(db.String(500))
    statut = db.Column(db.String(50), default='en_attente')
    remarque_modification = db.Column(db.Text)  # Raison de la modification
    commentaire_validation = db.Column(db.Text)
    valide_par_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_validation = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chantier = db.relationship('Chantier', back_populates='avances')
    beneficiaire = db.relationship('User', foreign_keys=[user_id], back_populates='avances')
    valide_par = db.relationship('User', foreign_keys=[valide_par_id])

class Heure(db.Model):
    __tablename__ = 'heures'
    
    id = db.Column(db.Integer, primary_key=True)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantiers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantite = db.Column(db.Float, nullable=False)
    tarif_unitaire = db.Column(db.Float, nullable=False)
    cout_total = db.Column(db.Float, nullable=False)
    date_travail = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    type_travail = db.Column(db.String(100), default='main_oeuvre')
    statut = db.Column(db.String(50), default='en_attente')
    remarque_modification = db.Column(db.Text)  # Raison de la modification
    commentaire_validation = db.Column(db.Text)
    valide_par_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_validation = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chantier = db.relationship('Chantier', back_populates='heures')
    saisi_par = db.relationship('User', foreign_keys=[user_id], back_populates='heures')
    valide_par = db.relationship('User', foreign_keys=[valide_par_id])

class Alerte(db.Model):
    __tablename__ = 'alertes'
    
    id = db.Column(db.Integer, primary_key=True)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantiers.id'))
    type_alerte = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    niveau = db.Column(db.String(50), default='warning')
    lu = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chantier = db.relationship('Chantier')

class Ouvrier(db.Model):
    __tablename__ = 'ouvriers'

    id = db.Column(db.Integer, primary_key=True)
    entreprise_id = db.Column(db.Integer, db.ForeignKey('entreprises.id'), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20))
    poste = db.Column(db.String(100))
    taux_horaire = db.Column(db.Float, default=0.0)
    actif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    entreprise = db.relationship('Entreprise', backref=db.backref('ouvriers', lazy='dynamic'))
    pointages = db.relationship('Pointage', back_populates='ouvrier', lazy='dynamic')

class Pointage(db.Model):
    __tablename__ = 'pointages'

    id = db.Column(db.Integer, primary_key=True)
    ouvrier_id = db.Column(db.Integer, db.ForeignKey('ouvriers.id'), nullable=False)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantiers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Saisi par
    date_pointage = db.Column(db.Date, nullable=False)
    heures = db.Column(db.Float, default=0.0)
    montant = db.Column(db.Float, default=0.0)
    valide = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ouvrier = db.relationship('Ouvrier', back_populates='pointages')
    chantier = db.relationship('Chantier', backref=db.backref('pointages', lazy='dynamic'))
    saisi_par = db.relationship('User', foreign_keys=[user_id])
