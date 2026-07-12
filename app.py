"""
Eye Disease Detection Application
Detects: Diabetic Retinopathy, Cataract, and Glaucoma
Framework: Flask | Models: EfficientNetB0 | Database: SQLite via SQLAlchemy
"""

import os
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, send_file, abort
from PIL import Image

# Database
from database import init_db, get_or_create_patient, save_prediction
from database import get_recent_predictions, get_disease_counts
from database import get_total_patients, get_total_predictions
from database import get_all_patients, get_patient_by_id, get_predictions_by_patient

# Models
from model_diabetic_retinopathy import pred_diabetic_disease
from model_cataract import pred_cataract_disease
from model_glucoma import pred_glucoma_disease

# PDF
from generate_pdf import generate_report_pdf


# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(BASE_DIR, 'eye_disease.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'eyecare-ai-secret-2024'

init_db(app)

# ---------------------------------------------------------------------------
# File Paths
# ---------------------------------------------------------------------------
# BUG FIX #4: Single consistent output image path used everywhere
OUTPUT_IMAGE      = 'static/output_image.png'
METRICS_DIR       = 'static/img2'
PDF_OUTPUT_DIR    = 'static/reports'

os.makedirs('static', exist_ok=True)
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Disease Knowledge Base
# ---------------------------------------------------------------------------

DIABETIC_RETINOPATHY_INFO = {
    "No_DR": {
        "cause": "No signs of diabetic retinopathy. Healthy retina despite diabetes.",
        "treatment": "Regular eye checkups and diabetes control.",
        "homeopathy": "Syzygium jambolanum, Phosphorus (supportive).",
        "allopathy": "Routine monitoring, blood sugar and BP control.",
        "ayurveda": "Triphala, amla, neem for eye health.",
        "india_hospitals": ["AIIMS Delhi", "Aravind Eye Hospital Madurai", "LV Prasad Eye Institute Hyderabad"],
        "usa_hospitals": ["Mayo Clinic", "Bascom Palmer Eye Institute", "Wills Eye Hospital"],
        "cost_india": "Rs.2,000-10,000/year (monitoring)",
        "cost_usa": "$200-1,000/year",
        "success_rate": "100% (no disease present)"
    },
    "Mild": {
        "cause": "Early stage with microaneurysms due to high blood sugar damage.",
        "treatment": "Blood sugar control and regular monitoring.",
        "homeopathy": "Phosphorus, Syzygium jambolanum.",
        "allopathy": "Observation, glucose control, lifestyle changes.",
        "ayurveda": "Triphala eye wash, turmeric, amla.",
        "india_hospitals": ["Aravind Eye Hospital", "LV Prasad Eye Institute", "AIIMS Delhi"],
        "usa_hospitals": ["Mayo Clinic", "Wills Eye Hospital", "Cleveland Clinic"],
        "cost_india": "Rs.5,000-20,000",
        "cost_usa": "$500-2,000",
        "success_rate": "90-95% (with proper control)"
    },
    "Moderate": {
        "cause": "Progression with blocked retinal blood vessels.",
        "treatment": "Laser therapy and strict diabetes management.",
        "homeopathy": "Phosphorus, Arnica (supportive).",
        "allopathy": "Focal/grid laser photocoagulation.",
        "ayurveda": "Neem, amla, triphala formulations.",
        "india_hospitals": ["LV Prasad Eye Institute", "Aravind Eye Hospital", "Narayana Nethralaya Bengaluru"],
        "usa_hospitals": ["Mayo Clinic", "Bascom Palmer Eye Institute", "Johns Hopkins Hospital"],
        "cost_india": "Rs.20,000-60,000",
        "cost_usa": "$2,000-6,000",
        "success_rate": "80-90%"
    },
    "Severe": {
        "cause": "Many blood vessels are blocked, leading to oxygen deprivation in retina.",
        "treatment": "Laser treatment and anti-VEGF injections.",
        "homeopathy": "Phosphorus, Lachesis (supportive).",
        "allopathy": "Pan-retinal photocoagulation, anti-VEGF therapy.",
        "ayurveda": "Supportive herbs like amla, turmeric, giloy.",
        "india_hospitals": ["Narayana Nethralaya", "LV Prasad Eye Institute", "AIIMS Delhi"],
        "usa_hospitals": ["Mayo Clinic", "Cleveland Clinic", "Wills Eye Hospital"],
        "cost_india": "Rs.50,000-1.5 lakhs",
        "cost_usa": "$5,000-15,000",
        "success_rate": "65-80%"
    },
    "Proliferate_DR": {
        "cause": "Advanced stage with abnormal blood vessel growth (neovascularization).",
        "treatment": "Laser surgery, vitrectomy, and injections.",
        "homeopathy": "Phosphorus, Secale cornutum (supportive).",
        "allopathy": "Vitrectomy, anti-VEGF injections, laser surgery.",
        "ayurveda": "Supportive care with triphala, amla.",
        "india_hospitals": ["Aravind Eye Hospital", "LV Prasad Eye Institute", "Sankara Nethralaya Chennai"],
        "usa_hospitals": ["Bascom Palmer Eye Institute", "Mayo Clinic", "Johns Hopkins Hospital"],
        "cost_india": "Rs.1.5-4 lakhs",
        "cost_usa": "$10,000-40,000",
        "success_rate": "50-70% (depends on stage and treatment timing)"
    }
}

