import os
import requests
import json
import logging

# Configuration
MD_DIR = "/Applications/renpy-8.0.3-sdk/projects/LetterWriting/JREinfo/Re_ request info about JRE"
API_KEY_PATH = "/Applications/renpy-8.0.3-sdk/projects/LetterWriting/scripts/API.txt"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_api_key():
    """
    Read the API key from the specified file path.
    
    Returns:
    str: The API key if found, None otherwise.
    """
    try:
        with open(API_KEY_PATH, 'r') as f:
            api_key = f.read().strip()
            if not api_key:
                logger.error(f"API key file at {API_KEY_PATH} is empty")
                return None
            return api_key
    except FileNotFoundError:
        logger.error(f"API key file not found at {API_KEY_PATH}")
        return None
    except IOError as e:
        logger.error(f"Error reading API key file: {str(e)}")
        return None

def extract_summary(md_content):
    """
    Extract the summary from the markdown content.
    
    Args:
    md_content (str): The content of the markdown file.
    
    Returns:
    str: The extracted summary, or an empty string if not found.
    """
    start_marker = "## Summary and Action Items"
    sections = md_content.split(start_marker)
    if len(sections) > 1:
        return sections[1].strip().replace('\n', ' ')
    return ""

def process_files(api_key, files):
    """
    Process the files using the LLM API.
    
    Args:
    api_key (str): The API key for authentication.
    files (list): List of dictionaries containing file information.
    
    Returns:
    str: The processed result from the LLM, or None if an error occurred.
    """
    prompt = """Analyze these documents and group them by their content similarity.
For each document:
1. List the file name
2. Keep the summary exactly as provided
3. Assign a descriptive group name (2-3 words) for documents that belong together

Format each entry exactly like this:
[FILE_NAME]
Summary: [EXACT_SUMMARY_TEXT]
Group: [GROUP_NAME]

Separate entries with a blank line. Only use the format above.

After the grouped entries, provide a synthesis of the files. Focus on one group per paragraph, discussing the files within that group, referencing their file names, and synthesizing their content. Each paragraph should start with the group name in bold, followed by a colon and a space. The synthesis should be 1-2 paragraphs per group, depending on the number of files in the group."""

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
        else:
            logger.error(f"API Error ({response.status_code}): {response.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return None

def main():
    """
    Main function to process markdown files and generate grouped summaries.
    """
    # Get API key
    api_key = read_api_key()
    if not api_key:
        return

    # Find markdown files
    files = []
    for fname in os.listdir(MD_DIR):
        if fname.lower().endswith('.md'):
            path = os.path.join(MD_DIR, fname)
            try:
                with open(path, 'r') as f:
                    content = f.read()
                summary = extract_summary(content)
                if summary:
                    files.append({'file': fname, 'summary': summary})
            except IOError as e:
                logger.warning(f"Error reading file {fname}: {str(e)}")

    if not files:
        logger.info("No markdown files with summaries found")
        return

    logger.info(f"Processing {len(files)} files...")

    # Process through LLM
    result = process_files(api_key, files)

    if result:
        output_file = os.path.join(MD_DIR, "grouped_files_with_synthesis.txt")
        try:
            with open(output_file, 'w') as f:
                f.write(result)
            logger.info(f"Results saved to {output_file}")
            logger.info("\nExample output format:\n")
            logger.info("filename1.md\nSummary: ...\nGroup: Technical Requirements\n")
            logger.info("\n**Technical Requirements**: This group includes files like 'requirements.md' and 'specs.md'. These files discuss the technical specifications needed for the project, including hardware requirements, software dependencies, and performance benchmarks. The synthesis of these files suggests that the project requires high-performance computing resources and specific software libraries to meet its goals.")
        except IOError as e:
            logger.error(f"Error writing to output file: {str(e)}")
    else:
        logger.error("Processing failed")

if __name__ == "__main__":
    main()
