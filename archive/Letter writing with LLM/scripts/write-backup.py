import os
import requests
import json
from datetime import datetime
import textwrap

# Configuration
API_KEY_PATH = "/Applications/renpy-8.0.3-sdk/projects/LetterWriting/scripts/API.txt"
DRAFT_DIR = "/Applications/renpy-8.0.3-sdk/projects/LetterWriting/drafts"
FILES = {
    'context': 'context.txt',
    'genre': 'genre.txt',
    'instructions': 'Instructions.txt',
    'draft': 'draft.txt'
}
WRAP_WIDTH = 80  # Set the desired line width for wrapping

def read_api_key():
    try:
        with open(API_KEY_PATH, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"API key file not found at {API_KEY_PATH}")
        return None

def read_file_content(filename):
    path = os.path.join(DRAFT_DIR, filename)
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Missing required file: {filename}")
        return None

def count_words(text):
    return len(text.split())

def process_draft(api_key, context, genre, instructions, existing_draft):
    task_type = "REVISE" if existing_draft else "GENERATE"
    
    prompt = f"""**Writing Task {task_type}**

Contextual Information:
{context}

Genre Requirements:
{genre}

Author Instructions:
{instructions}"""

    if task_type == "REVISE":
        prompt += f"\n\nCurrent Draft Version:\n{existing_draft}\n\nPlease revise this draft according to the above specifications."
    else:
        prompt += "\n\nPlease create a new draft according to the specifications."

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "x-ai/grok-beta",
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "temperature": 0.7,
                "max_tokens": 2000
            })
        )

        if response.status_code == 200:
            print("Draft processing complete with status: Success 🚀")
            return response.json()['choices'][0]['message']['content']
        print(f"API Error ({response.status_code}): {response.text}")
        return None
    except Exception as e:
        print(f"API request failed: {str(e)}")
        return None

def update_draft_file(new_content, existing_content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    version_header = f"=== Revised Version ({timestamp}) ===\n"
    
    if existing_content:
        version_history = f"\n\n\n=== Previous Versions ===\n{existing_content}"
    else:
        version_history = ""

    # Wrap the text
    wrapped_new_content = textwrap.fill(new_content, width=WRAP_WIDTH)
    wrapped_version_history = textwrap.fill(existing_content, width=WRAP_WIDTH)

    return f"{version_header}{wrapped_new_content}{version_history}"

def main():
    # Verify all files exist
    for fname in FILES.values():
        if not os.path.exists(os.path.join(DRAFT_DIR, fname)):
            print(f"Missing required file: {fname}")
            return
    
    # Read API key
    api_key = read_api_key()
    if not api_key:
        return

    # Read all files
    context = read_file_content(FILES['context'])
    genre = read_file_content(FILES['genre'])
    instructions = read_file_content(FILES['instructions'])
    existing_draft = read_file_content(FILES['draft']) or ""

    if None in [context, genre, instructions]:
        return

    # Process draft
    print(f"Processing {'revision' if existing_draft else 'new draft'}...")
    new_content = process_draft(api_key, context, genre, instructions, existing_draft)
    
    if not new_content:
        print("Processing failed")
        return

    # Update draft file
    draft_path = os.path.join(DRAFT_DIR, FILES['draft'])
    updated_content = update_draft_file(new_content, existing_draft)
    
    with open(draft_path, 'w') as f:
        f.write(updated_content)
    
    # Display draft statistics
    word_count = count_words(updated_content)
    print(f"\nSuccessfully updated draft at:\n{draft_path}")
    print(f"Word Count: {word_count}")

if __name__ == "__main__":
    main()
