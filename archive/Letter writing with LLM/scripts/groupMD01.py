import os
import requests
import json

# Configuration
MD_DIR = "/Applications/renpy-8.0.3-sdk/projects/LetterWriting/JREinfo/Re_ request info about JRE"
API_KEY_PATH = "/Applications/renpy-8.0.3-sdk/projects/LetterWriting/scripts/API.txt"

def read_api_key():
    try:
        with open(API_KEY_PATH, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"API key file not found at {API_KEY_PATH}")
        return None

def extract_summary(md_content):
    start_marker = "## Summary and Action Items"
    sections = md_content.split(start_marker)
    if len(sections) > 1:
        return sections[1].strip().replace('\n', ' ')
    return ""

def process_files(api_key, files):
    prompt = """Analyze these documents and group them by their content similarity. 
For each document:
1. List the file name
2. Keep the summary exactly as provided
3. Assign a descriptive group name (2-3 words) for documents that belong together

Format each entry exactly like this:
[FILE_NAME]
Summary: [EXACT_SUMMARY_TEXT]
Group: [GROUP_NAME]

Separate entries with a blank line. Only use the format above."""

    documents = "\n\n".join([f"Document {i}:\nFilename: {f['file']}\nSummary: {f['summary']}" 
                           for i, f in enumerate(files, 1)])

    full_prompt = f"{prompt}\n\nDocuments to analyze:\n\n{documents}"

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
                    "content": full_prompt
                }],
                "temperature": 0.3  # More deterministic output
            })
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        print(f"API Error ({response.status_code}): {response.text}")
        return None
    except Exception as e:
        print(f"API request failed: {str(e)}")
        return None

def main():
    # Get API key
    api_key = read_api_key()
    if not api_key:
        return

    # Find markdown files
    files = []
    for fname in os.listdir(MD_DIR):
        if fname.lower().endswith('.md'):
            path = os.path.join(MD_DIR, fname)
            with open(path, 'r') as f:
                content = f.read()
            summary = extract_summary(content)
            if summary:
                files.append({'file': fname, 'summary': summary})
    
    if not files:
        print("No markdown files with summaries found")
        return

    print(f"Processing {len(files)} files...")
    
    # Process through LLM
    result = process_files(api_key, files)
    
    if result:
        output_file = os.path.join(MD_DIR, "grouped_files.txt")
        with open(output_file, 'w') as f:
            f.write(result)
        print(f"Results saved to {output_file}")
        print("\nExample output format:\n")
        print("filename1.md\nSummary: ...\nGroup: Technical Requirements\n")
    else:
        print("Processing failed")

if __name__ == "__main__":
    main()
