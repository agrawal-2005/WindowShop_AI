import torch
import os
import json
from PIL import Image
from ultralytics import YOLO
import clip
import ssl

# This workaround for SSL errors is often needed on deployment platforms
# to ensure models can be downloaded if the cache is cleared. It's safe to keep.
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# --- Global variables for pre-trained models ---
yolo_model = None
clip_model = None
clip_preprocess = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def load_clip_model():
    """Loads the CLIP model and its preprocessor if they are not already in memory."""
    global clip_model, clip_preprocess
    if clip_model is None:
        clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
        clip_model.eval()

def load_models():
    """Ensures both YOLO and CLIP models are loaded."""
    global yolo_model
    if yolo_model is None:
        yolo_model = YOLO("yolov8n.pt")
    load_clip_model()

def detect_objects(image_path):
    """Detects objects in an image using the YOLO model."""
    try:
        results = yolo_model(image_path)
        return results[0] if results else None
    except Exception as e:
        # In production, you might want to log this error to a file instead of printing
        print(f"Error during object detection: {e}")
        return None

def crop_object(image, coordinates):
    """Crops a region from an image based on bounding box coordinates."""
    x1, y1, x2, y2 = map(int, coordinates)
    return image.crop((x1, y1, x2, y2))

def encode_image(image):
    """Encodes a single image using the CLIP model to get its feature vector."""
    image_input = clip_preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_feature = clip_model.encode_image(image_input)
    return image_feature

def find_similar_images(query_feature, dataset_features, top_k=5):
    """Finds the top_k most similar images from the dataset."""
    similarities = torch.nn.functional.cosine_similarity(query_feature, dataset_features, dim=-1)
    # Ensure top_k is not greater than the number of features
    k = min(top_k, len(dataset_features))
    values, indices = similarities.topk(k)
    return indices, values

def precompute_dataset_features(dataset_folder):
    """
    One-time process to encode all images in the dataset and save their
    features to a cache file for fast look-up.
    """
    metadata_file = os.path.join(dataset_folder, 'metadata.json')
    features_file = os.path.join(dataset_folder, 'features.pt')
    images_dir = os.path.join(dataset_folder, 'images')
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    dataset_image_features = []
    for item in metadata:
        img_path = os.path.join(images_dir, item['filename'])
        if os.path.exists(img_path):
            dataset_image = Image.open(img_path).convert("RGB")
            dataset_image_features.append(encode_image(dataset_image))

    if not dataset_image_features:
        return None, None
    
    dataset_features = torch.cat(dataset_image_features, dim=0).to(device)
    torch.save(dataset_features, features_file)
    return metadata, dataset_features

def load_dataset_features(dataset_folder):
    """Loads pre-computed features and metadata from files."""
    features_file = os.path.join(dataset_folder, 'features.pt')
    metadata_file = os.path.join(dataset_folder, 'metadata.json')
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    dataset_features = torch.load(features_file, map_location=device)
    return metadata, dataset_features

def ensure_precomputed_features(dataset_folder):
    """Checks if features are pre-computed, if not, it runs the process."""
    features_file = os.path.join(dataset_folder, 'features.pt')
    if not os.path.exists(features_file):
        # This will run on the server the very first time the app starts
        precompute_dataset_features(dataset_folder)

def hower_image_similarity(image_path, x_coord, y_coord):
    """
    Main function to find similar products based on a click location in an image.
    """
    load_models()

    dataset_folder = 'static/dataset'
    ensure_precomputed_features(dataset_folder)
    metadata, dataset_features = load_dataset_features(dataset_folder)

    results = detect_objects(image_path)
    if not results or results.boxes.xyxy.shape[0] == 0:
        return []

    valid_boxes = []
    for box in results.boxes.xyxy:
        x1, y1, x2, y2 = map(int, box[:4])
        if x1 <= x_coord <= x2 and y1 <= y_coord <= y2:
            area = (x2 - x1) * (y2 - y1)
            valid_boxes.append((area, (x1, y1, x2, y2)))

    if not valid_boxes:
        return []

    valid_boxes.sort(key=lambda x: x[0])
    smallest_box_coords = valid_boxes[0][1]
    
    image = Image.open(image_path).convert("RGB")
    cropped_image = crop_object(image, smallest_box_coords)
    
    cropped_image_feature = encode_image(cropped_image)
    indices, values = find_similar_images(cropped_image_feature, dataset_features)

    products = []
    for idx, value in zip(indices, values):
        match = metadata[idx]
        product = {
            'name': match.get('product_name', 'N/A'),
            'link': match.get('product_url', '#'),
            'image': match.get('image_url', ''),
            'score': value.item()
        }
        products.append(product)
        
    return products