CATARACT_INFO = {
    "normal": {
        "cause": "Healthy eye with no visible disease.",
        "treatment": "No treatment required. Maintain eye health with regular checkups.",
        "homeopathy": "Euphrasia, Ruta (for eye care support).",
        "allopathy": "Routine eye examination.",
        "ayurveda": "Triphala eye wash, amla, balanced diet.",
        "india_hospitals": ["AIIMS Delhi", "Aravind Eye Hospital Madurai", "LV Prasad Eye Institute Hyderabad"],
        "usa_hospitals": ["Mayo Clinic", "Wills Eye Hospital", "Bascom Palmer Eye Institute"],
        "cost_india": "Rs.1,000-5,000/year",
        "cost_usa": "$100-500/year",
        "success_rate": "100%"
    },
    "cataract": {
        "cause": "Clouding of the eye lens due to aging, diabetes, or injury.",
        "treatment": "Surgical removal of cloudy lens and replacement with artificial lens.",
        "homeopathy": "Calcarea fluorica, Silicea.",
        "allopathy": "Phacoemulsification surgery with intraocular lens (IOL).",
        "ayurveda": "Triphala, castor oil eye drops (under supervision).",
        "india_hospitals": ["Aravind Eye Hospital", "Sankara Nethralaya Chennai", "AIIMS Delhi"],
        "usa_hospitals": ["Mayo Clinic", "Cleveland Clinic", "Wills Eye Hospital"],
        "cost_india": "Rs.25,000-1 lakh",
        "cost_usa": "$3,000-8,000",
        "success_rate": "95-98%"
    },
    "glaucoma": {
        "cause": "Damage to optic nerve due to increased intraocular pressure.",
        "treatment": "Eye drops, laser therapy, or surgery to reduce pressure.",
        "homeopathy": "Physostigma, Osmium (supportive).",
        "allopathy": "Prostaglandin eye drops, laser trabeculoplasty, surgery.",
        "ayurveda": "Triphala, ghee-based eye therapies (under guidance).",
        "india_hospitals": ["LV Prasad Eye Institute", "Aravind Eye Hospital", "AIIMS Delhi"],
        "usa_hospitals": ["Bascom Palmer Eye Institute", "Mayo Clinic", "Johns Hopkins Hospital"],
        "cost_india": "Rs.20,000-1.5 lakhs",
        "cost_usa": "$2,000-10,000",
        "success_rate": "70-90% (early detection important)"
    },
    "retina_disease": {
        "cause": "Damage to retina due to diabetes, aging, or vascular issues.",
        "treatment": "Laser therapy, injections, or surgery depending on condition.",
        "homeopathy": "Phosphorus, Secale cornutum.",
        "allopathy": "Anti-VEGF injections, vitrectomy, laser photocoagulation.",
        "ayurveda": "Amla, triphala, neem-based therapies.",
        "india_hospitals": ["Narayana Nethralaya Bengaluru", "LV Prasad Eye Institute", "Aravind Eye Hospital"],
        "usa_hospitals": ["Mayo Clinic", "Wills Eye Hospital", "Cleveland Clinic"],
        "cost_india": "Rs.40,000-2 lakhs",
        "cost_usa": "$3,000-20,000",
        "success_rate": "60-85% (depends on severity)"
    }
}

