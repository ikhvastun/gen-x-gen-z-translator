from vertexai.generative_models import GenerativeModel

class SafetyAgent:
    def __init__(self):
        # We use Flash here because it's fast and perfect for classification
        self.model = GenerativeModel("gemini-2.5-flash")
        self.system_prompt = """
        You are a Content Safety Moderator. Your job is to inspect text for:
        1. Violence or self-harm
        2. Illegal drugs or paraphernalia
        3. Weapons or firearms
        4. Hate speech or extreme profanity
        
        If the text is SAFE, return ONLY the word: 'SAFE'
        If the text contains any of the above, return ONLY the word: 'REFUSED'
        """

    def check_vibe(self, text):
        prompt = f"{self.system_prompt}\
\
Inspect this text: {text}"
        response = self.model.generate_content(prompt)
        return response.text.strip().upper()
