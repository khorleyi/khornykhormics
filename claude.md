# Claude Code Development Guide
## AI-Powered Manga Visual Novel Generator - Streamlit Frontend

---

## Overview

You are developing the **Streamlit frontend** for an AI-powered manga visual novel generator. This application allows users to create interactive manga-style stories that adapt to their choices in real-time.

Your primary responsibilities:
1. Build the Streamlit web interface
2. Handle HTTP communication with n8n workflows
3. Manage session state and story progression
4. Display manga panels and narrative content
5. Process user inputs (both preset choices and custom text)

---

## System Context

### Architecture Overview

```
User → Streamlit App → Planning Workflow (n8n)
                            ↓
                     [Story + Visual Data]
                            ↓
                     Image Workflow (n8n)
                            ↓
                     [5 Manga Panel URLs]
                            ↓
         Streamlit App ← Planning Workflow
```

**Two n8n Workflows:**
- **Planning Workflow**: Generates narrative, dialogue, scene descriptions, and user choices
- **Image Workflow**: Creates five manga panels per scene in parallel

**Your Role:**
- Build Streamlit UI that communicates with these workflows
- Send user inputs to Planning Workflow webhook
- Receive and display complete scene packages (text + images)
- Manage story progression through 7-10 scenes

---

## Technical Requirements

### Technology Stack

- **Frontend Framework**: Streamlit
- **Python Version**: 3.8+
- **HTTP Client**: `requests` library
- **State Management**: Streamlit session state
- **Image Display**: Streamlit image components

### Required Python Packages

```python
streamlit>=1.28.0
requests>=2.31.0
python-dotenv>=1.0.0
```

---

## Application Flow

### Phase 1: Story Initialization

**User Actions:**
1. User enters story theme (text area)
2. User enters character description (text area)
3. User clicks "Generate Story" button

**Your Code Should:**
1. Validate inputs (non-empty, reasonable length)
2. Show loading state: "Planning your story..."
3. Send POST request to Planning Workflow webhook:
   ```json
   {
     "action": "initialize",
     "theme": "user's theme text",
     "character": "user's character description"
   }
   ```
4. Store session_id and initial framework in session state
5. Transition to Scene 1

**Expected Response:**
```json
{
  "session_id": "unique-uuid",
  "status": "initialized",
  "message": "Story framework created",
  "character_profile": {...}
}
```

### Phase 2: Scene Generation Loop

**Per Scene:**
1. Display loading state: "Generating Scene X..."
2. Send user's previous choice to Planning Workflow:
   ```json
   {
     "action": "generate_scene",
     "session_id": "session-uuid",
     "user_choice": "text of chosen option or custom input",
     "scene_number": 2
   }
   ```
3. Receive complete scene package
4. Display background, panels, narrative, and choices
5. Wait for user input
6. Repeat until final scene

**Expected Scene Response:**
```json
{
  "scene_number": 2,
  "background_description": "Rain-soaked Tokyo street at night",
  "narrative_text": "The rain hammered down as you...",
  "dialogue": [
    {"character": "Detective", "text": "Something's not right here"},
    {"character": "Partner", "text": "We should call for backup"}
  ],
  "panel_images": [
    "https://url-to-panel-1.jpg",
    "https://url-to-panel-2.jpg",
    "https://url-to-panel-3.jpg",
    "https://url-to-panel-4.jpg",
    "https://url-to-panel-5.jpg"
  ],
  "choice_prompt": "What do you do next?",
  "choices": [
    "Confront your partner about their deception",
    "Investigate the supernatural connection alone",
    "Trust your partner and share what you've discovered"
  ],
  "is_final_scene": false
}
```

### Phase 3: Story Conclusion

**Final Scene Handling:**
- Scene package has `"is_final_scene": true`
- No choices array present
- Display narrative with resolution
- Show "Create New Story" button
- Optionally show decision history

---

## Streamlit App Structure

### Recommended File Organization

