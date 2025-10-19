# Story Creator - Streamlit App

A multi-page Streamlit application for creating interactive stories with character input and sequential panel display.

## Project Structure

```
khornykhormics/
├── app.py                    # Main entry point
├── pages/
│   ├── 1_Input.py           # Story input screen (sidebar form)
│   └── 2_Results.py         # Sequential panel display screen
├── utils/
│   ├── __init__.py
│   └── api.py               # API helper functions (placeholder endpoints)
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Features

### Screen 1: Input Page
- **Sidebar form** with:
  - Story text area
  - Lead character description
  - Supporting characters (up to 5, dynamically add/remove)
  - Submit button
- **Main area**: Empty description section (placeholder)
- Validates inputs and makes POST API call on submit

### Screen 2: Results Page
- Displays 5 panels sequentially (one at a time)
- **Panels 1-4**: Left layout with background image and text
- **Panel 5**: Right layout with:
  - Background image and text
  - 3 MCQ choice buttons (horizontal)
  - Open-ended text input
  - Submit button
- Navigation: Next/Previous buttons to move between panels

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

Currently using **placeholder API endpoints** with mock responses for testing.

### To integrate real APIs:

1. Open `utils/api.py`
2. Replace placeholder endpoints in:
   - `submit_story()` - Story submission endpoint
   - `submit_final_answer()` - Final answer submission endpoint
3. Uncomment the actual API call code
4. Comment out the mock response code

## Usage Flow

1. Navigate to **Input** page from sidebar
2. Fill in story and character details
3. Click **Submit** to process story
4. View panels 1-4 sequentially using Next/Previous buttons
5. On panel 5, select an MCQ choice or write custom ending
6. Click **Submit Answer** to finalize

## Notes

- Maximum 5 supporting characters allowed
- Session state persists data between pages
- Mock API responses include placeholder images and text
- All styling uses Streamlit native components and custom HTML/CSS

## Future Enhancements

- Connect to actual API endpoints
- Add background images upload functionality
- Implement story ID tracking
- Add progress indicators
- Export/save story results
