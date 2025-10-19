# AI Visual Novel Generator - Streamlit Frontend
A multi-page Streamlit application for creating interactive manga-style visual novels. Users input a story theme and characters, then make choices that dynamically shape the narrative across multiple scenes with AI-generated manga panels.

## Cursor Hackathon Aimed Track:
**Most creative use of Gemini 2.5 Flash Image (Nano Banana)** 🍌✨

#### Technology Stack 🛠️
Frontend:
Streamlit 🌊 - Interactive web interface with multi-page navigation
Python 3.13 🐍 - Core application logic
requests 📡 - HTTP client for webhook communication

AI/ML Services (via n8n workflows):
Google Gemini 2.5 Flash 🤖 - Advanced LLM for story planning, narrative generation, character development, and dialogue
Nano Banana 🍌⚡ - High-speed image generation API for creating manga-style panel artwork in parallel (5 panels per scene)
Agent-based architecture 🎭 - Specialized agents orchestrating characters, narrative, and visual generation

Tools/Backend/Orchestration:
n8n 🔄 - Workflow automation platform orchestrating AI agents
Webhooks 🪝 - RESTful API endpoints for story initialization and scene generation
Cursor ⌨️ - Main IDE for streamlit dev
Claude Code 🎯 - Main Dev AI Agent

---

## 🎯 Project Overview

### What We're Building

An **AI-powered interactive manga visual novel generator** that creates personalized, choice-driven stories in real-time. Users provide a story concept and character descriptions, then make decisions that dynamically shape the narrative. Each scene is brought to life with 5 AI-generated manga panels, creating an immersive visual storytelling experience.

**Key Innovation:** Unlike traditional visual novels with pre-written branching paths, our system generates entirely unique stories on-the-fly based on user choices, powered by AI language models and image generation.


### Architecture Overview

```
┌─────────────────┐
│  Streamlit UI   │  ← User inputs story theme & characters
│   (Frontend)    │
└────────┬────────┘
         │ HTTP POST
         ▼
┌─────────────────────────────────────────────────────┐
│              n8n Workflow Platform                  │
│  ┌──────────────────┐  ┌──────────────────────────┐ │
│  │ Initialize Story │  │   Generate Scene         │ │
│  │    Webhook       │  │      Webhook             │ │
│  └────────┬─────────┘  └──────────┬───────────────┘ │
│           │                       │                  │
│  ┌────────▼─────────────────┐  ┌─▼─────────────────┐│
│  │ Character Agent          │  │ Planning Agent    ││
│  │ (Gemini 2.5 Flash)       │  │ (Gemini 2.5 Flash)││
│  │ Story Framework          │  │ Narrative + Scenes││
│  └──────────────────────────┘  └─┬─────────────────┘│
│                                   │                  │
│                        ┌──────────▼────────────────┐ │
│                        │  Image Generation Agent  │ │
│                        │  (Nano Banana)           │ │
│                        │  5 panels in parallel    │ │
│                        └──────────────────────────┘ │
└─────────────────────────────────────────────────────┘
         │ JSON Response
         ▼
┌─────────────────┐
│  Streamlit UI   │  → Display panels, narrative, choices
│  (Scene Display)│  → User makes decision → Loop continues
└─────────────────┘
```

### How It Works

1. **Story Initialization**: User provides theme and character descriptions → n8n workflow triggers Gemini 2.5 Flash to create story framework with character profiles
2. **Scene Generation**: Gemini 2.5 Flash generates narrative text and scene descriptions → Nano Banana creates 5 manga panels in parallel (15-20 seconds total)
3. **User Choice**: At panel 5, user selects from 3 AI-generated preset options or writes custom response
4. **Dynamic Continuation**: User's choice is sent to Gemini 2.5 Flash → New scene generated with updated narrative adapting to the decision
5. **Adaptive Storytelling**: Each decision influences the story direction, character development, and visual content through Gemini's contextual understanding
6. **Multi-Scene Journey**: Process repeats for 7-10 scenes until Gemini determines a natural conclusion based on narrative arc

### Hackathon Context

**Built for:** AI/ML Hackathon
**Build Time:** ~6 hours
**Focus:** Rapid prototyping of AI-powered interactive storytelling with visual generation
**Innovation:** Real-time narrative branching with synchronized text and manga art generation
**AI Models:** Leveraging Google's latest Gemini 2.5 Flash for intelligent story generation + Nano Banana for high-speed parallel image generation
**Unique Approach:** Agent-based architecture orchestrated through n8n workflows for scalable AI coordination

