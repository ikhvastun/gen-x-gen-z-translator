import streamlit as st
import vertexai
from google.cloud import firestore

from config import PROJECT_ID, LOCATION, DATABASE_ID
from agents import (
    LinguistAgent,
    VisualistAgent,
    AudioAgent,
    VocabAgent,
    SafetyAgent,
)

# Setup
vertexai.init(project=PROJECT_ID, location=LOCATION)

# --- AGENT INITIALIZATION ---
if "linguist" not in st.session_state:
    st.session_state.linguist = LinguistAgent()

if "visualist" not in st.session_state:
    st.session_state.visualist = VisualistAgent()

if "audio_agent" not in st.session_state:
    st.session_state.audio_agent = AudioAgent()

if "results" not in st.session_state:
    st.session_state.results = None

if "vocab_agent" not in st.session_state:
    st.session_state.vocab_agent = VocabAgent()

if "safety_agent" not in st.session_state:
    st.session_state.safety_agent = SafetyAgent()


def display_vault():
    st.sidebar.subheader("🗄️ The Slang Vault")

    firestore_url = f"https://console.cloud.google.com/firestore/databases/{DATABASE_ID}/data?project={PROJECT_ID}"
    st.sidebar.link_button("📂 View Live DB", firestore_url)
    st.sidebar.divider()

    db = firestore.Client(project=PROJECT_ID, database=DATABASE_ID)

    try:
        docs = (
            db.collection("slang_dictionary")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(10)
            .stream()
        )

        for doc in docs:
            data = doc.to_dict()
            word = data.get("word", "Unknown")
            definition = data.get("definition", "No definition")
            st.sidebar.write(f"**{word}**: {definition}")
    except Exception as e:
        st.sidebar.error(f"Vault load error: {e}")


def main():
    st.title("📂 Multi-Agent Corporate Translator")

    input_text = st.text_area("Paste Corporate Email:", key="main_input")

    if st.button("Run Agentic Workflow 🤖"):
        if input_text:
            try:
                with st.status("Safety Agent checking the vibe...") as s:
                    safety_check = st.session_state.safety_agent.check_vibe(input_text)

                    if "REFUSED" in safety_check:
                        s.update(label="Vibe Check Failed! ❌", state="error")
                        st.error(
                            "Hold up, fam. That input isn't main character energy. "
                            "We don't do violence, drugs, or weapons here. 🚩"
                        )
                        st.stop()

                    s.update(label="Vibe Check Passed! ✅", state="complete")

                with st.status("Linguist translating...") as s:
                    translation = st.session_state.linguist.translate(input_text)
                    s.update(label="Translation Ready!", state="complete")

                with st.status("Researcher creating glossary...") as s:
                    glossary = st.session_state.vocab_agent.create_glossary(
                        input_text, translation
                    )
                    st.session_state.vocab_agent.update_public_dictionary(glossary)
                    s.update(
                        label="Glossary Ready & Vault Updated!", state="complete"
                    )

                with st.status("Audio is on the way...") as s:
                    audio_data = st.session_state.audio_agent.speak(translation)
                    concept, img_obj = st.session_state.visualist.generate_vibe(
                        translation
                    )

                st.session_state.results = {
                    "translation": translation,
                    "glossary": glossary,
                    "audio": audio_data,
                    "concept": concept,
                    "image": img_obj._pil_image if img_obj else None,
                }
                st.rerun()

            except Exception as e:
                st.error(f"Execution Error: {e}")
        else:
            st.warning("Please enter some text.")

    if st.session_state.results:
        res = st.session_state.results
        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📱 The Group Chat")
            st.info(res["translation"])
            st.audio(res["audio"], format="audio/mp3")
        with c2:
            if res["image"]:
                st.image(
                    res["image"], caption=res["concept"], use_column_width=True
                )
        with st.expander("📚 Open Intern-to-Corporate Glossary"):
            st.markdown(res["glossary"])

    display_vault()


if __name__ == "__main__":
    main()