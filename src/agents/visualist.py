from vertexai.generative_models import GenerativeModel
from vertexai.preview.vision_models import ImageGenerationModel
from config import GEMINI_FLASH_MODEL, IMAGEN_MODEL

class VisualistAgent:
    def __init__(self):
        self.model = GenerativeModel(GEMINI_FLASH_MODEL)
        self.image_model = ImageGenerationModel.from_pretrained(IMAGEN_MODEL)
        self.system_prompt = "You are a creative director. Create a funny, safe-for-work, high-quality meme prompt based on this text."

    def generate_vibe(self, translated_text):
        # First, brainstorm the prompt
        prompt_refiner = f"{self.system_prompt}\
\
Context: {translated_text}\
\
Return ONLY a 1-sentence prompt for an image generator."
        refined_prompt = self.model.generate_content(prompt_refiner).text
        
        # Second, generate the image
        images = self.image_model.generate_images(
            prompt=f"Funny office meme, digital art: {refined_prompt}",
            number_of_images=1
        )
        return refined_prompt, images[0] if images else None