```
streamlit_app/
├── app.py                 # Main Streamlit application
├── components/
│   ├── scene_display.py   # Scene rendering component
│   ├── input_handler.py   # User input component
│   └── loading_states.py  # Loading animations
├── utils/
│   ├── api_client.py      # n8n workflow communication
│   ├── state_manager.py   # Session state management
│   └── validators.py      # Input validation
├── config.py              # Configuration and environment variables
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (not in git)
```

### Core App.py Structure

```python
import streamlit as st
from utils.api_client import WorkflowClient
from utils.state_manager import StateManager
from components.scene_display import display_scene
from components.input_handler import get_user_input

# Page configuration
st.set_page_config(
    page_title="AI Manga Visual Novel",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize state manager
state = StateManager()

# Main application flow
def main():
    if state.is_new_session():
        show_welcome_screen()
    elif state.is_initializing():
        show_initialization_loading()
    elif state.is_story_active():
        show_current_scene()
    elif state.is_story_complete():
        show_conclusion_screen()

if __name__ == "__main__":
    main()
```

---

## Key Implementation Details

### Session State Management

**Required State Variables:**

```python
# Initialize in st.session_state
{
    "session_id": None,              # UUID from Planning Workflow
    "current_scene": 0,              # Current scene number (0 = not started)
    "story_theme": "",               # User's input theme
    "character_description": "",     # User's character description
    "character_profile": {},         # From Character Agent
    "scene_history": [],             # Array of all scene data
    "choice_history": [],            # Array of user decisions
    "is_initializing": False,        # Loading state flag
    "is_generating_scene": False,    # Scene generation flag
    "current_scene_data": None,      # Current scene package
    "error_message": None            # Error handling
}
```

**State Manager Pattern:**

```python
class StateManager:
    def __init__(self):
        self._initialize_defaults()

    def _initialize_defaults(self):
        defaults = {
            "session_id": None,
            "current_scene": 0,
            "scene_history": [],
            "choice_history": [],
            # ... other defaults
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def is_new_session(self):
        return st.session_state.session_id is None

    def start_story(self, session_id, character_profile):
        st.session_state.session_id = session_id
        st.session_state.character_profile = character_profile
        st.session_state.current_scene = 1

    def add_scene(self, scene_data):
        st.session_state.scene_history.append(scene_data)
        st.session_state.current_scene_data = scene_data

    def add_choice(self, choice_text):
        st.session_state.choice_history.append({
            "scene": st.session_state.current_scene,
            "choice": choice_text
        })
```

### API Client for n8n Workflows

**Workflow Communication:**

```python
import requests
from typing import Dict, Any, Optional

class WorkflowClient:
    def __init__(self, planning_webhook_url: str):
        self.planning_url = planning_webhook_url
        self.timeout = 120  # 2 minutes for scene generation

    def initialize_story(self, theme: str, character: str) -> Dict[str, Any]:
        """
        Initialize story with Planning Workflow

        Args:
            theme: User's story theme
            character: Character description

        Returns:
            Response with session_id and character_profile
        """
        payload = {
            "action": "initialize",
            "theme": theme,
            "character": character
        }

        try:
            response = requests.post(
                self.planning_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to initialize story: {str(e)}")

    def generate_scene(
        self,
        session_id: str,
        user_choice: str,
        scene_number: int
    ) -> Dict[str, Any]:
        """
        Generate next scene based on user choice

        Args:
            session_id: Unique session identifier
            user_choice: User's selected or typed choice
            scene_number: Next scene number to generate

        Returns:
            Complete scene package with narrative and images
        """
        payload = {
            "action": "generate_scene",
            "session_id": session_id,
            "user_choice": user_choice,
            "scene_number": scene_number
        }

        try:
            response = requests.post(
                self.planning_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to generate scene: {str(e)}")

class APIError(Exception):
    """Custom exception for API communication errors"""
    pass
```

### Scene Display Component

**Rendering Scene Data:**

