"""
Database Models for Eye Disease Detection Application
Tables:
    - Patient       : stores patient identity info
    - Prediction    : stores each diagnosis result linked to a patient
"""

from datetime import datetime
from database import db


# ---------------------------------------------------------------------------
# Patient Table
# ---------------------------------------------------------------------------

class Patient(db.Model):
    __tablename__ = 'patients'

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name          = db.Column(db.String(100), nullable=False, default='Unknown')
    age           = db.Column(db.Integer, nullable=True)
    gender        = db.Column(db.String(10), nullable=True)       # Male / Female / Other
    contact       = db.Column(db.String(20), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # One patient can have many predictions
    predictions   = db.relationship('Prediction', backref='patient', lazy=True)

    def __repr__(self):
        return f'<Patient id={self.id} name={self.name}>'

    def to_dict(self):
        return {
            'id':         self.id,
            'name':       self.name,
            'age':        self.age,
            'gender':     self.gender,
            'contact':    self.contact,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


# ---------------------------------------------------------------------------
# Prediction Table
# ---------------------------------------------------------------------------

class Prediction(db.Model):
    __tablename__ = 'predictions'

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id      = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    # Which model/route was used
    disease_type    = db.Column(db.String(50),  nullable=False)   # diabetic_retinopathy | cataract | glaucoma

    # Model output
    prediction      = db.Column(db.String(100), nullable=False)
    confidence      = db.Column(db.Float,       nullable=False)

    # Knowledge base details
    cause           = db.Column(db.Text,        nullable=True)
    treatment       = db.Column(db.Text,        nullable=True)
    homeopathy      = db.Column(db.Text,        nullable=True)
    allopathy       = db.Column(db.Text,        nullable=True)
    ayurveda        = db.Column(db.Text,        nullable=True)
    india_hospitals = db.Column(db.Text,        nullable=True)
    usa_hospitals   = db.Column(db.Text,        nullable=True)
    cost_india      = db.Column(db.String(100), nullable=True)
    cost_usa        = db.Column(db.String(100), nullable=True)
    success_rate    = db.Column(db.String(100), nullable=True)

    # Timestamp
    diagnosed_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prediction id={self.id} disease={self.disease_type} result={self.prediction}>'

    def to_dict(self):
        return {
            'id':              self.id,
            'patient_id':      self.patient_id,
            'disease_type':    self.disease_type,
            'prediction':      self.prediction,
            'confidence':      f"{self.confidence:.2%}",
            'cause':           self.cause,
            'treatment':       self.treatment,
            'homeopathy':      self.homeopathy,
            'allopathy':       self.allopathy,
            'ayurveda':        self.ayurveda,
            'india_hospitals': self.india_hospitals,
            'usa_hospitals':   self.usa_hospitals,
            'cost_india':      self.cost_india,
            'cost_usa':        self.cost_usa,
            'success_rate':    self.success_rate,
            'diagnosed_at':    self.diagnosed_at.strftime("%Y-%m-%d %H:%M:%S"),
        }