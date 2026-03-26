from vertexai.generative_models import GenerativeModel
from vertexai.preview.vision_models import ImageGenerationModel
from google.cloud import texttospeech, firestore

# --- LINGUIST AGENT TOOL ---
def translate_to_gen_z(text: str) -> str:
    """Translates corporate jargon into Gen Z slang."""
    model = GenerativeModel("gemini-2.5-flash")
    system_prompt = "You are an expert in Gen Z slang. Translate corporate jargon into hilarious, relatable Gen Z slang."
    prompt = f"{system_prompt}\
\
Email: {text}\
\
Return ONLY the translation."
    response = model.generate_content(prompt)
    return response.text

# --- VISUALIST AGENT TOOL ---
def generate_visual_vibe(translated_text: str) -> dict:
    """Generates an image and a creative prompt based on translated text."""
    model = GenerativeModel("gemini-2.5-flash")
    image_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
    
    # First, brainstorm the prompt
    prompt_refiner = f"You are a creative director. Create a funny, safe-for-work, high-quality meme prompt based on this text.\
\
Context: {translated_text}\
\
Return ONLY a 1-sentence prompt for an image generator."
    refined_prompt = model.generate_content(prompt_refiner).text
    
    # Second, generate the image
    images = image_model.generate_images(
        prompt=f"Funny office meme, digital art: {refined_prompt}",
        number_of_images=1
    )
    
    # Return the prompt and the raw image data if available
    image_data = images[0]._image_bytes if images and hasattr(images[0], '_image_bytes') else None
    
    return {
        "concept": refined_prompt,
        "image_bytes": image_data
    }

# --- AUDIO AGENT TOOL ---
def generate_audio_narration(text: str) -> bytes:
    """Converts text to speech with a Gen Z-like voice."""
    client = texttospeech.TextToSpeechClient()
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", 
        name="en-US-Neural2-H"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        pitch=3.0,
        speaking_rate=1.15
    )
    synthesis_input = texttospeech.SynthesisInput(text=text)
    response = client.synthesize_speech(
        input=synthesis_input, 
        voice=voice, 
        audio_config=audio_config
    )
    return response.audio_content

# --- VOCAB AGENT TOOLS ---
def create_slang_glossary(original_text: str, translated_text: str) -> str:
    """Creates a glossary of Gen Z slang from the translation."""
    model = GenerativeModel("gemini-2.5-flash")
    system_prompt = """
    You are a Lexicographer. Your job is to extract Gen Z slang from a provided translation
    and create a 'Glossary' for a Gen X/Boomer audience.

    Format your response as a simple markdown list:
    - **Slang Word**: Meaning in standard corporate English.
    """
    prompt = f"{system_prompt}\
\
Original Corporate Email: {original_text}\
Gen Z Translation: {translated_text}\
\
Identify the key slang terms used in the translation and define them based on the context."
    response = model.generate_content(prompt)
    return response.text
def update_slang_vault(glossary_text: str, project_id: str, database_id: str) -> bool:
    """Parses a glossary and saves each term to a Firestore database."""
    try:
        db = firestore.Client(project=project_id, database=database_id)
        lines = glossary_text.split("\
")
        for line in lines:
            if "**:" in line or "**: " in line:
                clean_line = line.replace("- **", "").replace("**", "")
                if ":" in clean_line:
                    word, definition = clean_line.split(":", 1)
                    doc_ref = db.collection("slang_dictionary").document(word.strip().lower())
                    doc_ref.set({
                        "word": word.strip(),
                        "definition": definition.strip(),
                        "timestamp": firestore.SERVER_TIMESTAMP
                    })
        return True
    except Exception as e:
        print(f"Firestore Error in update_slang_vault: {e}")
        return False

# --- SAFETY AGENT TOOL ---
def check_content_safety(text: str) -> str:
    """Checks text for harmful content."""
    model = GenerativeModel("gemini-2.5-flash")
    system_prompt = """
    You are a Content Safety Moderator. Your job is to inspect text for:
    1. Violence or self-harm
    2. Illegal drugs or paraphernalia
    3. Weapons or firearms
    4. Hate speech or extreme profanity
    
    If the text is SAFE, return ONLY the word: 'SAFE'
    If it's unsafe, return ONLY 'REFUSED'.
    """
    prompt = f"{system_prompt}\
\
Inspect this text: {text}"
    response = model.generate_content(prompt)
    return response.text.strip().upper()