```python
import streamlit as st
from typing import Dict, List, Any

def display_scene(scene_data: Dict[str, Any]) -> None:
    """
    Render complete scene with background, panels, and narrative

    Args:
        scene_data: Complete scene package from Planning Workflow
    """
    # Scene header
    scene_num = scene_data.get("scene_number", 1)
    total_scenes = 7  # Approximate

    st.markdown(f"### Scene {scene_num} of ~{total_scenes}")
    st.progress(scene_num / total_scenes)

    # Background description (optional atmospheric text)
    if bg := scene_data.get("background_description"):
        st.caption(f"🎬 {bg}")

    st.markdown("---")

    # Manga panels in grid layout
    display_manga_panels(scene_data.get("panel_images", []))

    # Narrative text
    narrative = scene_data.get("narrative_text", "")
    st.markdown(f"**Story:**\n\n{narrative}")

    # Dialogue blocks
    if dialogue := scene_data.get("dialogue"):
        st.markdown("**Dialogue:**")
        for line in dialogue:
            character = line.get("character", "Unknown")
            text = line.get("text", "")
            st.markdown(f"> **{character}:** {text}")

    st.markdown("---")

def display_manga_panels(panel_urls: List[str]) -> None:
    """
    Display five manga panels in responsive grid

    Args:
        panel_urls: Array of image URLs for manga panels
    """
    if len(panel_urls) != 5:
        st.warning(f"Expected 5 panels, received {len(panel_urls)}")
        return

    # Top row: 3 panels
    cols_top = st.columns(3)
    for i, col in enumerate(cols_top):
        with col:
            if i < len(panel_urls):
                st.image(
                    panel_urls[i],
                    use_column_width=True,
                    caption=f"Panel {i+1}"
                )

    # Bottom row: 2 panels
    cols_bottom = st.columns([1, 2, 1])
    with cols_bottom[1]:
        cols_inner = st.columns(2)
        for i, col in enumerate(cols_inner):
            with col:
                panel_idx = i + 3
                if panel_idx < len(panel_urls):
                    st.image(
                        panel_urls[panel_idx],
                        use_column_width=True,
                        caption=f"Panel {panel_idx+1}"
                    )
```

### User Input Handler

**Choice Selection Component:**

```python
import streamlit as st
from typing import Optional, List

def get_user_input(
    choice_prompt: str,
    preset_choices: List[str]
) -> Optional[str]:
    """
    Display choice prompt and get user input

    Args:
        choice_prompt: Question to display to user
        preset_choices: Array of 3 preset choice strings

    Returns:
        Selected choice text or None if no selection yet
    """
    st.markdown(f"### {choice_prompt}")

    # Track selection in session state
    if "pending_choice" not in st.session_state:
        st.session_state.pending_choice = None

    # Display preset choice buttons
    st.markdown("**Choose an option:**")

    cols = st.columns(len(preset_choices))
    for i, (col, choice) in enumerate(zip(cols, preset_choices)):
        with col:
            if st.button(
                choice,
                key=f"choice_{i}",
                use_container_width=True,
                type="primary"
            ):
                st.session_state.pending_choice = choice
                st.rerun()

    st.markdown("---")

    # Custom input option
    st.markdown("**Or type your own response:**")

    custom_input = st.text_area(
        "Custom response",
        placeholder="Type your own action or decision...",
        max_chars=200,
        key="custom_input_field",
        label_visibility="collapsed"
    )

    if st.button("Submit Custom Response", type="secondary"):
        if custom_input.strip():
            st.session_state.pending_choice = custom_input.strip()
            st.rerun()
        else:
            st.warning("Please enter a response before submitting")

    return st.session_state.pending_choice
```

---

## Payload Structures

### 1. Story Initialization Request

**Endpoint:** Planning Workflow webhook URL
**Method:** POST

