from google.cloud import texttospeech

class AudioAgent:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
        # "en-US-Neural2-H" or "en-US-Neural2-F" are generally more "expressive"
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", 
            name="en-US-Neural2-H" 
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            # Increasing pitch makes it sound younger/higher energy
            pitch=3.0, 
            # 1.15x speed sounds more like a fast-talking Gen Z-er
            speaking_rate=1.15 
        )

    def speak(self, text):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=synthesis_input, 
            voice=self.voice, 
            audio_config=self.audio_config
        )
        return response.audio_content
