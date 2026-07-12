# 👁️ SmartDR+ / EYECARE AI - Multi-Disease Detection System

SmartDR+ (EYECARE AI) is an end-to-end deep learning web application designed for early detection of eye diseases. Powered by TensorFlow, Flask, and OpenCV, it analyzes retinal images to classify Diabetic Retinopathy, Cataract, and Glaucoma, offering dynamic analytics and automated PDF reporting.

---

## 🎥 Project Demo
*(Drag and drop your project demo video or GIF file right here in this section!)*

---

## ✨ Key Features
* **Multi-Disease Classification:** Accurately screens for Diabetic Retinopathy, Cataract, and Glaucoma using specialized deep learning models.
* **Interactive Dashboard:** Flask-based UI with dynamic disease analytics and visual charts.
* **Automated Medical Reports:** Generates downloadable PDF diagnostic summaries for patients.
* **Database Management:** Integrated SQLite/Flask-SQLAlchemy storage for tracking patient history and records.

---

## 🛠️ Tech Stack
* **Core Language:** Python 3.10
* **Deep Learning Frameworks:** TensorFlow, Keras, OpenCV, EfficientNet
* **Web & Database:** Flask, Flask-SQLAlchemy, PyMySQL
* **Data Processing & Analytics:** NumPy, Pandas, Scikit-Learn, Matplotlib, Seaborn
* **Reporting & Utilities:** ReportLab, Pillow, gTTS

---

## 🚀 Setup & Execution Guide

1. **Clone Repository:**
   git clone https://github.com/prathameshkhuledev-blip/SmartDR-Eye-Disease-Detection.git
   cd SmartDR-Eye-Disease-Detection

2. **Create Environment:**
   conda create -n eye_disease python=3.10 -y
   conda activate eye_disease

3. **Install Dependencies:**
   pip install tensorflow==2.13.0 numpy==1.23.5 pandas==2.1.1 scikit-learn==1.3.2 scikit-image==0.19.1 xgboost==1.5.2 opencv-python==4.8.1.78 efficientnet==1.1.1 Flask==2.2.5 Werkzeug==2.2.3 flask_sqlalchemy Pillow==10.0.1 reportlab==4.0.6 matplotlib==3.7.2 seaborn==0.13.2 PyMySQL==0.10.0 requests tqdm editdistance lmdb fuzzywuzzy path pydub pygame gTTS ipykernel

4. **Launch Application:**
   python check_db.py
   python app.py

5. **Access Web App:**
   Open http://127.0.0.1:5000 in your web browser.
