import os
import glob

def generate_architecture_docs():
    """Generate architecture documentation for the root directory."""

    # Define paths - we're running from the root directory
    root_path = os.getcwd()
    output_file = os.path.join(root_path, "ROOT_ARCHITECTURE.md")

    # Folders to skip
    skip_folders = {
        '.claude', '.qwen', '.specify', '.venv',
        'backend', 'docs', 'full-stack-todo',
        'history', 'specs', 'src', 'tests'
    }

    # Start the markdown file with UTF-8 encoding
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Root Directory Architecture\n\n")
        f.write("## Directory Structure\n")
        f.write("```\n")

        # Write directory listing
        f.write(f" Directory of {root_path}\n\n")

        # Get all items in the root directory
        all_items = os.listdir(root_path)
        directories = []
        files = []

        for item in all_items:
            item_path = os.path.join(root_path, item)
            if os.path.isdir(item_path) and item not in skip_folders:
                directories.append(item)
            elif os.path.isfile(item_path):
                # Only include non-md files
                if not item.lower().endswith('.md'):
                    files.append(item)

        # Write directories first
        for directory in sorted(directories):
            f.write(f"{directory}/\n")

        # Then write files
        for file in sorted(files):
            f.write(f"{file}\n")

        f.write("```\n\n")

        # Find all relevant root-level files (excluding skipped folders)
        file_patterns = ["*.py", "*.md", "*.txt", "*.json", "*.yaml", "*.yml", "*.toml", "*.lock"]

        for pattern in file_patterns:
            matched_files = []
            for file_path in glob.glob(os.path.join(root_path, pattern)):
                filename = os.path.basename(file_path)
                if os.path.isfile(file_path) and filename not in skip_folders:
                    matched_files.append(file_path)

            # Write content of each file
            for file_path in sorted(matched_files):
                # Get relative path for the header
                rel_path = os.path.relpath(file_path, root_path)

                # Skip certain files that might cause issues
                if not any(skip_dir in file_path for skip_dir in skip_folders):
                    # Determine file extension for syntax highlighting
                    ext = os.path.splitext(file_path)[1].lower()
                    lang_map = {
                        '.py': 'python',
                        '.md': 'markdown',
                        '.txt': 'text',
                        '.json': 'json',
                        '.yaml': 'yaml',
                        '.yml': 'yaml',
                        '.toml': 'toml',
                        '.lock': 'text'
                    }

                    language = lang_map.get(ext, 'text')  # Default to 'text' if extension not in map

                    f.write(f"## {rel_path}\n")
                    f.write(f"```{language}\n")

                    try:
                        # Read the file with UTF-8 encoding
                        with open(file_path, 'r', encoding='utf-8') as source_file:
                            content = source_file.read()
                            f.write(content)
                    except Exception as e:
                        f.write(f"# Error reading file: {str(e)}\n")

                    f.write("\n```\n\n")

    print("Root architecture documentation generated successfully in ROOT_ARCHITECTURE.md")

if __name__ == "__main__":
    generate_architecture_docs()