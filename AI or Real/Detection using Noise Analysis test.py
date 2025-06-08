import os
import numpy as np
from PIL import Image
from scipy.fftpack import dct, idct
import joblib
import argparse # For parsing command-line arguments
from sklearn.impute import SimpleImputer # For handling missing data
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from scipy import stats

# Standard JPEG quantization tables (luminance)
# These are used as a baseline to identify images with non-standard (potentially AI-generated) tables.
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
    """
    Extracts JPEG features from an image, focusing on quantization tables and DCT structure.
    These features can help differentiate between real and AI-generated images.
    """
    # Load the image
    try:
        image = Image.open(image_path)
    except FileNotFoundError: # Error handling: image file does not exist
        print(f"Error: Image file not found at {image_path}")
        return None
    except Image.UnidentifiedImageError: # Error handling: file is not a valid image or is corrupted
        print(f"Error: Cannot identify image file at {image_path}. It may be corrupted or not a valid image format.")
        return None

    # Get the JPEG quantization tables from the image metadata
    quant_tables = image.quantization

    # Initialize feature counters
    non_standard_tables = 0
    high_frequency_emphasis = 0
    quantization_values = []

    # Iterate over the quantization tables found in the image
    if quant_tables: # Check if quant_tables is not None (i.e., tables exist)
        for table_key in quant_tables:
            table = quant_tables[table_key]

            # Feature extraction safeguard: Convert table to numpy array if it's a list/tuple
            if isinstance(table, (list, tuple)):
                table = np.array(table)

            if isinstance(table, np.ndarray):
                # Check if the table matches any known standard JPEG tables
                is_standard = False
                for std_table in STANDARD_JPEG_QUANTIZATION_TABLES.values():
                    # Ensure dtype matches for accurate comparison
                    if np.array_equal(table.astype(std_table.dtype), std_table):
                        is_standard = True
                        break
                if not is_standard:
                    non_standard_tables += 1

                # Feature extraction safeguard: Check for high-frequency emphasis
                # Requires at least 6 elements for table[5:] and non-zero divisor to prevent ZeroDivisionError
                if table.size >= 6 and np.min(table[5:]) != 0:
                    if np.max(table[5:]) / np.min(table[5:]) > 2: # High ratio suggests emphasis
                        high_frequency_emphasis += 1
                else:
                    # Silently skip if conditions not met, or log a warning
                    # print(f"Info: Skipping high-frequency emphasis for a table in {image_path} due to insufficient data or zero minimum.")
                    pass # Pass to avoid incrementing high_frequency_emphasis

                quantization_values.extend(table.flatten())
            else:
                # Feature extraction safeguard: Handle cases where a table is not in a recognized array format
                # print(f"Warning: Table for key {table_key} in {image_path} is not a recognized array format, skipping.")
                non_standard_tables += 1 # Count as non-standard or handle as an anomaly
    else:
        # Handle cases where no quantization tables are found in the image
        # print(f"Warning: No quantization tables found for image {image_path}.")
        pass # Depending on strictness, could return None or default features here

    # Check the image structure (Progressive vs Baseline DCT)
    # Progressive DCT is more common in real images.
    if image.info.get('progressive', False):
        is_progressive_dct = 1
    else:
        is_progressive_dct = 0 # Baseline DCT is common in AI images

    # Compute statistical features from quantization values
    quantization_values_np = np.array(quantization_values)
    if len(quantization_values_np) > 0:
        std_of_quantization = np.std(quantization_values_np)
        skewness_of_quantization = stats.skew(quantization_values_np)
        kurtosis_of_quantization = stats.kurtosis(quantization_values_np)
    else: # Default values if no quantization values were extracted
        std_of_quantization = 0
        skewness_of_quantization = 0
        kurtosis_of_quantization = 0

    return [non_standard_tables, high_frequency_emphasis, is_progressive_dct,
            std_of_quantization, skewness_of_quantization, kurtosis_of_quantization]

