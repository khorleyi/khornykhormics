import requests
import uuid
import time
import json

def submit_story(story, lead_character, supporting_characters):
    """
    Submit story and character data to initialize-story API.

    Args:
        story (str): The story text (user_prompt)
        lead_character (str): Lead character description
        supporting_characters (list): List of supporting character descriptions

    Returns:
        dict: Full API response from initialize-story endpoint
    """
    endpoint = "http://localhost:5678/webhook/initialize-story"

    # Generate unique session ID
    session_id = str(uuid.uuid4())

    # Build character_inputs array with lead character first
    character_inputs = [lead_character] + supporting_characters

    # Format payload according to API spec
    payload = {
        "user_prompt": story,
        "character_inputs": character_inputs,
        "session_id": session_id
    }

    try:
        # Increased timeout to 120 seconds for AI processing
        response = requests.post(endpoint, json=payload, timeout=120)
        response.raise_for_status()

        # Try to parse JSON and handle errors
        try:
            response_data = response.json()
        except json.JSONDecodeError as e: 
            raise Exception(f"API returned invalid JSON: {str(e)}\nResponse: {response.text[:200]}")


        return response_data
    except requests.exceptions.Timeout:
        raise Exception("Request timed out after 120 seconds. The workflow may need more time to process.")
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to the API. Please ensure n8n is running at http://localhost:5678")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"API returned an error: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")


def generate_scene(initialize_story_response):
    """
    Generate scene data by passing the full initialize-story response.

    Args:
        initialize_story_response (dict): Complete response from initialize-story endpoint

    Returns:
        dict: Scene data with panels, narrative, dialogue, and choices
    """

    endpoint = "http://localhost:5678/webhook/generate-scene"

    print("🔵 GENERATE-SCENE API CALL - REQUEST BODY (SENT TO API)")    
    print(f"\ninitialize_story_response: ")
    print(initialize_story_response)
    print("="*80 + "\n")

    # Pass entire initialize-story response as the payload
    payload = initialize_story_response

    # Console log the request body

    try:
        # Same timeout as initialize-story (120 seconds)
        response = requests.post(endpoint, json=payload, timeout=120)
        response.raise_for_status()

        # Try to parse JSON and handle errors
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            raise Exception(f"API returned invalid JSON: {str(e)}\nResponse: {response.text[:200]}")

        return response_data
    except requests.exceptions.Timeout:
        raise Exception("Scene generation timed out after 120 seconds. The workflow may need more time to process.")
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to the API. Please ensure n8n is running at http://localhost:5678")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"API returned an error: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")


def submit_final_answer(story_id, selected_choice, custom_answer):
    """
    Submit the final answer for panel 5.

    Args:
        story_id (str): Unique identifier for the story session
        selected_choice (str): The MCQ choice selected (or None)
        custom_answer (str): Custom open-ended answer (or None)

    Returns:
        dict: API response
    """
    # Placeholder endpoint
    # TODO: Replace with actual API endpoint
    endpoint = "https://api.placeholder.com/answer"

    payload = {
        "story_id": story_id,
        "selected_choice": selected_choice,
        "custom_answer": custom_answer
    }

    try:
        # Uncomment when real API is ready
        # response = requests.post(endpoint, json=payload)
        # response.raise_for_status()
        # return response.json()

        # Mock response
        time.sleep(0.5)
        return {
            "success": True,
            "message": "Answer submitted successfully!"
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
