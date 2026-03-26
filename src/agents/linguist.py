from vertexai.generative_models import GenerativeModel
from config import GEMINI_FLASH_MODEL

class LinguistAgent:
    def __init__(self):
        self.model = GenerativeModel(GEMINI_FLASH_MODEL)
        self.system_prompt = "You are an expert in Gen Z slang. Translate corporate jargon into hilarious, relatable Gen Z slang."

    def translate(self, text):
        prompt = f"{self.system_prompt}\
\
Email: {text}\
\
Return ONLY the translation."
        response = self.model.generate_content(prompt)
        return response.text
