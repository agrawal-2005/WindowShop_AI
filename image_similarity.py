import torch, os, json
from PIL import Image
from ultralytics import YOLO
import clip
# from torchvision import transforms
import ssl

# --- FIX for SSL: CERTIFICATE_VERIFY_FAILED on macOS ---
# This workaround tells Python to trust the system's certificates
# and allows the clip.load() function to download the model.
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
# --- END SSL FIX ---

# Global variables for pre-trained models
yolo_model = None
clip_model = None
clip_preprocess = None
device = "cuda" if torch.cuda.is_available() else "cpu"

# Define preprocessing using CLIP's preprocessing
def load_clip_model():
    global clip_model, clip_preprocess
    if clip_model is None:
        print("Loading CLIP model...")
        clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
        clip_model.eval()

def load_models():
    global yolo_model
    if yolo_model is None:
        print("Loading YOLO model...")
        yolo_model = YOLO("yolov8n.pt")
    load_clip_model()

# Detects objects in an image using the YOLO model.
def detect_objects(image_path):
    try:
        results = yolo_model(image_path)
        return results[0] if results else None
    except Exception as e:
        print(f"Error detecting objects: {e}")
        return None

# Crops a region from an image based on bounding box coordinates.
def crop_object(image, coordinates):
    x1, y1, x2, y2 = coordinates
    return image.crop((x1, y1, x2, y2))

# Encodes a single image using the CLIP model to get its feature vector.
def encode_image(image):
    image_input = clip_preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_feature = clip_model.encode_image(image_input)
    return image_feature

# Finds the top_k most similar images from the dataset.
def find_similar_images(query_feature, dataset_features, top_k=5):
    similarities = torch.nn.functional.cosine_similarity(query_feature, dataset_features, dim=-1)
    values, indices = similarities.topk(min(top_k, len(dataset_features)))
    return indices, values

# One-time process to encode all images in the dataset and save their features to a file for fast look-up.
def precompute_dataset_features(dataset_folder):
    metadata_file = os.path.join(dataset_folder, 'metadata.json')
    features_file = os.path.join(dataset_folder, 'features.pt')
    images_dir = os.path.join(dataset_folder, 'images')
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    dataset_image_features = []
    print(f"Encoding {len(metadata)} images from the dataset...")
    for item in metadata:
        img_path = os.path.join(images_dir, item['filename'])
        if os.path.exists(img_path):
            dataset_image = Image.open(img_path).convert("RGB")
            dataset_image_features.append(encode_image(dataset_image))

    if not dataset_image_features:
        print("No images found or processed from the dataset.")
        return None, None
    
    dataset_features = torch.cat(dataset_image_features, dim=0).to(device)
    torch.save(dataset_features, features_file)
    print(f"Dataset features saved to {features_file}")
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
        print("Dataset features not found. Pre-computing now...")
        precompute_dataset_features(dataset_folder)
    else:
        print("Found cached dataset features.")

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
        print("No objects detected by YOLO.")
        return []

    # Find all bounding boxes that contain the user's click
    valid_boxes = []
    for box in results.boxes.xyxy:
        x1, y1, x2, y2 = map(int, box[:4])
        if x1 <= x_coord <= x2 and y1 <= y_coord <= y2:
            area = (x2 - x1) * (y2 - y1)
            valid_boxes.append((area, (x1, y1, x2, y2)))

    # If no box was clicked, return empty
    if not valid_boxes:
        print("Click was not inside any detected bounding box.")
        return []

    # --- LOGIC IMPROVEMENT ---
    # Sort boxes by area (smallest first) to find the most specific object
    valid_boxes.sort(key=lambda x: x[0])
    
    # Get the coordinates of the smallest (most specific) box
    smallest_box_coords = valid_boxes[0][1]
    
    # Crop just this one object from the main image
    image = Image.open(image_path).convert("RGB")
    cropped_image = crop_object(image, smallest_box_coords)
    
    # Encode the cropped image to get its feature vector
    cropped_image_feature = encode_image(cropped_image)

    # Find similar images in the dataset
    indices, values = find_similar_images(cropped_image_feature, dataset_features)

    # Format the results into a list of products
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

if __name__ == "__main__":
    # This block is for testing the script directly
    dataset_folder = 'static/dataset'
    ensure_precomputed_features(dataset_folder)

    # Example usage:
    # Make sure you have an image at this path to test
    test_image_path = 'static/uploads/frame_0.png'
    if os.path.exists(test_image_path):
        x_coord = 543  # Example x-coordinate
        y_coord = 521  # Example y-coordinate
        similar_products = hower_image_similarity(test_image_path, x_coord, y_coord)
        print("\n--- Found Similar Products ---")
        if similar_products:
            for p in similar_products:
                print(f"Name: {p['name']}, Score: {p['score']:.4f}")
        else:
            print("No similar products found.")
    else:
        print(f"Test image not found at: {test_image_path}")
