import json
import os
from pathlib import Path

def load_config():
    """Load configuration from setting.json file."""
    config_path = Path(__file__).parent / 'setting.json'
    with open(config_path, 'r') as f:
        return json.load(f)


def get_markdown_files(directory, config):
    """Get all markdown files in the specified directory."""
    base_dir = Path(__file__).parent
    files = []
    exclude_files = config.get("exclude_files", [])
    
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.endswith('.md') or filename.startswith('.'):
                continue
                
            file_path = os.path.join(root, filename)
            
            # Convert to relative path for comparison with exclude_files
            rel_path = os.path.relpath(file_path, base_dir)
            
            # Check if the file should be excluded
            if rel_path not in exclude_files:
                files.append(file_path)
    
    return files


def get_display_name(key, align_config):
    """Get display name from alignment config or use the key itself."""
    return align_config.get(key, key)


def process_directory(dir_name, base_dir, config):
    """Process a directory and generate markdown content for its files."""
    dir_path = base_dir / dir_name
    if not dir_path.exists():
        print(f"Directory {dir_name} does not exist. Skipping.")
        return ""

    # Create section header
    display_name = get_display_name(dir_name, config.get("align", {}))
    content = f"## {display_name}\n\n"
    
    # Add links to all markdown files
    nav_page_path = base_dir / 'nav_page.md'
    files = get_markdown_files(str(dir_path), config)
    
    for file_path in files:
        file_path = Path(file_path)
        if file_path != nav_page_path:
            file_name = file_path.name
            name_without_ext = file_name.replace(".md", "")
            display_name = get_display_name(name_without_ext, config.get("align", {}))
            content += f"- [{display_name}]({config['base_url'] + file_name})\n"
            
    return content


def generate_navigation_page():
    config = load_config()
    base_dir = Path(__file__).parent
    config["tmp"] = base_dir
    
    print("Using config:", config)
    
    # Start with title if provided
    nav_content = f"# {config['title']}\n\n" if config.get("title") else ""
    
    # Process directories based on configuration
    if not config.get("section") or len(config["section"]) == 0:
        # Auto-discover directories
        for item in base_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                nav_content += process_directory(item.name, base_dir, config)
    else:
        # Use ordered list of directories
        for dir_name in config["section"]:
            nav_content += process_directory(dir_name, base_dir, config)
    
    # Write the navigation page
    with open(base_dir / 'nav_page.md', 'w') as f:
        f.write(nav_content)

    print("Navigation page generated successfully.")
    print("After you host the page, please visit: \n", config["base_url"])

if __name__ == "__main__":
    generate_navigation_page()
