import os
import numpy as np
from PIL import Image
from scipy.fftpack import dct, idct
import joblib
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from scipy import stats

# Standard JPEG quantization tables
STANDARD_JPEG_QUANTIZATION_TABLES = {
    # Luminance quantization tables for different quality levels
    0: np.array([16, 11, 10, 16, 24, 40, 51, 61,
                12, 12, 14, 19, 26, 58, 60, 55,
                14, 13, 16, 24, 40, 57, 69, 56,
                14, 17, 22, 29, 51, 87, 80, 62,
                18, 22, 37, 56, 68, 109, 103, 77,
                24, 35, 55, 64, 81, 104, 113, 92,
                49, 64, 78, 87, 103, 121, 120, 101,
                72, 92, 95, 98, 112, 100, 103, 99]),
    1: np.array([17, 18, 24, 47, 99, 99, 99, 99,
                18, 21, 26, 66, 99, 99, 99, 99,
                24, 26, 56, 99, 99, 99, 99, 99,
                47, 66, 99, 99, 99, 99, 99, 99,
                99, 99, 99, 99, 99, 99, 99, 99,
                99, 99, 99, 99, 99, 99, 99, 99,
                99, 99, 99, 99, 99, 99, 99, 99,
                99, 99, 99, 99, 99, 99, 99, 99])}

def get_jpeg_features(image_path):
    # Load the image
    image = Image.open(image_path)

    # Get the JPEG quantization tables
    quant_tables = image.quantization

    # Analyze the quantization tables
    non_standard_tables = 0
    high_frequency_emphasis = 0
    quantization_values = []

    # Iterate over the quantization tables
    for table in quant_tables.values():
        # Check if the current table is a numpy array
        if isinstance(table, np.ndarray):
            # Check if the table is in the STANDARD_JPEG_QUANTIZATION_TABLES dictionary
            if any(np.array_equal(table, STANDARD_JPEG_QUANTIZATION_TABLES[i]) for i in STANDARD_JPEG_QUANTIZATION_TABLES):
                # Standard table, no need to increment non_standard_tables
                pass
            else:
                non_standard_tables += 1

            # Check for high-frequency emphasis
            if np.max(table[5:]) / np.min(table[5:]) > 2:
                high_frequency_emphasis += 1

            quantization_values.extend(table.flatten())
        else:
            # If the table is not a numpy array, skip it
            non_standard_tables += 1

    # Check the image structure
    if image.info.get('progressive', False):
        # Real images often use Progressive DCT
        is_progressive_dct = 1
    else:
        # AI-generated images often use Baseline DCT
        is_progressive_dct = 0

    # Compute additional features, such as the distribution of quantization values
    quantization_values = np.array(quantization_values)
    if len(quantization_values) > 0:
        std_of_quantization = np.std(quantization_values)
        skewness_of_quantization = stats.skew(quantization_values)
        kurtosis_of_quantization = stats.kurtosis(quantization_values)
    else:
        std_of_quantization = 0
        skewness_of_quantization = 0
        kurtosis_of_quantization = 0

    return [non_standard_tables, high_frequency_emphasis, is_progressive_dct,
            std_of_quantization, skewness_of_quantization, kurtosis_of_quantization]

def train_image_classifier(real_images_dir, ai_generated_images_dir, model_type='random_forest'):
    # Collect the real and AI-generated image paths
    real_image_paths = [os.path.join(real_images_dir, f) for f in os.listdir(real_images_dir)]
    ai_generated_image_paths = [os.path.join(ai_generated_images_dir, f) for f in os.listdir(ai_generated_images_dir)]

    # Extract the JPEG features for each image
    X_real = [get_jpeg_features(path) for path in real_image_paths]
    X_ai = [get_jpeg_features(path) for path in ai_generated_image_paths]
    X = np.array(X_real + X_ai)
    y = np.array([0] * len(X_real) + [1] * len(X_ai))  # 0 for real, 1 for AI-generated

    # Drop rows with missing values
    X_no_nan = X[~np.isnan(X).any(axis=1)]
    y_no_nan = y[~np.isnan(X).any(axis=1)]

    # Check if there are any samples left after dropping missing values
    if len(X_no_nan) == 0 or len(y_no_nan) == 0:
        print("No samples left after dropping missing values. Cannot train the model.")
        return None

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_no_nan, y_no_nan, test_size=0.2, random_state=42)

    # Train the model
    if model_type == 'random_forest':
        model = RandomForestClassifier()
    elif model_type == 'gradient_boosting':
        model = HistGradientBoostingClassifier()
    else:
        model = make_pipeline(
            SimpleImputer(strategy='mean'),
            RandomForestClassifier()
        )
    model.fit(X_train, y_train)

    # Evaluate the model
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy:.2f}")

    # Save the trained model
    joblib.dump(model, "ai_generated_image_classifier.pkl")

    return model

def is_image_ai_generated(image_path):
    # Check if the model file exists
    if os.path.exists("ai_generated_image_classifier.pkl"):
        # Extract the JPEG features
        features = get_jpeg_features(image_path)

        # Load the pre-trained machine learning model
        model = joblib.load("ai_generated_image_classifier.pkl")

        # Use the model to predict if the image is AI-generated
        is_ai_generated = model.predict([features])[0]

        if is_ai_generated:
            print(f"Image {image_path} is likely AI-generated.")
        else:
            print(f"Image {image_path} is likely a real photograph.")

        return is_ai_generated
    else:
        print("No trained model available. Cannot determine if the image is AI-generated.")
        return None

def compare_images(image1_path, image2_path):
    # Determine if the images are likely AI-generated
    is_image1_ai_generated = is_image_ai_generated(image1_path)
    is_image2_ai_generated = is_image_ai_generated(image2_path)

    if is_image1_ai_generated is not None and is_image2_ai_generated is not None:
        if is_image1_ai_generated and not is_image2_ai_generated:
            print("Image 1 is more likely to be AI-generated, while Image 2 is more likely to be a real photograph.")
        elif not is_image1_ai_generated and is_image2_ai_generated:
            print("Image 2 is more likely to be AI-generated, while Image 1 is more likely to be a real photograph.")
        elif is_image1_ai_generated and is_image2_ai_generated:
            print("Both images are more likely to be AI-generated.")
        else:
            print("Both images are more likely to be real photographs.")
    else:
        print("Unable to determine the nature of the images.")

# Example usage
real_images_dir = r'E:\codes\pythonn\AI project\Real'
ai_generated_images_dir = r'E:\codes\pythonn\AI project\Ai'

# Train the image classifier using the default RandomForestClassifier
model = train_image_classifier(real_images_dir, ai_generated_images_dir)

if model is not None:
    # Compare two images
    compare_images("E:\codes\pythonn\AI project\image1.jpg", "E:\codes\pythonn\AI project\image2.jpg")