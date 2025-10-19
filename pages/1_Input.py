import streamlit as st
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api import submit_story, generate_scene

st.set_page_config(
    page_title="Story Input",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'supporting_characters' not in st.session_state:
    st.session_state.supporting_characters = []

if 'story_data' not in st.session_state:
    st.session_state.story_data = None

if 'scene_data' not in st.session_state:
    st.session_state.scene_data = None

if 'current_panel' not in st.session_state:
    st.session_state.current_panel = 1

if 'pending_submission' not in st.session_state:
    st.session_state.pending_submission = None

# Sidebar - Input Form
with st.sidebar:
    st.header("Story Input")

    # Story text area
    story = st.text_area(
        "Story",
        placeholder="Enter your story here...",
        height=150,
        key="story_input"
    )

    # Lead character
    lead_character = st.text_input(
        "Lead Character",
        placeholder="Describe your lead character...",
        key="lead_character_input"
    )

    # Supporting characters section
    st.subheader("Supporting Characters")

    # Display existing supporting characters
    for idx, char in enumerate(st.session_state.supporting_characters):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.session_state.supporting_characters[idx] = st.text_input(
                f"Supporting Character {idx + 1}",
                value=char,
                key=f"supporting_char_{idx}",
                label_visibility="collapsed"
            )
        with col2:
            if st.button("×", key=f"remove_{idx}"):
                st.session_state.supporting_characters.pop(idx)
                st.rerun()

    # Add supporting character button
    if len(st.session_state.supporting_characters) < 5:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("➕", key="add_char", width='stretch'):
                st.session_state.supporting_characters.append("")
                st.rerun()
    else:
        st.info("Maximum 5 supporting characters")

    # Submit button
    st.divider()
    submit_button = st.button("Submit", type="primary", width='stretch')

    if submit_button:
        # Validate inputs
        if not story.strip():
            st.error("Please enter a story")
        elif not lead_character.strip():
            st.error("Please describe the lead character")
        else:
            # Filter out empty supporting characters
            valid_supporting_chars = [
                char.strip() for char in st.session_state.supporting_characters
                if char.strip()
            ]

            # Store input data and set flag to trigger processing
            st.session_state.pending_submission = {
                'story': story.strip(),
                'lead_character': lead_character.strip(),
                'supporting_characters': valid_supporting_chars
            }

# Main area - Description
st.title("Description")

# Check if there's a pending submission to process
if 'pending_submission' in st.session_state and st.session_state.pending_submission:
    submission_data = st.session_state.pending_submission

    try:
        # Call initialize-story first
        with st.spinner("Initializing your story..."):
            story_response = submit_story(
                story=submission_data['story'],
                lead_character=submission_data['lead_character'],
                supporting_characters=submission_data['supporting_characters']
            )

        # Call generate-scene immediately with the initialize-story response
        with st.spinner("Generating scene..."):
            scene_response = generate_scene(story_response)

        # Only store in session state after BOTH calls succeed
        st.session_state.story_data = story_response
        st.session_state.scene_data = scene_response
        st.session_state.current_panel = 1

        # Clear pending submission
        st.session_state.pending_submission = None

        # Navigate to results page
        st.success("Story and scene generated successfully!")
        st.switch_page("pages/2_Results.py")

    except Exception as e:
        st.error(f"Error: {str(e)}")
        # Clear pending submission on error
        st.session_state.pending_submission = None
        st.stop()
else:
    st.info("Please use the sidebar to input your story details and click Submit.")
