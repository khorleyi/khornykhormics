import streamlit as st
import sys
import os
import json

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api import generate_scene

st.set_page_config(
    page_title="Story Results",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'current_panel' not in st.session_state:
    st.session_state.current_panel = 1

if 'selected_mcq' not in st.session_state:
    st.session_state.selected_mcq = None

# Check if we have scene data
if 'scene_data' not in st.session_state or st.session_state.scene_data is None:
    st.warning("No scene data found. Please submit a story first.")
    if st.button("Go to Input Page"):
        st.switch_page("pages/1_Input.py")
    st.stop()

# Extract render_scene data
render_scene = st.session_state.scene_data.get('render_scene', {})

# Get scene components
panels = render_scene.get('panels', [])  # Array of 5 image URLs
narrative = render_scene.get('narrative', [])  # Array of 5 text strings
dialogue = render_scene.get('dialogue', [])  # Array of dialogue objects
choices = render_scene.get('choices', [])  # Array of choice objects

if not panels or not narrative:
    st.error("Invalid scene data structure.")
    st.stop()

# Get current panel index (0-based)
current_panel_idx = st.session_state.current_panel - 1
if current_panel_idx >= len(panels):
    st.error("Invalid panel number")
    st.stop()

# Navigation functions
def next_panel():
    if st.session_state.current_panel < len(panels):
        st.session_state.current_panel += 1

def prev_panel():
    if st.session_state.current_panel > 1:
        st.session_state.current_panel -= 1

# Display panel based on panel number
is_last_panel = st.session_state.current_panel == 5

if not is_last_panel:
    # Panels 1-4: Left layout
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3>Panel {st.session_state.current_panel} of 5</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Background image
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # Display panel image
        st.image(panels[current_panel_idx], width='stretch')

        # Display narrative text
        st.markdown(
            f"""
            <div style="
                background-color: rgba(255, 255, 255, 0.9);
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
                text-align: left;
            ">
                <p style="font-size: 16px; line-height: 1.6; margin: 0;">{narrative[current_panel_idx]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Navigation buttons
    st.divider()
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])

    with col2:
        if st.session_state.current_panel > 1:
            st.button("← Previous", on_click=prev_panel, width='stretch')

    with col4:
        if st.session_state.current_panel < 5:
            st.button("Next →", on_click=next_panel, width='stretch', type="primary")

else:
    # Panel 5: Right layout with choices
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3>Panel 5 of 5 - Final Choice</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Background image and text
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # Display panel image
        st.image(panels[current_panel_idx], width='stretch')

        # Display narrative text
        st.markdown(
            f"""
            <div style="
                background-color: rgba(255, 255, 255, 0.9);
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
                text-align: left;
            ">
                <p style="font-size: 16px; line-height: 1.6; margin: 0;">{narrative[current_panel_idx]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        # MCQ choices (3 buttons in horizontal layout)
        if choices:
            st.subheader("Choose your ending:")
            cols = st.columns(len(choices))

            for idx, choice_obj in enumerate(choices):
                choice_text = choice_obj.get('text', '')
                choice_id = choice_obj.get('choice_id', '')
                with cols[idx]:
                    if st.button(
                        choice_text,
                        key=f"mcq_{idx}",
                        width='stretch',
                        type="primary" if st.session_state.selected_mcq == choice_id else "secondary"
                    ):
                        st.session_state.selected_mcq = choice_id
                        st.rerun()

        # Open-ended text input
        st.divider()
        st.subheader("Or write your own ending:")
        custom_answer = st.text_area(
            "Your custom ending",
            placeholder="Write your own ending to the story...",
            height=100,
            key="custom_answer",
            label_visibility="collapsed"
        )

        # Submit button
        st.divider()
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            st.button("← Previous", on_click=prev_panel, width='stretch')

        with col3:
            if st.button("Submit Answer", type="primary", width='stretch'):
                # Validate that user selected something
                if not st.session_state.selected_mcq and not custom_answer.strip():
                    st.error("Please select a choice or write your own ending")
                else:
                    # Get the choice text (not the choice_id)
                    user_decision_text = None

                    if st.session_state.selected_mcq:
                        # User selected an MCQ - find the matching choice text
                        for choice_obj in choices:
                            if choice_obj.get('choice_id') == st.session_state.selected_mcq:
                                user_decision_text = choice_obj.get('text')
                                break
                    elif custom_answer.strip():
                        # User wrote custom answer
                        user_decision_text = custom_answer.strip()

                    if not user_decision_text:
                        st.error("Could not determine your choice. Please try again.")
                    else:
                        # Build the payload in the correct format for generate-scene
                        # Get data from previous responses
                        session_data_to_save = st.session_state.scene_data.get('session_data_to_save', {})
                        story_data = st.session_state.story_data

                        # Get overall_story - ensure it's a JSON STRING (not an object)
                        overall_story = session_data_to_save.get('overall_story', story_data.get('overall_story', ''))

                        # If overall_story is a dict/object, stringify it
                        if isinstance(overall_story, dict):
                            overall_story = json.dumps(overall_story)

                        # Get character data directly from story_data
                        characters = story_data.get('characters', [])
                        protagonist_name = story_data.get('protagonist_name', '')

                        # Update decision tracking
                        decision_history = session_data_to_save.get('decision_history', [])
                        decision_history.append(user_decision_text)

                        decision_count = (session_data_to_save.get('decision_count') or 0) + 1
                        current_scene = (session_data_to_save.get('current_scene') or 1) + 1

                        # Build the complete payload matching the correct format
                        payload = {
                            "session_id": story_data.get('session_id'),
                            "user_prompt": story_data.get('user_prompt', ''),
                            "overall_story": overall_story,  # JSON string
                            "character_profile": characters,  # ← FIX: Add this field (same as characters)
                            "characters": characters,  # Keep for backward compatibility
                            "protagonist_name": protagonist_name,
                            "current_scene": current_scene,
                            "decision_history": decision_history,
                            "phase": session_data_to_save.get('phase', 'ready_for_scene_1'),
                            "decision_count": decision_count,
                            "story_phase": session_data_to_save.get('story_phase', 'opening'),
                            "is_complete": session_data_to_save.get('is_complete', False)
                        }

                        # Console log the request body before sending
                        print("\n" + "="*80)
                        print("🔵 PANEL 5 SUBMIT - GENERATE-SCENE API CALL REQUEST BODY")
                        print("="*80)
                        print(f"Session ID: {payload.get('session_id')}")
                        print(f"Current Scene: {payload.get('current_scene')}")
                        print(f"Decision Count: {payload.get('decision_count')}")
                        print(f"Decision History: {payload.get('decision_history')}")
                        print(f"\nFull Request Body:")
                        print(json.dumps(payload, indent=2))
                        print("="*80 + "\n")

                        with st.spinner("Generating next scene..."):
                            try:
                                # Call generate-scene with updated data
                                new_scene_response = generate_scene(payload)

                                # Update session state with new scene
                                st.session_state.scene_data = new_scene_response
                                st.session_state.current_panel = 1
                                st.session_state.selected_mcq = None

                                # Rerun to show panel 1 of new scene
                                st.rerun()

                            except Exception as e:
                                st.error(f"Error generating next scene: {str(e)}")
