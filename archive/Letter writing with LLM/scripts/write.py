# https://grok.com/share/bGVnYWN5_9c095662-912b-4ea9-a0a6-847a77d8d1c8 

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
    'draft': 'draft.md'
}
WRAP_WIDTH = 80

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
    
    # Construct prompt without f-string backslash issues
    prompt = f"**Writing Task {task_type}**\n\n"
    prompt += "Contextual Information:\n"
    prompt += f"{context}\n\n"
    prompt += "Genre Requirements:\n"
    prompt += f"{genre}\n\n"
    prompt += "Author Instructions:\n"
    prompt += f"{instructions}\n\n"
    prompt += "Please provide your response in this exact format with clear section headings:\n"
    prompt += "# Outline\n"
    prompt += "[Your outline here]\n\n"
    prompt += "# Drafting Process\n"
    prompt += "[Your explanation of reasoning and process here]\n\n"
    prompt += "# Draft\n"
    prompt += "[Your complete draft here in paragraph form with minimal subheadings, strictly following the outline provided above]\n\n"
    prompt += "# Questions\n"
    prompt += "[Three thought-provoking questions, one per line]\n\n"
    
    if task_type == "REVISE":
        prompt += "Revise the following draft according to the specifications:\n"
        prompt += "Current Draft Version:\n"
        prompt += f"{existing_draft}"
    else:
        prompt += "Create a new draft according to the specifications:"

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "x-ai/grok-beta",
                "messages": [{"role": "user", "content": prompt}],
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

def extract_sections(response_content):
    sections = {'outline': '', 'process': '', 'draft': '', 'questions': []}
    current_section = None
    lines = response_content.split('\n')
    
    for line in lines:
        if line.strip() == '# Outline':
            current_section = 'outline'
        elif line.strip() == '# Drafting Process':
            current_section = 'process'
        elif line.strip() == '# Draft':
            current_section = 'draft'
        elif line.strip() == '# Questions':
            current_section = 'questions'
        elif current_section and line.strip():
            if current_section == 'questions':
                if len(sections['questions']) < 3:
                    sections['questions'].append(line.strip())
            else:
                sections[current_section] += line.strip() + '\n'
    
    return sections

def update_instructions_file(questions):
    instructions_path = os.path.join(DRAFT_DIR, FILES['instructions'])
    try:
        with open(instructions_path, 'r') as f:
            existing_content = f.read().strip()
        
        new_content = "\n\n".join(questions) + "\n\n" + existing_content
        with open(instructions_path, 'w') as f:
            f.write(new_content)
        print("Successfully updated Instructions.txt with new questions")
    except Exception as e:
        print(f"Failed to update Instructions.txt: {str(e)}")

def update_draft_file(sections, existing_content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_content = f"# Revised Version ({timestamp})\n\n"
    new_content += "# Outline\n\n" + textwrap.fill(sections['outline'].strip(), width=WRAP_WIDTH) + "\n\n"
    new_content += "# Drafting Process\n\n" + textwrap.fill(sections['process'].strip(), width=WRAP_WIDTH) + "\n\n"
    new_content += "# Draft\n\n" + textwrap.fill(sections['draft'].strip(), width=WRAP_WIDTH) + "\n\n"
    
    if existing_content:
        new_content += "# Previous Versions\n\n" + existing_content
    
    return new_content

def main():
    for fname in FILES.values():
        if not os.path.exists(os.path.join(DRAFT_DIR, fname)):
            print(f"Missing required file: {fname}")
            return
    
    api_key = read_api_key()
    if not api_key:
        return

    context = read_file_content(FILES['context'])
    genre = read_file_content(FILES['genre'])
    instructions = read_file_content(FILES['instructions'])
    existing_draft = read_file_content(FILES['draft']) or ""

    if None in [context, genre, instructions]:
        return

    print(f"Processing {'revision' if existing_draft else 'new draft'}...")
    response_content = process_draft(api_key, context, genre, instructions, existing_draft)
    
    if not response_content:
        print("Processing failed")
        return

    sections = extract_sections(response_content)
    if sections['questions']:
        update_instructions_file(sections['questions'])

    draft_path = os.path.join(DRAFT_DIR, FILES['draft'])
    updated_content = update_draft_file(sections, existing_draft)
    
    with open(draft_path, 'w') as f:
        f.write(updated_content)
    
    draft_word_count = count_words(sections['draft'])
    print(f"\nSuccessfully updated draft at:\n{draft_path}")
    print(f"Draft Word Count: {draft_word_count}")

if __name__ == "__main__":
    main()