```json
{
  "action": "initialize",
  "theme": "A detective solving supernatural crimes in rain-soaked Tokyo",
  "character": "A cynical former police officer with psychic abilities"
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "initialized",
  "message": "Story framework created",
  "character_profile": {
    "name": "Detective Kaito Nakamura",
    "age": 42,
    "appearance": "Weathered face, dark circles under eyes, traditional trench coat",
    "personality": "Cynical, intuitive, haunted by past cases",
    "abilities": "Psychic visions triggered by physical contact",
    "background": "Left police force after controversial supernatural case"
  }
}
```

### 2. Scene Generation Request

**Endpoint:** Planning Workflow webhook URL
**Method:** POST

```json
{
  "action": "generate_scene",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_choice": "Confront your partner about their deception",
  "scene_number": 2
}
```

**Response:**
```json
{
  "scene_number": 2,
  "background_description": "Dimly lit police interrogation room, flickering fluorescent lights",
  "narrative_text": "You didn't hesitate. The door slammed open before they could react. Your partner's eyes widened as you laid the evidence on the table—photos, witness statements, psychic impressions that couldn't be ignored. The room felt smaller with each passing second as the truth hung between you like a blade.",
  "dialogue": [
    {
      "character": "Detective Nakamura",
      "text": "I've been seeing the visions. Every crime scene, every victim—they all point to you."
    },
    {
      "character": "Partner",
      "text": "You don't understand what you're getting into. Some doors shouldn't be opened."
    }
  ],
  "panel_images": [
    "https://storage.example.com/panels/scene2-panel1.jpg",
    "https://storage.example.com/panels/scene2-panel2.jpg",
    "https://storage.example.com/panels/scene2-panel3.jpg",
    "https://storage.example.com/panels/scene2-panel4.jpg",
    "https://storage.example.com/panels/scene2-panel5.jpg"
  ],
  "choice_prompt": "Your partner stands up, hand moving toward their weapon. What do you do?",
  "choices": [
    "Use your psychic powers to predict their next move",
    "Draw your weapon and demand they stand down",
    "Try to reason with them about the victims who deserve justice"
  ],
  "is_final_scene": false
}
```

### 3. Final Scene Response

**Same request format, but response includes:**

```json
{
  "scene_number": 7,
  "background_description": "Tokyo rooftop at dawn, first light breaking through clouds",
  "narrative_text": "The case was closed, but at what cost? Your choices throughout this investigation—trusting your partner, following the supernatural leads, confronting the darkness within yourself—they had all led to this moment. The city stretched below you, oblivious to the forces that moved in its shadows. You were different now. Changed. The psychic visions had become clearer, more insistent. There would be other cases, other mysteries. But for now, you watched the sunrise and allowed yourself a moment of peace.",
  "dialogue": [
    {
      "character": "Detective Nakamura",
      "text": "Some endings aren't what you expect. But they're the ones you earn."
    }
  ],
  "panel_images": [
    "https://storage.example.com/panels/scene7-panel1.jpg",
    "https://storage.example.com/panels/scene7-panel2.jpg",
    "https://storage.example.com/panels/scene7-panel3.jpg",
    "https://storage.example.com/panels/scene7-panel4.jpg",
    "https://storage.example.com/panels/scene7-panel5.jpg"
  ],
  "is_final_scene": true,
  "referenced_choices": [
    "You trusted your partner despite the warnings",
    "You embraced your psychic abilities instead of fearing them"
  ]
}
```

---

## Environment Configuration

### .env File

```bash
# n8n Workflow URLs
PLANNING_WORKFLOW_URL=https://your-n8n-instance.com/webhook/planning-workflow
IMAGE_WORKFLOW_URL=https://your-n8n-instance.com/webhook/image-workflow

# Optional: API Keys if needed
N8N_API_KEY=your-api-key-here

# App Configuration
MAX_SCENES=7
SCENE_TIMEOUT=120
INIT_TIMEOUT=60
```

