import os
import asyncio
import httpx  # An async-compatible HTTP client, replacement for 'requests'
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---

# Load environment variables from a .env file
load_dotenv()

# Get the API key from environment variables
FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY")

# Define API constants
API_URL = "https://api.freepik.com/v1/ai/gemini-2-5-flash-image-preview"
# API_URL = "https://api.freepik.com/v1/ai/text-to-image/imagen3"
POLLING_INTERVAL_SECONDS = 3  # Time to wait between status checks
TIMEOUT_SECONDS = 300  # Max time to wait for an image


# --- 2. THE CORE UTILITY FUNCTION ---

async def create_image(
    keywords: list,
    company_name: str = "Aura",
    product_name: str = "Cold Brew",
    tagline_prompt: str = "Elevate Your Moment"
) -> str:
    """
    Generates an image using the Freepik AI API based on a list of keywords.

    This function is async and handles the entire task submission and polling
    process required by the Freepik API.

    Args:
        keywords: A list of strings describing the desired image subject.
        company_name: The brand/company name (default: "Aura")
        product_name: The product name (default: "Cold Brew")
        tagline_prompt: The tagline to display (default: "Elevate Your Moment")

    Returns:
        A string containing the URL of the generated image.

    Raises:
        Exception: If the API key is missing, the request fails, or it times out.
    """
    if not FREEPIK_API_KEY:
        raise Exception("ERROR: FREEPIK_API_KEY not found in environment variables.")

    if not keywords:
        raise ValueError("Keywords list cannot be empty.")

    # Step 1: Dynamically build a high-quality prompt from the keywords
    full_prompt = f"""
    Professional high-resolution close-up product photography of:
    {company_name} {product_name}, featuring a sleek can with the Starbucks logo and product name clearly visible in bold letters. The can sits at the center, surrounded by simple, stylized swirls of iced coffee shaped like a soft tornado, with droplets or small lines suggesting motion. The scene should feel refreshing, modern, and energetic, with smooth clean shapes, vector-style gradients, and soft shadows. Place the tagline {tagline_prompt} in a clear, modern sans-serif font below or above the can. Visual style: flat illustration, simple composition, vector aesthetic, minimal details, strong brand visibility, summer mood, refreshing energy, balanced negative space. Keywords: illustration, minimalist design, vector, clean composition, summer vibe, refreshing coffee, clear logo, bold typography, pastel background.
    """

    # Step 2: Define the payload for the API request
    headers = {
        "x-freepik-api-key": FREEPIK_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": full_prompt,
        "num_images": 1,
        "aspect_ratio": "square_1_1",
        "styling": {
            "style": "photo",  # Changed from "studio-shot" to "photo" for photorealism
            "effects": { 
                "color": "vibrant",  # Changed from "pastel" to "vibrant" for commercial appeal
                "lightning": "studio",  # Keep studio lighting for professional look
                "framing": "close-up"  # Keep close-up framing for product focus
            }
        },
        "person_generation": "dont_allow"
    }

    # Step 3: Use an async HTTP client to make the requests
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        try:
            # Make the initial POST request to start the task
            start_response = await client.post(API_URL, json=payload, headers=headers)
            start_response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            
            data = start_response.json()["data"]
            task_id = data["task_id"]
            status = data["status"]
            print(f"-> Freepik task started with ID: {task_id}")

            # Step 4: Poll the API until the task is completed
            status_url = f"{API_URL}/{task_id}"
            start_time = asyncio.get_event_loop().time()

            while status != "COMPLETED":
                if asyncio.get_event_loop().time() - start_time > TIMEOUT_SECONDS:
                    raise Exception("Timeout reached while waiting for image generation.")

                print(f"  > Waiting for task... (current status: {status})")
                await asyncio.sleep(POLLING_INTERVAL_SECONDS)
                
                status_response = await client.get(status_url, headers=headers)
                status_response.raise_for_status()
                status = status_response.json()["data"]["status"]

            # Step 5: Once completed, extract and return the image URL
            final_data = status_response.json()["data"]
            if final_data.get("generated"):
                image_url = final_data["generated"][0]
                print(f"-> Freepik task COMPLETED. Image URL ready.")
                return image_url
            else:
                raise Exception("Task completed but no image data was found.")

        except httpx.HTTPStatusError as e:
            print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise


# --- 3. STANDALONE TEST BLOCK ---
# You can run this file directly (`python utils/freepik_utils.py`) to test it.
if __name__ == "__main__":
    async def test_generation():
        print("--- Running Freepik Utility Standalone Test ---")
        try:
            # Define some example keywords for the test
            example_keywords = ["Starbucks Cold Brew can", "splashes of coffee", "ice cubes"]

            # Call the main function
            url = await create_image(example_keywords)
            
            print("\n--- TEST SUCCEEDED ---")
            print(f"Generated Image URL: {url}")
        except Exception as e:
            print("\n--- TEST FAILED ---")
            print(f"Error: {e}")

    # Run the async test function
    asyncio.run(test_generation())
