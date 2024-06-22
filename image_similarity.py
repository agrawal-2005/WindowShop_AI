import torch
import timm
import os
import json
from PIL import Image
from ultralytics import YOLO
from torchvision import transforms
import clip

# Global variables for pre-trained models
yolo_model = None
clip_model = None
clip_preprocess = None
device = "cuda" if torch.cuda.is_available() else "cpu"

# Define preprocessing using CLIP's preprocessing
def load_clip_model():
    global clip_model, clip_preprocess
    clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
    clip_model.eval()

def load_models():
    global yolo_model, clip_model, device
    if yolo_model is None:
        yolo_model = YOLO("yolov8n.pt")
    if clip_model is None:
        load_clip_model()

def detect_objects(image_path):
    try:
        results = yolo_model(image_path)
        return results
    except Exception as e:
        print(f"Error detecting objects: {e}")
        return None

def crop_object(image, coordinates):
    x1, y1, x2, y2 = coordinates
    cropped_image = image.crop((x1, y1, x2, y2))
    return cropped_image

def encode_image(image):
    image = clip_preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_feature = clip_model.encode_image(image)
    return image_feature

def find_similar_images(query_feature, dataset_features, top_k=5):
    similarities = torch.nn.functional.cosine_similarity(query_feature, dataset_features, dim=-1)
    values, indices = similarities.topk(top_k)
    return indices, values

def hower_image_similarity(image_path, x_coordi, y_coordi):
    # Ensure models are loaded
    load_models()

    products = [] 
    dataset_folder = 'static/dataset'
    metadata_file = os.path.join(dataset_folder, 'metadata.json')
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Load and encode dataset images (this could be done once and cached)
    dataset_image_features = []
    for item in metadata:
        img_path = os.path.join(dataset_folder, 'images', item['filename'])
        dataset_image = Image.open(img_path).convert("RGB")
        dataset_image_features.append(encode_image(dataset_image))

    dataset_image_features = torch.cat(dataset_image_features, dim=0).to(device)

    results = detect_objects(image_path)
    if isinstance(results, list):
        results = results[0]  # Take the first detection if there are multiple

    if results and results.boxes.xyxy.shape[0] > 0:
        boxes = results.boxes.xyxy  # Accessing bounding boxes

        valid_boxes = []
        for box in boxes:
            x1, y1, x2, y2 = map(int, box[:4])
            if x1 <= x_coordi <= x2 and y1 <= y_coordi <= y2:
                area = (x2 - x1) * (y2 - y1)
                valid_boxes.append((area, (x1, y1, x2, y2)))

        # Sort valid_boxes by area (smallest first)
        valid_boxes.sort(key=lambda x: x[0])

        for i, (area, coordinates) in enumerate(valid_boxes):
            cropped_image = crop_object(Image.open(image_path).convert("RGB"), coordinates)
            cropped_image_feature = encode_image(cropped_image)

            indices, values = find_similar_images(cropped_image_feature, dataset_image_features)

            for idx, value in zip(indices, values):
                match = metadata[idx]
                product = {
                    'name': match['product_name'],
                    'link': match['product_url'],
                    'image': match['image_url'],
                    'score': value.item()
                }
                print(product)
                products.append(product)
    else:
        print("No objects detected.")

    return products

if __name__ == "__main__":
    image_path = 'static/uploads/sample_video_29.png'
    x_coordi = 543  # Example x-coordinate
    y_coordi = 521  # Example y-coordinate
    hower_image_similarity(image_path, x_coordi, y_coordi)