### config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Workflow URLs
    PLANNING_WORKFLOW_URL = os.getenv("PLANNING_WORKFLOW_URL")
    IMAGE_WORKFLOW_URL = os.getenv("IMAGE_WORKFLOW_URL")

    # API Configuration
    N8N_API_KEY = os.getenv("N8N_API_KEY")

    # App Settings
    MAX_SCENES = int(os.getenv("MAX_SCENES", 7))
    SCENE_TIMEOUT = int(os.getenv("SCENE_TIMEOUT", 120))
    INIT_TIMEOUT = int(os.getenv("INIT_TIMEOUT", 60))

    # Validation
    @classmethod
    def validate(cls):
        if not cls.PLANNING_WORKFLOW_URL:
            raise ValueError("PLANNING_WORKFLOW_URL not set in environment")
        return True

# Validate on import
Config.validate()
```

---

## Error Handling

### Required Error Scenarios

**1. Network/API Errors:**
```python
try:
    response = workflow_client.generate_scene(...)
except APIError as e:
    st.error(f"Failed to generate scene: {str(e)}")
    if st.button("Retry"):
        st.rerun()
    if st.button("Start New Story"):
        reset_session_state()
        st.rerun()
```

**2. Timeout Handling:**
```python
try:
    response = requests.post(url, json=payload, timeout=120)
except requests.exceptions.Timeout:
    st.error("Scene generation timed out. The AI is taking longer than expected.")
    # Offer retry or restart options
```

**3. Invalid Response Data:**
```python
if "panel_images" not in scene_data or len(scene_data["panel_images"]) != 5:
    st.warning("Scene generated with incomplete images. Displaying available content.")
    # Display narrative even if images are incomplete
```

**4. Session State Loss:**
```python
if not st.session_state.session_id and st.session_state.current_scene > 0:
    st.error("Session data lost. Please start a new story.")
    reset_session_state()
