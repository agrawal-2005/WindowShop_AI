from flask import Flask, request, render_template, jsonify, url_for
import os
from PIL import Image
import cv2
from werkzeug.utils import secure_filename
from image_similarity import hower_image_similarity

app = Flask(__name__)

# --- Helper Functions ---

def crop_object(image_path, x, y, crop_size=100):
    try:
        image = Image.open(image_path).convert("RGB")
        width, height = image.size
        
        left = max(0, x - crop_size // 2)
        top = max(0, y - crop_size // 2)
        right = min(width, x + crop_size // 2)
        bottom = min(height, y + crop_size // 2)

        cropped_image = image.crop((left, top, right, bottom))
        return cropped_image
    except FileNotFoundError:
        return None

def extract_frames(video_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps) if fps > 0 else 30

    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if count % frame_interval == 0:
            second = count // frame_interval
            frame_filename = os.path.join(output_folder, f"frame_{second}.png")
            cv2.imwrite(frame_filename, frame)
        count += 1
    cap.release()
    print(f"Frames extracted to {output_folder}")

# --- Flask Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_videos')
def get_videos():
    upload_folder = 'static/uploads'
    video_files = []
    try:
        if os.path.exists(upload_folder):
            for filename in os.listdir(upload_folder):
                full_path = os.path.join(upload_folder, filename)
                if os.path.isfile(full_path) and filename.lower().endswith(('.mp4', '.mov', '.webm')):
                    video_files.append(url_for('static', filename=f'uploads/{filename}'))
        return jsonify(video_files)
    except Exception as e:
        print(f"Error in /get_videos: {e}")
        return jsonify({"error": "Failed to retrieve video list from server"}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    upload_folder = 'static/uploads'
    os.makedirs(upload_folder, exist_ok=True)

    video_filename = secure_filename(file.filename)
    video_path = os.path.join(upload_folder, video_filename)
    file.save(video_path)

    video_name_without_ext = os.path.splitext(video_filename)[0]
    output_folder_for_frames = os.path.join(upload_folder, video_name_without_ext)

    extract_frames(video_path, output_folder_for_frames)

    video_url = url_for('static', filename=f'uploads/{video_filename}')
    return jsonify({'video_url': video_url}), 200

@app.route('/capture', methods=['POST'])
def capture():
    data = request.get_json()
    x = data.get('x')
    y = data.get('y')
    timestamp = data.get('timestamp')
    video_url = data.get('filename')

    if any(v is None for v in [x, y, timestamp, video_url]):
        return jsonify({'error': 'Missing data in request'}), 400

    base_video_filename = os.path.basename(video_url)
    video_name_without_ext = os.path.splitext(base_video_filename)[0]
    
    second = round(timestamp)

    frame_folder = os.path.join('static/uploads', video_name_without_ext)
    image_path = os.path.join(frame_folder, f"frame_{second}.png")

    if not os.path.exists(image_path):
        return jsonify({'error': f'Frame not found. Looked for: {image_path}'}), 404
    products = hower_image_similarity(image_path, x, y)
    
    # Format the product data for the client
    products_json = [{'name': p.get('name'), 'link': p.get('link'), 'image': p.get('image')} for p in products]
    
    return jsonify({
        'message': 'Frame and coordinates captured successfully',
        'products': products_json
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