GLAUCOMA_INFO = {
    "Glaucoma_Negative": {
        "cause": "No signs of glaucoma. Optic nerve is healthy and intraocular pressure is normal.",
        "treatment": "No treatment required. Regular eye checkups recommended.",
        "homeopathy": "Euphrasia, Ruta (supportive care).",
        "allopathy": "Routine monitoring and eye pressure check.",
        "ayurveda": "Triphala, amla for maintaining eye health.",
        "india_hospitals": ["LV Prasad Eye Institute", "Aravind Eye Hospital", "AIIMS Delhi"],
        "usa_hospitals": ["Mayo Clinic", "Wills Eye Hospital", "Cleveland Clinic"],
        "cost_india": "Rs.1,000-5,000/year",
        "cost_usa": "$100-500/year",
        "success_rate": "100%"
    },
    "Glaucoma_Positive": {
        "cause": "Damage to optic nerve due to increased intraocular pressure.",
        "treatment": "Eye drops, laser therapy, or surgery to reduce pressure.",
        "homeopathy": "Physostigma, Osmium (supportive).",
        "allopathy": "Prostaglandin eye drops, laser trabeculoplasty, glaucoma surgery.",
        "ayurveda": "Triphala, ghee-based therapies (under supervision).",
        "india_hospitals": ["LV Prasad Eye Institute", "Aravind Eye Hospital", "AIIMS Delhi"],
        "usa_hospitals": ["Bascom Palmer Eye Institute", "Mayo Clinic", "Johns Hopkins Hospital"],
        "cost_india": "Rs.20,000-1.5 lakhs",
        "cost_usa": "$2,000-10,000",
        "success_rate": "70-90% (early detection is important)"
    }
}

# ---------------------------------------------------------------------------
# "Healthy" prediction labels per disease — used in templates
# ---------------------------------------------------------------------------
HEALTHY_LABELS = {"No_DR", "normal", "Glaucoma_Negative"}


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def extract_disease_details(disease_info: dict, prediction: str) -> dict:
    """Extract and flatten disease details from the knowledge base."""
    details = disease_info.get(prediction, {})
    if not details:
        print(f"WARNING: No info found for key: '{prediction}'. "
              f"Available: {list(disease_info.keys())}")
    return {
        "cause":           details.get("cause",           "Information not available."),
        "treatment":       details.get("treatment",       "Information not available."),
        "homeopathy":      details.get("homeopathy",      "Information not available."),
        "allopathy":       details.get("allopathy",       "Information not available."),
        "ayurveda":        details.get("ayurveda",        "Information not available."),
        "india_hospitals": ", ".join(details.get("india_hospitals", [])),
        "usa_hospitals":   ", ".join(details.get("usa_hospitals",   [])),
        "cost_india":      details.get("cost_india",      "N/A"),
        "cost_usa":        details.get("cost_usa",        "N/A"),
        "success_rate":    details.get("success_rate",    "N/A"),
    }


