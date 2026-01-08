import os
import glob

def generate_architecture_docs():
    """Generate architecture documentation for the backend."""

    # Define paths - we're running from the backend directory
    backend_path = os.path.join(os.getcwd(), "backend")
    output_file = os.path.join(backend_path, "BACKEND_ARCHITECTURE.md")

    # Start the markdown file with UTF-8 encoding
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("## Directory Structure\n")
        f.write("```\n")

        # Write directory listing
        f.write(f" Directory of {backend_path}\n\n")

        # Get all items in the backend directory
        all_items = os.listdir(backend_path)
        directories = []
        files = []

        for item in all_items:
            item_path = os.path.join(backend_path, item)
            if os.path.isdir(item_path):
                directories.append(item)
            else:
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

        # Find all Python files in the backend directory recursively
        py_files = glob.glob(os.path.join(backend_path, "**", "*.py"), recursive=True)

        # Write content of each Python file
        for py_file in sorted(py_files):
            # Get relative path for the header
            rel_path = os.path.relpath(py_file, backend_path)

            # Skip __pycache__ directories
            if "__pycache__" not in py_file:
                f.write(f"# {rel_path}\n")
                f.write("```python\n")

                try:
                    # Read the file with UTF-8 encoding
                    with open(py_file, 'r', encoding='utf-8') as source_file:
                        content = source_file.read()
                        f.write(content)
                except Exception as e:
                    f.write(f"# Error reading file: {str(e)}\n")

                f.write("\n```\n\n")

    print("Backend architecture documentation generated successfully in BACKEND_ARCHITECTURE.md")

if __name__ == "__main__":
    generate_architecture_docs()