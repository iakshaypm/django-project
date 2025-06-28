import os


def get_file_language(file_path):
    """
    Detect programming language based on file extension or filename.

    Parameters:
    - file_path (str): Path to the file

    Returns:
    - str: Detected programming language for syntax highlighting
    """
    # First, handle special filenames
    filename = os.path.basename(file_path).lower()

    # Handle Dockerfiles
    if filename in ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
        return 'dockerfile'

    # Handle environment files
    if filename.startswith('.env') or filename.endswith('.env'):
        return 'dotenv'

    # Standard extension mapping
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'jsx',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.go': 'go',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.rs': 'rust',
        '.html': 'html',
        '.css': 'css',
        '.sql': 'sql',
        '.sh': 'bash',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.json': 'json',
        '.md': 'markdown',
        '.xml': 'xml',
        '.env': 'dotenv',
        '.conf': 'plaintext',
        '.ini': 'ini',
        '.toml': 'toml',
        '.dockerfile': 'dockerfile',
    }

    # Get the file extension
    _, ext = os.path.splitext(file_path.lower())

    # Special case for files like .env.development, .env.production, etc.
    if '.env.' in filename:
        return 'dotenv'

    # Return the mapped language or default to plaintext
    return extension_map.get(ext, 'plaintext')


def set_note_template(line_no, data, file_path=None):
    """
    Function to format the response from the model with enhanced output.

    Parameters:
    - line_no (int): The line number of the issue
    - data (dict): The input data containing comments and related information
    - file_path (str, optional): Path to the file being reviewed, used for language detection

    Returns:
    - markdown (str): The formatted markdown response
    - line_number (int): The line number of the last error found
    """
    # If no data or no issues, return empty
    if data is None or not any(data.get(key) for key in ['issue', 'review', 'suggestion', 'code']):
        return "", line_no

    # Prepare markdown with a more structured format
    markdown = ""

    # File context (if file path is provided)
    if file_path:
        language = get_file_language(file_path)

    # Issue section with emoji and prominence
    if issue := data.get('issue'):
        markdown += f"🔍 **Issue Identified**\n\n{issue}\n\n"

    # Detailed review section
    if review := data.get('review'):
        markdown += f"📝 **Detailed Review**\n\n{review}\n\n"

    # Suggestion section with checkmark
    if suggestion := data.get('suggestion'):
        markdown += f"✅ **Suggested Improvement**\n\n{suggestion}\n\n"

    # Code resolution with syntax highlighting
    if code := data.get('code'):
        # Detect language if file_path is provided, otherwise default to python
        language = get_file_language(file_path) if file_path else 'python'
        markdown += f"💡 **Resolved Code**\n```{language}\n{code}\n```\n"

    return markdown, line_no


def blank_file_note_format(file_path):
    """
    Generates a note for a blank file.

    Parameters:
    - file_path (str): The path to the file.

    Returns:
    - note (str): A formatted note indicating the file has no content.
    """
    note = '\n\n'
    note += f"### 📄 File Analysis\n\n"
    note += f"**File Path**: `{file_path}`\n\n"
    note += "🚫 **Status**: This file does not have any content.\n\n"
    return note