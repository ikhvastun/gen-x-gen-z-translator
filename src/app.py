import streamlit as st
import vertexai
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.cloud import firestore
from PIL import Image
import io

from config import PROJECT_ID, LOCATION, DATABASE_ID
import tools

# Setup
vertexai.init(project=PROJECT_ID, location=LOCATION)

# --- AGENT INITIALIZATION ---
if "agent" not in st.session_state:
    # The new agent will use the functions from our tools file
    agent_tools = [
        tools.check_content_safety,
        tools.translate_to_gen_z,
        tools.create_slang_glossary,
        tools.generate_visual_vibe,
        tools.generate_audio_narration,
        tools.update_slang_vault
    ]

    # This is our new "super agent" that can access all the tools
    st.session_state.agent = Agent(
        name="Gen_Z_Translator",
        description="Multi-modal expert for corporate-to-slang translation.",
        instruction="""You are a multi-modal translator who is an expert in corporate and Gen Z slang.

        Given a corporate text, you must follow this strict workflow:
        1.  First, check if the content is safe using the `check_content_safety` tool. If it's 'REFUSED', stop immediately and inform the user.
        2.  If the content is safe, translate it to Gen Z slang using the `translate_to_gen_z` tool.
        3.  Create a glossary for the translated slang using the `create_slang_glossary` tool.
        4.  Update the slang vault with the new glossary using the `update_slang_vault` tool. You must use this `project_id` and `database_id`: '{PROJECT_ID}', '{DATABASE_ID}'.
        5.  Generate a visual vibe (an image) based on the translated text using the `generate_visual_vibe` tool.
        6.  Generate an audio narration of the translated text using the `generate_audio_narration` tool.
        7.  Finally, return a single JSON object that contains all the results from the tool calls: "translation", "glossary", "concept", "image_bytes", and "audio_content".
        """,
        model="gemini-2.5-flash",
        tools=agent_tools
    )
    st.session_state.runner = InMemoryRunner(st.session_state.agent)
    # st.session_state.runner.create_session(session_id="demo_session")

if "results" not in st.session_state:
    st.session_state.results = None

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
    st.subheader("Powered by a Vertex AI Agent")

    input_text = st.text_area("Paste Corporate Email:", key="main_input", height=200)

    if st.button("Run Agentic Workflow 🤖"):
        if input_text:
            try:
                with st.spinner("🤖 Agent is thinking..."):
                    runner = st.session_state.runner
                    
                    user_content = types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=input_text)]
                    )

                    response_events = runner.run(
                        user_id="demo_user",
                        session_id="demo_session",
                        new_message=user_content
                    )
                    
                    results = {}
                    final_answer = ""
                    for event in response_events:
                        if event.type == "text":
                            final_answer += event.text
                        elif event.type == "tool_code":
                            # The ADK automatically executes the tool code
                            # and returns the results in a subsequent event.
                            pass
                        elif event.type == "tool_result":
                            # We can inspect the results of each tool call
                            if event.tool_name == "translate_to_gen_z":
                                results["translation"] = event.outputs[0]["text"]
                            elif event.tool_name == "create_slang_glossary":
                                results["glossary"] = event.outputs[0]["text"]
                            elif event.tool_name == "generate_visual_vibe":
                                # The tool returns a dict
                                results["concept"] = event.outputs[0]["concept"]
                                results["image_bytes"] = event.outputs[0]["image_bytes"]
                            elif event.tool_name == "generate_audio_narration":
                                results["audio_content"] = event.outputs[0]["bytes"]


                    st.session_state.results = results
                    st.rerun()

            except Exception as e:
                st.error(f"Agent Execution Error: {e}")
        else:
            st.warning("Please enter some text.")

    if st.session_state.results:
        res = st.session_state.results
        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📱 The Group Chat")
            st.info(res.get("translation", "No translation available."))
            if res.get("audio_content"):
                st.audio(res["audio_content"], format="audio/mp3")
        with c2:
            if res.get("image_bytes"):
                try:
                    img = Image.open(io.BytesIO(res["image_bytes"]))
                    st.image(img, caption=res.get("concept", ""), use_column_width=True)
                except Exception as e:
                    st.error(f"Image display error: {e}")

        with st.expander("📚 Open Intern-to-Corporate Glossary"):
            st.markdown(res.get("glossary", "No glossary available."))

    display_vault()

if __name__ == "__main__":
    main()