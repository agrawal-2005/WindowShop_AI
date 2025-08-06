import torch
import timm
import os
import json
from PIL import Image
from ultralytics import YOLO
from torchvision import transforms
from image_similarity import hower_image_similarity

# Global variables for pre-trained models
yolo_model = None
dino_model = None
device = "cuda" if torch.cuda.is_available() else "cpu"

# Define preprocessing for DINOv2
preprocess = transforms.Compose([
    transforms.Resize((224, 224)), # DINO models often use 224x224
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def save_dino_model(model, path='dino_model.pth'):
    """Saves the DINO model's state to a local file."""
    torch.save(model.state_dict(), path)
    print(f"DINO model saved to {path}")

def load_dino_model_from_file(path='dino_model.pth'):
    """Loads the DINO model from a local file."""
    model = timm.create_model('vit_base_patch14_dinov2', pretrained=False)
    model.load_state_dict(torch.load(path, map_location=device))
    return model

def load_models():
    """Manages loading for both YOLO and the DINOv2 model."""
    global yolo_model, dino_model
    if yolo_model is None:
        yolo_model = YOLO("yolov8n.pt")
    if dino_model is None:
        dino_model_path = 'dino_model.pth'
        if os.path.exists(dino_model_path):
            print("Loading saved DINO model from file...")
            dino_model = load_dino_model_from_file(dino_model_path)
        else:
            print("Downloading and saving new DINO model...")
            dino_model = timm.create_model('vit_base_patch14_dinov2', pretrained=True)
            save_dino_model(dino_model, dino_model_path)
        dino_model = dino_model.to(device)
        dino_model.eval()

def detect_objects(image_path):
    """Detects objects in an image using YOLO."""
    try:
        results = yolo_model(image_path)
        return results[0] if results else None
    except Exception as e:
        print(f"Error detecting objects: {e}")
        return None

def crop_object(image, coordinates):
    """Crops a rectangular region from an image."""
    x1, y1, x2, y2 = map(int, coordinates)
    return image.crop((x1, y1, x2, y2))

def encode_image(image):
    """Encodes an image into a DINOv2 feature vector."""
    image_tensor = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_feature = dino_model(image_tensor)
    return image_feature

def find_similar_images(query_feature, dataset_features, top_k=5):
    """Finds the top_k most similar images using cosine similarity."""
    similarities = torch.nn.functional.cosine_similarity(query_feature, dataset_features, dim=-1)
    values, indices = similarities.topk(min(top_k, len(dataset_features)))
    return indices, values

def precompute_dataset_features(dataset_folder):
    """
    CRITICAL EFFICIENCY STEP: Encodes all dataset images once and saves
    the features to a cache file ('features_dino.pt').
    """
    metadata_file = os.path.join(dataset_folder, 'metadata.json')
    # Use a different name for the DINO features file to avoid conflicts
    features_file = os.path.join(dataset_folder, 'features_dino.pt')
    images_dir = os.path.join(dataset_folder, 'images')

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    dataset_image_features = []
    print(f"DINO: Encoding {len(metadata)} images from the dataset...")
    for item in metadata:
        img_path = os.path.join(images_dir, item['filename'])
        if os.path.exists(img_path):
            dataset_image = Image.open(img_path).convert("RGB")
            dataset_image_features.append(encode_image(dataset_image))

    if not dataset_image_features:
        return None, None

    dataset_features = torch.cat(dataset_image_features, dim=0).to(device)
    torch.save(dataset_features, features_file)
    print(f"DINO dataset features saved to {features_file}")
    return metadata, dataset_features

def load_dataset_features(dataset_folder):
    """Loads the pre-computed DINO features from the cache file."""
    features_file = os.path.join(dataset_folder, 'features_dino.pt')
    metadata_file = os.path.join(dataset_folder, 'metadata.json')
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    dataset_features = torch.load(features_file, map_location=device)
    return metadata, dataset_features

def ensure_precomputed_features(dataset_folder):
    """Checks if the DINO cache file exists, and creates it if it doesn't."""
    features_file = os.path.join(dataset_folder, 'features_dino.pt')
    if not os.path.exists(features_file):
        print("DINO dataset features not found. Pre-computing now...")
        precompute_dataset_features(dataset_folder)
    else:
        print("Found cached DINO dataset features.")

def find_similar_products_dino(image_path, x_coord, y_coord):
    """Main function to find similar products using the DINOv2 engine."""
    load_models()

    dataset_folder = 'static/dataset'
    # Use the caching system for efficiency
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

if __name__ == "__main__":
    image_path = 'static/uploads/sample_video_29.png'
    x_coordi = 543  # Example x-coordinate
    y_coordi = 521  # Example y-coordinate
    hower_image_similarity(image_path, x_coordi, y_coordi)