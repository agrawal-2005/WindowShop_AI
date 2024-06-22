from flask import Flask, request, jsonify,render_template, Response, request
app = Flask(__name__)
import os
import base64
from io import BytesIO
from PIL import Image
import cv2
# from hower_object import hower_image_similarity
from image_similarity import hower_image_similarity
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def crop_object(image_path, x, y, crop_size=100):
    image = Image.open(image_path).convert("RGB")
    width, height = image.size

    # Calculate the crop coordinates
    left = x - crop_size // 2
    top = y - crop_size // 2
    right = x + crop_size // 2
    bottom = y + crop_size // 2

    # Ensure the crop coordinates are within the image boundaries
    left = max(0, left)
    top = max(0, top)
    right = min(width, right)
    bottom = min(height, bottom)

    # Crop the image
    cropped_image = image.crop((left, top, right, bottom))
    return cropped_image





@app.route('/')
def index():
    return render_template('index.html')
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    upload_folder = 'static/uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    video_filename = file.filename
    video_path = os.path.join(upload_folder, video_filename)
    file.save(video_path)

    extract_frames(video_path, video_filename, upload_folder)

    return jsonify({'video_url': f'{video_path}'}), 200

def extract_frames(video_path, video_filename, output_folder):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count % fps == 0:
            second = count // fps
            frame_filename = os.path.join(output_folder, f"{os.path.splitext(video_filename)[0]}_{second}.png")
            cv2.imwrite(frame_filename, frame)
        count += 1
    cap.release()



@app.route('/capture', methods=['POST'])
def capture():
    data = request.get_json()
    x = data['x']
    y = data['y']
    timestamp = data['timestamp']
    filename = data['filename']
    filename_without_ext = os.path.splitext(filename)[0]
    timestamp = round(timestamp)
    image_path = f"{filename_without_ext}_{timestamp}.png"
    # crop_image=crop_object(image_path,x,y,300)
    # print(image_path)
    # crop_image.show()
    # image_path.show()
    print(f"Captured coordinates: ({x}, {y}) and saved frame to {timestamp}")
    # print("you are entered.........................")
    products=hower_image_similarity(image_path,x,y)
    products_json = [{'name': product['name'], 'link': product['link'], 'image':product['image']} for product in products]
    return jsonify({'message': 'Frame and coordinates captured successfully', 'products': products_json}), 200

if __name__ == '__main__':
    app.run(debug=True)
