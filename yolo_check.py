# from image_similarity import detect_objects
# from PIL import Image

# # Example usage

# image = 'static/uploads/sample2_96.png'
# show_image(image)
# img=detect_objects(image)
# img[0].show()

from image_similarity import detect_objects  # Ensure this is the correct import for your YOLO model
from PIL import Image

def show_image(image_path):
    """
    Display an image using PIL/Pillow.

    :param image_path: Path to the image file.
    """
    try:
        # Open the image file
        with Image.open(image_path) as img:
            # Display the image
            img.show()
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    image_path = 'static/uploads/sample2_96.png'
    show_image(image_path)

    detection_results = detect_objects(image_path)
    if detection_results is not None and len(detection_results) > 0:
        detection_results[0].show()
    else:
        print("No objects detected or an error occurred.")


# import timm
# print(timm.list_models("*dino*"))
#     {
#         "filename": "pr31.png",
#         "product_name": "Sunglasses",
#         "product_url": "https://amzn.in/d/0gxXko30"
#     },
#     {
#         "filename": "pr32.png",
#         "product_name": "Sunglasses",
#         "product_url": "https://amzn.in/d/0gxXko30"
#     },
#     {
#         "filename": "pr33.png",
#         "product_name": "Table",
#         "product_url": "https://amzn.in/d/07XU1GYq"
#     },
#     {
#         "filename": "pr33.png",
#         "product_name": "Table Lamp",
#         "product_url": "https://amzn.in/d/0aXGWf8E"
#     },
#     {
#         "filename": "pr34.png",
#         "product_name": "Table Lamp",
#         "product_url": "https://amzn.in/d/0aXGWf8E"
#     },
#      {
#         "filename": "pr35.png",
#         "product_name": "Table Lamp",
#         "product_url": "https://amzn.in/d/0aXGWf8E"
#     },
#      {
#         "filename": "pr36.png",
#         "product_name": "Table Lamp",
#         "product_url": "https://amzn.in/d/0aXGWf8E"
#     },
#     {
#        "filename": "pr37.png",
#        "product_name": "Table Lamp",
#        "product_url": "https://amzn.in/d/0aXGWf8E"
#    },
#    {
#       "filename": "pr38.png",
#       "product_name": "Table Lamp",
#       "product_url": "https://amzn.in/d/07NHfVSW"
#   },
#   {
#      "filename": "pr39.png",
#      "product_name": "Table Lamp",
#      "product_url": "https://amzn.in/d/07NHfVSW"
#  },
#  {
#     "filename": "pr40.png",
#     "product_name": "Table Lamp",
#     "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr41.png",
#    "product_name": "Table Lamp",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr42.png",
#    "product_name": "Photo_frame",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr43.png",
#    "product_name": "tie",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr44.png",
#    "product_name": "telephone",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr45.png",
#    "product_name": "watch",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr46.png",
#    "product_name": "white_paper",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr47.png",
#    "product_name": "telephone",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr48.png",
#    "product_name": "white_paper",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr49.png",
#    "product_name": "white_paper",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr50.png",
#    "product_name": "black_coat",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr51.png",
#    "product_name": "potted plant",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr52.png",
#    "product_name": "mouse",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr53.png",
#    "product_name": "telephone",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr54.png",
#    "product_name": "PC",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr55.png",
#    "product_name": "white_paper",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr56.png",
#    "product_name": "potted plant",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr57.png",
#    "product_name": "telephone",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr58.png",
#    "product_name": "Tissue_box",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr59.png",
#    "product_name": "Tissue_box",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr60.png",
#    "product_name": "PC",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# },
# {
#    "filename": "pr61.png",
#    "product_name": "white_paper",
#    "product_url": "https://amzn.in/d/07NHfVSW"
# }