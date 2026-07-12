"""
Database Setup & Query Helper Functions
Uses SQLite via Flask-SQLAlchemy.

To switch to MySQL/PostgreSQL later, just change SQLALCHEMY_DATABASE_URI in app.py.
Example MySQL URI:  'mysql+pymysql://user:password@localhost/eye_disease_db'
Example Postgres:   'postgresql://user:password@localhost/eye_disease_db'
"""

from flask_sqlalchemy import SQLAlchemy

# ---------------------------------------------------------------------------
# Single shared db instance — imported by app.py and models.py
# ---------------------------------------------------------------------------
db = SQLAlchemy()


# ---------------------------------------------------------------------------
# Database Initialization
# ---------------------------------------------------------------------------

def init_db(app):
    db.init_app(app)
    with app.app_context():
        import models   # ← THIS LINE was missing — registers tables before create_all
        db.create_all()
        print("✅ Database tables created / verified.")

# ---------------------------------------------------------------------------
# Patient Helpers
# ---------------------------------------------------------------------------

def get_or_create_patient(name='Unknown', age=None, gender=None, contact=None):
    """
    Return an existing patient by contact number, or create a new one.
    If contact is None, always creates a new patient record.

    Returns:
        Patient instance
    """
    from models import Patient

    if contact:
        patient = Patient.query.filter_by(contact=contact).first()
        if patient:
            return patient

    patient = Patient(name=name, age=age, gender=gender, contact=contact)
    db.session.add(patient)
    db.session.commit()
    return patient


def get_patient_by_id(patient_id: int):
    """Fetch a patient by primary key. Returns None if not found."""
    from models import Patient
    return Patient.query.get(patient_id)


def get_all_patients():
    """Return all patients ordered by most recently added."""
    from models import Patient
    return Patient.query.order_by(Patient.created_at.desc()).all()


# ---------------------------------------------------------------------------
# Prediction Helpers
# ---------------------------------------------------------------------------

def save_prediction(patient_id: int, disease_type: str,
                    prediction: str, confidence: float, details: dict):
    """
    Save a new prediction record linked to the given patient.

    Args:
        patient_id   : FK to patients.id
        disease_type : 'diabetic_retinopathy' | 'cataract' | 'glaucoma'
        prediction   : raw label from the model e.g. 'Mild', 'cataract'
        confidence   : float between 0 and 1
        details      : dict from extract_disease_details()

    Returns:
        Prediction instance
    """
    from models import Prediction

    record = Prediction(
        patient_id      = patient_id,
        disease_type    = disease_type,
        prediction      = prediction,
        confidence      = confidence,
        cause           = details.get('cause'),
        treatment       = details.get('treatment'),
        homeopathy      = details.get('homeopathy'),
        allopathy       = details.get('allopathy'),
        ayurveda        = details.get('ayurveda'),
        india_hospitals = details.get('india_hospitals'),
        usa_hospitals   = details.get('usa_hospitals'),
        cost_india      = details.get('cost_india'),
        cost_usa        = details.get('cost_usa'),
        success_rate    = details.get('success_rate'),
    )

    db.session.add(record)
    db.session.commit()
    print(f"✅ Prediction saved: patient={patient_id} | type={disease_type} | result={prediction}")
    return record


def get_predictions_by_patient(patient_id: int):
    """Return all predictions for a given patient, newest first."""
    from models import Prediction
    return (Prediction.query
            .filter_by(patient_id=patient_id)
            .order_by(Prediction.diagnosed_at.desc())
            .all())


def get_predictions_by_type(disease_type: str):
    """
    Return all predictions of a given disease type.
    disease_type: 'diabetic_retinopathy' | 'cataract' | 'glaucoma'
    """
    from models import Prediction
    return (Prediction.query
            .filter_by(disease_type=disease_type)
            .order_by(Prediction.diagnosed_at.desc())
            .all())


def get_all_predictions():
    """Return every prediction record, newest first."""
    from models import Prediction
    return Prediction.query.order_by(Prediction.diagnosed_at.desc()).all()


def get_prediction_by_id(prediction_id: int):
    """Fetch a single prediction by primary key."""
    from models import Prediction
    return Prediction.query.get(prediction_id)


def get_recent_predictions(limit: int = 10):
    """Return the most recent N predictions across all disease types."""
    from models import Prediction
    return (Prediction.query
            .order_by(Prediction.diagnosed_at.desc())
            .limit(limit)
            .all())


# ---------------------------------------------------------------------------
# Stats / Dashboard Helpers
# ---------------------------------------------------------------------------

def get_disease_counts():
    """
    Return a dict of { disease_label: count } for all predictions.
    Useful for dashboard pie/bar charts.
    """
    from models import Prediction
    from sqlalchemy import func

    results = (db.session.query(Prediction.prediction, func.count(Prediction.id))
               .group_by(Prediction.prediction)
               .all())
    return {label: count for label, count in results}


def get_total_patients():
    """Return total number of patient records."""
    from models import Patient
    return Patient.query.count()


def get_total_predictions():
    """Return total number of prediction records."""
    from models import Prediction
    return Prediction.query.count()