def train_image_classifier(real_images_dir, ai_generated_images_dir, model_path="ai_generated_image_classifier.pkl", model_type='random_forest'):
    """
    Trains a machine learning model to classify images as real or AI-generated
    based on extracted JPEG features.
    """
    # Collect image file paths from the specified directories
    try: # Error handling: Catch if provided directories are not found
        real_image_files = os.listdir(real_images_dir)
    except FileNotFoundError:
        print(f"Error: Training directory not found: {real_images_dir}")
        return None
    try: # Error handling: Catch if provided directories are not found
        ai_generated_image_files = os.listdir(ai_generated_images_dir)
    except FileNotFoundError:
        print(f"Error: Training directory not found: {ai_generated_images_dir}")
        return None

    # Filter for JPEG/JPG images and create full paths
    real_image_paths = [os.path.join(real_images_dir, f) for f in real_image_files if f.lower().endswith(('.jpg', '.jpeg'))]
    ai_generated_image_paths = [os.path.join(ai_generated_images_dir, f) for f in ai_generated_image_files if f.lower().endswith(('.jpg', '.jpeg'))]

    # Extract JPEG features for each image
    X_real_features = []
    for path in real_image_paths:
        features = get_jpeg_features(path)
        # Data handling: Skip images if feature extraction fails (get_jpeg_features returns None)
        if features is not None:
            X_real_features.append(features)
        else:
            print(f"Warning: Skipping image {path} (Real) due to feature extraction error or unsupported format.")

    X_ai_features = []
    for path in ai_generated_image_paths:
        features = get_jpeg_features(path)
        # Data handling: Skip images if feature extraction fails
        if features is not None:
            X_ai_features.append(features)
        else:
            print(f"Warning: Skipping image {path} (AI) due to feature extraction error or unsupported format.")

    # Data handling: Check if enough valid features were extracted for training
    if not X_real_features and not X_ai_features:
        print("Error: No valid image features extracted from either directory. Cannot train model.")
        return None
    if not X_real_features:
        print("Warning: No valid real images found/features extracted. Model training will proceed with only AI images if available (not recommended).")
    if not X_ai_features:
        print("Warning: No valid AI-generated images found/features extracted. Model training will proceed with only real images if available (not recommended).")

    # Combine features and create labels (0 for real, 1 for AI-generated)
    # This handles cases where one category might be empty after filtering.
    if not X_real_features and len(X_ai_features) > 0: # Only AI images
        print("Warning: Training with AI images only.")
        X = np.array(X_ai_features)
        y = np.array([1] * len(X_ai_features))
    elif not X_ai_features and len(X_real_features) > 0: # Only Real images
        print("Warning: Training with Real images only.")
        X = np.array(X_real_features)
        y = np.array([0] * len(X_real_features))
    elif len(X_real_features) > 0 and len(X_ai_features) > 0: # Both types of images
        X = np.array(X_real_features + X_ai_features)
        y = np.array([0] * len(X_real_features) + [1] * len(X_ai_features))
    else: # Safeguard: Should be caught by earlier checks
        print("Error: No features to train on after processing images. Cannot train the model.")
        return None

    # Data handling: Ensure X is not empty before proceeding
    if X.shape[0] == 0:
        print("Error: No features to train on after processing images. Cannot train the model.")
        return None

    # Data handling: Impute NaN values that might have occurred during feature extraction
    # This uses the mean of each feature column to fill missing values.
    imputer = SimpleImputer(strategy='mean')
    X_imputed = imputer.fit_transform(X)

    # Data handling: Check if any samples remain after imputation
    if X_imputed.shape[0] == 0:
        print("Error: No samples left after attempting to handle NaNs. Cannot train the model.")
        return None

    # Stratification logic for train_test_split:
    # Ensures that the train/test split has proportional representation of classes if possible.
    unique_classes, counts = np.unique(y, return_counts=True)
    if len(unique_classes) > 1 and all(c > 1 for c in counts): # Requires at least 2 samples per class for stratification
        stratify_option = y
    else:
        stratify_option = None # Do not stratify if only one class or insufficient samples
        if len(unique_classes) <=1:
            print("Warning: Only one class present in the training data. Stratification is not possible and model may not be useful.")
        else:
            print("Warning: Not enough samples in one or more classes for stratified split. Proceeding without stratification.")

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_imputed, y, test_size=0.2, random_state=42, stratify=stratify_option)

    # Initialize and train the selected model type
    if model_type == 'random_forest':
        model = RandomForestClassifier(random_state=42)
    elif model_type == 'gradient_boosting':
        model = HistGradientBoostingClassifier(random_state=42)
    else: # Default to RandomForestClassifier
        model = RandomForestClassifier(random_state=42)

    model.fit(X_train, y_train)

    # Evaluate the model's accuracy on the test set
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy:.2f}")

    # Save the trained model to the specified path
    try: # Error handling: Catch issues during model saving
        joblib.dump(model, model_path)
        print(f"Model saved to {model_path}")
    except Exception as e:
        print(f"Error saving model to {model_path}: {e}")
        return None # Return None if model saving fails, or model itself if partial success is acceptable

    return model

