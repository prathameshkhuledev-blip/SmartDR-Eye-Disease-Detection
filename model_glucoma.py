"""
Glaucoma Detection Model
Classes: Glaucoma_Negative | Glaucoma_Positive
Architecture: EfficientNetB0 + custom dense head
Input size: 100x100
"""

import cv2
import numpy as np
from sklearn.preprocessing import LabelEncoder
from efficientnet.tfkeras import EfficientNetB0
from tensorflow.keras import models
from tensorflow.keras.layers import (
    Dense, BatchNormalization, Dropout, GlobalAveragePooling2D
)
from tensorflow.keras.regularizers import l1
from tensorflow.keras.optimizers import RMSprop


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INPUT_SIZE = (100, 100)
WEIGHTS_PATH = 'efficientnet_glucoma.h5'

# BUG FIX #3: Use a path constant so it stays consistent with app.py
OUTPUT_IMAGE_PATH = 'static/output_image.png'

CLASS_NAMES = [
    "Glaucoma_Negative",
    "Glaucoma_Positive"
]


# ---------------------------------------------------------------------------
# Label Encoder Setup
# ---------------------------------------------------------------------------

label_encoder = LabelEncoder()
label_encoder.classes_ = np.array(CLASS_NAMES)
num_classes = len(CLASS_NAMES)


# ---------------------------------------------------------------------------
# Model Definition
# ---------------------------------------------------------------------------

def build_model() -> models.Model:
    """Build and return the EfficientNetB0-based classification model."""
    base_model = EfficientNetB0(
        input_shape=(*INPUT_SIZE, 3),
        include_top=False,
        weights=None
    )

    x = GlobalAveragePooling2D()(base_model.layers[-1].output)

    for units in [128, 64, 32]:
        x = Dense(units, kernel_regularizer=l1(0.0001), activation='relu')(x)
        x = BatchNormalization(renorm=True)(x)
        x = Dropout(0.3)(x)

    outputs = Dense(num_classes, activation='softmax')(x)

    model = models.Model(inputs=base_model.input, outputs=outputs)
    model.compile(
        optimizer=RMSprop(learning_rate=0.0001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


model = build_model()
model.load_weights(WEIGHTS_PATH, by_name=True, skip_mismatch=True)


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------

def preprocess_image(image_path: str) -> np.ndarray:
    """
    Load and preprocess an eye image for model inference.

    Steps:
        1. Resize to INPUT_SIZE
        2. CLAHE enhancement on grayscale channel
        3. Gaussian blur + Canny edge detection
        4. Overlay edges (red channel) onto original image
        5. Normalize to [0, 1]

    Returns:
        np.ndarray: Shape (1, H, W, 3) ready for model.predict()
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot load image: {image_path}")

    image = cv2.resize(image, INPUT_SIZE)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)

    edges_colored = np.zeros_like(image)
    edges_colored[:, :, 2] = edges  # Red channel overlay

    processed = cv2.addWeighted(image, 0.8, edges_colored, 0.5, 0)

    # BUG FIX #3: Use consistent path constant
    cv2.imwrite(OUTPUT_IMAGE_PATH, processed)

    processed = processed / 255.0
    return np.expand_dims(processed, axis=0)


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

def pred_glucoma_disease(img_path: str) -> tuple[str, float]:
    """
    Predict glaucoma presence from the given image path.

    Args:
        img_path: Path to the input eye image.

    Returns:
        Tuple of (predicted_label: str, confidence: float)
    """
    preprocessed = preprocess_image(img_path)
    predictions = model.predict(preprocessed)

    predicted_label = label_encoder.inverse_transform([np.argmax(predictions)])[0]
    confidence = float(np.max(predictions))

    print(f"[Glaucoma] Predicted: {predicted_label} | Confidence: {confidence:.2%}")
    return predicted_label, confidence