```

---

## UI/UX Guidelines

### Design Principles

1. **Dark Theme**: Noir manga aesthetic with dark backgrounds
2. **Clear Typography**: Readable fonts for narrative text
3. **Smooth Transitions**: Loading states between scenes
4. **Responsive Layout**: Works on desktop and mobile
5. **Visual Hierarchy**: Manga panels prominent, choices clear

### Recommended Styling

```python
# Custom CSS for manga aesthetic
st.markdown("""
<style>
    /* Dark theme overrides */
    .stApp {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }

    /* Manga panel container */
    .manga-panel {
        border: 2px solid #333;
        padding: 5px;
        background-color: #222;
        border-radius: 5px;
    }

    /* Choice buttons */
    .stButton > button {
        background-color: #2d2d2d;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 15px;
        font-size: 16px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #3d3d3d;
        border-color: #666;
    }

    /* Dialogue blocks */
    blockquote {
        border-left: 4px solid #666;
        padding-left: 15px;
        margin: 10px 0;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)
```

### Loading States

```python
def show_loading_scene(scene_number: int):
    """Display animated loading state"""
    with st.spinner(f"✨ Generating Scene {scene_number}..."):
        st.markdown("The AI is crafting your story...")
        st.markdown("- Planning narrative flow")
        st.markdown("- Creating manga panels")
        st.markdown("- Generating character dialogues")
```

---

## Testing Checklist

### Functional Testing

- [ ] Story initialization completes successfully
- [ ] All three preset choices trigger scene generation
- [ ] Custom text input triggers scene generation
- [ ] Scenes display all 5 manga panels correctly
- [ ] Narrative text displays properly
- [ ] Dialogue blocks render correctly
- [ ] Final scene shows no choices, only "New Story" button
- [ ] Session state persists across scenes
- [ ] Choice history tracked accurately

### Error Handling Testing

- [ ] Network timeout handled gracefully
- [ ] Invalid webhook URL shows clear error
- [ ] Missing image URLs don't crash app
- [ ] Malformed API response handled
- [ ] Session state recovery works

### UX Testing

- [ ] Loading states display during API calls
- [ ] Buttons disabled during processing
- [ ] Images load efficiently
- [ ] Layout responsive on mobile
- [ ] Text readable against dark background

---

## Development Priorities

### MVP Features (Must Have)

1. Story initialization screen with theme/character input
2. Scene display with panels, narrative, dialogue
3. Three preset choice buttons working
4. Custom text input working
5. Session state management
6. Basic error handling

### Enhanced Features (Should Have)

1. Loading animations and progress indicators
2. Choice history sidebar
3. Smooth transitions between scenes
4. Responsive grid layout for panels
5. Custom CSS styling for manga aesthetic

### Optional Features (Nice to Have)

1. Story export functionality
2. Decision tree visualization
3. Character profile display
4. Background music/sound effects
5. Social sharing capabilities

---

## Common Issues & Solutions

### Issue: Images Not Loading

**Symptom:** Panels show broken image icons
**Causes:**
- Image URLs not accessible from Streamlit server
- CORS restrictions
- Image generation failed in workflow

**Solutions:**
```python
# Add image loading error handling
try:
    st.image(panel_url, use_column_width=True)
except Exception as e:
    st.warning(f"Panel could not load: {str(e)}")
    st.image("https://via.placeholder.com/400x300?text=Panel+Loading+Error")
```

### Issue: Session State Reset

**Symptom:** Story progress lost on page refresh
**Causes:**
- Streamlit rerun clearing state
- Browser refresh

**Solutions:**
```python
# Warn user about refresh
st.sidebar.warning("⚠️ Don't refresh the page or you'll lose your story progress!")

# Consider adding persistence
import json

def save_session_to_local():
    session_data = {
        "session_id": st.session_state.session_id,
        "scene_history": st.session_state.scene_history,
        # ... other state
    }
    # Save to browser local storage via JavaScript component
```

### Issue: Long Generation Times

**Symptom:** Users wait too long for scenes
**Causes:**
- Image generation takes 15-20 seconds
- Sequential processing

**Solutions:**
```python
# Show detailed progress
progress_bar = st.progress(0)
status_text = st.empty()

status_text.text("Generating narrative... (1/3)")
progress_bar.progress(33)
# ... continue updating

# Consider streaming updates from backend
```

---

## Quick Start Commands

```bash
# Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your webhook URLs

# Run Streamlit app
streamlit run app.py

# Access at: http://localhost:8501
```

---

## Resources & References

**Streamlit Documentation:**
- Session State: https://docs.streamlit.io/library/api-reference/session-state
- Layout: https://docs.streamlit.io/library/api-reference/layout
- Images: https://docs.streamlit.io/library/api-reference/media/st.image

**HTTP Communication:**
- Requests library: https://requests.readthedocs.io/
- Webhook testing: https://webhook.site/

**Project Context:**
- Full PRD: `docs/PRD.md`
- n8n workflow documentation: TBD

---

## Notes for Claude Code

**Key Reminders:**

1. **All user inputs are treated equally** - Whether preset button or custom text, send as plain string to workflow
2. **Scene generation takes 15-20 seconds** - Always show loading states
3. **Five panels per scene** - Grid layout with 3 top, 2 bottom
4. **No authentication needed** - Direct webhook calls (for MVP)
5. **Session ID is crucial** - Always include in scene generation requests
6. **Final scene has no choices** - Check `is_final_scene` flag

**Common Pitfalls to Avoid:**

- Don't parse or validate user choice content - send as-is
- Don't assume image URLs are immediately available
- Don't skip error handling for network calls
- Don't lose session state between reruns
- Don't block UI during API calls without loading indicators

**Testing Tips:**

- Use mock API responses during development
- Test with very long user inputs
- Test network failure scenarios
- Verify mobile responsive layout
- Check choice history persists correctly

---

## Support

For questions about the overall architecture and n8n workflows, refer to the PRD at `docs/PRD.md`.

For Streamlit-specific issues, consult the official Streamlit documentation.

This is a hackathon project with a 6-hour build constraint - prioritize MVP features and focus on demonstrating the core user experience.