def is_image_ai_generated(image_path, model_path="ai_generated_image_classifier.pkl", model_obj=None):
    """
    Predicts if an image is AI-generated using a trained model.
    Can load a model from `model_path` or use a pre-loaded `model_obj`.
    """
    features = get_jpeg_features(image_path)
    # If feature extraction fails, cannot classify the image
    if features is None:
        print(f"Info: Could not extract features for {image_path}. Cannot classify.")
        return None

    model_to_use = model_obj
    # Efficiency improvement: If a model object is not passed, load it from file.
    # This avoids reloading the model if it's already in memory (e.g., when comparing multiple images).
    if model_to_use is None:
        # Error handling: Check if model file exists before attempting to load
        if not os.path.exists(model_path):
            print(f"Error: Model file '{model_path}' not found for prediction.")
            return None
        try: # Error handling: Catch issues during model loading (e.g., corrupted file)
            model_to_use = joblib.load(model_path)
        except Exception as e:
            print(f"Error loading model from '{model_path}': {e}")
            return None

    # Safeguard: Ensure a model is available
    if model_to_use is None:
        print("Error: Model could not be loaded or provided. Cannot classify.")
        return None

    features_array = np.array(features).reshape(1, -1)
    # Data handling for prediction: Impute NaNs in features (e.g., with 0)
    # A more robust approach might involve saving and reusing the imputer from training.
    if np.isnan(features_array).any():
        print(f"Warning: NaN values found in features for {image_path}. Imputing with 0 for prediction.")
        features_array = np.nan_to_num(features_array, nan=0.0) # Replace NaNs with 0.0

    try: # Error handling: Catch issues during the prediction phase
        prediction = model_to_use.predict(features_array)[0]
        proba = model_to_use.predict_proba(features_array)[0] # Get prediction probabilities
    except Exception as e:
        print(f"Error during prediction for {image_path}: {e}")
        return None

    # Output classification result with confidence
    if prediction == 1: # Assuming class 1 is AI-generated
        print(f"Image {image_path}: Classified as AI-generated (Confidence: {proba[1]:.2f})")
    elif prediction == 0: # Assuming class 0 is Real
        print(f"Image {image_path}: Classified as Real photograph (Confidence: {proba[0]:.2f})")
    else:
        print(f"Image {image_path} received an unexpected prediction class: {prediction}.")

    return prediction


def compare_images(image1_path, image2_path, model_path="ai_generated_image_classifier.pkl", model_obj=None):
    """
    Compares two images and prints which is more likely AI-generated or real.
    Uses `model_obj` if provided to avoid redundant model loading.
    """
    print(f"\nComparing '{os.path.basename(image1_path)}' and '{os.path.basename(image2_path)}':")
    # Efficiency improvement: Pass the loaded model_obj to is_image_ai_generated
    # This prevents each call from reloading the model from disk.
    is_image1_ai_generated = is_image_ai_generated(image1_path, model_path=model_path, model_obj=model_obj)
    is_image2_ai_generated = is_image_ai_generated(image2_path, model_path=model_path, model_obj=model_obj)

    # Interpret and print comparison results
    if is_image1_ai_generated is not None and is_image2_ai_generated is not None:
        if is_image1_ai_generated == 1 and is_image2_ai_generated == 0:
            print("Comparison Result: Image 1 is more likely AI-generated; Image 2 is more likely Real.")
        elif is_image1_ai_generated == 0 and is_image2_ai_generated == 1:
            print("Comparison Result: Image 1 is more likely Real; Image 2 is more likely AI-generated.")
        elif is_image1_ai_generated == 1 and is_image2_ai_generated == 1:
            print("Comparison Result: Both images are more likely AI-generated.")
        elif is_image1_ai_generated == 0 and is_image2_ai_generated == 0:
            print("Comparison Result: Both images are more likely Real photographs.")
        else:
            print("Comparison Result: Could not definitively compare the images based on current predictions.")
    else:
        print("Comparison Result: Unable to determine the nature of one or both images; comparison incomplete.")