def save_uploaded_image(file) -> None:
    """Save uploaded image to the static folder for model reading."""
    # BUG FIX #4: Save directly to the consistent OUTPUT_IMAGE path
    img = Image.open(file)
    img.save(OUTPUT_IMAGE)


# ---------------------------------------------------------------------------
# Metric Charts (generated once at startup)
# ---------------------------------------------------------------------------

def generate_metric_charts() -> None:
    model_metrics = {
        "EfficientNet": {"accuracy": 0.9650, "precision": 0.9695, "recall": 0.9650, "f1_score": 0.9646},
        "ResNet50":     {"accuracy": 0.9800, "precision": 0.9804, "recall": 0.9800, "f1_score": 0.9800},
        "MobileNet":    {"accuracy": 0.9800, "precision": 0.9816, "recall": 0.9800, "f1_score": 0.9799},
    }
    os.makedirs(METRICS_DIR, exist_ok=True)
    model_names = list(model_metrics.keys())
    colors = ['#4caf50', '#2196f3', '#ff9800']
    metrics_to_plot = {
        "Accuracy":  [model_metrics[m]["accuracy"]  for m in model_names],
        "Precision": [model_metrics[m]["precision"] for m in model_names],
        "Recall":    [model_metrics[m]["recall"]    for m in model_names],
        "F1_Score":  [model_metrics[m]["f1_score"]  for m in model_names],
    }
    for metric_name, values in metrics_to_plot.items():
        plt.figure(figsize=(10, 6))
        bars = plt.bar(model_names, values, color=colors, edgecolor='black')
        plt.title(f"{metric_name} Comparison", fontsize=16)
        plt.ylabel(metric_name)
        plt.xlabel("Model")
        plt.ylim(0.9, 1.01)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height + 0.002,
                     f"{height:.4f}", ha='center', fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(METRICS_DIR, f"{metric_name.lower()}_comparison.png"))
        plt.close()
    print("Metric charts saved.")


