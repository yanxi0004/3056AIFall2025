import os
import requests
import json
from PyPDF2 import PdfReader

def read_api_key():
    api_path = "/Applications/renpy-8.0.3-sdk/projects/LetterWriting/scripts/API.txt"
    try:
        with open(api_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"API key file not found at {api_path}")
        return None

def pdf_to_text(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def process_pdf(api_key, pdf_path, md_path):
    text = pdf_to_text(pdf_path)
    if not text.strip():
        print(f"Warning: No text extracted from {pdf_path}")
        return False
    
    prompt = f"""Convert this PDF content into markdown format. Keep the structure similar to the original document. 
At the end, add a '## Summary and Action Items' section with: 
1. A brief summary of the document
2. Clear actionable steps a new candidate can take based on the information
Here's the PDF content:\n\n{text}"""

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "x-ai/grok-beta",
                "messages": [{"role": "user", "content": prompt}]
            })
        )

        if response.status_code == 200:
            result = response.json()
            md_content = result['choices'][0]['message']['content']
            
            with open(md_path, 'w') as f:
                f.write(md_content)
            return True
        else:
            print(f"API Error ({response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return False

def main():
    api_key = read_api_key()
    if not api_key:
        return

    pdf_dir = "/Applications/renpy-8.0.3-sdk/projects/LetterWriting/JREinfo/Re_ request info about JRE"
    posts_dir = pdf_dir  # Save MD files in same directory
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("No PDF files found in directory")
        return

    total = len(pdf_files)
    processed = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        md_file = os.path.splitext(pdf_file)[0] + ".md"
        md_path = os.path.join(posts_dir, md_file)
        
        print(f"Processing file {i}/{total}: {pdf_file}...", end=' ', flush=True)
        
        if process_pdf(api_key, pdf_path, md_path):
            print("✅")
        else:
            print("❌")
        
        processed += 1
        
        if processed % 10 == 0 and i != total:
            print(f"\nProcessed {processed} files. Continue?")
            choice = input("Enter 'y' to continue, any other key to exit: ").strip().lower()
            if choice != 'y':
                print("Exiting...")
                break

    print(f"\nProcessing complete. Total files processed: {processed}/{total}")

if __name__ == "__main__":
    main()
