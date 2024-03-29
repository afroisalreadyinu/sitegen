"""
Directory monitory functionality for sitegen
"""
import socketserver
import traceback
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from sitegen.content import generate_site

PORT = 8000


class RequestHandler(SimpleHTTPRequestHandler):
    BASE = None

    def __init__(self, *args, **kwargs):
        kwargs["directory"] = self.BASE
        super().__init__(*args, **kwargs)


class EventHandler(FileSystemEventHandler):
    def __init__(self, basedir, context):
        self.basedir = basedir
        self.context = context

    def dispatch(self, event):
        if (
            event.event_type not in ["created", "modified", "deleted"]
            or event.is_directory
        ):
            return
        eventpath = Path(event.src_path)
        filename = eventpath.name
        if filename.startswith(".#"):
            # Emacs backup file
            return
        relpath = eventpath.relative_to(self.basedir)
        dirname = relpath.parts[0]
        if dirname not in ["content", "templates"]:
            return
        print(f"{dirname.capitalize()} directory changed, regenerating")
        try:
            generate_site(self.basedir, self.context)
        except:  # pylint: disable=bare-except
            print("Error generating site:")
            traceback.print_exc()


def monitor(basedir, context):
    basedirectory = Path(basedir)
    public = basedirectory / "public"

    observer = Observer()
    observer.schedule(EventHandler(basedir, context), basedirectory, recursive=True)
    observer.start()

    RequestHandler.BASE = public
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()
            observer.stop()
