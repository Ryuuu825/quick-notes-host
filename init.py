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
        # Convert to relative path for comparison with exclude_files
        rel_path = os.path.relpath(file_path, base_dir)
        if file_path != nav_page_path:
            file_name = file_path.name
            name_without_ext = file_name.replace(".md", "")
            display_name = get_display_name(name_without_ext, config.get("align", {}))
            if config.get("ignore_dir_name", False):
                content += f"- [{display_name}]({config['hosting_url']}/?md={file_name})\n"
            else:
                content += f"- [{display_name}]({config['hosting_url']}?md={rel_path})\n"
            
    return content


def generate_navigation_page():
    config = load_config()
    base_dir = Path(__file__).parent
    config["tmp"] = base_dir
    config["hosting_url"] = config["base_url"]
    if "githubusercontent" in config["hosting_url"]:
        config["hosting_url"] = f"https://{config['base_url'].split('/')[3]}.github.io/{config['base_url'].split('/')[4]}"
    
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
    html_content = """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Markdown Previewer</title>
        <!-- preview your markdown with provided link -->
    <body>
        <!-- Include markdown-it from CDN -->
        <script src="https://cdn.jsdelivr.net/npm/markdown-it@13.0.1/dist/markdown-it.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pako/2.0.4/pako.min.js"></script>
        
        <div id="markdown-output" style="width: 100vw;"></div>

        <script>
            // Initialize markdown-it
            const md = window.markdownit();

            // Function to convert markdown to HTML
            function convertMarkdownToHTML(markdown) {
                return md.render(markdown);
            }

            // Function to handle the conversion and display
            function handleConversion(markdownFileLink) {
                // fetch the markdown file from the provided link
                // if the link is in query string format, decode it
                fetch(markdownFileLink)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.text();
                    })
                    .then(markdown => {
                        // Convert markdown to HTML
                        const html = convertMarkdownToHTML(markdown);
                        // Display the HTML in the output div
                        document.getElementById('markdown-output').innerHTML = html;
                    })
                    .catch(error => {
                        document.getElementById('markdown-output').innerHTML = `<p>Error: ${error.message}</p>`;
                        console.error('There was a problem with the fetch operation:', error);
                    });
            }
            // Event listeners for buttons
            if (window.location.search) {
                const urlParams = new URLSearchParams(window.location.search);
                const markdownFileLink = decodeURIComponent(urlParams.get('md'));
                handleConversion(markdownFileLink);
            }

        </script>


    </body>
</html>
"""
    with open(base_dir / 'index.html', 'w') as f:
        f.write(html_content)

    print("Navigation page generated successfully.")
    print("HTML file generated successfully.")
    print("Please also host the 'nav_page.md' file.")

    print("\nAfter you host the page, please visit:")
    print(f"{config['hosting_url']}?md=nav_page.md")

if __name__ == "__main__":
    generate_navigation_page()