# Main execution block: Script entry point when run directly
if __name__ == "__main__":
    # argparse setup: Defines how command-line arguments are parsed and used.
    # This allows users to specify training data, images for comparison, and model paths.
    parser = argparse.ArgumentParser(
        description="Detect AI-generated images using JPEG noise analysis. "\
                    "The script can operate in two modes: training or comparison.\n"
                    "Training mode: Provide --real_images_dir and --ai_images_dir.\n"
                    "Comparison mode: Provide --image1_path and --image2_path.\n"
                    "Both modes can be run sequentially. If training is done, the resulting model is used for comparison.",
        formatter_class=argparse.RawTextHelpFormatter # For better help message formatting
    )

    # Arguments for training mode
    parser.add_argument("--real_images_dir", type=str, help="Directory of real images (JPEG/JPG) for training the model.")
    parser.add_argument("--ai_images_dir", type=str, help="Directory of AI-generated images (JPEG/JPG) for training the model.")

    # Arguments for comparison mode
    parser.add_argument("--image1_path", type=str, help="Path to the first image (JPEG/JPG) for comparison.")
    parser.add_argument("--image2_path", type=str, help="Path to the second image (JPEG/JPG) for comparison.")

    # Argument for model path (used in both modes)
    parser.add_argument("--model_path", type=str, default="ai_generated_image_classifier.pkl",
                        help="Path to save the trained model or load an existing model for comparison (default: ai_generated_image_classifier.pkl).")

    args = parser.parse_args() # Parse the provided command-line arguments

    model_for_session = None # Variable to hold the model if it's trained or loaded during the session

    # --- Training Mode Logic ---
    # If both training directories are provided, initiate training.
    if args.real_images_dir and args.ai_images_dir:
        print(f"--- Training Mode Initiated ---")
        print(f"Real images directory: '{args.real_images_dir}'")
        print(f"AI-generated images directory: '{args.ai_images_dir}'")
        print(f"Model will be saved to/updated at: '{args.model_path}'")

        model_for_session = train_image_classifier(
            args.real_images_dir,
            args.ai_images_dir,
            model_path=args.model_path
        )
        if model_for_session:
            print("--- Training completed successfully. ---")
        else:
            print("--- Training failed or did not produce a model. ---")
    elif args.real_images_dir or args.ai_images_dir: # Error: Only one training directory provided
        print("Error: For training, both --real_images_dir and --ai_images_dir must be specified.")
        parser.print_help()

    # --- Comparison Mode Logic ---
    # If paths for two images are provided, initiate comparison.
    if args.image1_path and args.image2_path:
        print(f"\n--- Comparison Mode Initiated ---")
        print(f"Image 1: '{args.image1_path}'")
        print(f"Image 2: '{args.image2_path}'")
        print(f"Model path for comparison: '{args.model_path}'")

        # Efficiency improvement: If a model wasn't trained in this session, load it once.
        if model_for_session is None:
            # Error handling: Check if the specified model file exists
            if not os.path.exists(args.model_path):
                print(f"Error: Model file '{args.model_path}' not found. Please train a model first or provide a valid path to an existing model.")
            else:
                try: # Error handling: Catch issues during model loading
                    print(f"Loading model from '{args.model_path}' for comparison...")
                    model_for_session = joblib.load(args.model_path)
                    print("Model loaded successfully from file.")
                except Exception as e:
                    print(f"Error loading model from '{args.model_path}': {e}")
                    model_for_session = None # Ensure model is None if loading fails
        elif model_for_session: # A model was trained in this session
             print("Using model trained in the current session for comparison.")

        # Proceed with comparison if a model is available (either trained or loaded)
        if model_for_session:
            compare_images(args.image1_path, args.image2_path, model_path=args.model_path, model_obj=model_for_session)
            print("--- Comparison completed. ---")
        else:
            print("--- Comparison cannot proceed: Model is not available (either failed to train or load). ---")
    elif args.image1_path or args.image2_path: # Error: Only one image path provided for comparison
        print("Error: For comparison, both --image1_path and --image2_path must be specified.")
        parser.print_help()

    # --- Guidance if no valid mode is fully specified ---
    # This checks if no primary arguments for either mode were given.
    if not (args.real_images_dir and args.ai_images_dir) and \
       not (args.image1_path and args.image2_path) and \
       not (args.real_images_dir or args.ai_images_dir) and \
       not (args.image1_path or args.image2_path) :
        print("\nNo action performed. Please provide arguments for training or comparison.")
        print("Example for training: python your_script.py --real_images_dir path/to/real --ai_images_dir path/to/ai")
        print("Example for comparison: python your_script.py --image1_path path/to/img1.jpg --image2_path path/to/img2.jpg")
        parser.print_help()
    # This handles cases where some arguments were given but not enough for a full mode (e.g., only --real_images_dir).
    # Specific error messages for such partial arguments are handled within the mode blocks above.
    # This is a fallback to ensure help/guidance is printed if no complete mode was triggered.
    elif not (args.real_images_dir and args.ai_images_dir) and not (args.image1_path and args.image2_path):
        print("\nPlease ensure you provide all required arguments for the desired mode (training or comparison).")

print("\nScript execution finished.")