---

## Project Structure

```
khornykhormics/
├── app.py                    # Main entry point and homepage
├── pages/
│   ├── 1_Input.py           # Story initialization and scene generation
│   └── 2_Results.py         # Interactive panel display with choices
├── utils/
│   ├── __init__.py
│   └── api.py               # n8n workflow API client
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Features

### Page 1: Story Input
**Sidebar Form:**
- Story theme text area (main concept/plot)
- Lead character description
- Supporting characters (up to 5, dynamically add/remove)
- Submit button

**Workflow:**
1. Validates all inputs
2. Calls `initialize-story` webhook to create story framework
3. Immediately calls `generate-scene` webhook to create first scene
4. Redirects to Results page with scene data

### Page 2: Interactive Results
**Panels 1-4:**
- Centered layout with manga panel image
- Narrative text overlay
- Navigation: Previous/Next buttons

**Panel 5 (Choice Panel):**
- Manga panel image and narrative text
- 3 preset choice buttons (horizontal layout)
- Custom text input option
- Submit button triggers next scene generation

**Scene Loop:**
- User selections are sent to `generate-scene` webhook
- New scene data (5 panels + narrative + choices) is returned
- Process repeats until story concludes

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the App

1. Make sure the virtual environment is activated:
```bash
source venv/bin/activate
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## API Integration

The app integrates with **n8n workflows** running locally on port 5678. Two webhooks are used:

### 1. Initialize Story Endpoint
**URL:** `http://localhost:5678/webhook/initialize-story`

**Request Payload:**
```json
{
  "user_prompt": "Story theme text",
  "character_inputs": [
    "Lead character description",
    "Supporting character 1",
    "Supporting character 2"
  ],
  "session_id": "unique-uuid"
}
```

**Response Structure:**
```json
{
  "session_id": "uuid",
  "user_prompt": "Story theme",
  "overall_story": "{...story framework JSON string...}",
  "characters": [...character objects...],
  "protagonist_name": "Character Name"
}
```

### 2. Generate Scene Endpoint
**URL:** `http://localhost:5678/webhook/generate-scene`

**Request Payload (First Call):**
```json
{
  "session_id": "uuid",
  "user_prompt": "Story theme",
  "overall_story": "{...story JSON string...}",
  "character_profile": [...characters...],
  "characters": [...characters...],
  "protagonist_name": "Character Name"
}
```

**Request Payload (Subsequent Calls):**
```json
{
  "session_id": "uuid",
  "user_prompt": "Story theme",
  "overall_story": "{...updated story JSON...}",
  "character_profile": [...characters...],
  "characters": [...characters...],
  "protagonist_name": "Character Name",
  "current_scene": 2,
  "decision_history": ["User's previous choice"],
  "decision_count": 1,
  "phase": "ready_for_scene_1",
  "story_phase": "opening",
  "is_complete": false
}
```

**Response Structure:**
```json
{
  "render_scene": {
    "panels": [
      "https://image-url-1.jpg",
      "https://image-url-2.jpg",
      "https://image-url-3.jpg",
      "https://image-url-4.jpg",
      "https://image-url-5.jpg"
    ],
    "narrative": [
      "Panel 1 narrative text",
      "Panel 2 narrative text",
      "Panel 3 narrative text",
      "Panel 4 narrative text",
      "Panel 5 narrative text"
    ],
    "dialogue": [],
    "choices": [
      {"choice_id": "A", "text": "Choice option 1"},
      {"choice_id": "B", "text": "Choice option 2"},
      {"choice_id": "C", "text": "Choice option 3"}
    ]
  },
  "session_data_to_save": {
    "overall_story": "{...updated story JSON...}",
    "decision_history": [...],
    "current_scene": 1,
    "decision_count": 0,
    "phase": "ready_for_scene_1",
    "story_phase": "opening",
    "is_complete": false
  }
}
```

### Prerequisites

**n8n must be running** with the story generation workflows active:
- Ensure n8n is accessible at `http://localhost:5678`
- Both webhook endpoints must be configured and active
- Image generation workflow should be integrated

To modify API endpoints, edit `utils/api.py`:
- Change endpoint URLs in `submit_story()` and `generate_scene()`
- Adjust timeout values if needed (default: 120 seconds)

## Usage Flow

