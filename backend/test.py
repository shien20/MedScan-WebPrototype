from gradcam import generate_heatmap_overlay
from PIL import Image

img = Image.open("C:\\Users\\shien\\OneDrive - Sunway Education Group\\Sunway materials\\Capstone Project 2\\MedScan\\data\\processed\\all_data\\Images\\00000150_002.png")
overlay, description = generate_heatmap_overlay(img)
print(description)