generate_metric_charts()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard showing overall stats and recent predictions."""
    stats = {
        'total_patients':    get_total_patients(),
        'total_predictions': get_total_predictions(),
        'disease_counts':    get_disease_counts(),
        'recent':            [p.to_dict() for p in get_recent_predictions(limit=10)],
    }
    return render_template('dashboard.html', **stats)


# ---------------------------------------------------------------------------
# DISEASE PREDICTION ROUTES
# ---------------------------------------------------------------------------

@app.route('/disease-predict', methods=['GET', 'POST'])
def disease_prediction():
    """Diabetic Retinopathy prediction endpoint."""
    title = 'Diabetic Retinopathy Detection using Deep Learning'
    if request.method == 'POST':
        file    = request.files.get('file')
        name    = request.form.get('name', 'Unknown')
        age     = request.form.get('age', None)
        gender  = request.form.get('gender', None)
        contact = request.form.get('contact', None)

        save_uploaded_image(file)
        prediction, confidence = pred_diabetic_disease(OUTPUT_IMAGE)
        details = extract_disease_details(DIABETIC_RETINOPATHY_INFO, prediction)

        patient = get_or_create_patient(name=name, age=age, gender=gender, contact=contact)
        pred_record = save_prediction(patient.id, 'diabetic_retinopathy', prediction, confidence, details)

        # BUG FIX #2: correct is_healthy check using HEALTHY_LABELS set
        is_healthy = prediction in HEALTHY_LABELS

        return render_template(
            'rust-result.html',
            prediction  = prediction.replace("_", " ").title(),
            raw_pred    = prediction,
            confidence  = f"{confidence:.2%}",
            patient_id  = patient.id,
            pred_id     = pred_record.id,
            is_healthy  = is_healthy,
            title       = "Diabetic Retinopathy Diagnosis Result",
            **details
        )
    return render_template('rust.html', title=title)


@app.route('/disease-predict2', methods=['GET', 'POST'])
def disease_prediction2():
    """Cataract prediction endpoint."""
    title = 'Cataract Detection using Deep Learning'
    if request.method == 'POST':
        file    = request.files.get('file')
        name    = request.form.get('name', 'Unknown')
        age     = request.form.get('age', None)
        gender  = request.form.get('gender', None)
        contact = request.form.get('contact', None)

        save_uploaded_image(file)
        prediction, confidence = pred_cataract_disease(OUTPUT_IMAGE)
        details = extract_disease_details(CATARACT_INFO, prediction)

        patient = get_or_create_patient(name=name, age=age, gender=gender, contact=contact)
        pred_record = save_prediction(patient.id, 'cataract', prediction, confidence, details)

        is_healthy = prediction in HEALTHY_LABELS

        return render_template(
            'rust-result2.html',
            prediction  = prediction.replace("_", " ").title(),
            raw_pred    = prediction,
            confidence  = f"{confidence:.2%}",
            patient_id  = patient.id,
            pred_id     = pred_record.id,
            is_healthy  = is_healthy,
            title       = "Cataract Diagnosis Result",
            **details
        )
    return render_template('rust2.html', title=title)


@app.route('/disease-predict3', methods=['GET', 'POST'])
def disease_prediction3():
    """Glaucoma prediction endpoint."""
    title = 'Glaucoma Detection using Deep Learning'
    if request.method == 'POST':
        file    = request.files.get('file')
        name    = request.form.get('name', 'Unknown')
        age     = request.form.get('age', None)
        gender  = request.form.get('gender', None)
        contact = request.form.get('contact', None)

        save_uploaded_image(file)
        prediction, confidence = pred_glucoma_disease(OUTPUT_IMAGE)
        details = extract_disease_details(GLAUCOMA_INFO, prediction)

        patient = get_or_create_patient(name=name, age=age, gender=gender, contact=contact)
        pred_record = save_prediction(patient.id, 'glaucoma', prediction, confidence, details)

        is_healthy = prediction in HEALTHY_LABELS

        return render_template(
            'rust-result3.html',
            prediction  = prediction.replace("_", " ").title(),
            raw_pred    = prediction,
            confidence  = f"{confidence:.2%}",
            patient_id  = patient.id,
            pred_id     = pred_record.id,
            is_healthy  = is_healthy,
            title       = "Glaucoma Diagnosis Result",
            **details
        )
    return render_template('rust3.html', title=title)


# ---------------------------------------------------------------------------
# PATIENT ROUTES
# ---------------------------------------------------------------------------

@app.route('/patients')
def patients_list():
    """Show all patients."""
    patients = get_all_patients()
    return render_template('patients.html', patients=[p.to_dict() for p in patients])


@app.route('/patient/<int:patient_id>')
def patient_detail(patient_id):
    """Show a single patient and all their diagnoses."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        abort(404)
    predictions = get_predictions_by_patient(patient_id)
    return render_template(
        'patient_history.html',
        patient     = patient.to_dict(),
        predictions = [p.to_dict() for p in predictions]
    )


# ---------------------------------------------------------------------------
# PDF REPORT ROUTE
# ---------------------------------------------------------------------------

@app.route('/report/<int:pred_id>')
def download_report(pred_id):
    """Generate and serve a PDF report for a given prediction."""
    from database import get_prediction_by_id
    pred    = get_prediction_by_id(pred_id)
    if not pred:
        abort(404)
    patient = get_patient_by_id(pred.patient_id)
    if not patient:
        abort(404)

    pdf_path = os.path.join(PDF_OUTPUT_DIR, f"report_{pred_id}.pdf")
    generate_report_pdf(patient.to_dict(), pred.to_dict(), OUTPUT_IMAGE, pdf_path)

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"EyeCare_Report_{patient.name}_{pred_id}.pdf",
        mimetype='application/pdf'
    )


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)