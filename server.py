import threading
import time
from http import server
import socketserver
from pathlib import Path
from typing import Dict, Any

# Third-party imports
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

import init

# Constants
PORT = 8000
IGNORED_FILES = ["nav_page.md", "index.html"]


class FileChangeHandler(FileSystemEventHandler):
    """Handles file system events and regenerates navigation when files change."""
    
    def on_any_event(self, event: FileSystemEvent) -> None:
        """React to file system events by regenerating navigation.
        
        Args:
            event: The file system event that occurred
        """
        # Skip directory events
        if event.is_directory:
            return
            
        # Handle config file changes
        if event.event_type == 'modified' and event.src_path.endswith("setting.json"):
            global config
            config = init.load_config()
            print("Config reloaded")
            
        # Skip ignored files and hidden directories
        path_parts = event.src_path.split("/")
        if (event.src_path.endswith(tuple(IGNORED_FILES)) or 
                any(part.startswith(".") for part in path_parts)):
            return
            
        # Generate navigation page for valid file changes
        init.generate_navigation_page(config=config)
        print(f"Event type: {event.event_type}  Path: {event.src_path}")


def run_http_server(port: int) -> None:
    """Start the HTTP server on the specified port.
    
    Args:
        port: Port number to serve on
    """
    handler = server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()


def main() -> None:
    """Main function to run the server and file watcher."""
    global config
    config = init.load_config()
    
    # Start HTTP server in a separate thread
    server_thread = threading.Thread(target=run_http_server, args=(PORT,))
    server_thread.daemon = True
    server_thread.start()
    
    # Set up and start file system observer
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()
    
    # Keep the program running until interrupted
    try:
        print(f"Server running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nServer stopped")
    
    observer.join()


if __name__ == "__main__":
    main()
