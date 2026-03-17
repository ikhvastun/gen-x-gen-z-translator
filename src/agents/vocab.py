from google.cloud import firestore
from vertexai.generative_models import GenerativeModel

class VocabAgent:
    def __init__(self):
        self.model = GenerativeModel("gemini-2.5-flash")
        self.system_prompt = """
        You are a Lexicographer. Your job is to extract Gen Z slang from a provided translation 
        and create a 'Glossary' for a Gen X/Boomer audience.
        
        Format your response as a simple list:
        - **Slang Word**: Meaning in standard corporate English.
        """
        self.db = firestore.Client(
            project="qwiklabs-asl-01-964394115550",
            database="gen-x-gen-z-vocabulary"
        )

    def create_glossary(self, original, translation):
        prompt = f"""
        {self.system_prompt}
        
        Original Corporate Email: {original}
        Gen Z Translation: {translation}
        
        Identify the key slang terms used in the translation and define them based on the context.
        """
        response = self.model.generate_content(prompt)
        return response.text
    
    def update_public_dictionary(self, glossary_text):
        """
        Parses glossary and saves each word as a document in Firestore
        """
        try:
            lines = glossary_text.split("\
")
            for line in lines:
                if "**:" in line or "**: " in line:
                    clean_line = line.replace("- **", "").replace("**", "")
                    if ":" in clean_line:
                        word, definition = clean_line.split(":", 1)
                        # Save to a collection called 'slang_dictionary'
                        doc_ref = self.db.collection("slang_dictionary").document(word.strip().lower())
                        doc_ref.set({
                            "word": word.strip(),
                            "definition": definition.strip(),
                            "timestamp": firestore.SERVER_TIMESTAMP
                        })
            return True
        except Exception as e:
            print(f"Firestore Error: {e}")
            return False
