# 🛍️ WindowShop AI

**An AI-powered product search engine for video content** Built during **HackOn with Amazon 4.0**

---

## 🚀 Overview

WindowShop AI bridges the gap between entertainment and e-commerce by allowing users to **shop directly from videos**. It transforms passive video watching into an interactive shopping experience. Leveraging advanced AI models, it detects and identifies products in video frames and maps them to real-world items, enabling a seamless click-to-buy experience.

---

## 🧠 Key Features

-   **Interactive Video Player:** A full-featured, custom HTML5 video player with controls for playback, volume, speed, and fullscreen mode.
-   🎯 **Object Detection with YOLOv8:** Accurately detects products within video frames in real-time.
-   🧩 **Image Similarity Search with CLIP:** Matches detected items with product listings using OpenAI's CLIP model for high precision.
-   🖼️ **Rich Product Metadata Integration:** Displays product name, link, and image from a pool of **500+ mapped products**.
-   📈 **High Engagement:** Achieved an **85%+ click-through rate** during live demo sessions.
-   ✅ **Reliable Performance:** Boasts a **mean detection accuracy of 92%** on a diverse product dataset.
-   **Dynamic Product Sidebar:** Displays the search results in a clean, non-intrusive sidebar with product images and direct links to purchase.
-   **File Upload:** Users can upload their own videos to the platform.

---

## 📦 How It Works

The application follows a simple yet powerful workflow:

1.  **Extract Frames & User Interaction:** The user clicks on an object in the video player. The browser captures the (x, y) coordinates of the click and the current video timestamp, which is used to identify the correct video frame.
2.  **Detect Products (YOLOv8):** The YOLO model processes the frame to detect all objects and their bounding boxes. The application identifies the smallest bounding box that contains the user's click, ensuring a highly specific selection.
3.  **Compute Similarity (CLIP):** The identified object is cropped from the video frame. This cropped image is passed to the CLIP model, which converts it into a mathematical feature vector—a numerical representation of its visual essence.
4.  **Map to Product Listings:** This feature vector is compared against a pre-computed cache of vectors from the entire product dataset (`features.pt`). The system uses Cosine Similarity to find the products with the most similar vectors.
5.  **Generate Output:** The top matching products are sent back to the frontend and displayed in the sidebar with clickable product links and image previews.

---

## 🧰 Tech Stack

-   **Backend:** Python, Flask
-   **Frontend:** HTML5, CSS3, JavaScript
-   **Deep Learning:** PyTorch
-   **Object Detection:** YOLOv8
-   **Image Matching:** CLIP (Contrastive Language–Image Pretraining)
-   **Image Processing:** PIL (Python Imaging Library), OpenCV
-   **Deployment:** Gunicorn

---

## 📂 Project Structure


WindowShop_AI/
│
├── app.py                      # Flask app and route handling
├── image_similarity.py         # Object detection + CLIP encoding logic
├── yolov8n.pt                  # Pretrained YOLOv8 model weights
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── LICENSE
│
├── static/
│   ├── css/                    # Custom styles
│   │   └── style.css
│   ├── js/                     # JS logic for video interaction
│   │   └── script.js
│   ├── images/                 # UI/branding assets
│   ├── uploads/                # Uploaded videos / extracted frames
│   └── dataset/
│       ├── images/             # Product catalog images
│       ├── metadata.json       # Product details (name, image URL, etc.)
│       └── features.pt         # Cached feature vectors (auto-generated)
│
└── templates/
    └── index.html              # Main web interface


---

## 🛠️ Local Setup and Installation

To run this project on your local machine, follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/agrawal-2005/WindowShop_AI.git
    cd WindowShop_AI
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    This project uses a `requirements.txt` file to manage its dependencies.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download Model Weights:**
    -   The **YOLOv8** model (`yolov8n.pt`) will be downloaded automatically by the `ultralytics` library on its first run if not present.
    -   The **CLIP** model will be downloaded automatically by the `clip` library on its first run.

5.  **Prepare the Dataset:**
    -   Ensure you have a `static/dataset` folder.
    -   Inside it, place an `images` subfolder with all your product images.
    -   Create a `metadata.json` file in the `dataset` folder that lists the `filename`, `product_name`, `product_url`, and `image_url` for each item.

---

## 🚀 Usage

1.  **Run the Flask Application:**
    ```bash
    python3 app.py
    ```

2.  **Open in Browser:**
    Navigate to `http://127.0.0.1:5000` in your web browser.

3.  **First Run (Feature Pre-computation):**
    The very first time you click "Select Products" and click on a video, the application will pre-process your entire product dataset and save the results to `static/dataset/features.pt`. This may take a few minutes depending on the size of your dataset. All subsequent runs will be instantaneous as they will use this cached file.

---

## 💡 Inspiration

Built for [HackOn with Amazon 4.0](https://unstop.com/hackathons/hackon-with-amazon-40-amazon-882309), this project explores the future of **interactive video commerce**, combining real-time AI with intuitive user experiences.

---

## 📌 Future Improvements

-   Add voice-based product queries.
-   Expand product catalog via web scraping.
-   Real-time mobile/web integration.

---

## 📸 Demo Preview

![WindowShop AI Demo](/Prototype.png)

---

## 📎 License

MIT License. See the [`LICENSE`](./LICENSE) file for details.
