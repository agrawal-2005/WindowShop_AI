
import torch
import timm
import os
import json
from PIL import Image
from ultralytics import YOLO
from torchvision import transforms
device = "cuda" if torch.cuda.is_available() else "cpu"
model = timm.create_model('vit_base_patch14_dinov2', pretrained=True).to(device)
model.eval()

# Define preprocessing
preprocess = transforms.Compose([
    transforms.Resize((518, 518)),  # Resize to 518x518
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def encode_image(image):
    image_tensor = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_feature = model(image_tensor)
    return image_feature

def precompute_dataset_features(dataset_folder='dataset'):
    metadata_file = os.path.join(dataset_folder, 'metadata.json')
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    image_features = []
    for item in metadata:
        img_path = os.path.join(dataset_folder, 'images', item['filename'])
        dataset_image = Image.open(img_path).convert("RGB")
        feature = encode_image(dataset_image).unsqueeze(0)  # Add batch dimension
        image_features.append(feature)
    
    image_features = torch.cat(image_features, dim=0).to(device)
    torch.save(image_features, os.path.join(dataset_folder, 'image_features.pt'))
    return metadata, image_features
