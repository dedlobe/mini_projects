# Summary
This program analyzes images to classify them as real photos or AI-generated based on JPEG features.

## Explanation
`Standard JPEG Tables`: It stores standard JPEG compression settings for comparison.

`get_jpeg_features`: This function analyzes an image's JPEG data and extracts features like the type of quantization tables used and statistics of those values.

`train_image_classifier`: This function trains a machine learning model to differentiate between real and AI-generated images.

  - It collects image paths from separate directories for real and AI-generated images.
  - Extracts features for each image.
  - Trains a model (Random Forest by default) to classify images based on their features.
  - Saves the trained model for later use.
    
    
`is_image_ai_generated`: This function uses a trained model to predict if a new image is likely AI-generated based on its features.

`compare_images`: This function uses the `is_image_ai_generate`d function on two images and compares the results, printing a message indicating which image is more likely to be real or AI-generated (or if the analysis is inconclusive).

`Example Usage`: This section shows how to use the functions to train a model and compare two images.

### ps.
The dataset I used for trainning contains 4000 for AI images and 3500 for real images.
