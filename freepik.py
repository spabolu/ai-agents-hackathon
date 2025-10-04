import requests
from dotenv import load_dotenv
import os
import time

# Load FREEPIK_API_KEY as environment variable from .env file
load_dotenv() 

API_URL = "https://api.freepik.com/v1/ai/text-to-image/imagen3"
timeout = 300 # 5 minutes
generation_ok = True

headers = {"x-freepik-api-key": os.getenv("FREEPIK_API_KEY"), "Content-Type": "application/json"}

payload = {
    "prompt": """
    A minimalist flat-style illustration for Starbucks Cold Brew, featuring a sleek can with the Starbucks logo and product name clearly visible in bold letters. The text on the product should be standard marketing words. The can sits at the center, surrounded by simple, stylized swirls of iced coffee shaped like a soft tornado, with droplets or small lines suggesting motion. The scene should feel refreshing, modern, and energetic, with smooth clean shapes, vector-style gradients, and soft shadows. Place the tagline “Enjoy the best coffee coming this Summer” in a clear, modern sans-serif font below or above the can. Visual style: flat illustration, simple composition, vector aesthetic, minimal details, strong brand visibility, summer mood, refreshing energy, balanced negative space. Keywords: illustration, minimalist design, vector, clean composition, summer vibe, refreshing coffee, clear logo, bold typography, pastel background.
    """,
    #"webhook_url": "https://www.example.com/webhook", # only if you want send the status of the task to a webhook
    "num_images": 1,
    "aspect_ratio": "square_1_1",
    "styling": {
        "style": "studio-shot", # Posssible values photo, digital-art, 3d, painting, low-poly, pixel-art, anime, cyberpunk, comic, vintage, cartoon, vector, studio-shot, dark, sketch, mockup, 2000s-pone, 70s-vibe, watercolor, art-nouveau, origami, surreal, fantasy, traditional-japan
        "effects": {
            "color": "pastel", # Possible values: b&w, pastel, sepia, dramatic, vibrant, orange&teal, film-filter, split, electric, pastel-pink, gold-glow, autumn, muted-green, deep-teal, duotone, terracotta&teal, red&blue, cold-neon, burgundy&blue 
            "lightning": "cinematic", # Possible values: tudio, warm, cinematic, volumetric, golden-hour, long-exposure, cold, iridescent, dramatic, hardlight, redscale, indoor-light
            "framing": "close-up" # Possible values: portrait, macro, panoramic, aerial-view, close-up, cinematic, high-angle, low-angle, symmetry, fish-eye, first-person
        }
    },
    "person_generation": "dont_allow", # Possible values: dont_allow, allow_adult, allow_all
    "safety_settings": "block_low_and_above" # Possible values: block_low_and_above, block_medium_and_above, block_only_high, block_none
}

start_time = time.time()
response = requests.post(API_URL, json=payload, headers=headers)
print(response.json())

if response.status_code == 200:
    # Active wait until the task is completed

    # Get the task_id from the initial response
    task_id = response.json()["data"]["task_id"]
    status = response.json()["data"]["status"]

    # Polling until the status is "COMPLETED"
    while status != "COMPLETED":
        print(f"Waiting for the task to complete... (current status: {status})")
        time.sleep(2)  # Wait 2 seconds before checking again
        status_url = f"{API_URL}/{task_id}"
        response = requests.get(status_url, headers={"x-freepik-api-key": os.getenv("FREEPIK_API_KEY")})
        if response.status_code == 200:
            status = response.json()["data"]["status"]
        else:
            print(f"Error while checking the task status: {response.status_code}")
            time.sleep(2)
        if time.time() - start_time > timeout:
            print("Timeout reached")
            generation_ok = False
            break
            
    if generation_ok:
        print("COMPLETED")
        # Download the image ---------------------------------------------------------------
        IMG_URL = response.json()["data"]["generated"][0]
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_name = os.path.join(current_dir, "generated_image.jpg")
        img_response = requests.get(IMG_URL)
        if img_response.status_code == 200:
            with open(file_name, "wb") as f:
                f.write(img_response.content)
            print(f"Image successfully downloaded as {file_name}")
        else:
            print(f"Could not download the image. Status code: {img_response.status_code}")
else:
    print(f"Error while generating the image. Status code: {response.status_code}, message: {response.json()['message']}")