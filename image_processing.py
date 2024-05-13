import os
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def is_image_file(filename):
    """Check if a file is an image based on its extension."""
    valid_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"]
    return any(filename.lower().endswith(ext) for ext in valid_extensions)

def analyze_dataset(directory):
    """Analyze the dataset to count images and categorize them by type and style."""
    count = 0
    categories = {}
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            if is_image_file(file):
                category = subdir.split(os.sep)[-2]  # Assuming subdir format is 'Train/<type>/<style>'
                style = subdir.split(os.sep)[-1]
                label = f"{category}_{style}"
                if label not in categories:
                    categories[label] = 0
                categories[label] += 1
                count += 1
    return count, categories

def extract_features(img_path, model):
    """Extract features from an image using the EfficientNetB0 model."""
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    features = model.predict(preprocessed_img)
    flattened_features = features.flatten()
    normalized_features = flattened_features / np.linalg.norm(flattened_features)
    return normalized_features

def compute_average_features(directory, model):
    """Compute average features for each category in the directory."""
    category_features = {}
    category_counts = {}
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            if is_image_file(file):
                img_path = os.path.join(subdir, file)
                features = extract_features(img_path, model)
                category = subdir.split(os.sep)[-2] + "_" + subdir.split(os.sep)[-1]
                if category not in category_features:
                    category_features[category] = np.zeros_like(features)
                    category_counts[category] = 0
                category_features[category] += features
                category_counts[category] += 1
    # Averaging features by category
    for category in category_features:
        category_features[category] /= category_counts[category]
    return category_features

def find_closest_category(image_path, category_features, model):
    """Find the closest category for a given image."""
    image_features = extract_features(image_path, model)
    nearest_category = None
    min_distance = float('inf')
    for category, features in category_features.items():
        distance = np.linalg.norm(image_features - features)
        if distance < min_distance:
            min_distance = distance
            nearest_category = category
    return nearest_category

def extract_features_from_category(directory, category, model):
    """Extract features from all images in a specified category."""
    image_paths = []
    features_list = []
    for subdir, dirs, files in os.walk(directory):
        parts = subdir.split(os.sep)
        if len(parts) >= 2:
            constructed_category = '_'.join(parts[-2:])  # Safely join the last two parts
            if constructed_category == category:
                for file in files:
                    if is_image_file(file):
                        img_path = os.path.join(subdir, file)
                        image_paths.append(img_path)
                        features = extract_features(img_path, model)
                        features_list.append(features)
    return image_paths, features_list

def recommend_similar_images(features, all_features, all_paths, n=10):
    """Recommend n similar images based on feature similarity."""
    neighbors = NearestNeighbors(n_neighbors=n, metric='euclidean')
    # Ensure all_features is a 2D array and not empty
    if all_features:
        all_features = np.array(all_features)
        if len(all_features.shape) == 1:  # Handling 1D array to make it 2D
            all_features = all_features.reshape(1, -1)
        neighbors.fit(all_features)
        # Make sure features is also a 2D array
        features = np.array(features).reshape(1, -1)
        distances, indices = neighbors.kneighbors(features)
        return [all_paths[idx] for idx in indices.flatten()]
    else:
        return []  # Return an empty list if no features are available


def display_images(image_paths):
    """Display images in a grid."""
    plt.figure(figsize=(15, 10))
    for i, img_path in enumerate(image_paths):
        img = mpimg.imread(img_path)
        plt.subplot(2, 5, i + 1)  # Adjust the grid size depending on how many images you want to show
        plt.imshow(img)
        plt.axis('off')
        plt.title(os.path.basename(img_path))
    plt.show()