import os
import re
import json
import uuid
import requests

def process_file_with_llm(api_key, file_path, prompt):
    # Create backup of original file
    backup_id = uuid.uuid4().hex[:6]
    backup_path = f"{file_path}_backup_{backup_id}"
    os.rename(file_path, backup_path)
    
    # Read original code
    with open(backup_path, 'r') as f:
        original_code = f.read()
    
    # Create API request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "<YOUR_SITE_URL>",
        "X-Title": "<YOUR_SITE_NAME>",
    }
    
    data = {
        "model": "x-ai/grok-2-1212",
        "messages": [
            {"role": "system", "content": "You are a Python expert. Please help modify this code."},
            {"role": "user", "content": f"Original code:\n{original_code}\n\nUser request: {prompt}"}
        ],
        "temperature": 0.3
    }
    
    # Send to LLM
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )
    
    if response.status_code != 200:
        print(f"API Error: {response.status_code} - {response.text}")
        os.rename(backup_path, file_path)  # Restore original
        return False
    
    # Process response
    result = response.json()
    ai_response = result['choices'][0]['message']['content']
    
    # Extract code blocks and comment non-code
    code_pattern = r'```python(.*?)```'
    matches = re.findall(code_pattern, ai_response, re.DOTALL)
    
    if matches:
        # Get the first code block and clean up
        new_code = "\n".join([
            line.strip() 
            for block in matches 
            for line in block.strip().split('\n')
        ])
    else:
        # Comment out everything if no code block found
        new_code = '\n'.join(f'# {line}' for line in ai_response.split('\n'))
    
    # Create new file with original name
    with open(file_path, 'w') as f:
        f.write(f"# Original backup: {backup_path}\n")
        f.write("# LLM Response (non-code comments):\n")
        f.write('\n'.join(f'# {line}' for line in ai_response.replace('```', '').split('\n')))
        f.write("\n\n# Generated code:\n")
        f.write(new_code)
    
    return True

def get_input_from_user():
    file_path = input("Please enter the file path of the Python program to revise: ").strip()
    if not os.path.exists(file_path):
        print(f"Error: File at {file_path} does not exist.")
        return None, None
    
    prompt = input("Please enter the modification prompt: ").strip()
    if not prompt:
        print("Error: Prompt cannot be empty.")
        return None, None
    
    return file_path, prompt

def read_api_key(api_key_path):
    try:
        with open(api_key_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"API key file not found at {api_key_path}")
        return None
    
def main():
    api_key_path = '/Applications/renpy-8.0.3-sdk/projects/LetterWriting/scripts/API.txt'
    
    # Read API key
    api_key = read_api_key(api_key_path)
    if not api_key:
        return
    
    # Get the file path and prompt from the user
    file_path, prompt = get_input_from_user()
    if not file_path or not prompt:
        return
    
    print(f"Processing {file_path}...")
    success = process_file_with_llm(api_key, file_path, prompt)
    
    if success:
        print(f"Successfully updated {file_path}")
        print(f"Original file backed up with random suffix")
    else:
        print("Processing failed - original file restored")

if __name__ == "__main__":
    main()
