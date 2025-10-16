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
            {"role": "system", "content": "You are a Python expert. Please help modify this code. Make sure to avoid indentation errors."},
            {"role": "user", "content": f"Original code:\n{original_code}\n\nUser request: {prompt}\n\nImportant: Do not include any of the original code in your response. Only provide the modified code."}
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
    ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '')

    # Extract code blocks using regex pattern
    code_pattern = r'```python(.*?)```'
    matches = re.findall(code_pattern, ai_response, re.DOTALL)

    if matches:
        # Clean up the first code block
        new_code = "\n".join([
            line.rstrip() 
            for line in matches[0].strip().split('\n')
        ])
    else:
        # Use entire response as fallback
        new_code = ai_response.strip()

    # Create new file with original name
    with open(file_path, 'w') as f:
        f.write(new_code)
    
    return True
