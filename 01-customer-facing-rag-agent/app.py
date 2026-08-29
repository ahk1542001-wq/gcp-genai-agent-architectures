import os
import streamlit as st
from google.adk import Runner
from google.adk.apps import App
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import root_agent, get_menu

st.set_page_config(page_title="Artisanal AI Barista", page_icon="☕", layout="wide")

# Sidebar: Grounded Menu Viewer
with st.sidebar:
    st.title("☕ Coffee Shop Menu")
    st.markdown("All responses are strictly grounded in this live dataset:")
    menu_data = get_menu()
    st.json(menu_data)

st.title("☕ Welcome to AI Coffee Barista")
st.caption("Powered by Google ADK, Gemini on Vertex AI, and Cloud Run")

# Initialize ADK Runner in session state
if "runner" not in st.session_state:
    app = App(name="barista_app", root_agent=root_agent)
    st.session_state.runner = Runner(
        app=app,
        session_service=InMemorySessionService(),
        auto_create_session=True
    )
    st.session_state.messages = []

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle user input
if prompt := st.chat_input("Ask the Barista for recommendations, ingredients, or allergens..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Brewing answer..."):
            new_msg = types.Content(parts=[types.Part(text=prompt)])
            events = st.session_state.runner.run(
                user_id="customer",
                session_id="session_001",
                new_message=new_msg
            )
            response_text = "".join(
                part.text
                for event in events
                if event.content and event.content.parts
                for part in event.content.parts
                if part.text
            ) or "I'm sorry, I couldn't process that request."
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