### Starting a New Story
1. Navigate to **Input** page from sidebar
2. Enter story theme (e.g., "A detective solving supernatural crimes in Tokyo")
3. Describe lead character (e.g., "A cynical former police officer with psychic abilities")
4. Optionally add up to 5 supporting characters
5. Click **Submit**
   - App calls `initialize-story` to create story framework
   - Immediately calls `generate-scene` to create first scene
   - Redirects to Results page

### Navigating Through a Scene
1. View panels 1-4 sequentially using **Next/Previous** buttons
2. Each panel displays:
   - AI-generated manga panel image
   - Narrative text describing the scene
3. Progress to panel 5 (the choice panel)

### Making Choices (Panel 5)
1. View the final panel and narrative
2. Choose one of three preset options OR write a custom response
3. Click **Submit Answer**
   - App sends choice to `generate-scene` webhook
   - New scene is generated (5 new panels + narrative + choices)
   - Returns to panel 1 of the new scene
4. Repeat until story concludes

### Multi-Scene Story Progression
- Each user choice advances the story
- `decision_history` tracks all choices made
- `current_scene` increments with each submission
- Story data persists in session state throughout the experience

## Session State Management

The app maintains the following in `st.session_state`:

**Story Data:**
- `story_data`: Response from `initialize-story` (session_id, characters, etc.)
- `scene_data`: Current scene from `generate-scene` (panels, narrative, choices)

**Navigation:**
- `current_panel`: Which of the 5 panels is currently displayed (1-5)
- `selected_mcq`: User's selected choice ID on panel 5

**Input Form:**
- `supporting_characters`: Array of supporting character descriptions
- `pending_submission`: Temporary storage during API calls

**Important Notes:**
- Session state is cleared on browser refresh
- All data is ephemeral (not persisted to database)
- Each story session has a unique `session_id` (UUID)

## Technical Details

### Error Handling
The app handles several error scenarios:
- **Connection errors**: If n8n is not running
- **Timeout errors**: If workflows take >120 seconds
- **Invalid JSON**: If API returns malformed data
- **Missing scene data**: If user navigates to Results without submitting a story

All errors display user-friendly messages with retry/restart options.

### API Call Flow
```
User Input → submit_story() → initialize-story webhook
                                       ↓
                               [Story Framework]
                                       ↓
                            generate_scene() → generate-scene webhook
                                       ↓
                               [Scene Data: 5 panels + narrative + choices]
                                       ↓
                            Display panels 1-5
                                       ↓
                            User makes choice on panel 5
                                       ↓
                            generate_scene() → generate-scene webhook (with choice)
                                       ↓
                               [New Scene Data]
                                       ↓
                            Loop continues...
```

### Payload Management
- `overall_story` must be a JSON **string**, not an object
- `character_profile` and `characters` fields both included for compatibility
- `decision_history` is an array of plain text (not choice_ids)
- App logs all request payloads to console for debugging

## Development Notes

- Built with Streamlit's multi-page app structure
- Uses custom HTML/CSS for manga panel styling
- 120-second timeout accounts for AI image generation time
- Session ID generated client-side using `uuid.uuid4()`
- Minimum 5 supporting characters allowed (can be fewer)

### Why Gemini 2.5 Flash + Nano Banana?

**Gemini 2.5 Flash:**
- Fast response times (critical for interactive experience)
- Excellent contextual understanding for maintaining story coherence across scenes
- Strong creative writing capabilities for narrative generation
- Cost-effective for hackathon rapid prototyping
- Superior character consistency and dialogue generation

**Nano Banana:**
- High-speed parallel image generation (5 panels in ~15-20 seconds)
- Consistent manga/anime art style across panels
- API-based access (no complex model hosting required)
- Reliable uptime and performance for hackathon demos
- Cost-effective for generating multiple images per scene

## Troubleshooting

**"Could not connect to the API"**
- Check that n8n is running: `http://localhost:5678`
- Verify webhook endpoints are active in n8n workflows

**"Request timed out after 120 seconds"**
- Image generation may be taking longer than expected
- Check n8n workflow execution logs
- Consider increasing timeout in `utils/api.py`

**"No scene data found"**
- User navigated to Results page without submitting a story
- Click "Go to Input Page" button to start over

**Session state lost**
- Browser was refreshed (not supported)
- Use navigation buttons within the app instead

## Future Enhancements

- Add persistent storage (database) for story sessions
- Implement story export/download functionality
- Add decision tree visualization
- Support for story branching and multiple endings
- Background music and sound effects
- Social sharing capabilities
- Story resume from previous sessions
