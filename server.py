import time
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
import http.server
import socketserver
from pathlib import Path
import threading

import init

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

class MyEventHandler(FileSystemEventHandler):
    def on_any_event(self, event: FileSystemEvent) -> None:
        # Respond to any file change (created, modified, moved, deleted)
        if not event.is_directory \
            and str(event.src_path) not in [str(Path(__file__).parent / "nav_page.md"), str(Path(__file__).parent / "index.html")]:
            init.generate_navigation_page()
            print(f"Event type: {event.event_type}  Path: {event.src_path}")

# Run HTTP server in a separate thread
def run_http_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

# Start the HTTP server in a thread
server_thread = threading.Thread(target=run_http_server)
server_thread.daemon = True  # Thread will exit when main program exits
server_thread.start()

# Start the file observer
event_handler = MyEventHandler()
observer = Observer()
observer.schedule(event_handler, ".", recursive=True)
observer.start()

# Keep the program running until interrupted
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    print("Observer stopped")

observer.join()